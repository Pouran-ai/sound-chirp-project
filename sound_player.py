import sys
import threading
import soundfile as sf
import sounddevice as sd
import argparse
import queue
def int_or_str(text):
    try:
        return int(text)
    except ValueError:
        return text
parser=argparse.ArgumentParser(add_help=False)
parser.add_argument("-1","--list-devices",action="store_true",help="show list of audio device and exit")
args,remaining=parser.parse_known_args()
if args.list_devices:
    print(sd.query_devices())
    parser.exit(0)
parser=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter,parents=[parser])
parser.add_argument("filename",metavar="FILENAME",help="audio file to play")
parser.add_argument("-d","--device",type=int_or_str,help="output device (numeric ID or substring)")
parser.add_argument("-b","--blocksize",type=int,default=2048,help="blocksize(default:%(default)s)")
parser.add_argument("-q","--buffersize",type=int,default=20,help="buffersize(default:%(default)s)")
args=parser.parse_args()
if args.blocksize==0:
    parser.error("blocksize must not be zero")
if args.buffersize<1:
    parser.error("buffersize must be at least 1")
q=queue.Queue(maxsize=args.buffersize)
event=threading.Event()
def callback(outdata,frames,time,status):
    assert frames==args.blocksize
    if status.output_underflow:
        print("output underflow:increase blocksize?",file=sys.stderr)
        raise sd.CallbackAbort
    assert not status
    try:
        data=q.get_nowait()
    except q.Empty as e:
        print("buffer is empty: increase buffersize",file=sys.stderr)
        raise sd.CallbackAbort from e
    if len(data) < len(outdata):
        outdata[:len(data)]=data
        outdata[len(data):].fill(0)
        raise sd.CallbackStop
    else:
        outdata[:]=data.reshape(-1,1)
try:
    with sf.SoundFile(args.filename) as f:
        for _ in range(args.buffersize):
            data=f.read(args.blocksize)
            if not len(data):
                break
            q.put_nowait(data)
        stream=sd.OutputStream(samplerate=f.samplerate,blocksize=args.blocksize,device=args.device,channels=f.channels,callback=callback,finished_callback=event.set)  
        with stream:
            timeout=args.blocksize*args.buffersize/f.samplerate
            while len(data):
                data=f.read(args.blocksize) 
                q.put(data,timeout=timeout)
            event.wait()
except KeyboardInterrupt:
    parser.exit(1,'\nInterrupted by user')
except queue.Full:
    parser.exit
except Exception as e:
    parser.exit(1,type(e).__name__ +" : " +str(e))