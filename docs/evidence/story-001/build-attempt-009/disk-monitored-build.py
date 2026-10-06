from pathlib import Path
import subprocess,os,time,shutil,json,signal
root=Path('/Users/cam/Documents/Projects/ultima-iv-web/vlc-thumbs')
workspace=root/'work/build';source=workspace/'vlc-source';build=workspace/'vlc-arm64'
evidence=root/'docs/evidence/story-001/build-attempt-009'
cmd=['bash',str(source/'extras/package/macosx/build.sh'),'-a','aarch64','-c','-j','4','-C',str(build)]
env=os.environ.copy();env['VLC_PATH']='/usr/local/bin';env['PKG_CONFIG_LIBDIR']=str(source/'contrib/aarch64-apple-darwin27/lib/pkgconfig');env['PKG_CONFIG_PATH']='';env['ACLOCAL_PATH']='/usr/local/share/aclocal';env['VLC_CONFIGURE_ARGS']='--disable-sparkle'
start=time.time();initial=shutil.disk_usage(root).free;minimum=initial
record={'date':'2026-10-04','source_revision':'6de05adcbaf2e8b85fe86aad4169393098628119','command':cmd,'cwd':str(workspace),'environment_overrides':{'VLC_PATH':'/usr/local/bin','PKG_CONFIG_LIBDIR':env['PKG_CONFIG_LIBDIR'],'PKG_CONFIG_PATH':'','ACLOCAL_PATH':'/usr/local/share/aclocal','VLC_CONFIGURE_ARGS':'--disable-sparkle'},'initial_free_bytes':initial,'disk_stop_floor_bytes':1024**3,'status':'running'}
(evidence/'attempt.json').write_text(json.dumps(record,indent=2)+'\n')
with (evidence/'build.log').open('w') as log:
 proc=subprocess.Popen(cmd,cwd=workspace,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
 print(f'Build started, PID {proc.pid}; free space {initial/1024**3:.2f} GiB',flush=True)
 stopped=False;last=0
 while proc.poll() is None:
  free=shutil.disk_usage(root).free;minimum=min(minimum,free)
  if free<1024**3:
   stopped=True;os.killpg(proc.pid,signal.SIGTERM)
   try:proc.wait(timeout=10)
   except subprocess.TimeoutExpired:os.killpg(proc.pid,signal.SIGKILL);proc.wait()
   break
  if time.time()-last>=30:
   usage=subprocess.run(['du','-sk',str(workspace)],capture_output=True,text=True)
   size=int(usage.stdout.split()[0])*1024 if usage.returncode==0 else None
   record.update(elapsed_seconds=round(time.time()-start,1),minimum_free_bytes=minimum,workspace_bytes=size,pid=proc.pid)
   (evidence/'attempt.json').write_text(json.dumps(record,indent=2)+'\n')
   print(f'Running {record["elapsed_seconds"]:.0f}s; free {free/1024**3:.2f} GiB; workspace {(size or 0)/1024**2:.0f} MiB',flush=True);last=time.time()
  time.sleep(2)
 record.update(status='stopped-low-disk' if stopped else 'finished',exit_code=proc.returncode,elapsed_seconds=round(time.time()-start,1),minimum_free_bytes=minimum)
 usage=subprocess.run(['du','-sk',str(workspace)],capture_output=True,text=True)
 record['workspace_bytes_before_cleanup']=int(usage.stdout.split()[0])*1024 if usage.returncode==0 else None
 if stopped:
  assert workspace==root/'work/build' and workspace.is_dir()
  shutil.rmtree(workspace)
  record['cleanup']='Removed only project-owned work/build attempt directory; pristine upstream checkout and evidence preserved.'
 record['final_free_bytes']=shutil.disk_usage(root).free
 (evidence/'attempt.json').write_text(json.dumps(record,indent=2)+'\n')
 print(json.dumps(record,indent=2),flush=True)
