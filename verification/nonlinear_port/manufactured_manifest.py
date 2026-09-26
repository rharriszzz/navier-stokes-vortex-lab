"""Strict non-executable R255 manufactured pilot proposal and source contract."""
import hashlib
import json
from pathlib import Path

from .prototype import Refusal


REFERENCE = Path(__file__).resolve().parents[2]/'docs/realizability/evidence/r255/proposal.json'


def canonical(value):
    try:
        return json.dumps(value, sort_keys=True, separators=(',', ':'),
                          allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise Refusal('non-JSON manufactured proposal') from exc


def expected():
    return json.loads(REFERENCE.read_text(encoding='utf-8'))


def contract_digest(value):
    validate(value)
    return hashlib.sha256(canonical(value).encode('utf-8')).hexdigest()


def validate(value):
    if type(value) is not dict or canonical(value) != canonical(expected()):
        raise Refusal('missing or changed manufactured proposal')
    if (value['execution_admitted'] is not False
            or type(value['attempts_granted']) is not int
            or value['attempts_granted'] != 0):
        raise Refusal('manufactured proposal cannot admit execution')
    return value
