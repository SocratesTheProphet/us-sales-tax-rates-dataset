# Changelog

## v1.0.0 — 2026-07-04

Initial public release.

- 51 jurisdictions (50 states + DC).
- All base rates validated against official DOR sources on 2026-07-01.
- Quarter-bps storage; all values exact multiples of 0.25 bps.
- 14 jurisdictions flagged authoritative (no local variation): CT, DE, IN, KY, ME, MD, MA, MI, MT, NH, NJ, OR, RI, DC.
- 3 enacted future changes carried with effective dates: DC (2026-10-01), SD (2027-07-01), LA (2030-01-01).
- Formats: `data/state-rates.json` (source of truth), `data/state-rates.csv` (flat).
