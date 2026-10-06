import subprocess, pathlib, json, hashlib, time
root = pathlib.Path(__file__).resolve().parent
repo = root.parents[2]
events = []
def run(argv, timeout=40):
    begin = time.monotonic()
    p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    events.append(dict(argv=argv, elapsed_seconds=time.monotonic()-begin, returncode=p.returncode, stderr=p.stderr, stdout=p.stdout))
    (root/'commands.json').write_text(json.dumps(events,indent=2))
    if p.returncode: raise RuntimeError(p.stderr)
    return p.stdout
ff = '/usr/local/bin/ffmpeg'
run([ff,'-version'])
vf = "drawtext=fontfile=/System/Library/Fonts/Supplemental/Arial.ttf:text='frame %{n}  t %{pts\\:hms}':x=8:y=8:fontsize=18:fontcolor=white:box=1:boxcolor=black@0.8"
run([ff,'-hide_banner','-loglevel','error','-f','lavfi','-i','testsrc2=size=320x180:rate=24','-t','8','-vf',vf,'-an','-c:v','libx264','-preset','veryfast','-crf','22','-g','48','-pix_fmt','yuv420p','-movflags','+faststart',str(root/'known-h264.mp4')])
run([ff,'-hide_banner','-loglevel','error','-i',str(root/'known-h264.mp4'),'-map','0:v:0','-c','copy',str(root/'known-h264.mkv')])
run(['xcrun','clang','-fobjc-arc','-fblocks','-Wno-deprecated-declarations',str(root/'probe.m'),'-framework','Foundation','-framework','AVFoundation','-framework','CoreMedia','-framework','CoreGraphics','-framework','ImageIO','-framework','CoreServices','-o',str(root/'probe')])
inputs = [root/'known-h264.mp4',root/'known-h264.mkv',repo/'work/fixtures/build-smoke.mp4']
results = []
for media in inputs:
    results.append(json.loads(run([str(root/'probe'),str(media),str(root)],timeout=30)))
(root/'results.json').write_text(json.dumps(results,indent=2))
manifest = {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [*inputs,root/'probe.m',root/'run.py',root/'probe',root/'results.json']}
(root/'sha256.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps(results,indent=2))
print(json.dumps({'files':len(list(root.iterdir())),'total_bytes':sum(p.stat().st_size for p in root.iterdir() if p.is_file()),'sha256':manifest},indent=2))
