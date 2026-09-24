"""
config.py — Scenario dataclass shared by every scenarios/<crop>/*.py file.
"""

from dataclasses import dataclass


@dataclass
class Scenario:
    name: str
    description: str
    crop: str                  # "cocoa" or "coffee" — selects LUC/removal/drying/roasting constants
    product_unit_label: str    # e.g. "dry cocoa beans" / "green coffee beans" — FARM-GATE functional
                                # unit, used in plot axes. NOTE: if roast_level != "none", the roasting
                                # EXTENSION (main.py: run_roasting_extension) reports a SEPARATE
                                # roasted-product PCF under its own label (factors.ROASTED_LABEL) — it
                                # never overwrites this field, since the two units are not directly
                                # comparable (see SOURCES.md #13).
    area_ha: float                          # ILLUSTRATIVE - demo farm profile
    yield_kg_per_ha_yr: float               # ILLUSTRATIVE - demo farm profile
    synthetic_n_kg_per_ha_yr: float         # ILLUSTRATIVE - demo farm profile
    organic_n_kg_per_ha_yr: float           # ILLUSTRATIVE - demo farm profile
    land_use_change: bool                   # converted from forest within last 20 yrs
    canopy_cover_pct: float                 # 0-100, ILLUSTRATIVE - demo farm profile
    transport_distance_km: float            # ILLUSTRATIVE - demo farm profile
    transport_mode: str                     # "truck", "rail", "air", "sea"

    # --- New fields (2026-09-24) ---
    drying_method: str = "mechanical"
    # "sun" or "mechanical" — post-harvest drying, IN the farm-gate boundary
    # (the functional unit "dry cocoa beans"/"green coffee beans" is already
    # POST-drying). Default "mechanical" is the conservative Tier 1 choice
    # and keeps all 8 existing scenario files unchanged/valid. See
    # SOURCES.md #12.

    roast_level: str = "none"
    # "none" (default) / "light" / "medium" / "dark". OPTIONAL,
    # OUT-OF-FARM-BOUNDARY extension (main.py: run_roasting_extension) —
    # applies to BOTH crops, since cocoa is roasted downstream just like
    # coffee (see SOURCES.md #13). "none" behaves exactly like the old
    # `roasting_included=False`; any other value both enables the extension
    # AND sets its intensity, so a separate boolean flag is redundant and
    # has been removed. Default keeps all 8 existing scenario files
    # unchanged/valid — nothing computes a roasted PCF unless a scenario
    # explicitly opts in.