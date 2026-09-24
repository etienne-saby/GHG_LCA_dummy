# Cocoa Smallholder Product Carbon Footprint — Prototype

A small, transparent, Tier 1 product carbon footprint (PCF) tool for a
smallholder cocoa farm, built as a hands-on talking point for a Junior Climate
Analyst interview. **This is a learning/demo project, not an audited
inventory** — but every number in it is traceable to a named source, and
every formula says what it computes and where the factor came from.

## How to run

```
pip install pandas matplotlib
python main.py
```

This prints a console report (scenario comparison, category breakdown, and a
full multi-dimensional Data Quality Rating), writes `scenario_results.csv`,
writes `cocoa_footprint_comparison.png`, and then runs the verification suite
in `test_calculations.py` and prints its actual pass/fail output.

To run just the tests: `python -m unittest test_calculations.py -v`

## What's sourced vs. illustrative — up front, not buried in comments

**Sourced** (traceable to IPCC / GHG Protocol / SBTi FLAG / peer-reviewed LCA
literature — full citations in `SOURCES.md`):
- All N₂O emission factors (direct + both indirect pathways)
- The GWP₁₀₀ used to convert N₂O to CO₂e
- The land-use-change amortisation *mechanism* (20-year convention) and the
  Ghana/Côte d'Ivoire forest-vs-cocoa carbon-stock magnitude it's applied to
- Transport emission factors (flagged lower-confidence — see below)
- The agroforestry/shade CO₂ removal rates at 0% and ~100% canopy cover

**Illustrative / our own modelling choices** (flagged inline in code, not
hidden):
- The four scenarios' farm profiles (area, yield, fertiliser rate, transport
  distance) are round, plausible demo numbers for a hypothetical farm, not a
  specific real one — see `scenarios.py`
- Linearly interpolating the removal rate between the two sourced endpoints
  by % canopy cover is our simplification, not itself from the literature
- Using the aggregate (not urea-specific) volatilisation factor, since the
  scenarios don't specify a fertiliser sub-type

Every constant's full citation, confidence tier (Sourced/Estimated/
Illustrative), and — where relevant — the specific caveat on it, is in
`SOURCES.md`. The console output and this README both surface the
sourced-vs-illustrative split; it isn't only in code comments.

## Methodology notes

**Tier 1, not Tier 2/3.** Every emission/removal factor here is a generic
international or systematic-review default, not site-measured primary data.
A real operational tool for a trader like ECOM would need to move to Tier
2/3: farm-level fertiliser records, regional (not UK) freight factors,
supplier-specific deforestation risk mapping, and ideally direct soil/biomass
measurement rather than literature defaults. **Primary data matters
disproportionately for smallholder supply chains** specifically because
Tier 1 defaults are typically calibrated on larger, more commercial
production systems; a 3-5 ha smallholder plot's actual fertiliser use,
shade regime, and land history can diverge substantially from a global
median, and that divergence is exactly what a trader needs to know to price
or manage deforestation and emissions risk in its sourcing portfolio.

**LUC amortisation.** Land-use-change emissions are not charged entirely in
the conversion year. Following the PAS 2050 / GHG Protocol convention (also
consistent with SBTi FLAG's 20-year inclusion window), the total carbon-stock
loss from converting forest to cocoa is spread evenly over 20 years. This
tool's ΔC comes from Becker et al. (2024), which measured aboveground carbon
density specifically in Ghana and Côte d'Ivoire (36.6 t C/ha forest vs. 13.7
t C/ha average cocoa landscape) — geographically closer to ECOM's sourcing
footprint than a generic IPCC ecozone default, though it only covers
aboveground biomass (see Data Quality Rating below for what it excludes).

**Direct vs. indirect N₂O.** Both pathways are modelled explicitly and kept
as separate line items in the breakdown (direct / volatilisation / leaching),
not collapsed into one fertiliser number.

**Emissions vs. removals.** Total farm emissions and total removals are
always reported separately (console, CSV, and the chart's PCF metric is
emissions-only) — they are never netted into a single hidden number.

**Why Scenario B (agroforestry) doesn't show a dramatically lower PCF.**
This is intentional, and matches a real finding worth knowing for the
interview: a peer-reviewed meta-analysis of cacao LCAs found that while
agroforestry's *area-based* footprint and yields are both significantly
lower than unshaded systems, the *product-level* footprint (per kg) does
**not** differ significantly — the yield penalty partly offsets the
emissions-per-hectare gain. This prototype holds yield and fertiliser
constant between Scenarios A and B specifically to isolate the removal-credit
mechanism in the *removals* column (which does increase substantially); it
deliberately doesn't model a yield trade-off, so don't read Scenario B's
similar PCF to Scenario A as a modelling error — it's the point.

## Data Quality Rating summary

Each input category is rated on five separate dimensions (technological,
geographical, temporal representativeness, completeness, reliability), not a
single score — full detail in the console output / `dqr.py`. Headlines:
- **Transport** rates weakest overall (Poor on geographical
  representativeness): the emission factors are a UK government default
  standing in for West African freight — the most honest Tier 1 option
  available without a licensed regional dataset, but flagged clearly.
- **Land-use change** rates Fair on completeness: the sourced ΔC is
  aboveground-biomass-only and excludes belowground biomass and soil organic
  carbon, so it likely understates the true LUC penalty in Scenario C.
- **Fertiliser N₂O** is the strongest-rated category: a complete, current,
  peer-consensus IPCC Tier 1 default, only marked down for not being
  West-Africa-specific.

## Order-of-magnitude sanity check

`test_calculations.py` checks Scenario A/B/D land within a peer-reviewed
meta-analysis's literature decile range (0.05–3.74 kg CO₂e/kg dry beans,
no LUC) and Scenario C clears that ceiling while staying within a broad
plausible bound anchored to Côte d'Ivoire's sourced with-LUC figure (30 kg
CO₂e/kg). All four scenarios pass; see console output for actual test
results, not just a description of the check.

## Repository map

- `main.py` — calculation formulas, orchestration, console/CSV/chart output
- `factors.py` — every emission/removal factor, each commented with its source
- `scenarios.py` — the four scenario definitions
- `dqr.py` — multi-dimensional Data Quality Rating logic
- `test_calculations.py` — verification tests
- `SOURCES.md` — full source ledger: value, unit, citation, version/year, tier
- `scenario_results.csv`, `cocoa_footprint_comparison.png` — generated output
