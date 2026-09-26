"""
scenarios/coffee/scenarios_sea.py — Coffee farm profiles, sea transport.

Yield references (see chat research): smallholder coffee (<5ha) global range
~500-1000 kg green beans/ha/yr; Brazil/intensive systems 1500-2500+ kg/ha/yr;
Ethiopia smallholder ~250-600 kg/ha/yr; agroforestry shade <50% has only a mild
yield penalty in coffee (unlike cacao) per Peruvian Amazon shade-system data.
Fertiliser inputs are illustrative-but-plausible, bounded by literature noting
coffee N applications commonly 100-300+ kg N/ha/yr in intensive systems.
Farm size (3 ha) is a DESIGN CHOICE for cross-crop comparability with cocoa's
Becker et al. convention — NOT itself a sourced coffee smallholder farm-size
figure (no single equivalent found; coffee smallholder plots range ~0.16-5+ ha
worldwide depending on country).

Design note: transport distance/mode held identical across A-F, as in cocoa.
"""
from src.config import Scenario

SCENARIOS_SEA = [
    Scenario(
        name="A. Conventional baseline",
        description="No agroforestry, moderate synthetic N, no recent LUC.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=900,
        synthetic_n_kg_per_ha_yr=150, organic_n_kg_per_ha_yr=0,
        land_use_change=False, canopy_cover_pct=0,
        transport_distance_km=6000, transport_mode="sea",
    ),
    Scenario(
        name="B. + Agroforestry",
        description="Same fertiliser as A, 40% shade added — coffee shows only a mild yield penalty at this shade level (unlike cacao).",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=850,
        synthetic_n_kg_per_ha_yr=150, organic_n_kg_per_ha_yr=0,
        land_use_change=False, canopy_cover_pct=40,
        transport_distance_km=6000, transport_mode="sea",
    ),
    Scenario(
        name="C. Recent conversion, high input",
        description="Converted from forest <20yr, intensive high-N system, no shade.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=1800,
        synthetic_n_kg_per_ha_yr=300, organic_n_kg_per_ha_yr=0,
        land_use_change=True, canopy_cover_pct=0,
        transport_distance_km=6000, transport_mode="sea",
    ),
    Scenario(
        name="D. Certified / improved practice",
        description="Agroforestry + reduced, partly-organic fertiliser + no recent LUC.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=1000,
        synthetic_n_kg_per_ha_yr=50, organic_n_kg_per_ha_yr=60,
        land_use_change=False, canopy_cover_pct=40,
        transport_distance_km=6000, transport_mode="sea",
    ),
    Scenario(
        name="E. Agroforestry, organic in forest",
        description="Agroforestry + fully organic fertiliser + recent LUC.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=600,
        synthetic_n_kg_per_ha_yr=0, organic_n_kg_per_ha_yr=100,
        land_use_change=True, canopy_cover_pct=50,
        transport_distance_km=6000, transport_mode="sea",
    ),
    Scenario(
        name="F. Agroforestry, organic, no recent LUC",
        description="Agroforestry + fully organic fertiliser + no recent LUC.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=600,
        synthetic_n_kg_per_ha_yr=0, organic_n_kg_per_ha_yr=100,
        land_use_change=False, canopy_cover_pct=50,
        transport_distance_km=6000, transport_mode="sea",
    ),
]