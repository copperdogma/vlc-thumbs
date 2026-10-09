#!/usr/bin/env python3
"""Bounded generated-only AB/BA worker comparison; preserves exclusive NAS copy."""
import hashlib,json,os,select,signal,subprocess,time,uuid,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
RESERVE=1024**3
SOURCE=ROOT/'work/story005-nas-admission001/preparation300s-clusters.mkv'
EXPECTED='b4ec452c1c95b8cc18cd9802617444402a4dc6f2994536584621653cff5c7f8e'
HELPERS={'prior':ROOT/'work/story005-helper9-proof/normal-pre-admission-vlc-timeline-preview','current':ROOT/'work/story005-master-candidate/bin/vlc-timeline-preview'}
HASHES={'prior':'6d90de5bded764f4471d7c70db86fe62da1df72685493d7e93720ab418880483','current':'b2b5e5d13bf6d3e92f9e23193ec516d86b1f54547783fb5c53ce2fbbf6dadf73'}
TARGETS=[0,150125000,299000000]
start=time.monotonic();minimum=shutil.disk_usage(ROOT).free

def guard():
 global minimum
 free=shutil.disk_usage(ROOT).free;minimum=min(minimum,free)
 if free<RESERVE:raise RuntimeError('resource-stop: below1GiB free reserve')
 if time.monotonic()-start>240:raise RuntimeError('budget-stop:240seconds')

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
guard()
for a,p in HELPERS.items():assert digest(p)==HASHES[a],('helper drift',a)
assert digest(SOURCE)==EXPECTED
OUT=ROOT/'work/story005-nas-admission002';OUT.mkdir(exist_ok=False)
NAS=Path('/Volumes/Movies')/('.codex-vlc-story005-admission-'+uuid.uuid4().hex+'.mkv')
record={'scope':'Generated finite228cluster300sremuxfixture; descriptive paired readiness/3persistent requests; not native,cold-cache,p95or causality proof','fixture':{'source':str(SOURCE),'sha256':EXPECTED,'bytes':SOURCE.stat().st_size,'cluster_count':228,'input_id':1,'video_count':1},'helper_hashes':HASHES,'targets_us':TARGETS,'warmth':'Local hash read and NAScopy+hash performed before measurement; no caches flushed; SMB/server/host warmth uncontrolled; user preview remains active,owned baseline terminated','nas_copy':str(NAS),'rows':[],'reserve_bytes':RESERVE,'per_reply_deadline_seconds':15,'total_budget_seconds':240}
def save():
 record['minimum_free_bytes']=minimum
 (OUT/'results.json').write_text(json.dumps(record,indent=2)+'\n')
try:
 guard();copy_start=time.monotonic()
 with NAS.open('xb') as dest, SOURCE.open('rb') as source:shutil.copyfileobj(source,dest,128*1024)
 record['copy_elapsed_ms']=(time.monotonic()-copy_start)*1000
 record['nas_sha256']=digest(NAS);assert record['nas_sha256']==EXPECTED
 st=NAS.stat();record['nas_stat_before']={'bytes':st.st_size,'mtime_ns':st.st_mtime_ns,'inode':st.st_ino,'owner':st.st_uid,'mode':oct(st.st_mode & 0o777)};save()
 def reply(p):
  deadline=time.monotonic()+15
  def read(n):
   b=bytearray()
   while len(b)<n:
    guard();left=deadline-time.monotonic()
    if left<=0:raise TimeoutError('15s response deadline')
    if not select.select([p.stdout],[],[],min(.2,left))[0]:continue
    part=os.read(p.stdout.fileno(),n-len(b))
    if not part:raise EOFError('reply EOF')
    b.extend(part)
   return bytes(b)
  line=bytearray()
  while not line.endswith(b'\n'):
   assert len(line)<4096,'header bound';line.extend(read(1))
  h=json.loads(line);size=h.get('payload_bytes',0)
  assert h['version']==4 and type(size)is int and 0<=size<=320*180*4
  pixels=read(size)
  if size:assert h['ok'] and h['channels']==4 and size==h['width']*h['height']*4
  return dict(h,pixel_sha256=hashlib.sha256(pixels).hexdigest() if pixels else None)
 for medium,path in [('local',SOURCE),('NAS',NAS)]:
  for pair,order in enumerate([['prior','current'],['current','prior'],['prior','current']]):
   for arm in order:
    guard();assert digest(HELPERS[arm])==HASHES[arm]
    row={'medium':medium,'pair':pair,'arm':arm,'requests':[]};record['rows'].append(row);save();p=None
    argv=[str(HELPERS[arm]),'--worker','--input',str(path),'--video-input-id','1','--video-count','1','--max-width','320','--max-height','180'];row['argv']=argv
    with (OUT/(medium+'-'+str(pair)+'-'+arm+'.stderr')).open('wb') as err:
     try:
      t=time.monotonic();p=subprocess.Popen(argv,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=err,bufsize=0,start_new_session=True);row['pid']=p.pid
      h=reply(p);row['ready_ms']=(time.monotonic()-t)*1000;row['ready']=h;save()
      if h.get('type')!='ready' or not h.get('ok'):raise RuntimeError('not ready')
      for i,target in enumerate(TARGETS,1):
       guard();t=time.monotonic();p.stdin.write(f'{i} {target}\n'.encode());h=reply(p);row['requests'].append({'request_id':i,'target_us':target,'elapsed_ms':(time.monotonic()-t)*1000,'header':h});save()
       assert h.get('ok') and h.get('pixel_sha256'),'request failed'
      p.stdin.close();p.wait(timeout=3);row['returncode']=p.returncode
     except Exception as e:
      row['error']=type(e).__name__+': '+str(e)
      if 'resource-stop' in str(e) or 'budget-stop' in str(e):raise
     finally:
      if p:
       try:os.killpg(p.pid,signal.SIGKILL)
       except ProcessLookupError:pass
       p.wait(timeout=3);row['reaped']=True
      save()
 record['nas_stat_after']={'bytes':NAS.stat().st_size,'mtime_ns':NAS.stat().st_mtime_ns,'inode':NAS.stat().st_ino};record['nas_sha256_after']=digest(NAS)
 record['complete']=True
except Exception as e:record['stop_reason']=type(e).__name__+': '+str(e)
finally:
 record['total_elapsed_seconds']=time.monotonic()-start;record['nas_copy_preserved']=NAS.exists();save()
print(json.dumps({'complete':record.get('complete',False),'stop_reason':record.get('stop_reason'),'rows':len(record['rows']),'minimum_free_bytes':minimum,'nas_copy':str(NAS)}),flush=True)
