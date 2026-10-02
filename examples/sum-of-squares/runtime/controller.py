#!/usr/bin/env python3
import contextlib, fcntl, hashlib, json, os, platform, subprocess, sys, time, uuid
from pathlib import Path
from protocol import replay, ProtocolError
ROOT=Path(__file__).resolve().parents[1]
LOG=ROOT/'research.log.jsonl'
def js(value): return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False)
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def syncdir(path):
    fd=os.open(path,os.O_RDONLY); os.fsync(fd); os.close(fd)
def publish(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f: f.write(data); f.flush(); os.fsync(f.fileno())
    syncdir(path.parent)
    return {'path':str(path.relative_to(ROOT)),'sha256':digest(path)}
def state(): return replay(LOG.read_bytes())
def append(kind,**fields):
    seq=state()['seq']+1 if LOG.exists() else 1
    e={'v':2,'seq':seq,'id':uuid.uuid4().hex,'type':kind,**fields}
    old=LOG.read_bytes() if LOG.exists() else b''
    data=(js(e)+'\n').encode(); replay(old+data)
    with LOG.open('ab') as f: f.write(data); f.flush(); os.fsync(f.fileno())
    syncdir(ROOT)
def refs(s):
    for x in [*s['history'],s['experiment']]:
        if x:
            yield from x['artifacts']
def integrity(s):
    ready=json.loads((ROOT/'initialization.json').read_text())
    for a in ready['manifest']+list(refs(s)):
        p=ROOT/a['path']
        if p.is_symlink() or not p.resolve().is_relative_to(ROOT) or digest(p)!=a['sha256']: raise ValueError('integrity: '+a['path'])
def view(s):
    body='# Results (derived from committed JSON)\n\nCurrent: '+s['currentCandidate']['id']+'\n\n'
    for x in s['history']+([s['experiment']] if s['experiment'] else []):
        body+=f"- {x['experimentId']}: {x['lastOutcome']}, promoted={x['promoted']}, mode={x['mode']}\n"
    for name,data in [('current.json',js(s['currentCandidate'])),('RESULTS.md',body)]:
        p=ROOT/name; temp=ROOT/(name+'.tmp'); temp.write_text(data); os.replace(temp,p)
def run_eval(argument,tag):
    (ROOT/'logs').mkdir(exist_ok=True)
    # Persist conservative reservations before invocation; interrupted calls stay charged.
    cfg=json.loads((ROOT/'research.config.json').read_text())
    ledger=ROOT/'usage.json'
    usage=json.loads(ledger.read_text()) if ledger.exists() else {'evaluatorCalls':0,'startedAt':time.time()}
    if usage['evaluatorCalls']>=cfg['maxEvaluatorCalls']: raise ValueError('evaluator budget exhausted')
    if time.time()-usage['startedAt']>=cfg['maxWallSeconds']: raise ValueError('wall budget exhausted')
    usage['evaluatorCalls']+=1
    tmp=ROOT/'usage.tmp'
    with tmp.open('w') as f: f.write(js(usage)); f.flush(); os.fsync(f.fileno())
    os.replace(tmp,ledger); syncdir(ROOT)
    start=time.monotonic()
    try:
        p=subprocess.run([sys.executable,str(ROOT/'runtime/evaluator.py'),str(argument)],cwd=ROOT,capture_output=True,timeout=15)
    except subprocess.TimeoutExpired as e:
        (ROOT/'logs'/f'{tag}.stderr').write_text('timeout'); raise ValueError('evaluator timeout') from e
    (ROOT/'logs'/f'{tag}.stdout').write_bytes(p.stdout); (ROOT/'logs'/f'{tag}.stderr').write_bytes(p.stderr)
    if p.returncode: raise ValueError('evaluator process failed')
    out=json.loads(p.stdout)
    if type(out) is not dict: raise ValueError('malformed evaluator output')
    out['invocationId']=tag; out['wallSeconds']=time.monotonic()-start
    return out
@contextlib.contextmanager
def lock():
    with (ROOT/'.writer.lock').open('a') as f:
        try: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError: raise ValueError('busy')
        yield

def initialize():
    if LOG.exists(): raise ValueError('already initialized')
    checked=run_eval('validate','init-validation')
    pilot=run_eval(ROOT/'candidates/baseline.py','init-pilot')
    manifest=[{'path':str(p.relative_to(ROOT)),'sha256':digest(p)} for p in sorted([*ROOT.glob('candidates/*.py'),ROOT/'runtime/evaluator.py',ROOT/'research.config.json',ROOT/'RESEARCH.md'])]
    report={'mode':'real','backendReady':False,'measurementReady':True,'validation':checked,'baselinePilot':pilot,'manifest':manifest,'environment':{'python':sys.version,'platform':platform.platform(),'cpu':platform.processor()},'canonicalEncoding':'UTF-8 sorted keys compact JSON; exact file bytes SHA-256'}
    publish(ROOT/'initialization.json',(js(report)+'\n').encode())
    cfg=json.loads((ROOT/'research.config.json').read_text())
    append('initialized',workflow=cfg['workflow'],baseline={'id':'baseline','mode':'real'}); view(state())

def recover():
    s=state(); integrity(s); x=s['experiment']
    if x and x['activeAttempt']:
        # Evaluator is synchronous, bounded and has no external side effects. Recovery
        # is invoked only after the old controller process has exited and lock released.
        append('stage_interrupted',experimentId=x['experimentId'],stage=x['stage'],attemptId=x['activeAttempt'],buildRevision=x['buildRevision'],reason='operator recovery after terminated controller; local evaluator side effects are logs only')
    view(state())

def evidence(x):
    return [json.loads((ROOT/a['path']).read_text()) for a in x['artifacts'] if a['path'].endswith('.json')]
def step():
    s=state(); integrity(s)
    if s['experiment'] and s['experiment']['activeAttempt']: raise ValueError('pending attempt: use recover after old process exits')
    x=s['experiment']
    if x and x['stage'] is None:
        append('experiment_closed',experimentId=x['experimentId'],outcome=x['lastOutcome']); s=state(); x=None
    cfg=json.loads((ROOT/'research.config.json').read_text())
    if len(s['attemptIds'])>=cfg['maxAttempts']: raise ValueError('budget exhausted')
    if x is None:
        if len(s['history'])>=cfg['maxExperiments']: view(s); return {'stopped':True}
        candidate=['wrong','closed_form'][len(s['history'])]
        append('experiment_started',experimentId='x'+str(len(s['history'])+1),candidateId=candidate,parentId=s['currentCandidate']['id'],mode='real')
        x=state()['experiment']
    stage=x['stage']; attempt=uuid.uuid4().hex; rev=x['buildRevision']+(stage=='build')
    shared={'experimentId':x['experimentId'],'stage':stage,'attemptId':attempt,'buildRevision':rev}
    append('stage_started',**shared)
    dest=ROOT/'experiments'/x['experimentId']/attempt
    artifacts=[]; promote=False
    try:
        if stage=='build':
            source=ROOT/'candidates'/(x['candidateId']+'.py')
            artifacts.append(publish(dest/'candidate.py',source.read_bytes()))
            data={'builder':'deterministic test fixture import','agentGenerated':False,'observationMode':'real','candidateSnapshot':artifacts[0],'parentId':x['parentId'],'buildRevision':rev}; outcome='built'
        elif stage in ('measure','confirm'):
            candidate=next(ROOT/a['path'] for a in x['artifacts'] if a['path'].endswith('candidate.py'))
            data=run_eval(candidate,attempt)
            data.update(parentId=x['parentId'],buildRevision=rev,batchId=attempt,stage=stage)
            outcome=('measured' if data['correctness']['passed'] else 'incorrect') if stage=='measure' else 'confirmed'
        else:
            ev=evidence(x); measurements=[e for e in ev if e.get('mode')=='real']
            correct=all(e['correctness']['passed'] for e in measurements)
            supported=len(measurements)==2 and all(e.get('supported') for e in measurements)
            same=len({e['source_sha256'] for e in measurements})==1
            promote=correct and supported and same and x['parentId']==s['currentCandidate']['id']
            outcome='accept' if promote else ('reject' if not correct else 'inconclusive')
            data={'outcome':outcome,'controllerComputed':True,'evidence':x['artifacts'],'correct':correct,'supported':supported,'sameSnapshot':same,'mode':'real'}
        artifacts.append(publish(dest/'output.json',(js(data)+'\n').encode()))
    except Exception as e:
        append('stage_failed',**shared,reason=str(e)); raise
    if os.environ.get('RESEARCH_CRASH')=='before_commit': os._exit(81)
    append('stage_completed',**shared,outcome=outcome,nextStage=cfg['workflow']['edges'][stage][outcome],artifacts=artifacts,promote=promote)
    if os.environ.get('RESEARCH_CRASH')=='after_commit': os._exit(82)
    view(state()); return {'attemptedStage':stage,'outcome':outcome,'promoted':promote}

def main():
    command=sys.argv[1] if len(sys.argv)>1 else 'status'
    if command=='replay': print(js(replay(Path(sys.argv[2]).read_bytes()))); return 0
    if command in ('init','step','continue','recover'):
        with lock():
            result=initialize() if command=='init' else recover() if command=='recover' else step()
        print(js(result or {'ok':True})); return 2 if result and result.get('stopped') else 0
    if command=='describe': print((ROOT/'RESEARCH.md').read_text()); return 0
    if command=='doctor': print(js({'backendReady':False,'measurementRuntime':sys.version,'lock':'fcntl','timeoutSeconds':15})); return 0
    s=state()
    if command in ('validate','status'): integrity(s)
    if command=='status':
        p=ROOT/'current.json'; s['viewsStale']=not p.exists() or json.loads(p.read_text())!=s['currentCandidate']
        s['backendReady']=False
    if command=='history': s=s['history']
    if command=='inspect': s={'state':s,'initialization':json.loads((ROOT/'initialization.json').read_text()),'evidence':[{'ref':a,'content':json.loads((ROOT/a['path']).read_text())} for a in refs(s) if a['path'].endswith('.json')]}
    if command not in ('status','history','inspect','validate'): raise ValueError('unknown command')
    print(js(s)); return 0
if __name__=='__main__':
    try: sys.exit(main())
    except (ValueError,OSError,ProtocolError) as e: print(str(e),file=sys.stderr); sys.exit(3)
