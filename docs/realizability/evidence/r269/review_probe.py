"""Reproduce the old map-count gap without numerical modules or workloads."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import runpy
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
runner=runpy.run_path(str(HERE.parent/'r265/test_runner.py'))
guard=runner['NoNumericalImports']()
sys.meta_path.insert(0,guard)
try:
    from verification.nonlinear_port import manufactured_angular as current
    from verification.nonlinear_port.test_manufactured_angular import sample,BINDING
    from verification.nonlinear_port.prototype import Refusal
    old_source=subprocess.check_output(['git','show',
        '2c25fc6:verification/nonlinear_port/manufactured_angular.py'],cwd=ROOT,text=True)
    old=dict(__name__='verification.nonlinear_port.r268_angular_review',
             __package__='verification.nonlinear_port')
    exec(compile(old_source,'R268_saved_source','exec'),old)
    item=sample(); bad=deepcopy(item); vm=bad['phi']['velocity_parent_map']; moved=vm[-3:]
    bad['phi']['velocity_parent_map']=vm[:-3]
    bad['phi']['pressure_parent_map']+=moved
    bad['phi']['velocity_node_coordinates'].pop()
    for i in moved: bad['phi']['coefficients'][i]=0.
    for entry in bad['degrees'].values():
        entry['reductions'],entry['comparisons']=current._reductions(
            bad['phi']['coefficients'],entry['raw_residual'],bad['fixed_indices'],
            entry['scalar'],entry['original'])
    assert old['validate_record'](bad,BINDING) is bad
    try: current.validate_record(bad,BINDING)
    except Refusal as exc: refusal=str(exc)
    else: raise AssertionError('invalid map counts accepted')
    current.validate_record(item,BINDING)
    synthetic_bytes=len((json.dumps(item,sort_keys=True,separators=(',',':'),allow_nan=False)+'\n').encode())
    assert synthetic_bytes < current.MAX_BYTES
    loaded=sorted(n for n in sys.modules if n.split('.')[0] in runner['FORBIDDEN'])
    assert not loaded
    result=dict(status='PASS',old_wrong_partition_accepted=True,
        wrong_velocity_count=372,wrong_pressure_count=30,new_refusal=refusal,
        valid_synthetic_json_bytes=synthetic_bytes,actual_runtime_size_unmeasured=True,
        old_source_sha256=hashlib.sha256(old_source.encode()).hexdigest(),
        numerical_modules_loaded=loaded)
    (HERE/'review_probe.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,sort_keys=True))
finally:
    sys.meta_path.remove(guard)
