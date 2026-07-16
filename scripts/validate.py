#!/usr/bin/env python3
"""Validate data/state-rates.json against data/state-rates.csv.

Stdlib-only. Exits non-zero on any failure, prints itemized failures.
Exits 0 with a PASS summary when everything checks out.
"""
import csv
import json
import os
import sys
from decimal import Decimal
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(ROOT, "data", "state-rates.json")
CSV_PATH = os.path.join(ROOT, "data", "state-rates.csv")
HISTORY_PATH = os.path.join(ROOT, "data", "rate-history.csv")

CUTOFF = date(2026, 1, 1)

failures = []


def fail(msg):
    failures.append(msg)


def load_json():
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            fail(f"JSON: failed to parse {JSON_PATH}: {e}")
            return None
    if "_meta" not in data:
        fail("JSON: missing required '_meta' key")
    return data


def load_csv():
    with open(CSV_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    return rows


def parse_iso_date(s, ctx):
    try:
        y, m, d = s.split("-")
        return date(int(y), int(m), int(d))
    except Exception:
        fail(f"{ctx}: '{s}' is not a valid ISO YYYY-MM-DD date")
        return None


def bps_to_pct_str(bps_decimal):
    return str((bps_decimal / Decimal(100)).quantize(Decimal("1.000")))


def main():
    json_data = load_json()
    csv_rows = load_csv()

    if json_data is None:
        print_failures_and_exit()
        return

    json_codes = set(k for k in json_data.keys() if k != "_meta")
    csv_codes = set(r["code"] for r in csv_rows)
    csv_by_code = {r["code"]: r for r in csv_rows}

    # (1) exactly 51 jurisdiction codes, identical sets
    if len(json_codes) != 51:
        fail(f"JSON: expected exactly 51 jurisdiction codes, found {len(json_codes)}")
    if len(csv_codes) != 51:
        fail(f"CSV: expected exactly 51 jurisdiction codes, found {len(csv_codes)}")
    if json_codes != csv_codes:
        only_json = json_codes - csv_codes
        only_csv = csv_codes - json_codes
        if only_json:
            fail(f"Code set mismatch: only in JSON: {sorted(only_json)}")
        if only_csv:
            fail(f"Code set mismatch: only in CSV: {sorted(only_csv)}")

    # duplicate codes in CSV?
    if len(csv_rows) != len(csv_codes):
        seen = {}
        for r in csv_rows:
            seen[r["code"]] = seen.get(r["code"], 0) + 1
        dupes = [c for c, n in seen.items() if n > 1]
        fail(f"CSV: duplicate code rows for {dupes}")

    common_codes = json_codes & csv_codes

    for code in sorted(common_codes):
        jrow = json_data[code]
        crow = csv_by_code[code]

        # (2) per-row parity: name, local_varies, source
        if jrow.get("name") != crow.get("name"):
            fail(f"{code}: name mismatch JSON={jrow.get('name')!r} CSV={crow.get('name')!r}")

        j_local_varies = jrow.get("local_varies")
        c_local_varies_raw = crow.get("local_varies")
        c_local_varies = c_local_varies_raw.strip().lower() == "true" if c_local_varies_raw is not None else None
        if c_local_varies_raw not in ("true", "false"):
            fail(f"{code}: CSV local_varies must be 'true' or 'false', got {c_local_varies_raw!r}")
        if j_local_varies != c_local_varies:
            fail(f"{code}: local_varies mismatch JSON={j_local_varies!r} CSV={c_local_varies_raw!r}")

        if jrow.get("source") != crow.get("source"):
            fail(f"{code}: source mismatch JSON={jrow.get('source')!r} CSV={crow.get('source')!r}")

        # (8) source non-empty
        if not jrow.get("source"):
            fail(f"{code}: JSON source is empty")
        if not crow.get("source"):
            fail(f"{code}: CSV source is empty")

        # state_bps parity (JSON vs CSV) -- required for checks (3)/(4) below
        j_bps_raw = jrow.get("state_bps")
        c_bps_raw = crow.get("state_bps")
        try:
            j_bps = Decimal(str(j_bps_raw))
        except Exception:
            fail(f"{code}: JSON state_bps {j_bps_raw!r} is not numeric")
            j_bps = None
        try:
            c_bps = Decimal(c_bps_raw)
        except Exception:
            fail(f"{code}: CSV state_bps {c_bps_raw!r} is not numeric")
            c_bps = None

        if j_bps is not None and c_bps is not None and j_bps != c_bps:
            fail(f"{code}: state_bps mismatch JSON={j_bps} CSV={c_bps}")

        # (4) every state_bps an exact multiple of 0.25 (quarter-bps resolution)
        if j_bps is not None and (j_bps % Decimal("0.25")) != 0:
            fail(f"{code}: JSON state_bps {j_bps} is not a multiple of 0.25")
        if c_bps is not None and (c_bps % Decimal("0.25")) != 0:
            fail(f"{code}: CSV state_bps {c_bps} is not a multiple of 0.25")

        # (3) state_rate_pct == state_bps/100 (3 decimals)
        c_pct_raw = crow.get("state_rate_pct")
        if c_bps is not None and c_pct_raw is not None:
            expected_pct = bps_to_pct_str(c_bps)
            if c_pct_raw.strip() != expected_pct:
                fail(f"{code}: state_rate_pct {c_pct_raw!r} != expected {expected_pct!r} (from state_bps={c_bps})")

        # (5) CSV authoritative_combined == NOT local_varies
        auth_raw = crow.get("authoritative_combined")
        if auth_raw not in ("true", "false"):
            fail(f"{code}: CSV authoritative_combined must be 'true' or 'false', got {auth_raw!r}")
        else:
            auth = auth_raw.strip().lower() == "true"
            if c_local_varies is not None and auth != (not c_local_varies):
                fail(f"{code}: authoritative_combined={auth} but local_varies={c_local_varies} (must be opposite)")

        # (6)/(7) scheduled_change parity + date validity
        j_sched = jrow.get("scheduled_change")
        c_sched_date = (crow.get("scheduled_change_date") or "").strip()
        c_sched_pct = (crow.get("scheduled_change_pct") or "").strip()

        j_has_sched = j_sched is not None
        c_has_sched = bool(c_sched_date) or bool(c_sched_pct)

        if bool(c_sched_date) != bool(c_sched_pct):
            fail(f"{code}: CSV scheduled_change_date/scheduled_change_pct must be both-present-or-both-absent "
                 f"(date={c_sched_date!r}, pct={c_sched_pct!r})")

        if j_has_sched != c_has_sched:
            fail(f"{code}: scheduled_change presence mismatch JSON={'present' if j_has_sched else 'absent'} "
                 f"CSV={'present' if c_has_sched else 'absent'}")
        elif j_has_sched and c_has_sched:
            j_date = j_sched.get("date")
            j_sched_bps_raw = j_sched.get("state_bps")

            if j_date != c_sched_date:
                fail(f"{code}: scheduled_change date mismatch JSON={j_date!r} CSV={c_sched_date!r}")

            try:
                j_sched_bps = Decimal(str(j_sched_bps_raw))
                expected_sched_pct = bps_to_pct_str(j_sched_bps)
                if c_sched_pct != expected_sched_pct:
                    fail(f"{code}: scheduled_change pct mismatch CSV={c_sched_pct!r} "
                         f"expected={expected_sched_pct!r} (from JSON state_bps={j_sched_bps})")
            except Exception:
                fail(f"{code}: JSON scheduled_change.state_bps {j_sched_bps_raw!r} is not numeric")

            # (7) scheduled dates valid ISO YYYY-MM-DD and > 2026-01-01
            for label, dstr in (("JSON scheduled_change.date", j_date), ("CSV scheduled_change_date", c_sched_date)):
                d = parse_iso_date(dstr, f"{code}: {label}")
                if d is not None and not (d > CUTOFF):
                    fail(f"{code}: {label} {dstr} must be > 2026-01-01")

    validate_history_csv()

    print_failures_and_exit(len(common_codes))


def validate_history_csv():
    if not os.path.exists(HISTORY_PATH):
        return  # built in a parallel stage; skip silently if absent

    expected_header = [
        "date_observed", "code", "field", "old_value", "new_value",
        "effective_date", "source",
    ]
    with open(HISTORY_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            fail("rate-history.csv: file is empty, expected a header row")
            return
        if header != expected_header:
            fail(f"rate-history.csv: header mismatch, expected {expected_header}, got {header}")
            return
        ncols = len(expected_header)
        for i, row in enumerate(reader, start=2):
            if len(row) != ncols:
                fail(f"rate-history.csv: row {i} has {len(row)} columns, expected {ncols}")


def print_failures_and_exit(n_rows=None):
    if failures:
        print(f"FAIL: {len(failures)} issue(s) found\n")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)
    else:
        suffix = f" ({n_rows} jurisdictions)" if n_rows is not None else ""
        print(f"PASS: state-rates.json and state-rates.csv are consistent{suffix}")
        sys.exit(0)


if __name__ == "__main__":
    main()
