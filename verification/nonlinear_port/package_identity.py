"""Exact FFCx artifact exception; package pins and runtime strings stay separate.

R229 verified the archive/transaction. This gate reuses that retained evidence
under R103's ordinary owner/OS trust, not a hostile filesystem threat model.
No numerical modules are imported here.
"""
import hashlib
import json
from email.parser import Parser
from pathlib import Path

from .prototype import Refusal

FFCX_ARTIFACT = dict(
    name='fenics-ffcx', version='0.10.1', build='pyhbc3ee6d_1', subdir='noarch',
    sha256='727926ec2782375707cd036f86ab3d5004d53074ee80cf127619134f763e3473',
    md5='d37671d8e59bdccbc1ef2defa740bdaa',
    url='https://conda.anaconda.org/conda-forge/noarch/fenics-ffcx-0.10.1-pyhbc3ee6d_1.conda')
FFCX_RUNTIME = '0.10.0'
MODULE = 'lib/python3.12/site-packages/ffcx/__init__.py'
METADATA = 'lib/python3.12/site-packages/fenics_ffcx-0.10.0.dist-info/METADATA'
RECOVERY_EVIDENCE = {
    'run/cache_verified.json': '3c5a61e8747238ac557cce800f1881c5131847ebf1212f4c388018f08f7199ce',
    'run/verification.json': '8c91f6cc2f1494be477885e9e0cfd535b72e4f6c36fb01208ce44bb044b2d3f5',
}


def validate_ffcx_artifact(evidence):
    if (not isinstance(evidence, dict)
            or evidence != dict(package=FFCX_ARTIFACT, embedded_version=FFCX_RUNTIME,
                                recovery_evidence=RECOVERY_EVIDENCE)):
        raise Refusal('missing or different exact FFCx artifact evidence')


def read_ffcx_artifact(prefix, evidence_root=None):
    """Run inside the admitted worker; no archive scan, installation or imports."""
    prefix = Path(prefix).resolve(strict=True)
    if evidence_root is None:
        evidence_root = Path(__file__).resolve().parents[2]/'docs/realizability/evidence/r229'
    try:
        for name, expected in RECOVERY_EVIDENCE.items():
            if hashlib.sha256((Path(evidence_root)/name).read_bytes()).hexdigest() != expected:
                raise Refusal('changed FFCx recovery evidence')
        record = json.loads((prefix/'conda-meta/fenics-ffcx-0.10.1-pyhbc3ee6d_1.json').read_text())
        package = {k: record.get(k) for k in FFCX_ARTIFACT}
        for relative in (MODULE, METADATA):
            path = prefix/relative
            if (relative not in record.get('files', []) or not path.is_file()
                    or not path.resolve(strict=True).is_relative_to(prefix)):
                raise Refusal('FFCx files absent from installed artifact/prefix')
        metadata = Parser().parsestr((prefix/METADATA).read_text())
        if metadata.get_all('Name') != ['fenics-ffcx'] or metadata.get_all('Version') != [FFCX_RUNTIME]:
            raise Refusal('unexpected embedded FFCx distribution metadata')
    except (OSError, ValueError, TypeError, AttributeError) as exc:
        raise Refusal('missing or malformed FFCx installation evidence') from exc
    evidence = dict(package=package, embedded_version=metadata['Version'],
                    recovery_evidence=dict(RECOVERY_EVIDENCE))
    validate_ffcx_artifact(evidence)
    return evidence


def validate_versions(actual, versions, artifact):
    """Apply the sole artifact-bound exception in worker and raw-result reader."""
    validate_ffcx_artifact(artifact)
    if versions.get('ffcx') != FFCX_ARTIFACT['version']:
        raise Refusal('FFCx package pin changed')
    expected = dict(versions, ffcx=FFCX_RUNTIME)
    if not isinstance(actual, dict) or any(actual.get(k) != v for k, v in expected.items()):
        raise Refusal('worker reported different pinned runtime versions')
