#!/usr/bin/env python3
# SPDX-License-Identifier: LGPL-2.1-or-later
"""Generate fresh synthetic MP4 timeline controls; never modify existing media."""
import argparse, hashlib, json, shutil, struct, subprocess
from pathlib import Path

CONTAINERS = {b'moov', b'trak', b'mdia', b'minf', b'stbl', b'edts'}
def boxes(data):
    result=[]; offset=0
    while offset < len(data):
        if len(data)-offset < 8: raise ValueError('trailing box bytes')
        size, kind=struct.unpack_from('>I4s',data,offset)
        if size<8 or offset+size>len(data): raise ValueError('unsupported box bounds')
        body=data[offset+8:offset+size]
        result.append([kind, boxes(body) if kind in CONTAINERS else body])
        offset+=size
    return result

def encode(nodes):
    output=b''
    for kind,body in nodes:
        body=encode(body) if isinstance(body,list) else body
        output+=struct.pack('>I4s',len(body)+8,kind)+body
    return output

def find(nodes,kind):
    return next(node for node in nodes if node[0]==kind)

def duration(node,value):
    kind,body=node
    if body[0]!=0: raise ValueError('fixture requires version-zero timing headers')
    offset=20 if kind==b'tkhd' else 16
    body=bytearray(body);struct.pack_into('>I',body,offset,value);node[1]=bytes(body)

def edit(source, destination, segments):
    tree=boxes(source.read_bytes())
    kinds=[node[0] for node in tree]
    # Encode after mdat: changing moov size cannot invalidate chunk offsets.
    if kinds.index(b'moov')<kinds.index(b'mdat'): raise ValueError('moov must follow mdat')
    moov=find(tree,b'moov')[1]; trak=find(moov,b'trak')[1]
    movie_scale=struct.unpack_from('>I',find(moov,b'mvhd')[1],12)[0]
    media_scale=struct.unpack_from('>I',find(find(trak,b'mdia')[1],b'mdhd')[1],12)[0]
    edts=next((n for n in trak if n[0]==b'edts'),None)
    if edts is None: edts=[b'edts',[]];trak.append(edts)
    elst=next((n for n in edts[1] if n[0]==b'elst'),None)
    origin=0
    if elst:
        if elst[1][0]!=0: raise ValueError('fixture requires version-zero edit')
        count=struct.unpack_from('>I',elst[1],4)[0]
        if count!=1: raise ValueError('base must have at most one edit')
        origin=struct.unpack_from('>i',elst[1],12)[0]
        if origin<0: raise ValueError('base edit must be nonempty')
    else: elst=[b'elst',b''];edts[1].append(elst)
    entries=[]
    for start,length,rate in segments:
        entries.append((round(length*movie_scale), origin+round(start*media_scale),rate,0))
    elst[1]=b'\0\0\0\0'+struct.pack('>I',len(entries))+b''.join(struct.pack('>Iihh',*entry) for entry in entries)
    total=sum(entry[0] for entry in entries)
    duration(find(moov,b'mvhd'),total);duration(find(trak,b'tkhd'),total)
    destination.write_bytes(encode(tree))
    return {'movie_timescale':movie_scale,'media_timescale':media_scale,'base_edit_media_time':origin,'entries':entries,'segments_source_seconds':segments}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--ffmpeg',default='ffmpeg');p.add_argument('--ffprobe',default='ffprobe')
    args=p.parse_args()
    if args.output.exists():p.error('output already exists')
    tools={name:shutil.which(getattr(args,name)) for name in ['ffmpeg','ffprobe']}
    if not all(tools.values()):p.error('FFmpeg/ffprobe required')
    if shutil.disk_usage(args.output.parent).free<1024**3:p.error('need 1 GiB reserve')
    args.output.mkdir();out=args.output.resolve();commands=[]
    def run(tool,argv,stdout=None):
        commands.append({'tool':tool,'argv':argv,'stdout':stdout})
        with (out/'stderr.log').open('ab') as log:
            if stdout:
                with (out/stdout).open('xb') as dest:subprocess.run([tools[tool]]+argv,cwd=out,stdout=dest,stderr=log,check=True,timeout=45)
            else:subprocess.run([tools[tool]]+argv,cwd=out,stdout=subprocess.DEVNULL,stderr=log,check=True,timeout=45)
        if sum(x.stat().st_size for x in out.iterdir() if x.is_file())>64*1024*1024:raise RuntimeError('64 MiB fixture limit')
    base=['-nostdin','-hide_banner','-loglevel','error','-n','-f','lavfi','-i','testsrc2=size=320x180:rate=24:duration=12','-c:v','libx264','-preset','veryfast','-crf','23','-pix_fmt','yuv420p','-threads','2','-g','240','-keyint_min','240','-sc_threshold','0','-bf','3','-b_strategy','0']
    run('ffmpeg',base+['base.mp4'])
    run('ffmpeg',base+['-movflags','+negative_cts_offsets','negative-ctts.mp4'])
    records=[]
    for name,src,segments in [
        ('nonkeyframe-trim.mp4','base.mp4',[(3.25,8,1)]),
        ('two-edits.mp4','base.mp4',[(3.25,3,1),(7.25,3,1)]),
        ('negative-ctts-trim.mp4','negative-ctts.mp4',[(3.25,8,1)]),
        ('dwell-control.mp4','base.mp4',[(3.25,1,0)])]:
        details=edit(out/src,out/name,segments)
        records.append({'name':name,'source':src,**details})
    for name in ['base.mp4','negative-ctts.mp4']+[r['name'] for r in records]:
        run('ffprobe',['-v','error','-show_streams','-show_format','-of','json',name],name+'.probe.json')
        run('ffprobe',['-v','error','-select_streams','v','-show_packets','-show_data_hash','md5','-of','json',name],name+'.packets.json')
        run('ffprobe',['-v','error','-select_streams','v','-show_frames','-of','json',name],name+'.frames.json')
    manifest={'schema':'story005-mp4-experiment-v1','tools':{k:subprocess.check_output([v,'-version'],text=True) for k,v in tools.items()},'commands':commands,'fixtures':records,'files':{x.name:hashlib.sha256(x.read_bytes()).hexdigest() for x in out.iterdir() if x.is_file()},'limits':{'aggregate_bytes':64*1024*1024,'command_seconds':45},'oracle':'FFprobe packet MD5 and PTS/DTS; FFmpeg independent edit-list interpretation. Source samples generated by testsrc2. Dwell control is diagnostic, not acceptance.'}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
if __name__=='__main__':main()
