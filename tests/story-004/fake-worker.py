#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-or-later
"""Generated-file protocol faults; never points at user media."""
import hashlib,json,os,sys,time
args=sys.argv[1:]
def out(header,payload=b''):
    sys.stdout.buffer.write(json.dumps(header).encode()+b'\n'+payload);sys.stdout.buffer.flush()
def stat_identity(p):
    s=os.stat(p)
    return f'{s.st_dev}:{s.st_ino}:{s.st_size}:{s.st_mtime_ns//10**9}:{s.st_mtime_ns%10**9}:{s.st_ctime_ns//10**9}:{s.st_ctime_ns%10**9}'
if args[0]=='--fingerprint':
    p=args[args.index('--input')+1]
    if args[1]=='stat' and open(p).read().strip()=='metadata-slow':
        with open(p+'.statcalls','a') as calls:calls.write('stat\n')
        delay_path=p+'.metadata-delay'
        time.sleep(float(open(delay_path).read()) if os.path.isfile(delay_path) else .25)
    identity=stat_identity(p)
    content=identity.encode() if args[1]=='stat' else open(p,'rb').read()
    out(dict(version=3,type='identity',ok=True,fingerprint=hashlib.sha256(content).hexdigest(),policy=args[1],stat_identity=identity,bytes_read=0 if args[1]=='stat' else len(content),read_calls=0 if args[1]=='stat' else 1,payload_bytes=0));sys.exit(0)
p=args[args.index('--input')+1];mode=open(p).read().strip()
if mode=='startup-hang':time.sleep(40)
if mode=='startup-malformed':sys.stdout.write('garbage\n');sys.stdout.flush();sys.exit(0)
out(dict(version=3,type='ready',ok=True,duration_us=90_000_000))
for line in sys.stdin:
    ident,target=map(int,line.split())
    if mode=='slow':time.sleep(.25)
    if mode=='cache-slow':time.sleep(1)
    if mode=='hang':time.sleep(40)
    if mode=='crash':sys.exit(1)
    if mode=='malformed':out(dict(version=3,id=ident,requested_us=target,ok=True,payload_bytes=999999999));continue
    if mode=='fractional':out(dict(version=3.5,id=ident,requested_us=target,ok=True,payload_bytes=0));continue
    if mode=='unsupported':out(dict(version=3,id=ident,requested_us=target,ok=False,payload_bytes=0,error='unsupported_codec'));continue
    if mode=='fail-once' and ident==1:
        out(dict(version=3,id=ident,requested_us=target,ok=False,payload_bytes=0,error='read_failed'));continue
    if mode=='mutating':time.sleep(.25)
    actual=target//2_000_000*2_000_000
    w,h=64,36;pixels=bytes([30,90,160,255])*(w*h)
    out(dict(version=3,id=ident,ok=True,sampling='keyframe',requested_us=target,actual_us=actual,width=w,height=h,channels=4,payload_bytes=len(pixels),video_ordinal=0,open_count=1),pixels)
