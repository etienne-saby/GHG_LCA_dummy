"""
scenarios/cocoa/scenarios_sea.py — Cocoa farm profiles, sea transport.

Illustrative-but-plausible farm profiles (not a specific real farm); emission/
removal FACTORS applied to them are sourced (factors.py/SOURCES.md). Farm size
(3 ha) follows Becker et al. 2024's Ghana/Cote d'Ivoire smallholder note.

Design note: transport distance/mode held identical across A-F so the
comparison isolates fertiliser/LUC/shade effects, not transport.
"""
from src.config import Scenario

SCENARIOS_SEA = [
    Scenario(
        name="A. Conventional baseline",
        description="No agroforestry, moderate synthetic fertiliser, no recent LUC.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=400,
        synthetic_n_kg_per_ha_yr=60, organic_n_kg_per_ha_yr=0,
        land_use_change=False, canopy_cover_pct=0,
        transport_distance_km=6000, transport_mode="sea",
    ),
    Scenario(
        name="B. + Agroforestry",
        description="Same fertiliser/yield as A, 40% shade added — isolates removal-credit effect.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=400,
        synthetic_n_kg_per_ha_yr=60, organic_n_kg_per_ha_yr=0,
        land_use_change=False, canopy_cover_pct=40,
        transport_distance_km=6000, transport_mode="sea",
    ),
    Scenario(
        name="C. Recent conversion, high input",
        description="Converted from forest <20yr, high synthetic fertiliser, no shade.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=500,
        synthetic_n_kg_per_ha_yr=120, organic_n_kg_per_ha_yr=0,
        land_use_change=True, canopy_cover_pct=0,
        transport_distance_km=6000, transport_mode="sea",
    ),
    Scenario(
        name="D. Certified / improved practice",
        description="Agroforestry + reduced, partly-organic fertiliser + no recent LUC.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=350,
        synthetic_n_kg_per_ha_yr=20, organic_n_kg_per_ha_yr=40,
        land_use_change=False, canopy_cover_pct=40,
        transport_distance_km=6000, transport_mode="sea",
    ),
    Scenario(
        name="E. Agroforestry, organic in forest",
        description="Agroforestry + fully organic fertiliser + recent LUC.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=300,
        synthetic_n_kg_per_ha_yr=0, organic_n_kg_per_ha_yr=80,
        land_use_change=True, canopy_cover_pct=50,
        transport_distance_km=6000, transport_mode="sea",
    ),
    Scenario(
        name="F. Agroforestry, organic, no recent LUC",
        description="Agroforestry + fully organic fertiliser + no recent LUC.",
        crop="cocoa", product_unit_label="dry cocoa beans",
        area_ha=3.0, yield_kg_per_ha_yr=300,
        synthetic_n_kg_per_ha_yr=0, organic_n_kg_per_ha_yr=80,
        land_use_change=False, canopy_cover_pct=50,
        transport_distance_km=6000, transport_mode="sea",
    ),
]