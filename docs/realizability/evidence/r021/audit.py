"""R021 saved-data and continuity audit; standard library, no FEM execution."""
import ast
import hashlib
import json
import math
from pathlib import Path
import re
import runpy
import subprocess

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finite(value):
    if isinstance(value, float):
        assert math.isfinite(value)
    elif isinstance(value, dict):
        for item in value.values():
            finite(item)
    elif isinstance(value, list):
        for item in value:
            finite(item)


def read(path):
    def reject(value):
        raise ValueError('Nonfinite JSON: ' + value)
    value = json.loads(path.read_text(), parse_constant=reject)
    finite(value)
    return value


def main():
    identities = read(HERE / 'identities.json')
    assert identities['historical_files'] == 433
    assert len(identities['production_sha256']) == 19
    for group in ('production_sha256', 'historical_sha256'):
        for name, digest in identities[group].items():
            assert sha(ROOT / name) == digest, name
    prior = read(HERE / 'reaudit-r020-validation.json')
    assert prior['status'] == 'passed'
    assert prior['physical_stage'] == 'A_32_primary_rhs_compatibility'
    review = read(HERE / 'review.json')
    calculation = runpy.run_path(str(HERE / 'review.py'))['calculate']()
    assert calculation == review
    assert review['status'] == 'passed_saved_data_audit'
    assert all(review[key] == 0 for key in ('new_physical_meshes', 'new_FEM_assemblies',
        'new_PDE_solves', 'new_reference_evaluations', 'new_quadrature_evaluations'))
    assert not review['physical_gate_passed'] and not review['campaign_ready']
    compatibility = review['compatibility']
    assert compatibility['removal_over_tolerance'] > 11
    assert compatibility['A64_assembled_compatibility'].startswith('unmeasured')
    assert review['quadrature_cost']['point_count_ratio'] == 2.6
    base_log = subprocess.check_output(['git', 'show', identities['base_commit'] + ':REQUEST_LOG.md'],
                                       cwd=ROOT, text=True)
    log = (ROOT / 'REQUEST_LOG.md').read_text()
    assert log.startswith(base_log)
    assert log.count('## R021 —') == 1
    syntax = json_count = 0
    for path in HERE.glob('*.py'):
        tree = ast.parse(path.read_text())
        # All imported modules in these new audits are standard-library modules.
        allowed = {'ast', 'contextlib', 'hashlib', 'io', 'json', 'math', 'pathlib',
                   're', 'runpy', 'subprocess', 'unittest'}
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                assert all(alias.name.split('.')[0] in allowed for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                assert node.module.split('.')[0] in allowed
        syntax += 1
    for path in HERE.glob('*.json'):
        if path.name != 'validation.json':
            read(path)
            json_count += 1
    markdown = ['REQUEST_LOG.md', 'SESSION_HANDOFF.md', 'STATUS.md', 'PROJECT_TRACKS.md',
        'docs/realizability/B2_NEXT_STEPS.md', 'docs/realizability/B2_MATCHED_TRACE_REVIEW.md',
        'docs/realizability/B2_BLOCK_RHS_TOY_REPAIR_RESULT.md',
        'docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_REVIEW.md',
        'docs/realizability/B2_COMPATIBLE_TRACE_INTEGRATION_EVIDENCE.md']
    links = fences = 0
    for name in markdown:
        path = ROOT / name
        body = path.read_text()
        count = sum(line.lstrip().startswith('```') for line in body.splitlines())
        assert count % 2 == 0, name
        fences += count // 2
        for destination in re.findall(r'\[[^\]]*\]\(([^)]+)\)', body):
            if destination.startswith(('https://', 'http://', 'mailto:')):
                continue
            links += 1
            local, separator, anchor = destination.partition('#')
            target = (path.parent / local).resolve() if local else path
            if target == HERE / 'validation.json' and not target.exists():
                continue
            assert target.exists(), (name, destination)
            if separator:
                headings = [re.sub(r'[^a-z0-9 _-]', '', line.lstrip('#').strip().lower()).replace(' ', '-')
                            for line in target.read_text().splitlines() if line.startswith('#')]
                assert anchor in headings, (name, destination)
    artifacts = {p.name: sha(p) for p in sorted(HERE.iterdir())
                 if p.is_file() and p.name != 'validation.json'}
    result = dict(status='passed', scope='saved arithmetic, identities and documentation only',
        base_commit=identities['base_commit'], production_identities=19,
        historical_files_preserved=433, historical_audits_reexecuted=1,
        archived_facet_records_checked=564, request_history_preserved=True,
        saved_calculation_reproduced=True, new_python_syntax_checks=syntax,
        finite_json_inputs=json_count, markdown_files=len(markdown),
        local_links_and_anchors=links, fenced_blocks=fences, artifact_sha256=artifacts,
        new_physical_meshes=0, new_FEM_assemblies=0, new_PDE_solves=0,
        new_reference_or_quadrature_evaluations=0, new_toy_executions=0,
        future_experiment='specified only; fixed 64/96 pair; all primary compatibility before solve',
        physical_gate_passed=False, campaign_ready=False)
    (HERE / 'validation.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
