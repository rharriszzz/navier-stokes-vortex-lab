"""Strict, non-executable proposal for the exact-field rotation assembly."""
import hashlib
import json
from pathlib import Path

from .manifest import validate as validate_poiseuille_manifest
from .prototype import Refusal
from .rotation_oracle import contract_record, validate_contract
from .supervision import CAPS, MAX_REPORT_BYTES


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'),
                          allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise Refusal('non-JSON rotation proposal') from exc


def contract_digest(contract):
    validate_contract(contract)
    return hashlib.sha256(canonical(contract).encode('utf-8')).hexdigest()


def expected():
    old = json.loads(Path(__file__).with_name('future_fem.json').read_text())
    validate_poiseuille_manifest(old)
    return dict(schema=1, kind='rotation_assembly', fixture='rotation',
                mode='exact_field_assembly', execution_admitted=False,
                attempts_granted=0, proposed_attempts=1,
                contract=contract_record(), versions=old['versions'],
                proposed_caps=dict(CAPS), report_bytes_max=MAX_REPORT_BYTES)


def validate(value):
    if type(value) is not dict or canonical(value) != canonical(expected()):
        raise Refusal('missing or changed rotation proposal')
    # Canonical JSON distinguishes true from 1 and 1.0; validate nested policy too.
    validate_contract(value['contract'])
    return value
