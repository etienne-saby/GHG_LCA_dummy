"""
factors.py — Every emission/removal factor and methodological constant used by this
prototype. Every value below is traceable to SOURCES.md. Nothing here is a bare
"looks about right" number: sourced values are commented with their citation and
confidence tier; anything that could not be sourced is flagged
`# ILLUSTRATIVE - unverified` per CLAUDE.md's "no fabricated precision" rule.

Full citations, confidence tiers (Sourced / Estimated / Illustrative) and the
reasoning behind each choice live in SOURCES.md — this file only carries the
values and a one-line pointer back to the relevant SOURCES.md section.
"""

# ---------------------------------------------------------------------------
# Unit conversions
# ---------------------------------------------------------------------------

N2O_N_TO_N2O = 44 / 28          # molecular weight ratio: convert kg N2O-N -> kg N2O
C_TO_CO2 = 44 / 12              # molecular weight ratio: convert kg C -> kg CO2
KG_TO_TONNE = 1 / 1000

# ---------------------------------------------------------------------------
# 1-4. Fertiliser N2O — IPCC 2019 Refinement to the 2006 Guidelines, Vol.4 Ch.11
# SOURCES.md items #1-#4. Tropical-wet-climate-disaggregated values used
# throughout (cocoa belt = IPCC "tropical wet"), since IPCC offers that
# disaggregation for every factor where a wet/dry split exists.
# ---------------------------------------------------------------------------

# --- Direct N2O (Table 11.1) — Sourced ---
EF1_SYNTHETIC_WET = 0.016   # kg N2O-N / kg synthetic N applied (range 0.013-0.019)
EF1_ORGANIC_WET = 0.006     # kg N2O-N / kg organic N applied (range 0.001-0.011)

# --- Indirect N2O, volatilisation pathway (Table 11.3) — Sourced ---
# FracGASF/FracGASM are disaggregated by fertiliser TYPE, not climate (a separate
# axis from EF1's wet/dry split) — the aggregate default is used here since the
# scenarios don't specify a fertiliser sub-type. Urea-specific FracGASF = 0.15
# is available if that detail is ever added.
FRAC_GASF = 0.11             # kg N volatilised / kg synthetic N applied (aggregate)
FRAC_GASM = 0.21             # kg N volatilised / kg organic N applied (aggregate)
EF4_WET = 0.014              # kg N2O-N / kg N volatilised (wet climate; aggregate=0.010)

# --- Indirect N2O, leaching pathway (Table 11.3) — Sourced ---
# FracLEACH-(H) is explicitly the wet-climate value (IPCC states the dry-climate
# default is 0); EF5 has no wet/dry disaggregation in IPCC Tier 1 at all, so 0.011
# is simply the only available default, not an "aggregate vs wet" choice.
FRAC_LEACH_WET = 0.24        # kg N leached / kg N applied (wet climate only)
EF5 = 0.011                  # kg N2O-N / kg N leached (single Tier 1 default)

# --- GWP100 for N2O — Sourced ---
GWP_N2O = 273                # IPCC AR6 WG1 Table 7.SM.7 (100-yr, no climate-carbon feedback)

# ---------------------------------------------------------------------------
# 5-6. Land-use change — SOURCES.md items #5, #6
# ---------------------------------------------------------------------------

LUC_AMORTISATION_YEARS = 20
# Mechanism source: PAS 2050:2011 / GHG Protocol Land Sector & Removals Guidance
# convention. Screening rule (has land been converted within the amortisation
# window at all) follows SBTi FLAG Guidance v1.2 (2025)'s 20-year inclusion
# window / 2020 no-deforestation cutoff framing. — Sourced (mechanism)

LUC_DELTA_C_FOREST_TO_COCOA = 22.9   # t C/ha aboveground biomass, forest -> cocoa
# Source: Becker et al. 2024 (arXiv:2410.20882), Ghana/Côte d'Ivoire field data:
# intact forest 36.6 t C/ha minus average cocoa landscape 13.7 t C/ha. — Sourced,
# but Completeness = Fair: aboveground biomass only, excludes belowground biomass
# and soil organic carbon (see SOURCES.md #6), so this understates true LUC impact.

# ---------------------------------------------------------------------------
# 7. Transport — UK DESNZ "Conversion Factors 2024" — SOURCES.md item #7
# Sourced via a secondary aggregator (Climatiq) naming the exact official
# dataset/category; not independently re-verified against the primary DESNZ
# spreadsheet cell — Reliability flagged Fair (not Very Good) in dqr.py.
# Geographical representativeness flagged Poor: UK default standing in for
# West African freight.
# ---------------------------------------------------------------------------

TRANSPORT_EF_TRUCK = 0.07547   # kg CO2e / tonne-km (diesel articulated HGV, avg laden)
TRANSPORT_EF_RAIL = 0.02779    # kg CO2e / tonne-km (rail freight, diesel+electric mix)
TRANSPORT_EF_SEA_CONTAINER = 0.016   # kg CO2e / tonne-km, container ship avg — ESTIMATED
TRANSPORT_EF_AIR_LONGHAUL = 0.55     # kg CO2e / tonne-km, international >3700km, WITHOUT RF multiplier — ESTIMATED

# ---------------------------------------------------------------------------
# 8. Agroforestry / shade carbon removal credit — SOURCES.md item #8
# Source: peer-reviewed meta-analytical review, "Carbon footprint of primary
# production of cacao" (Environmental Reviews, 2024/2025).
# The tool linearly interpolates between these two sourced endpoints by %
# canopy cover — that interpolation step is our modelling choice (Estimated),
# not itself drawn from the review.
# ---------------------------------------------------------------------------

REMOVAL_RATE_UNSHADED = 3445    # kg CO2/ha/yr at 0% canopy cover
REMOVAL_RATE_AGROFORESTRY = 10237  # kg CO2/ha/yr at ~100% canopy cover (review's shaded median)

# ---------------------------------------------------------------------------
# 9. Literature benchmarks for the order-of-magnitude verification test
# (test_calculations.py) — SOURCES.md items #9, #9b. Not used in the
# calculation itself, only to sanity-check its output.
# ---------------------------------------------------------------------------

# Global meta-analysis (cacao, all origins), excluding LUC:
LIT_PCF_NO_LUC_DECILE_LOW = 0.05    # kg CO2e/kg dry beans (1st decile)
LIT_PCF_NO_LUC_DECILE_HIGH = 3.74   # kg CO2e/kg dry beans (8th decile)
LIT_PCF_NO_LUC_MEDIAN = 1.55        # kg CO2e/kg dry beans

# Global meta-analysis, paired sub-sample with vs. without LUC:
LIT_PCF_LUC_MEDIAN = 15.55          # kg CO2e/kg dry beans (with LUC)

# Ghana / Côte d'Ivoire specific (Becker et al. 2024, via Quantis/WFLDB):
LIT_PCF_GHANA_NO_LUC = 2.0
LIT_PCF_GHANA_LUC = 4.0
LIT_PCF_CIV_NO_LUC = 2.0
LIT_PCF_CIV_LUC = 30.0

# ---------------------------------------------------------------------------
# 10-11. Coffee-specific LUC and removal constants — SOURCES.md items #10-#11
# Fertiliser N2O methodology (IPCC Tables 11.1/11.3) and transport EFs are
# crop-agnostic and reused as-is from the cocoa section above.
# ---------------------------------------------------------------------------

LUC_DELTA_C_FOREST_TO_COFFEE = 101.1  # t C/ha, secondary forest -> unshaded coffee
# Source: Peruvian Amazon study (PMC11670197): secondary forest biomass C stock
# 132.2 t/ha minus unshaded coffee 31.1 t/ha. — Sourced, but Completeness = Fair:
# (a) aboveground biomass only, excludes soil organic carbon; (b) baseline is
# SECONDARY forest, not primary/intact forest (more conservative than Ethiopian
# corroboration of ~98.9 t C/ha vs undisturbed natural forest); (c) this value
# is ~4-5x the cocoa ΔC (22.9 t C/ha) mainly because reference forest carbon
# stocks vary hugely by biome/region between the two source studies, not
# necessarily because coffee LUC is intrinsically worse than cocoa LUC —
# flagged explicitly to avoid a spurious cross-crop comparison.

REMOVAL_RATE_UNSHADED_COFFEE = 6990      # kg CO2/ha/yr at 0% canopy cover
REMOVAL_RATE_AGROFORESTRY_COFFEE = 17676  # kg CO2/ha/yr at ~100% canopy cover
# Source: Cornelius et al. 2025, "Carbon footprints and CO2 removal in primary
# production of coffee: a meta-analytical review" (Environmental Reviews),
# median CDR rates. Same review also found PCF does NOT differ significantly
# between agroforestry and unshaded coffee despite ~2.5x higher removals —
# same "do not net removals against PCF" caveat as the cocoa section (#8).

# --- Coffee literature band (verification test only) — derived, not a new source ---
# Cornelius et al. 2025 gives median +/- IQR, not deciles (unlike the cacao paper),
# so this band is a rougher analogue of LIT_PCF_NO_LUC_DECILE_LOW/HIGH — median +/- IQR
# used as a stand-in range. Flagged as lower precision than the cocoa decile band.
LIT_PCF_COFFEE_NO_LUC_LOW = 0.14   # max(0, 2.18 - 2.04)
LIT_PCF_COFFEE_NO_LUC_HIGH = 4.22  # 2.18 + 2.04

# Fraction of the forest-to-crop delta-C that is "avoided" when conversion occurs to
# a 100%-canopy agroforestry system, rather than to a full-sun
# monoculture. Illustrative Tier 1 value, conservatively calibrated at the lower end of the
# 2.5x-5x range reported in the cocoa literature (see SOURCES.md #X).
# To be refined if a Tier 2 factor specific to cocoa/coffee becomes available.
LUC_RETENTION_FRACTION_AGROFORESTRY = 0.30

# ---------------------------------------------------------------------------
# 12. Drying — post-harvest, IN farm-gate boundary — SOURCES.md item #12
#
# Applies to both crops. The functional units "dry cocoa beans" / "green
# coffee beans" are already POST-drying, so drying energy belongs INSIDE the
# existing farm-gate boundary — unlike roasting (item #13 below), which
# happens after export and is therefore kept as a separate extension.
# ---------------------------------------------------------------------------

DRYING_EF_SUN = 0.0
# kg CO2e / kg dried product. Sun/open-air drying: no fossil-fuel energy
# input (ambient solar heat + manual turning labour, the latter not
# modelled). Source (qualitative contrast, not a quantified factor): sector
# guidance confirming solar drying's footprint is far lower than mechanical
# drying. — Sourced (direction/ranking), Estimated (=0 as the point value).

DRYING_EF_MECHANICAL_COFFEE = 0.616
# kg CO2e / kg dried parchment coffee. Source: Honduras biomass-dryer field
# study comparing three dryer types — rotary (1.017 kg CO2e/kg, 12.60
# MJ/kg), vertical (0.616 kg CO2e/kg, 7.46 MJ/kg), static (0.33 kg CO2e/kg,
# 3.91 MJ/kg). The VERTICAL dryer value is used as the single Tier 1
# "mechanical" default (mid-point of the three), since scenarios don't (yet)
# specify a dryer sub-type. — Sourced; Completeness: Fair (one
# country/technology set standing in for "mechanical drying" in general).

DRYING_EF_MECHANICAL_COCOA = 0.616
# ILLUSTRATIVE - unverified: no cocoa-specific mechanical-drying LCA factor
# was found in the literature search. This reuses the coffee (Honduras)
# vertical-dryer value as a cross-crop proxy, on the reasoning that both are
# biomass/diesel-fired batch dryers removing a broadly comparable order of
# magnitude of moisture (cocoa ~60%->7-8%; coffee parchment ~50%->11-12%).
# Flagged Reliability: Poor in the DQR pending a cocoa-specific source.

# ---------------------------------------------------------------------------
# 13. Roasting — OPTIONAL, OUT-OF-FARM-BOUNDARY extension — SOURCES.md item #13
#
# Roasting happens downstream of the farm-gate functional unit (typically
# after export, at/near the consuming market) for BOTH crops: cocoa is
# roasted as part of chocolate manufacture (cleaning/roasting/winnowing/
# milling/... chain) just as coffee is roasted before grinding. It is kept
# OUT of the main PCF calculation (main.py: run_scenario()) by default, and
# is only computed as a separate, clearly-labelled extension
# (main.py: run_roasting_extension) when a scenario opts in via
# `roast_level != "none"`, because:
#   (a) it changes the functional unit (green/dry beans -> roasted beans)
#       via a mass-loss factor that differs sharply between the two crops;
#   (b) published roasting emission factors vary by ~100-300x across studies
#       depending on fuel (electric vs gas), degree of roast, and whether
#       heat-recovery/afterburner post-combustion is fitted — far more
#       variable than any other factor in this model, so it must never be
#       silently netted into a "PCF" that reads as directly comparable to
#       the farm-gate one.
# ---------------------------------------------------------------------------

ROASTING_MASS_LOSS_FRACTION_COFFEE = 0.16
# 15-18% mass loss on roasting (moisture + volatile compounds) is the
# commonly cited range for coffee; midpoint used. — Sourced (range),
# Estimated (point value).

ROASTING_MASS_LOSS_FRACTION_COCOA = 0.04
# ILLUSTRATIVE - unverified: cocoa roasting (lower temperature/shorter
# duration than coffee, ~120-150C vs coffee's ~200-230C) is understood to
# lose much less mass — essentially residual moisture only. No specific
# published figure was found for cocoa; placeholder pending a sourced value.

ROAST_LEVEL_KWH_PER_KG = {
    "light": 3.5,     # 17.5 kWh / 5 kg batch
    "medium": 5.04,   # 25.2 kWh / 5 kg batch
    "dark": 7.855,    # 39.275 kWh / 5 kg batch
}
# Source: batch-roaster energy/cost study, electric roaster, per-batch energy
# by roast degree (green coffee basis). — Sourced (single study/technology);
# Estimated as a general Tier 1 default given roaster energy intensity
# varies enormously by equipment (see caveat below).

GRID_EF_ROASTING_ILLUSTRATIVE = 0.3   # kg CO2e / kWh
# Generic grid emission factor assumed by the same source study — NOT
# specific to any real country's grid mix. ILLUSTRATIVE - unverified as a
# general default; a real deployment should use the roaster's actual
# electricity (or gas) supplier's factor.

ROASTING_CROP_MULTIPLIER = {"coffee": 1.0, "cocoa": 0.5}
# ILLUSTRATIVE - unverified: cocoa is roasted at a lower temperature and
# often for a shorter duration than coffee, so its energy intensity is
# ASSUMED (not measured) to be roughly half of coffee's per unit mass. No
# cocoa-specific roasting-energy study was found to confirm this ratio —
# treat strictly as an order-of-magnitude placeholder, not a sourced figure.

# Caveat carried into the DQR and into every chart/console label showing a
# roasted PCF: an alternative published case study (efficient gas-fired
# roaster with afterburner heat recovery) found that roasting contributes
# only ~4% of a coffee product's total cradle-to-grave footprint —
# equivalent to roughly 8 g CO2e/kg green coffee, i.e. 100-300x LOWER than
# the electric-roaster-derived figures above. Both figures are documented in
# SOURCES.md #13; ROAST_LEVEL_KWH_PER_KG is kept as the single Tier 1
# default only because it is the more conservative (higher) of the two.

ROASTED_LABEL = {"cocoa": "roasted cocoa beans", "coffee": "roasted coffee beans"}