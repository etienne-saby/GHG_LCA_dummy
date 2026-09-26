"""
scenarios/cocoa/scenarios_sea_roasted.py — Same six cocoa farm profiles as
scenarios_sea.py, sea transport, but with roast_level="dark" to demonstrate
the merged roasting extension (SOURCES.md #13). NOT imported into main.py's
CROP_SCENARIOS — wired in separately via ROASTED_SCENARIOS / run_roasted(),
writing to its own data/output/cocoa/roasted_demo/ subfolder so it never
mixes with the unroasted charts (which would otherwise silently combine two
different functional units — dry beans vs. roasted beans — in the same
stacked bar).

Scenario names are suffixed " — dark roast" to avoid colliding with the
plain (unroasted) sea scenarios' (name, transport_mode) keys in charts/CSVs
that group results by that psea.
"""
from src.config import Scenario

SCENARIOS_SEA_ROASTED = [
    Scenario(
        name="A. Conventional baseline — dark roast",
        description="No agroforestry, moderate synthetic fertiliser, no recent LUC. Roasted, dark.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=400,
        synthetic_n_kg_per_ha_yr=60, organic_n_kg_per_ha_yr=0,
        land_use_change=False, canopy_cover_pct=0,
        transport_distance_km=6000, transport_mode="sea",
        roast_level="dark",
    ),
    Scenario(
        name="B. + Agroforestry — dark roast",
        description="Same fertiliser/yield as A, 40% shade added. Roasted, dark.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=400,
        synthetic_n_kg_per_ha_yr=60, organic_n_kg_per_ha_yr=0,
        land_use_change=False, canopy_cover_pct=40,
        transport_distance_km=6000, transport_mode="sea",
        roast_level="dark",
    ),
    Scenario(
        name="C. Recent conversion, high input — dark roast",
        description="Converted from forest <20yr, high synthetic fertiliser, no shade. Roasted, dark.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=500,
        synthetic_n_kg_per_ha_yr=120, organic_n_kg_per_ha_yr=0,
        land_use_change=True, canopy_cover_pct=0,
        transport_distance_km=6000, transport_mode="sea",
        roast_level="dark",
    ),
    Scenario(
        name="D. Certified / improved practice — dark roast",
        description="Agroforestry + reduced, partly-organic fertiliser + no recent LUC. Roasted, dark.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=350,
        synthetic_n_kg_per_ha_yr=20, organic_n_kg_per_ha_yr=40,
        land_use_change=False, canopy_cover_pct=40,
        transport_distance_km=6000, transport_mode="sea",
        roast_level="dark",
    ),
    Scenario(
        name="E. Agroforestry, organic in forest — dark roast",
        description="Agroforestry + fully organic fertiliser + recent LUC. Roasted, dark.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=300,
        synthetic_n_kg_per_ha_yr=0, organic_n_kg_per_ha_yr=80,
        land_use_change=True, canopy_cover_pct=50,
        transport_distance_km=6000, transport_mode="sea",
        roast_level="dark",
    ),
    Scenario(
        name="F. Agroforestry, organic, no recent LUC — dark roast",
        description="Agroforestry + fully organic fertiliser + no recent LUC. Roasted, dark.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=300,
        synthetic_n_kg_per_ha_yr=0, organic_n_kg_per_ha_yr=80,
        land_use_change=False, canopy_cover_pct=50,
        transport_distance_km=6000, transport_mode="sea",
        roast_level="dark",
    ),
]