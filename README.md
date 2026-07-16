# US Sales-Tax Rates (statewide base) — a small, honest, validated dataset

Machine-readable **statewide base sales-tax rates for all 50 US states + DC**, validated against official state Department of Revenue (DOR) sources on **2026-07-01**. Available as JSON and CSV, at quarter-basis-point precision, with enacted future rate changes included and dated.

Most free sales-tax data is ZIP-code-based and quietly wrong — ZIP codes cross tax jurisdictions, so a single "rate per ZIP" is a guess that can be off by a full percent or more. This dataset takes the opposite stance: it gives **authoritative statewide rates**, and where local rates genuinely vary, it **says so instead of fabricating a number**.

## What makes it different

- **Exact rates, not float dust.** Rates are stored as basis points at quarter-bps resolution (1% = 100 bps), so fractional rates are exact in IEEE-754: Minnesota 6.875%, New Jersey 6.625%, New Mexico 4.875%, Missouri 4.225%. No `0.0650000001` surprises.
- **Honest about local variation.** 14 jurisdictions have no local sales tax or a uniform statewide rate — for those, the statewide rate **is** the authoritative combined rate. For the other 37, `local_varies: true` flags that a rooftop-level lookup is required, and the dataset does **not** invent a single combined number.
- **Documented conventions.** Where a "statewide rate" bundles mandatory uniform local components (the Tax Foundation min-combined convention — e.g. California's 7.25% = 6% state + 1.25% mandatory uniform local), the decomposition is spelled out in the row's `source` string. No hidden assumptions.
- **Future changes, dated.** Enacted-but-not-yet-effective changes are carried as `scheduled_change` with an effective date, so you can apply the right rate by date:
  - District of Columbia — 6.500% → 7.000% on 2026-10-01
  - South Dakota — 4.200% → 4.500% on 2027-07-01
  - Louisiana — 5.000% → 4.750% on 2030-01-01
- **Sourced per row.** Every state carries the DOR/source it was checked against.

## The 14 authoritative (no-local-variation) jurisdictions

`CT, DE, IN, KY, ME, MD, MA, MI, MT, NH, NJ, OR, RI, DC`

For these, the statewide rate is the full combined rate you can charge. (DE, MT, NH, and OR levy **no** state sales tax → 0%.)

## Files

| File | What it is |
|---|---|
| `data/state-rates.json` | Source of truth. Keyed by two-letter code, plus a `_meta` field with the honesty notes. |
| `data/state-rates.csv` | Flat version — one row per jurisdiction, spreadsheet-friendly. |
| `SCHEMA.md` | Field-by-field definitions for both formats. |
| `CHANGELOG.md` | Versions and validation dates. |

## Usage

**JSON**

```js
import rates from "./data/state-rates.json" with { type: "json" };
const ca = rates.CA;               // { name, state_bps: 725, local_varies: true, source: ... }
const ratePct = ca.state_bps / 100; // 7.25
```

**CSV** — open in any spreadsheet, or:

```python
import csv
with open("data/state-rates.csv") as f:
    rows = list(csv.DictReader(f))
# each row has: code, name, state_rate_pct, state_bps, local_varies,
# authoritative_combined, scheduled_change_date, scheduled_change_pct, source
```

To apply a scheduled change: if today ≥ `scheduled_change_date`, use `scheduled_change_pct`; otherwise use `state_rate_pct`.

## Sourcing & validation

All 51 base rates were validated on **2026-07-01** against official state DOR sources (a multi-pass sweep). Values are the minimum combined statewide rate under the Tax Foundation convention. Each row's `source` field records what it was checked against.

## Limitations (please read)

- These are **statewide base rates**. For the 37 `local_varies: true` jurisdictions, this is **not** a full rooftop (address-level) combined rate — cities, counties, and special districts add amounts this dataset intentionally does not guess.
- Rates change. This is a dated snapshot; the `scheduled_change` fields cover known upcoming changes only. **Verify against the official DOR before charging, collecting, or filing.**
- Alaska has no statewide tax but ~110 of 162 municipalities levy local sales tax (`local_varies: true`, `state_bps: 0`).

## License

Released under **CC BY 4.0** — free to use, share, and adapt, including commercially, with attribution. See `LICENSE`.

## Disclaimer

This dataset is provided for informational purposes only and is **not** tax, legal, or accounting advice. It is provided **as-is, without warranty** of any kind. Always confirm current rates with the relevant state authority before relying on them.

---

*Maintained by Sean Murphy. Validated 2026-07-01. Contributions and corrections welcome — open an issue with a DOR source link.*
