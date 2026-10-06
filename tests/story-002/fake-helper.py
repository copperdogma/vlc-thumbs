#!/usr/bin/python3
"""Owned service fault fixture; input file contains the mode (never real media)."""
import json, os, signal, sys, time
args = dict(zip(sys.argv[1::2], sys.argv[2::2]))
mode = open(args['--input']).read().strip()
if mode == 'hang':
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
    time.sleep(30)
elif mode == 'crash':
    os._exit(2)
elif mode == 'malformed':
    sys.stdout.buffer.write(b'not json\n')
    sys.exit(0)
elif mode == 'oversized':
    sys.stdout.buffer.write(b'x' * 500000)
    sys.exit(0)
elif mode == 'slow':
    time.sleep(.3)
w, h = 320, 180
requested = int(args['--time-us'])
header = dict(version=2, sampling="keyframe", ok=True, requested_us=requested, actual_us=requested,
              width=w, height=h, channels=4, payload_bytes=w*h*4,
              video_ordinal=int(args['--video-ordinal']))
sys.stdout.buffer.write(json.dumps(header).encode() + b'\n' + bytes([40, 80, 120, 255])*(w*h))
