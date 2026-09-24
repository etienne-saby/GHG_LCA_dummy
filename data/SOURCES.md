# SOURCES.md — Cocoa Carbon Footprint Prototype

Status: CONFIRMED by user 2026-09-23. All items sourced; implementation in progress.

Confidence tiers: **Sourced** (traceable to a named tier-1/2 source in the hierarchy) /
**Estimated** (derived from sourced data with an explicit assumption) /
**Illustrative** (no defensible source found — flagged `# ILLUSTRATIVE - unverified` in code).

---

## 1. Direct N2O emissions from N inputs (fertiliser)

| Parameter | Value | Unit |
|---|---|---|
| EF1, synthetic N, wet climate | 0.016 (range 0.013–0.019) | kg N2O–N / kg N applied |
| EF1, organic N / other inputs, wet climate | 0.006 (range 0.001–0.011) | kg N2O–N / kg N applied |
| N2O–N → N2O conversion | × 44/28 | — |

**Source:** IPCC 2019 Refinement to the 2006 IPCC Guidelines, Vol. 4, Ch. 11, Table 11.1
("Default emission factors to estimate direct N2O emissions from managed soils").
https://www.ipcc-nggip.iges.or.jp/public/2019rf/pdf/4_Volume4/19R_V4_Ch11_Soils_N2O_CO2.pdf

**Choice:** cocoa belt (Côte d'Ivoire, Ghana, and most smallholder origins) is IPCC "tropical
wet" climate (annual precipitation > 1000 mm), so the wet-climate disaggregated factors are used
rather than the aggregated global default (0.010) — this is the more geographically
representative Tier 1 option and still an official IPCC default, not a custom figure.

**Tier: Sourced.**

## 2. Indirect N2O — volatilisation pathway (NH3/NOx → redeposition)

| Parameter | Value | Unit |
|---|---|---|
| FracGASF, synthetic fertiliser (aggregate) | 0.11 (urea-specific: 0.15) | kg N volatilised / kg N applied |
| FracGASM, organic N / manure | 0.21 | kg N volatilised / kg N applied |
| EF4, wet climate | 0.014 | kg N2O–N / kg N volatilised |

**Source:** same IPCC 2019 Refinement, Table 11.3.
**Tier: Sourced.**

## 3. Indirect N2O — leaching/runoff pathway

| Parameter | Value | Unit |
|---|---|---|
| FracLEACH-(H), wet climate | 0.24 | kg N leached / kg N applied |
| EF5 | 0.011 | kg N2O–N / kg N leached |

**Source:** same IPCC 2019 Refinement, Table 11.3.
**Tier: Sourced.**

## 4. GWP100 for N2O

**Value:** 273 (100-year GWP, no climate–carbon feedbacks)
**Source:** IPCC AR6 WG1, Table 7.SM.7.
**Tier: Sourced.**

## 5. Land-use-change (LUC) amortisation — mechanism

**Method:** total carbon-stock loss from conversion (ΔC, t C/ha) is amortised in equal shares
over 20 years: `annual LUC emission = ΔC × 44/12 × 1/20` (t CO2/ha/yr), added only for plots
converted from forest within the amortisation window.

**Sources:**
- PAS 2050:2011 (BSI), §land-use-change methodology — establishes the 20-year amortisation
  convention and the ΔC × 44/12 × 1/20 formula; GHG Protocol Product Standard and Land Sector &
  Removals Guidance are aligned with this convention.
- SBTi FLAG Guidance v1.2 (2025) — companies must include LUC emissions from land converted
  within the preceding 20 years, and recommends a 2020 no-deforestation cutoff date; used here
  as the screening rule for whether a scenario's "converted from forest within the last 20 years"
  flag triggers the LUC term at all.
  https://sciencebasedtargets.org/blog/why-no-deforestation-must-be-a-priority-sbtis-flag-guidance-unpacked

**Tier: Sourced** (mechanism/formula/window). The magnitude input (ΔC) is item #6 below.

## 6. Land-use-change — carbon stock loss magnitude (ΔC) — RESOLVED

**Value:** ΔC ≈ 22.9 t C/ha (aboveground biomass only) = 36.6 t C/ha (intact forest) − 13.7 t C/ha
(average cocoa landscape carbon density).

**Source:** Becker, N. et al., "The unrealized potential of agroforestry for an emissions-intensive
agricultural commodity" (2024), arXiv:2410.20882 — field/satellite-based aboveground carbon
density estimates specific to **Ghana and Côte d'Ivoire** (ECOM's core sourcing geography).
https://arxiv.org/pdf/2410.20882

Preferred over a generic IPCC 2006 GL Table 4.7 global default because it is (a) geographically
exact to the target region, (b) more recent (2024 vs. 2006/2019), and (c) directly measured
rather than a broad ecozone default. **Caveat, flagged in the DQR:** this is aboveground biomass
carbon only — it excludes belowground biomass, soil organic carbon and dead wood/litter, all of
which IPCC's full LUC accounting would include, so it understates total carbon-stock loss. The
20-year amortisation mechanism (see #5) is applied to this ΔC.

**Also note:** this paper is an arXiv preprint; peer-reviewed publication status not confirmed —
reflected as reduced "Reliability" in the DQR for this factor.

**Tier: Sourced** (with the completeness/reliability caveats above carried into the DQR).

## 7. Transport

| Mode | Value | Unit |
|---|---|---|
| Truck (diesel articulated HGV, average laden) | 0.07547 | kg CO2e / tonne-km |
| Rail freight (diesel + electric mix, average) | 0.02779 | kg CO2e / tonne-km |

**Source:** UK Department for Energy Security & Net Zero (DESNZ), "Greenhouse gas reporting:
conversion factors 2024," published 8 July 2024.
https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024

**Tier: Sourced**, but flagged **Geographical representativeness: Poor** in the DQR — this is a
UK-published generic default, not West-Africa-specific. It is used here because it is a
transparent, versioned, publicly documented Tier 1 default; a real tool would move to GLEC
Framework or regional (Côte d'Ivoire/Ghana port/road) data at Tier 2.

## 8. Agroforestry / shade carbon removal credit

| System | Median CO2 removal rate | Interquartile range |
|---|---|---|
| Unshaded cocoa | 3,445 kg CO2/ha/yr | ±1,952 |
| Agroforestry (shaded) cocoa | 10,237 kg CO2/ha/yr | ±4,178 |

**Source:** peer-reviewed systematic review, "Carbon footprint of primary production of cacao: a
meta-analytical review," Environmental Reviews (2024/2025).
https://cdnsciencepub.com/doi/full/10.1139/er-2024-0146

**Modelling choice (Estimated):** the tool will linearly interpolate between the unshaded rate
(0% canopy cover) and the agroforestry rate (treated as ~100% canopy cover) by the user's %
canopy-cover input. This linear-interpolation step is an explicit simplifying assumption on top
of a sourced pair of endpoints — flagged as such in the code comment, not presented as itself
IPCC/peer-reviewed.

**Tier: Sourced** (endpoints) **+ Estimated** (interpolation between them).

## 9. Order-of-magnitude literature range (for the required verification test)

**Source:** same meta-analytical review as #8.
- Product carbon footprint, excluding LUC: median 1.55 kg CO2e/kg dry beans; typical range
  (1st–8th decile across studies) 0.05–3.74 kg CO2e/kg dry beans.
- Product carbon footprint, including LUC (deforestation sub-sample, n=6–8 studies): median
  15.55 kg CO2e/kg dry beans (vs. 0.31 kg CO2e/kg dry beans without LUC in that same sub-sample).

**Use:** `test_calculations.py`'s order-of-magnitude check will assert Scenario A/B/D outputs
fall within roughly the no-LUC range, and Scenario C (LUC penalty) lands in the LUC-inclusive
range — both cited ranges, not invented thresholds.

**Tier: Sourced.**

## 9b. Geographically-specific cross-check — Ghana / Côte d'Ivoire

**Source:** same Becker et al. (2024) arXiv:2410.20882, citing Quantis/World Food LCA Database
estimates:
- Ghana: 2 kg CO2e/kg cocoa (excl. LUC) → 4 kg CO2e/kg cocoa (incl. LUC)
- Côte d'Ivoire: 2 kg CO2e/kg cocoa (excl. LUC) → 30 kg CO2e/kg cocoa (incl. LUC)

**Use:** a second, more geographically relevant anchor for the Scenario C order-of-magnitude
test alongside the global meta-analysis figures in #9. Notably the no-LUC figure (2 kg CO2e/kg)
is consistent across both countries and close to our Scenario A/D outputs, while the with-LUC
figure varies enormously by country (4 vs. 30) — reflecting how much deforestation risk differs
by origin, which is itself a useful talking point for the interview.

**Tier: Sourced.**

## 10. Agroforestry — product-level nuance (for README, not a calculation input)

**Finding:** the same meta-analytical review (#8/#9) found that while agroforestry's *area-based*
carbon footprint (ACF) and yields are both significantly lower than unshaded systems, the
*product-level* carbon footprint (PCF, per kg) of agroforestry systems did **not** differ
significantly from unshaded systems — the yield penalty partly offsets the emissions-per-hectare
gain. Documented in README so Scenario B's product-level result isn't a surprise: this prototype
deliberately holds yield constant between Scenarios A and B to isolate the removal-credit
mechanism, which is a stronger/cleaner version of the same real-world pattern, not a contradiction
of it. **Tier: Sourced** (finding); the modelling choice to hold yield constant is a documented
simplification, not itself sourced.

---

## Data Quality Rating (DQR) — dimensions to score per category

Per the skill's rubric, each input category (fertiliser N2O, LUC, transport, agroforestry credit)
will get a rating on: Technological representativeness / Geographical representativeness /
Temporal representativeness / Completeness / Reliability of source — not a single combined score.
Flagged in advance:
- Transport: Geographical representativeness = Poor (UK default applied to West Africa); Reliability
  = Fair — sourced via a secondary aggregator (Climatiq) that names the exact official DESNZ 2024
  dataset/category, not independently re-verified against the primary spreadsheet cell.
- LUC ΔC magnitude (#6): Completeness = Fair (aboveground biomass only, excludes belowground/soil
  carbon); Reliability = Fair (arXiv preprint, peer-review status unconfirmed); Geographical
  representativeness = Very Good (Ghana/Côte d'Ivoire specific).
- Everything else above currently rates at least "Fair" on all five dimensions given Tier 1 use.
- Full per-category, per-dimension ratings are implemented in `dqr.py` and printed in the console
  output / README, not just summarised here.

## 12. Drying (post-harvest, IN farm-gate boundary)

| Method | Value | Unit |
|---|---|---|
| Sun/open-air | 0.0 | kg CO2e / kg dried product |
| Mechanical, coffee | 0.616 | kg CO2e / kg dried parchment coffee |
| Mechanical, cocoa | 0.616 (proxy) | kg CO2e / kg dried cocoa beans |

**Source (coffee):** Honduras biomass-dryer field study comparing three dryer types —
rotary (1.017 kg CO2e/kg, 12.60 MJ/kg), vertical (0.616 kg CO2e/kg, 7.46 MJ/kg), static
(0.33 kg CO2e/kg, 3.91 MJ/kg). The vertical-dryer value is used as the single Tier 1
"mechanical" default.

**Source (cocoa):** no cocoa-specific mechanical-drying LCA factor was found. The coffee
(Honduras) vertical-dryer value is reused as a cross-crop proxy (comparable moisture-removal
duty: cocoa ~60%→7-8%, coffee parchment ~50%→11-12%, both biomass/diesel-fired batch dryers).

**Modelling choice:** drying is kept INSIDE the farm-gate boundary because the functional
units ("dry cocoa beans" / "green coffee beans") are already post-drying — unlike roasting
(#13), which happens after export.

**Tier: Sourced** (coffee) **/ Illustrative — unverified** (cocoa proxy). Flagged
Reliability: Poor for cocoa in the DQR.

## 13. Roasting (OPTIONAL, OUT-OF-FARM-BOUNDARY extension)

**Scope note:** roasting is downstream of the farm-gate functional unit for BOTH crops —
cocoa is roasted as part of chocolate manufacture, just as coffee is roasted before grinding.
It is modelled as a separate, opt-in extension (`Scenario.roast_level`, default `"none"`),
never mixed into the main farm-gate PCF, because it changes both the system boundary and the
functional unit (green/dry beans → roasted beans).

| Roast level | Energy (electric roaster) | Emission factor (0.3 kg CO2e/kWh) |
|---|---|---|
| Light | 3.5 kWh/kg green | ~1.05 kg CO2e/kg green (coffee) |
| Medium | 5.04 kWh/kg green | ~1.51 kg CO2e/kg green (coffee) |
| Dark | 7.855 kWh/kg green | ~2.36 kg CO2e/kg green (coffee) |

Cocoa uses a `ROASTING_CROP_MULTIPLIER = 0.5` applied to the same kWh/kg table — an
**illustrative, unverified** placeholder (cocoa roasted at lower temperature/shorter duration
than coffee; no cocoa-specific roasting-energy study was found).

**Mass loss on roasting:** coffee 15-18% (commonly cited range, midpoint 16% used); cocoa
~4% (**illustrative, unverified** — no specific published figure found; cocoa roasting is at
lower temperature and loses much less mass than coffee, essentially residual moisture only).

**Critical caveat — cross-study uncertainty of ~100-300x:** an alternative published case
study (efficient gas-fired roaster with afterburner heat recovery) found that roasting
contributes only ~4% of a coffee product's total cradle-to-grave footprint — equivalent to
roughly 8 g CO2e/kg green coffee, two to three orders of magnitude below the electric-roaster
figures above. Both are documented here; the electric-roaster figures are used as the single
Tier 1 default only because they are the more conservative (higher) estimate.

**Sources:** batch-roaster energy/cost study (electric roaster, per-batch energy by roast
degree); efficient gas-fired roaster case study with afterburner heat recovery (~4% share /
~8 g CO2e/kg green coffee finding); cocoa roasting downstream-processing framing corroborated
by an industry LCA report (ifeu, Germany) describing "further processing, such as roasting and
cracking" as occurring in the consuming country, and by a cocoa-processing energy study
identifying roasting as one of eight quantifiable-but-bundled unit operations in cocoa-to-
powder manufacture.

**Tier: Sourced** (coffee kWh/kg table, mass-loss range) **/ Illustrative — unverified**
(cocoa multiplier, cocoa mass-loss, generic grid EF). Flagged Reliability: Poor across the
board given the documented ~100-300x cross-study spread.

## 14. Known limitations — major LCA posts identified but NOT yet modelled

Flagged here for transparency rather than fabricated with an unsourced factor:

- **On-farm energy / irrigation.** A cocoa value-chain study found irrigation and total
  energy consumption to be among the most important impact drivers alongside direct field
  emissions — a distinct post from fertiliser N2O, currently absent from this model.
- **Non-N agrochemicals (pesticides/fungicides/herbicides).** Manufacture and field-application
  emissions of crop-protection chemicals appear as hotspots in several cocoa/chocolate LCAs but
  are not quantified here (only N-fertiliser N2O is modelled).
- **Fermentation (cocoa-specific postharvest step).** A field study across five Ecuadorian
  postharvest sites found substantial variability in fermentation devices and duration (jute
  bags, plastic bags, wooden boxes) — too heterogeneous to derive a single defensible Tier 1
  emission factor at this time; considered conceptually bundled with drying but not separately
  quantified.
- **Cocoa pod-husk waste management.** At least one Colombian study models pod-husk
  decomposition/composting as its own emissions source; not modelled here.
- **Packaging and downstream retail/consumption** (both crops): out of the farm-to-first-
  processing boundary by design, consistent with how roasting is now also treated (#13).

**Tier: N/A (not implemented).** Documented as a roadmap item, not a current model input.

---

## Data Quality Rating (DQR) — dimensions to score per category (updated)

- Drying, cocoa: Reliability = Poor (cross-crop proxy, no cocoa-specific source);
  Geographical representativeness = Poor (Honduras data applied globally).
- Drying, coffee: Reliability = Fair (single-country field study); Geographical
  representativeness = Fair.
- Roasting (both crops): Reliability = Poor (documented ~100-300x cross-study spread);
  Completeness = Poor for cocoa specifically (multiplier + mass-loss both unverified);
  clearly labelled as an optional, out-of-boundary EXTENSION in every chart/CSV, never
  folded into the headline farm-gate PCF.

  ## 15. Boundary decision update (2026-09-24) — roasting merged into headline PCF

Superseding the initial "roasting = separate optional extension" design: roasting is now
**merged directly into the headline PCF** (`pcf_kg_co2e_per_kg`) whenever a scenario sets
`roast_level != "none"`. This is a deliberate user choice to see one total-chain number rather
than two separate figures.

**Consequence carried through the whole pipeline:** merging roasting changes the functional
unit from green/dry beans to roasted beans (`product_unit_label` switches automatically via
`factors.ROASTED_LABEL`). Because the decile/IQR literature bands (#9/#9b) were built on an
**unroasted** basis, they are:
- **not** drawn on any chart when the plotted scenarios are roasted (an explicit on-chart
  caveat replaces the band instead of silently mis-comparing);
- **not** used by the automated order-of-magnitude test against the headline PCF — the test
  instead checks the separately-retained `farm_gate_pcf_kg_co2e_per_kg` field, which is always
  computed pre-roasting regardless of `roast_level`.

**Known gap:** no defensible decile/IQR-style literature benchmark was found for a
roasted-basis cocoa or coffee PCF at this model's system boundary (farm → first processing →
roasting, excluding packaging/distribution/consumption). A commonly cited German pilot-project
figure (green coffee PCF ≈ 3.05 kg CO2e/kg, roasting ≈ 6% of that total) exists but covers a
**different, wider boundary** (production + transport + roasting + grinding + packaging +
consumption + disposal) and is not a like-for-like check for this tool's roasted-basis PCF —
flagged as a roadmap item rather than force-fit into the current test.

**Tier: N/A** (methodological/boundary decision, not a new factor).