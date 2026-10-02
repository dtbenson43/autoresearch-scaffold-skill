"""Reproducible, bounded Linux/macOS integration checks; no model or network calls."""
import fcntl, hashlib, json, os, shutil, subprocess, sys, tempfile
from pathlib import Path
SOURCE=Path(__file__).resolve().parent

def run(root,*args,expected=0,crash=None):
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
    if crash: env['RESEARCH_CRASH']=crash
    p=subprocess.run([sys.executable,str(root/'research'),*args],cwd='/',env=env,capture_output=True,text=True,timeout=25)
    assert p.returncode==expected,(args,p.returncode,p.stderr)
    return json.loads(p.stdout) if p.stdout.strip() else None

def snapshot(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def fresh(path):
    path.mkdir()
    for name in ('research','research.config.json','RESEARCH.md'):
        shutil.copy2(SOURCE/name,path/name)
    for name in ('runtime','candidates'):
        shutil.copytree(SOURCE/name,path/name,ignore=shutil.ignore_patterns('__pycache__'))
    (path/'logs').mkdir()
    run(path,'init')
    return path

def main():
    checks=[]
    with tempfile.TemporaryDirectory() as tmp:
        root=fresh(Path(tmp)/'real')
        before=snapshot(root); run(root,'status'); assert snapshot(root)==before
        checks.append('read-only status and invocation from other cwd')
        stages=[]
        for _ in range(7):
            prior=run(root,'status'); result=run(root,'step'); after=run(root,'status')
            assert len(after['attemptIds'])==len(prior['attemptIds'])+1
            stages.append(result)
        assert stages[1]['outcome']=='incorrect'
        assert stages[2]['outcome']=='reject'
        assert stages[-1]['outcome'] in ('accept','inconclusive')
        run(root,'step',expected=2)
        checks.append('one stage per call, wrong candidate rejected, genuine measurements and separate confirmation, bounded stop')
        state=run(root,'status'); ev=[]
        for x in state['history']:
            for a in x['artifacts']:
                if a['path'].endswith('output.json'):
                    d=json.loads((root/a['path']).read_text())
                    if d.get('pairs'): ev.append(d)
        assert len(ev)==2 and all(len(d['pairs'])==6 for d in ev)
        assert ev[0]['invocationId']!=ev[1]['invocationId']
        summary={'real_decision':stages[-1]['outcome'],'exploration_ratio_range':ev[0]['ratio_range'],'confirmation_ratio_range':ev[1]['ratio_range']}
        with (root/'.writer.lock').open('a') as handle:
            fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
            before=snapshot(root); run(root,'step',expected=3); assert snapshot(root)==before
        checks.append('single-writer lock contention')
        limited=fresh(Path(tmp)/'limited')
        run(limited,'step')
        usage=json.loads((limited/'usage.json').read_text()); usage['evaluatorCalls']=8
        (limited/'usage.json').write_text(json.dumps(usage))
        run(limited,'step',expected=3)
        blocked=run(limited,'status')
        assert blocked['experiment']['stage']=='measure' and blocked['experiment']['activeAttempt'] is None
        assert json.loads((limited/'usage.json').read_text())['evaluatorCalls']==8
        checks.append('persisted evaluator reservation cap blocks another invocation')
        for point,code in [('before_commit',81),('after_commit',82)]:
            case=fresh(Path(tmp)/point)
            run(case,'step',expected=code,crash=point)
            s=run(case,'status'); pending=s['experiment']['activeAttempt']
            assert bool(pending)==(point=='before_commit')
            count=len(s['attemptIds']); run(case,'recover'); recovered=run(case,'status')
            assert len(recovered['attemptIds'])==count
            assert recovered['experiment']['activeAttempt'] is None
            assert recovered['experiment']['stage']==('build' if point=='before_commit' else 'measure')
            run(case,'step')
            if point=='before_commit': assert run(case,'status')['experiment']['buildRevision']==2
        checks.append('before/after completion interruption, recovery, no rerun of committed build')
        # Commit a candidate decision but intentionally omit derived view refresh.
        case=fresh(Path(tmp)/'promotion')
        for _ in range(6): run(case,'step')
        run(case,'step',expected=82,crash='after_commit')
        committed=run(case,'status'); attempts=len(committed['attemptIds'])
        run(case,'recover'); final=run(case,'status')
        assert final['currentCandidate']==committed['currentCandidate'] and len(final['attemptIds'])==attempts
        assert not final['viewsStale']
        checks.append('committed decision recovered without repeating measurement or decision')
        # Protocol-only mock scenario; these values never enter real measurements.
        mock=json.loads((SOURCE.parents[1]/'references/fixtures/inconclusive_remeasure.expected.json').read_text())
        actual=run(root,'replay',str(SOURCE.parents[1]/'references/fixtures/inconclusive_remeasure.jsonl'))
        assert actual==mock
        checks.append('isolated synthetic inconclusive/re-measure replay')
    print(json.dumps({'passed':len(checks),'checks':checks,**summary},indent=2))
if __name__=='__main__': main()
