import sys
import ffmpeg
import sounddevice as sd
import argparse
import queue
def int_or_str(text):
    #helper function to allow passing either device ID (int) or device name (str)
    try:
        return int(text)
    except ValueError:
        return text
#--- parser 1:check for --list-devices before processing main arguments ---
parser=argparse.ArgumentParser(add_help=False)
parser.add_argument("-1","--list-devices",action="store_true",help="show list of audio device and exit")
args,remaining=parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
#--- parser2: main arguments ---
# inherits arguments from the first parser (parents=[parser])
parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter,parents=[parser])
parser.add_argument("url",metavar="URL",help="stream url")
parser.add_argument("-d","--device",type=int_or_str,help="output device (numeric ID or substring)")
parser.add_argument("-b","--blocksize",type=int,default=1024,help="blocksize(default:%(default)s)")
parser.add_argument("-q","--buffersize",type=int,default=20,help="buffersize(default:%(default)s)")
args=parser.parse_args()

#validate inputs to prevent the program from hanging or cashing
if args.blocksize==0:
    parser.error("blocksize must not be zero")
if args.buffersize<1:
    parser.error("buffersize must be at least 1")
#Buffer queue to temporarily  store audio chunks between ffmpeg and sounddevice
q=queue.Queue(maxsize=args.buffersize)
print('get stream information ...')
try:
    #use ffmpeg.probe to get stream metadata(channels, sample rate,etc.)without downloading the whole file
    info=ffmpeg.probe(args.url)
except ffmpeg.Error as e:
    #print the raw ffmpeg error output to stderr for debugging
    sys.stderr.buffer.write(e.stderr)
    parser.exit(1,str(e))
#Extract streams from the metadata
streams=info.get('streams',[])
if len(streams) != 1:
    parser.exit(1,'There must be exactly one stream available' )
stream=streams[0]
# Ensure the stream is audio , not video
if stream.get('codec_type')!="audio":
    parser.exit(1,'the stream must be an audio stream')
# Extract audio properties needed for playback 
channels=stream['channels']
samplerate=float(stream['sample_rate'])
#callback function:sounddevice calls this continuously to get audio chunks
def callback(outdata,frames,time,status):
    assert frames==args.blocksize
    if status.output_underflow:
        print('output underflow:increase blocksize?' ,file=sys.stderr)
        raise sd.CallbackAbort
    assert not status
    try:
        #get the next chunk of audio data from the queue
        data=q.get_nowait()
    except q.Empty as e:
        print('buffer is empty:increase buffersize?' ,file=sys.stderr)
        raise sd.CallbackAbort from e
    #Fill the outdata buffer . If data is shorter (last chunk),pad it with silene(zeros)
    if len(data) < len(outdata):
        outdata[:len(data)] = data
        outdata[len(data):] =b'\x00' * (len(outdata)-len(data))
    else:
        outdata[:] = data
try:
    print('opening stream ...')
    #Run ffmpeg a background process to decode audio and pipe raw float32 data to stdout
    process=ffmpeg.input(args.url).output('pipe:',format='f32le',acodec='pcm_f32le',ac=channels,ar=samplerate,loglevel='quiet').run_async(pipe_stdout=True)
    #create the raw output stream for sounddevice
    stream=sd.RawOutputStream(samplerate=samplerate,blocksize=args.blocksize,device=args.device,channels=channels,dtype="float32",callback=callback)
    #calculate how many bytes to read per block(frames* channels * 4 bytes per float32)
    read_size=args.blocksize * channels * stream.samplesize
    print("buffering ...")
    #pre_fill the queue with initial audio chunks to prevent stuttering 
    for _ in range(args.buffersize):
        q.put_nowait(process.stdout.read(read_size))
    print('starting playback ...')
    with stream:
        #Timeout prevents the program from hanging if the queue stays full for too long
        timeout=args.blocksize * args.buffersize / samplerate 
        while True:
            #Keep reading from ffmpeg and putting into the queue
            #If the queue is full wait up to  "timeout" seconds before raising queue.Full
            q.put(process.stdout.read(read_size),timeout=timeout)
#--- Exception handling--- 
except KeyboardInterrupt:
    #user pressed ctrl+c
    parser.exit(1,'\nInterrupted by user')
except queue.Full:
    #queue was full for longer than the timeout
    parser.exit(1)
except Exception as e:
    #catch any other unexpected errors and print the error type + message
    parser.exit(1,type(e).__name__ +" : " +str(e))
        
        
    
    
    
    