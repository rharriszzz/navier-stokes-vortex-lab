"""Release-relative changes, independent numerical variations and definition sensitivity."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from .ring_concentration import PRIMARY

METRICS=('aeff_m2','ellipse_m2','minor_m','major_m','r25_m','r50_m','r75_m')


def read(path):
    data=defaultdict(list)
    with path.open() as f:
        for row in csv.DictReader(f):
            data[row['definition'],row['metric']].append(float(row['value_SI']))
    return {key:np.asarray(values) for key,values in data.items()}


def summarize(directory):
    cases={p.stem:read(p) for p in sorted(directory.glob('*.csv'))}
    def change(k,metric,label='whole'):
        y=cases[k][label,metric]
        if len(y)!=41:
            raise ValueError('Incomplete history: '+k)
        return 100*(y/y[0]-1)
    result={}
    for m in METRICS:
        base=change(PRIMARY,m)
        def diff(first,second):
            return abs(change(first,m)-change(second,m))
        errors=dict(space=diff(PRIMARY,'n12_L80_s4'),step=diff(PRIMARY,'n16_L80_s2'),
                    phase=diff(PRIMARY,PRIMARY+'_shift'),domain=diff('n12_L80_s2','n12_L160_s2'))
        def variant(label):
            return abs(change(PRIMARY,m,label)-base)
        if m.startswith('r'):
            errors.update(quadrature=variant('polar32'),ridge=variant('quadratic'),
                          field=variant('archived_field'),
                          center=np.maximum(variant('marker'),variant('centroid')))
        else:
            # Whole-section tail closure check, using an independent polar rule
            # on the widest two disks. Small apertures change the estimand.
            errors['tail_and_quadrature']=np.maximum(variant('disk_4a'),variant('disk_5a'))
        envelope=sum(errors.values())
        result[m]=dict(release=cases[PRIMARY]['whole',m][0],endpoint=cases[PRIMARY]['whole',m][-1],
                       water_pct=base[-1],inviscid_pct=change(PRIMARY+'_inviscid',m)[-1],
                       heat_pct=change('diffusion',m)[-1],
                       endpoint_errors_pp={k:y[-1] for k,y in errors.items()},
                       envelope_pp=envelope[-1],max_envelope_pp=max(envelope),
                       last_three_changes_pct=base[-3:].tolist(),
                       last_three_quarter_signal=bool(np.all(envelope[-3:]<abs(base[-3:])/4)))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('directory',type=Path)
    print(json.dumps(summarize(p.parse_args().directory),indent=2,allow_nan=False))
