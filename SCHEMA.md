# Schema

## `data/state-rates.json`

An object keyed by two-letter jurisdiction code (`"AL"`, `"AK"`, … `"DC"`), plus one special `_meta` string key describing the dataset's conventions. Each jurisdiction value:

| Field | Type | Meaning |
|---|---|---|
| `name` | string | Full jurisdiction name (e.g. `"California"`). |
| `state_bps` | number | Statewide base rate in **basis points** at quarter-bps resolution (1% = 100 bps; 6.875% = 687.5). Always an exact multiple of 0.25. Represents the minimum combined statewide rate (Tax Foundation convention — includes mandatory uniform local components where applicable). |
| `local_varies` | boolean | `false` → the statewide rate is authoritative and complete (no local variation). `true` → cities/counties/districts add amounts not represented here; a rooftop lookup is needed for a full combined rate. |
| `source` | string | The DOR/authority the row was validated against, plus any decomposition notes (e.g. how a min-combined floor breaks into state + mandatory local). |
| `scheduled_change` | object (optional) | Present only when an enacted future rate change exists. |
| `scheduled_change.date` | string | ISO date the new rate takes effect (`"YYYY-MM-DD"`). |
| `scheduled_change.state_bps` | number | The new `state_bps` effective on/after `date`. |

To get a percentage: `state_bps / 100`. To get a decimal rate: `state_bps / 10000`.

## `data/state-rates.csv`

One row per jurisdiction (no `_meta` row).

| Column | Meaning |
|---|---|
| `code` | Two-letter jurisdiction code. |
| `name` | Full name. |
| `state_rate_pct` | `state_bps / 100`, formatted to 3 decimals (e.g. `6.875`). |
| `state_bps` | Basis points (quarter-bps resolution). |
| `local_varies` | `true`/`false` — whether local rates add to this. |
| `authoritative_combined` | `true` when `local_varies` is false — i.e. the statewide rate is the full combined rate. |
| `scheduled_change_date` | Effective date of the next enacted change, or empty. |
| `scheduled_change_pct` | The rate that takes effect on `scheduled_change_date`, or empty. |
| `source` | Validation source / notes. |
