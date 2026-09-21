"""Fail-closed fixture accounting; unknown deaths never become assertion retries."""
import math

LIMIT = 120.0
AS_LIMIT = 256 << 20


def admit(history):
    if type(history) is not list:
        raise ValueError('history missing')
    total = 0.0
    for row in history:
        if (type(row) is not dict or type(row.get('schema')) is not int or row['schema'] != 1 or
                row.get('state') != 'COMPLETED' or row.get('status') != 'passed' or
                type(row.get('returncode')) is not int or row['returncode'] != 0 or
                row.get('resource_stop') is not False or
                type(row.get('charged_seconds')) not in (int,float) or
                not math.isfinite(row['charged_seconds']) or row['charged_seconds'] < 0 or
                type(row.get('receipt_sha256')) is not str or len(row['receipt_sha256']) != 64):
            raise ValueError('open/failed/unknown/resource-stopped history; no retry')
        total += row['charged_seconds']
    if not math.isfinite(total) or total >= LIMIT:
        raise ValueError('fixture allowance exhausted')
    return total


def classify(code, timed_out, stderr, rss):
    if (timed_out is not False or type(code) is not int or type(rss) is not int or
            rss > AS_LIMIT or code < 0 or 'MemoryError' in stderr):
        return 'resource_or_unknown_stop'
    return 'passed' if code == 0 else 'failed_unknown'
