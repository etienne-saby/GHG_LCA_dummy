"""
scenarios/coffee/scenarios_truck_roasted.py — Same six coffee farm profiles as
scenarios_truck.py (fertiliser/yield/LUC/shade unchanged), but with
transport_mode="truck" (distance 1000km, matching the cocoa truck convention) and
roast_level="dark" to demonstrate the merged roasting extension
(SOURCES.md #13). NOT imported by default in main.py's CROP_SCENARIOS — wired
in separately via ROASTED_SCENARIOS / run_roasted(), writing to its
own data/output/coffee/roasted_demo/ subfolder so it never mixes with the
unroasted charts (which would otherwise silently combine two different
functional units — green vs. roasted beans — in the same stacked bar).

Scenario names are suffixed " — dark roast" to avoid colliding with the plain
(unroasted) scenarios' (name, transport_mode) keys in any chart/CSV that
groups results by that pair.
"""
from src.config import Scenario

SCENARIOS_TRUCK_ROASTED = [
    Scenario(
        name="A. Conventional baseline — dark roast",
        description="No agroforestry, moderate synthetic N, no recent LUC. Roasted, dark.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=900,
        synthetic_n_kg_per_ha_yr=150, organic_n_kg_per_ha_yr=0,
        land_use_change=False, canopy_cover_pct=0,
        transport_distance_km=150, transport_mode="truck",
        roast_level="dark",
    ),
    Scenario(
        name="B. + Agroforestry — dark roast",
        description="Same fertiliser as A, 40% shade added. Roasted, dark.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=850,
        synthetic_n_kg_per_ha_yr=150, organic_n_kg_per_ha_yr=0,
        land_use_change=False, canopy_cover_pct=40,
        transport_distance_km=150, transport_mode="truck",
        roast_level="dark",
    ),
    Scenario(
        name="C. Recent conversion, high input — dark roast",
        description="Converted from forest <20yr, intensive high-N system, no shade. Roasted, dark.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=1800,
        synthetic_n_kg_per_ha_yr=300, organic_n_kg_per_ha_yr=0,
        land_use_change=True, canopy_cover_pct=0,
        transport_distance_km=150, transport_mode="truck",
        roast_level="dark",
    ),
    Scenario(
        name="D. Certified / improved practice — dark roast",
        description="Agroforestry + reduced, partly-organic fertiliser + no recent LUC. Roasted, dark.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=1000,
        synthetic_n_kg_per_ha_yr=50, organic_n_kg_per_ha_yr=60,
        land_use_change=False, canopy_cover_pct=40,
        transport_distance_km=150, transport_mode="truck",
        roast_level="dark",
    ),
    Scenario(
        name="E. Agroforestry, organic in forest — dark roast",
        description="Agroforestry + fully organic fertiliser + recent LUC. Roasted, dark.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=600,
        synthetic_n_kg_per_ha_yr=0, organic_n_kg_per_ha_yr=100,
        land_use_change=True, canopy_cover_pct=50,
        transport_distance_km=150, transport_mode="truck",
        roast_level="dark",
    ),
    Scenario(
        name="F. Agroforestry, organic, no recent LUC — dark roast",
        description="Agroforestry + fully organic fertiliser + no recent LUC. Roasted, dark.",
        crop="coffee", product_unit_label="green coffee beans",
        area_ha=3.0, yield_kg_per_ha_yr=600,
        synthetic_n_kg_per_ha_yr=0, organic_n_kg_per_ha_yr=100,
        land_use_change=False, canopy_cover_pct=50,
        transport_distance_km=150, transport_mode="truck",
        roast_level="dark",
    ),
]