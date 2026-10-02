"""Fixed independent authority: trusted candidate code, bounded by controller."""
import importlib.util, json, platform, sys, time, hashlib
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
def load(path):
    spec=importlib.util.spec_from_file_location('candidate', path)
    mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod.solve
def oracle():
    square=total=0; values=[0]
    for k in range(1,1001):
        square += 2*k-1; total += square; values.append(total)
    return values
def check(fn):
    values=oracle()
    for n, expected in enumerate(values):
        try: got=fn(n)
        except Exception as e: return {'passed':False,'n':n,'error':type(e).__name__}
        if type(got) is not int or got != expected:
            return {'passed':False,'n':n,'expected':expected,'actual':repr(got)}
    for n in (-1,1001,True,1.0,'1',None):
        try: fn(n)
        except ValueError: continue
        except Exception: return {'passed':False,'invalid_input':repr(n)}
        return {'passed':False,'accepted_invalid':repr(n)}
    return {'passed':True,'cases':1001,'invalid_cases':6}
def validate():
    values=oracle()
    assert {n:values[n] for n in (0,1,2,3,10,1000)} == {0:0,1:1,2:5,3:14,10:385,1000:333833500}
    assert check(load(ROOT/'candidates/baseline.py'))['passed']
    assert check(load(ROOT/'candidates/closed_form.py'))['passed']
    assert not check(load(ROOT/'candidates/wrong.py'))['passed']
    assert not check(lambda n:0)['passed']
    assert not check(lambda n:n*(n+1)*(2*n+1)/6)['passed']
    return {'hand_cases':6,'domain_cases':1001,'defects_rejected':3,'passed':True}
def measure(path):
    fn=load(path); correctness=check(fn)
    result={'mode':'real','correctness':correctness,'pairs':[],'unit':'ns/call','uncertainty':'descriptive paired block range; no inferential CI','source_sha256':hashlib.sha256(Path(path).read_bytes()).hexdigest(),'python':sys.version,'platform':platform.platform()}
    if not correctness['passed']: return result
    baseline=load(ROOT/'candidates/baseline.py'); workload=[0,1,10,100,500,1000]*100
    def block(f):
        total=0; start=time.perf_counter_ns()
        for n in workload: total+=f(n)
        return (time.perf_counter_ns()-start)/len(workload), total
    block(baseline); block(fn)
    for i in range(6):
        a,b=(block(baseline),block(fn)) if i%2==0 else (None,None)
        if i%2: b=block(fn); a=block(baseline)
        assert a[1]==b[1]
        result['pairs'].append({'baseline':a[0],'candidate':b[0],'ratio':b[0]/a[0],'order':'AB' if i%2==0 else 'BA'})
    ratios=[p['ratio'] for p in result['pairs']]
    result['ratio_range']=[min(ratios),max(ratios)]
    result['supported']=all(r<0.95 for r in ratios)
    return result
if __name__=='__main__':
    print(json.dumps(validate() if sys.argv[1]=='validate' else measure(Path(sys.argv[1]))))
