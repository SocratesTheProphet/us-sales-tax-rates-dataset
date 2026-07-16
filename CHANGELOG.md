# Changelog

## v1.1.0 — 2026-07-16

Tooling/infrastructure release. No data changes.

- Added `scripts/validate.py` — stdlib-only consistency check between `state-rates.json`, `state-rates.csv`, and `rate-history.csv`; exits non-zero on failure.
- Added `.github/workflows/validate.yml` — CI runs `validate.py` on every push and PR.
- Added `CONTRIBUTING.md` — correction/PR process and maintainer release checklist.
- Added `.github/ISSUE_TEMPLATE/rate-correction.yml` — structured rate-correction issue form.
- Added `CITATION.cff` — machine-readable citation metadata.
- Added `schema/state-rates.schema.json` — formal JSON Schema for `data/state-rates.json`.
- Added `data/rate-history.csv` — append-only ledger of realized rate corrections (documented in `SCHEMA.md`).
- `data/state-rates.json` `_meta`: prepended `v1.1.0 | validated 2026-07-01 (DC re-verified 2026-07-16) |` version/validation tokens ahead of the existing descriptive text (string field, non-breaking).

## v1.0.1 — 2026-07-16

Correction: DC OTR raised the District of Columbia base rate to 6.5% effective 2025-10-01. v1.0.0 shipped a stale 6.0% value.

- `DC` `state_bps` corrected 600 → 650 (6.0% → 6.5%) in both `data/state-rates.json` and `data/state-rates.csv`.
- `scheduled_change` to 7.0% on 2026-10-01 is unaffected and remains intact.

## v1.0.0 — compiled 2026-07-04, published 2026-07-16

Initial public release.

- 51 jurisdictions (50 states + DC).
- All base rates validated against official DOR/tax-authority sources on 2026-07-01.
- Quarter-bps storage; all values exact multiples of 0.25 bps.
- 14 jurisdictions flagged authoritative (no local variation): CT, DE, IN, KY, ME, MD, MA, MI, MT, NH, NJ, OR, RI, DC.
- 3 enacted future changes carried with effective dates: DC (2026-10-01), SD (2027-07-01), LA (2030-01-01).
- Formats: `data/state-rates.json` (source of truth), `data/state-rates.csv` (flat).
