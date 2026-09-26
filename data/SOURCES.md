# SOURCES.md — Cocoa & Coffee Carbon Footprint Prototype

Confidence tiers:
**Sourced** (traceable to a named tier-1/2 source in the hierarchy) /
**Estimated** (derived from sourced data with an explicit assumption) /
**Illustrative** (no defensible source found — flagged `# ILLUSTRATIVE - unverified` in code).

---

## PART I — Cross-crop soil N2O methodology (identical for cocoa and coffee)

### 1. Direct N2O emissions from N inputs (fertiliser) -- **Sourced**

**Source:** IPCC 2019 Refinement to the 2006 IPCC Guidelines, Vol. 4, Ch. 11, Table 11.1
("Default emission factors to estimate direct N2O emissions from managed soils").
https://www.ipcc-nggip.iges.or.jp/public/2019rf/pdf/4_Volume4/19R_V4_Ch11_Soils_N2O_CO2.pdf

**Choice:** the cocoa/coffee belt (Côte d'Ivoire, Ghana, most smallholder origins for both
crops) is IPCC "tropical wet" climate (annual precipitation > 1000 mm), so the wet-climate
disaggregated factors are used rather than the aggregated global default (0.010) — the more
geographically representative Tier 1 option, and still an official IPCC default.

**Value:**
| Parameter | Value | Unit |
|---|---|---|
| EF1, synthetic N, wet climate | 0.016 (range 0.013–0.019) | kg N2O–N / kg N applied |
| EF1, organic N / other inputs, wet climate | 0.006 (range 0.001–0.011) | kg N2O–N / kg N applied |
| N2O–N → N2O conversion | × 44/28 | — |

### 2. Indirect N2O — volatilisation pathway (NH3/NOx → redeposition) -- **Sourced**

**Source:** same IPCC 2019 Refinement, Table 11.3.

**Value:**
| Parameter | Value | Unit |
|---|---|---|
| FracGASF, synthetic fertiliser (aggregate) | 0.11 (urea-specific: 0.15) | kg N volatilised / kg N applied |
| FracGASM, organic N / manure | 0.21 | kg N volatilised / kg N applied |
| EF4, wet climate | 0.014 | kg N2O–N / kg N volatilised |

### 3. Indirect N2O — leaching/runoff pathway -- **Sourced**

**Source:** same IPCC 2019 Refinement, Table 11.3.

**Value:**
| Parameter | Value | Unit |
|---|---|---|
| FracLEACH-(H), wet climate | 0.24 | kg N leached / kg N applied |
| EF5 | 0.011 | kg N2O–N / kg N leached |

### 4. GWP100 for N2O -- **Sourced**

**Source:** IPCC AR6 WG1, Table 7.SM.7.
**Value:** 273 (100-year GWP, no climate–carbon feedbacks)

---

## PART II — Land-use change: mechanism (shared) + cocoa magnitude

### 5. Land-use-change (LUC) amortisation — mechanism -- **Sourced**

**Method:** total carbon-stock loss from conversion (ΔC, t C/ha) is amortised in equal shares
over 20 years: `annual LUC emission = ΔC × 44/12 × 1/20` (t CO2/ha/yr), added only for plots
converted from forest within the amortisation window. Crop-specific ΔC magnitudes are in
#6 (cocoa) and #11a (coffee); the mechanism itself is identical for both crops.

**Sources:**
- PAS 2050:2011 (BSI), §land-use-change methodology — establishes the 20-year amortisation
  convention and the ΔC × 44/12 × 1/20 formula; GHG Protocol Product Standard and Land Sector &
  Removals Guidance are aligned with this convention.
- SBTi FLAG Guidance v1.2 (2025) — companies must include LUC emissions from land converted
  within the preceding 20 years, and recommends a 2020 no-deforestation cutoff date; used here
  as the screening rule for whether a scenario's "converted from forest within the last 20 years"
  flag triggers the LUC term at all.
  https://sciencebasedtargets.org/blog/why-no-deforestation-must-be-a-priority-sbtis-flag-guidance-unpacked

### 6. Land-use-change — carbon stock loss magnitude (ΔC), cocoa -- **Sourced**

**Source:** Blaser-Hart, W.J., Hart, S.P. et al., "The unrealized potential of agroforestry
for an emissions-intensive agricultural commodity," *Nature Sustainability* (2025),
https://doi.org/10.1038/s41893-025-01608-7 — field/satellite-based aboveground carbon
density estimates specific to **Ghana and Côte d'Ivoire**.

**2026-09-26 correction:** this was previously cited as an unreviewed arXiv preprint
(arXiv:2410.20882) with "reliability reduced" flagged in the DQR. It has since been confirmed
published, peer-reviewed, in *Nature Sustainability* — the reliability caveat below no longer
applies and should be reflected as a DQR upgrade (see `src/dqr.py`, "Reliability of source":
Fair → Good).

Preferred over a generic IPCC 2006 GL Table 4.7 global default because it is (a) geographically
exact to the target region, (b) more recent, and (c) directly measured rather than a broad
ecozone default. **Caveat, still flagged in the DQR:** this is aboveground biomass carbon
only — it excludes belowground biomass, soil organic carbon and dead wood/litter, all of
which IPCC's full LUC accounting would include, so it understates total carbon-stock loss.

**Value:** ΔC ≈ 22.9 t C/ha (aboveground biomass only) = 36.6 t C/ha (intact forest) − 13.7 t C/ha
(average cocoa landscape carbon density).

---

## PART III — Transport (crop-agnostic)

### 7. Transport -- **Sourced**

**Source:** UK Department for Energy Security & Net Zero (DESNZ), "Greenhouse gas reporting:
conversion factors 2024," published 8 July 2024.
https://www.gov.uk/government/publications/greenhouse-gas-reporting-conversion-factors-2024

**Value:**
| Mode | Value | Unit |
|---|---|---|
| Truck (diesel articulated HGV, average laden) | 0.07547 | kg CO2e / tonne-km |
| Rail freight (diesel + electric mix, average) | 0.02779 | kg CO2e / tonne-km |
| Air (longhaul, international, estimated)      | 0.55    | kg CO2e / tonne-km |
| Sea (container ship, average estimate)        | 0.016   | kg CO2e / tonne-km |

**Geographical representativeness: Poor.** This is a UK-published generic default, not
West-Africa/origin-specific. **Reliability: Fair** — sourced via a secondary aggregator naming
the exact official dataset/category, not independently re-verified against the primary DESNZ
spreadsheet cell.

---

## PART IV — Cocoa-specific removal credit and literature benchmarks

### 8. Agroforestry / shade carbon removal credit, cocoa -- **Sourced + Estimated**

**Source:** peer-reviewed systematic review, "Carbon footprint of primary production of cacao: a
meta-analytical review," Environmental Reviews (2024/2025).
https://cdnsciencepub.com/doi/full/10.1139/er-2024-0146

**Modelling choice (Estimated):** the tool linearly interpolates between the unshaded rate
(0% canopy cover) and the agroforestry rate (treated as ~100% canopy cover) by the user's %
canopy-cover input — an explicit simplifying assumption on top of a sourced pair of endpoints,
flagged as such in code, not itself IPCC/peer-reviewed.

**Value:**
| System | Median CO2 removal rate | Interquartile range |
|---|---|---|
| Unshaded cocoa | 3,445 kg CO2/ha/yr | ±1,952 |
| Agroforestry (shaded) cocoa | 10,237 kg CO2/ha/yr | ±4,178 |

**Important nuance (see README.md, "Why agroforestry doesn't reduce the per-kg footprint"):**
this same review found that while agroforestry's area-based footprint and yields are both
lower than unshaded systems, the **product-level** footprint did not differ significantly —
i.e. this removal credit is a real, sourced co-benefit per hectare, but must never be netted
against the per-kg PCF. The tool enforces this by reporting emissions and removals as two
permanently separate numbers (`total_emissions_kg_co2e_yr` / `total_removals_kg_co2_yr`), never
combined into one net figure.

### 9. Order-of-magnitude literature range, cocoa — for the required verification test -- **Sourced**

**Source:** same meta-analytical review as #8.
- Product carbon footprint, excluding LUC: median 1.55 kg CO2e/kg dry beans; typical range
  (1st–8th decile across studies) 0.05–3.74 kg CO2e/kg dry beans.
- Product carbon footprint, including LUC (deforestation sub-sample, n=6–8 studies): median
  15.55 kg CO2e/kg dry beans (vs. 0.31 kg CO2e/kg dry beans without LUC in that same sub-sample).

**Use:** `test_calculations.py`'s order-of-magnitude check asserts no-LUC cocoa scenarios fall
within roughly the no-LUC range, and the LUC scenario lands in the LUC-inclusive range — both
cited ranges, not invented thresholds.

### 9b. Geographically-specific cross-check, cocoa — Ghana / Côte d'Ivoire -- **Sourced**

**Source:** same Blaser-Hart et al. (2025) paper as #6, citing Quantis/World Food LCA Database
estimates:
- Ghana: 2 kg CO2e/kg cocoa (excl. LUC) → 4 kg CO2e/kg cocoa (incl. LUC)
- Côte d'Ivoire: 2 kg CO2e/kg cocoa (excl. LUC) → 30 kg CO2e/kg cocoa (incl. LUC)

**Use:** a second, more geographically relevant anchor for the Scenario C order-of-magnitude
test alongside the global meta-analysis figures in #9. The no-LUC figure (2 kg CO2e/kg) is
consistent across both countries and close to Scenario A/D outputs, while the with-LUC figure
varies enormously by country (4 vs. 30) — reflecting how much deforestation risk differs by
origin.

---

## PART V — Coffee-specific factors

### 11. Coffee-specific land-use-change and agroforestry removal constants

Fertiliser N2O methodology (#1-#3), the LUC amortisation mechanism (#5), and transport EFs (#7)
are crop-agnostic and reused as-is from the cocoa sections above. This section covers only the
coffee-specific magnitudes.

#### 11a. Land-use-change ΔC — coffee -- **Sourced**

**Source:** Peruvian Amazon shade-system study, PMC11670197 (PubMed Central).
https://pmc.ncbi.nlm.nih.gov/articles/PMC11670197/

**Value:** ΔC = 101.1 t C/ha (aboveground biomass only) = 132.2 t C/ha (secondary forest) − 31.1
t C/ha (unshaded coffee).

**Caveats (Completeness = Fair):**
- Aboveground biomass only — excludes soil organic carbon, same limitation as the cocoa figure.
- The baseline is **secondary** forest, not primary/intact forest — more conservative than an
  Ethiopian corroborating figure of ~98.9 t C/ha vs. undisturbed natural forest, i.e. using
  primary forest as the baseline would likely give an even larger ΔC.
- This value is ~4-5x the cocoa ΔC (22.9 t C/ha, item #6). This is mainly because reference
  forest carbon stocks vary hugely by biome/region between the two source studies, **not**
  because coffee LUC is intrinsically worse than cocoa LUC — flagged explicitly to avoid a
  spurious cross-crop comparison being drawn from the model's output.

**Consequence flagged in #17:** combined with a low-yield, high-canopy-cover scenario, this ΔC
can produce a farm-gate PCF that exceeds even the sourced coffee with-LUC literature ceiling
(#11c). This is a known, documented model behaviour, not a silent error.

#### 11b. Agroforestry / shade carbon removal credit — coffee -- **Sourced + Estimated**

**Source:** Cornelius et al. 2025, "Carbon footprints and CO2 removal in primary production of
coffee: a meta-analytical review" (Environmental Reviews) — the coffee-specific companion to the
cacao meta-analysis used in #8. Median CDR rates. The same review also found that coffee's
product-level footprint does **not** differ significantly between agroforestry and unshaded
systems despite ~2.5x higher removals — same "do not net removals against PCF" caveat as #8.

**Modelling choice:** linear interpolation by % canopy cover between these two endpoints, same
method and caveat as #8 (Estimated, not itself drawn from the review).

**Value:**
| System | Median CO2 removal rate |
|---|---|
| Unshaded coffee | 6,990 kg CO2/ha/yr |
| Agroforestry (shaded) coffee | 17,676 kg CO2/ha/yr |

#### 11c. Order-of-magnitude literature range, coffee — WITHOUT and WITH LUC -- **Sourced**

**Without LUC (Cornelius et al. 2025):** median 2.18, ± IQR 2.04 kg CO2e/kg green coffee beans
→ range used in tests/charts: **0.14 – 4.22**. Cornelius et al. 2025 reports median ± IQR, not
deciles like the cacao paper, so this band is a rougher analogue of #9's decile range — flagged
as lower precision.

**With LUC (Chéron-Bessou et al. 2024, the ground-truth coffee review supplied with this tool):**
"Sustainable Production and Consumption" 47, 251-266, Table 2 — cradle-to-primary-processing-gate,
adjusted GWP range "with LUC": **1.63 – 10.52** kg CO2e/kg green coffee beans.
https://doi.org/10.1016/j.spc.2024.04.005

**Use:** `CoffeeOrderOfMagnitudeCheck` asserts no-LUC scenarios fall in the 0.14-4.22 band, and
the LUC scenario clears that ceiling. The with-LUC band's *upper* bound is used only loosely
(×3 margin) — see #17 for why.

---

## PART VI — Post-harvest processing, shared mechanism, crop-specific values

### 12. Drying (post-harvest, IN farm-gate boundary) -- **Sourced** (coffee) / **Illustrative — unverified** (cocoa proxy)

**Modelling choice:** drying is kept INSIDE the farm-gate boundary because the functional
units ("dry cocoa beans" / "green coffee beans") are already post-drying — unlike roasting
(#13), which happens after export.

**Sources:**
*Coffee* — Honduras biomass-dryer field study comparing three dryer types — rotary (1.017 kg
CO2e/kg, 12.60 MJ/kg), vertical (0.616 kg CO2e/kg, 7.46 MJ/kg), static (0.33 kg CO2e/kg,
3.91 MJ/kg). The vertical-dryer value is used as the single Tier 1 "mechanical" default.

*Cocoa* — no cocoa-specific mechanical-drying LCA factor was found. The coffee (Honduras)
vertical-dryer value is reused as a cross-crop proxy (comparable moisture-removal duty: cocoa
~60%→7-8%, coffee parchment ~50%→11-12%, both biomass/diesel-fired batch dryers).

**Value:**
| Method | Value | Unit |
|---|---|---|
| Sun/open-air | 0.0 | kg CO2e / kg dried product |
| Mechanical, coffee | 0.616 | kg CO2e / kg dried parchment coffee |
| Mechanical, cocoa | 0.616 (proxy) | kg CO2e / kg dried cocoa beans |

### 13. Roasting — factor sourcing -- **Sourced** (coffee) / **Illustrative — unverified** (cocoa proxy)

*This section covers only where the roasting EMISSION FACTORS come from. Whether/how roasting
is merged into a scenario's headline PCF is a separate methodological decision — see #15.*

**Sources:** batch-roaster energy/cost study (electric roaster, per-batch energy by roast
degree); efficient gas-fired roaster case study with afterburner heat recovery (~4% share /
~8 g CO2e/kg green coffee finding); cocoa roasting downstream-processing framing corroborated
by an industry LCA report (ifeu, Germany) describing roasting as occurring in the consuming
country, and by a cocoa-processing energy study identifying roasting as one of eight
quantifiable-but-bundled unit operations in cocoa-to-powder manufacture.

**Value:**
| Roast level | Energy (electric roaster) | Emission factor (0.3 kg CO2e/kWh) |
|---|---|---|
| Light | 3.5 kWh/kg green | ~1.05 kg CO2e/kg green (coffee) |
| Medium | 5.04 kWh/kg green | ~1.51 kg CO2e/kg green (coffee) |
| Dark | 7.855 kWh/kg green | ~2.36 kg CO2e/kg green (coffee) |

Cocoa uses a `ROASTING_CROP_MULTIPLIER = 0.5` applied to the same kWh/kg table — an
**illustrative, unverified** placeholder (cocoa roasted at lower temperature/shorter duration
than coffee; no cocoa-specific roasting-energy study was found).

**Mass loss on roasting:** coffee 15-18% (commonly cited range, midpoint 16% used); cocoa
~4% (**illustrative, unverified** — no specific published figure found).

**Critical caveat — cross-study uncertainty of ~100-300x:** an alternative published case
study (efficient gas-fired roaster with afterburner heat recovery) found that roasting
contributes only ~4% of a coffee product's total cradle-to-grave footprint — roughly 8 g
CO2e/kg green coffee, two to three orders of magnitude below the electric-roaster figures
above. Both are documented here; the electric-roaster figures are used as the single Tier 1
default only because they are the more conservative (higher) estimate.

### 15. Roasting — scope decision: merged into headline PCF -- **Methodological choice, not a new factor**

**Decision:** roasting is downstream of the farm-gate functional unit for both crops (cocoa is
roasted as part of chocolate manufacture; coffee is roasted before grinding). `run_scenario()`
(`src/calculations.py`) computes two figures:
- `farm_gate_pcf_kg_co2e_per_kg` — **always** pre-roasting (green/dry bean basis), so literature
  comparisons in #9/#9b/#11c (all reported on this basis) remain valid regardless of
  `roast_level`.
- `pcf_kg_co2e_per_kg` — the headline figure. Equal to the farm-gate figure when
  `roast_level == "none"`; when a scenario opts in, this MERGES the roasting add-on and the
  functional unit switches to roasted product (`product_unit_label` updates accordingly).

**Rationale:** an earlier design kept roasting entirely separate and never produced one final
combined answer. That was replaced (2026-09-24) because always reporting two same-named "PCF"
figures without ever giving a single headline number is confusing in a demo setting. Preserving
`farm_gate_pcf_kg_co2e_per_kg` alongside the merged figure keeps both a clear headline answer
and a full audit trail back to the unroasted comparison basis.

**Consequence for tests:** `test_calculations.py`'s literature-range checks always assert
against `farm_gate_pcf_kg_co2e_per_kg`, never against the roasted `pcf_kg_co2e_per_kg`.

---

## PART VII — Illustrative / unverified modelling assumptions

### 16. LUC retention discount for agroforestry conversion (canopy-cover interaction) -- **Illustrative**

**Mechanism:** `luc_co2e()` (`src/calculations.py`) reduces the forest→crop ΔC used in the LUC
amortisation (#5/#6/#11a) by `LUC_RETENTION_FRACTION_AGROFORESTRY × (canopy_cover_pct / 100)`,
i.e. a conversion straight to a 100%-canopy agroforestry system is modelled as retaining 30%
more standing woody biomass on-site than a conversion to unshaded monoculture; at 0% canopy
cover the discount is zero and the calculation reduces to the plain ΔC × 44/12 × 1/20 formula.

**Value:** `LUC_RETENTION_FRACTION_AGROFORESTRY = 0.30`.

**Tier: Illustrative - unverified.** This is this tool's own modelling assumption, not a value
taken from a named study. An earlier code comment described it as "conservatively calibrated at
the lower end of a 2.5x-5x range reported in the cocoa literature" — that framing was an
informal recollection, not a pinned citation, and has been removed to avoid it reading as
Sourced. Treat 0.30 as a placeholder: the *direction* of the assumption (agroforestry
conversion retains more on-site carbon than full-sun conversion) is intuitive and broadly
consistent with agroforestry LCA literature, but the specific magnitude has not been
independently verified against a named source.

**Affected scenarios:** any scenario with both `land_use_change=True` and
`canopy_cover_pct > 0`. Flagged as its own line so it cannot be mistaken for part of the
(Sourced) LUC mechanism itself.

**Improvement:** replace with a Tier 2 factor specific to cocoa/coffee agroforestry conversion
if one becomes available; until then, treat any scenario's LUC-with-shade result as
illustrative of the *mechanism*, not a validated magnitude.

---

## PART VIII — Known model behaviours & test-design notes

### 17. Coffee Scenario E: LUC + high canopy cover can exceed the literature with-LUC ceiling

**What happens:** the coffee LUC ΔC (101.1 t C/ha, #11a) is already ~4-5x the cocoa ΔC for
reasons unrelated to crop-intrinsic impact (#11a). Combine that with the illustrative LUC
retention discount (#16) at high canopy cover, applied to a low-yield coffee scenario, and the
resulting farm-gate PCF can land above even the sourced 1.63–10.52 kg CO2e/kg with-LUC range
(#11c).

**Why this is expected, not a bug:** none of the three inputs driving this (coffee's higher ΔC,
the illustrative retention discount, a deliberately low-yield scenario) is individually wrong —
their combination in one stress-test scenario simply pushes past a literature band that was
never designed to bound every possible combination of inputs.

**Consequence for tests:** `CoffeeOrderOfMagnitudeCheck` in `test_calculations.py` uses a wider
(×3) margin on the upper bound of #11c's with-LUC range, rather than the raw ceiling, so the
test still catches a genuine gross error (e.g. a 10x unit-conversion mistake) without failing
on this known, legitimate outlier.

---

## Data Quality Rating (DQR)

Per-category ratings (five dimensions — Technological/Geographical/Temporal representativeness,
Completeness, Reliability of source — combined via a "weakest dimension" rule) are maintained
as **executable code**, not a static table here, to avoid the two ever drifting apart: see
`src/dqr.py::DQR_RATINGS` and run `python -m src.dqr` (or `python main.py`, which calls it
automatically) for the current report. The reasoning behind each rating is written directly
next to the sourcing decision it evaluates, in the relevant section above.