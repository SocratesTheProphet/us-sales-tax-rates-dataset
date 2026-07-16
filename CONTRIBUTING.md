# Contributing

This is a small, honest dataset. The bar for a correction is: **an official state tax-authority source that disagrees with what's here.** That's it — no PRs needed to report a problem, just an issue.

## Reporting a rate correction

Open an issue using the **Rate correction** template. It'll ask for:

- **State** (two-letter code)
- **Current value** — what this dataset says today
- **Claimed value** — what you believe it should be
- **Effective date** — when the claimed value took/takes effect
- **Official source link** — the state's own DOR (Department of Revenue) or tax-authority page

**Aggregator links won't be accepted** (Avalara, TaxJar, SalesTaxHandbook, Wikipedia, etc.). This dataset exists because that layer of secondary sources is where errors creep in. Link the primary source: the state DOR/tax-authority site, a statute, or an official notice/bulletin.

If you don't have an official link, still open the issue — just say so. It'll sit until someone (you or a maintainer) finds one. No correction ships without a primary source.

## How corrections get merged

1. A maintainer verifies the claimed value against the linked authority (and independently, if the link is thin).
2. If confirmed, the maintainer updates, in the same commit:
   - `data/state-rates.json`
   - `data/state-rates.csv`
   - `data/rate-history.csv` (append a row: `date_observed, code, field, old_value, new_value, effective_date, source`)
   - `CHANGELOG.md` (new version entry describing the correction)
3. `CITATION.cff` — bump `version` and `date-released` in the **same commit**.
4. Version bump follows semver-ish convention: a rate correction is a **patch** (`1.0.1`), a new field or jurisdiction is **minor**, a breaking schema change is **major**.
5. The commit is tagged with the new version.

Corrections are maintainer-applied, not typically contributor PRs — but a PR is welcome if you want to do the legwork yourself. See below.

## Submitting a PR

If you'd rather fix it yourself:

- Update both `data/state-rates.json` and `data/state-rates.csv` — they must stay in sync (name, `local_varies`, `source`, `state_bps`, `scheduled_change`).
- Keep `state_bps` at quarter-basis-point resolution (multiples of 0.25).
- Include the official source link in the row's `source` field.
- Run `python scripts/validate.py` before opening the PR — it must pass. CI runs the same check on every push and PR.
- Don't bump the version or touch `CHANGELOG.md`/`CITATION.cff` yourself — the maintainer does that on merge, alongside the `rate-history.csv` entry.

## What this project won't take

This is a static dataset, not a service. Out of scope:

- Rooftop/address-level (ZIP+4 or lat/long) rate lookups
- An API, SDK, or hosted endpoint
- Rate calculation logic, tax filing, or nexus determination
- Non-US jurisdictions

If you want that, this dataset is a fine input to build it from — just not something this repo will grow into.

## Release checklist (maintainer reference)

- [ ] Claimed value verified against an official DOR/tax-authority source
- [ ] `data/state-rates.json` updated
- [ ] `data/state-rates.csv` updated (stays in sync with JSON)
- [ ] `data/rate-history.csv` row appended
- [ ] `CHANGELOG.md` entry added
- [ ] `CITATION.cff` `version` + `date-released` bumped, same commit
- [ ] `python scripts/validate.py` passes
- [ ] Commit tagged with the new version
