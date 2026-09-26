"""Frozen accuracy policy for the single manufactured spatial BE pilot."""
import json
from math import isfinite

from .prototype import Refusal


def policy_record():
    from .manufactured_manifest import expected
    return dict(expected()['diagnostic_policy'])


def validate_policy(record):
    try:
        actual = json.dumps(record, sort_keys=True, allow_nan=False)
        wanted = json.dumps(policy_record(), sort_keys=True, allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise Refusal('invalid manufactured diagnostic policy') from exc
    if actual != wanted:
        raise Refusal('changed manufactured diagnostic policy')
    return record


def compare(base, check, policy):
    validate_policy(policy)
    keys = set(policy['raw_keys'])
    signed = set(policy['signed_keys'])
    nonnegative = set(policy['nonnegative_keys'])
    if (len(keys) != 30 or len(signed) != 17 or len(nonnegative) != 12
            or signed & nonnegative):
        raise Refusal('invalid manufactured key partition')
    for raw in (base, check):
        if type(raw) is not dict or set(raw) != keys:
            raise Refusal('incomplete manufactured raw inventory')
        if any(type(value) not in (int, float) or not isfinite(value)
               for value in raw.values()):
            raise Refusal('nonfinite or non-native manufactured scalar')
        if any(raw[key] < 0 for key in nonnegative):
            raise Refusal('negative manufactured nonnegative scalar')
    result = {}
    for key in sorted(keys):
        difference = check[key]-base[key]
        limit = policy['relative']*max(policy['scale_floor'], abs(base[key]))
        if key in signed:
            limit = max(limit, policy['signed_absolute_floor'])
        result[key] = dict(difference=difference, limit=limit,
                           accepted=abs(difference) <= limit)
    return result
