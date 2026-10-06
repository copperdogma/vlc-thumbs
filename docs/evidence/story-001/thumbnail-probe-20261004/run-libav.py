import pathlib,subprocess,json,shlex,os,hashlib,time
root=pathlib.Path(__file__).resolve().parent
repo=root.parents[2]
prefix=repo/'work/build/vlc-source/contrib/aarch64-apple-darwin27'
source=repo/'work/build/vlc-source/contrib/contrib-aarch64-apple-darwin27/ffmpeg'
env=dict(os.environ,PKG_CONFIG_LIBDIR=str(prefix/'lib/pkgconfig'),PKG_CONFIG_PATH='')
commands=[]
def run(args,timeout=45):
 begin=time.monotonic();p=subprocess.run(args,env=env,capture_output=True,text=True,timeout=timeout)
 commands.append(dict(argv=args,returncode=p.returncode,elapsed_seconds=time.monotonic()-begin,stdout=p.stdout,stderr=p.stderr))
 (root/'libav-commands.json').write_text(json.dumps(commands,indent=2))
 if p.returncode:raise RuntimeError(p.stderr)
 return p.stdout
flags=shlex.split(run(['pkg-config','--static','--cflags','--libs','libavformat','libavcodec','libavutil','libswscale']))
run(['xcrun','clang','-arch','arm64','-mmacosx-version-min=11.0','-Os','-Wl,-dead_strip','-Wl,-S',str(root/'libav-probe.c'),'-o',str(root/'libav-probe'),*flags])
run(['strip','-x',str(root/'libav-probe')])
results=[]
for path in [root/'known-h264.mp4',root/'known-h264.mkv',repo/'work/fixtures/build-smoke.mp4']:
 r=json.loads(run([str(root/'libav-probe'),str(path)]));r['input']=str(path);results.append(r)
(root/'libav-results.json').write_text(json.dumps(results,indent=2))
inventory={name:run(args) for name,args in {'dependencies':['otool','-L',str(root/'libav-probe')],'deployment':['otool','-l',str(root/'libav-probe')],'architecture':['file',str(root/'libav-probe')]}.items()}
inventory['configuration']=str(source/'vlc_build/ffbuild/config.mak')
inventory['sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [root/'libav-probe.c',root/'run-libav.py',root/'libav-probe',root/'libav-results.json']}
inventory['size_bytes']=(root/'libav-probe').stat().st_size
(root/'libav-inventory.json').write_text(json.dumps(inventory,indent=2))
print(json.dumps({'results':results,'inventory':inventory},indent=2))
