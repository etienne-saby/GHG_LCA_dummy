"""
main_random_tests.py — Bulk random-scenario generator for statistical
exploration (Power BI training dataset), NOT a production pipeline.

Generates randomly-parameterised Scenario objects, runs them through the
exact same calculation engine as main.py (src/calculations.py::run_scenario
— zero duplicated logic), and writes flat CSVs to data/output/random_tests/:

    cocoa_values.csv            - unroasted (roast_level="none")
    coffee_values.csv           - unroasted (roast_level="none")
    cocoa_roasted_values.csv    - roast_level in {light, medium, dark}
    coffee_roasted_values.csv   - roast_level in {light, medium, dark}

No charts, no console report, no yield-effect decomposition — that analysis
(src/calculations.py::run_yield_effect_analysis) needs a fixed "A."-prefixed
baseline scenario per crop, which doesn't exist in a random batch.

Each CSV row = one run_scenario() result (src/reporting.py::RESULT_FIELDNAMES)
+ the raw random inputs that produced it, so every row is self-contained.

Run: python main_random_tests.py
"""

import os
import random

from src.config import Scenario  # adjust import path if config.py isn't at project root
from src.calculations import run_scenario
from src.reporting import write_csv, RESULT_FIELDNAMES

# ---------------------------------------------------------------------------
# Configuration — tweak freely
# ---------------------------------------------------------------------------

RANDOM_SEED = None  # set an int (e.g. 42) for reproducible draws; None = different every run

N_STANDARD_TOTAL = 400   # split 50/50 cocoa/coffee -> 200 each, roast_level="none"
N_ROASTED_TOTAL = 400    # separate batch, split 50/50 -> 200 each, roast_level in {light,medium,dark}

OUTPUT_DIR = "data/output/random_tests"

CROPS = ["cocoa", "coffee"]
TRANSPORT_MODES = ["truck", "sea"]       # matches main.py's standard (unroasted) runs
DRYING_METHODS = ["sun", "mechanical"]
ROAST_LEVELS = ["light", "medium", "dark"]

LAND_USE_CHANGE_TRUE_PROB = 0.4  # ~40% True / 60% False

PRODUCT_UNIT_LABEL = {
    "cocoa": "dry cocoa beans",
    "coffee": "green coffee beans",
}

RANGES = {
    "area_ha": (0.1, 50),                          # Estimated
    "yield_kg_per_ha_yr": {
        "cocoa": (200, 2500),                      # Estimated
        "coffee": (200, 3500),                     # Estimated
    },
    "synthetic_n_kg_per_ha_yr": {
        "cocoa": (0, 150),                          # Estimated
        "coffee": (0, 350),                         # Estimated
    },
    "organic_n_kg_per_ha_yr": (0, 400),             # Illustrative - unverified (proxy café->cacao)
    "canopy_cover_pct": (0, 100),                   # uniform, no bias
    "transport_distance_km": (10, 1000),            # Illustrative - unverified
}

# Extra input columns appended to every row, on top of RESULT_FIELDNAMES, so
# every random input (not just derived results) is directly usable downstream.
EXTRA_INPUT_FIELDNAMES = [
    "area_ha",
    "synthetic_n_kg_per_ha_yr",
    "organic_n_kg_per_ha_yr",
    "land_use_change",
    "canopy_cover_pct",
    "transport_distance_km",
]

RANDOM_FIELDNAMES = RESULT_FIELDNAMES + EXTRA_INPUT_FIELDNAMES


def make_random_scenario(index, crop, roast_level):
    """Build one Scenario with every tunable field drawn uniformly at random."""
    area_ha = round(random.uniform(*RANGES["area_ha"]), 2)
    yield_kg_ha = round(random.uniform(*RANGES["yield_kg_per_ha_yr"][crop]), 1)
    synthetic_n = round(random.uniform(*RANGES["synthetic_n_kg_per_ha_yr"][crop]), 1)
    organic_n = round(random.uniform(*RANGES["organic_n_kg_per_ha_yr"]), 1)
    canopy_cover = round(random.uniform(*RANGES["canopy_cover_pct"]), 1)
    transport_distance = round(random.uniform(*RANGES["transport_distance_km"]), 1)
    land_use_change = random.random() < LAND_USE_CHANGE_TRUE_PROB
    transport_mode = random.choice(TRANSPORT_MODES)
    drying_method = random.choice(DRYING_METHODS)

    suffix = "-ROASTED" if roast_level != "none" else ""
    name = f"RANDOM-{crop.upper()}{suffix}-{index:04d}"
    description = f"Randomly generated scenario for statistical exploration (roast_level={roast_level})."

    return Scenario(
        name=name,
        description=description,
        crop=crop,
        product_unit_label=PRODUCT_UNIT_LABEL[crop],
        area_ha=area_ha,
        yield_kg_per_ha_yr=yield_kg_ha,
        synthetic_n_kg_per_ha_yr=synthetic_n,
        organic_n_kg_per_ha_yr=organic_n,
        land_use_change=land_use_change,
        canopy_cover_pct=canopy_cover,
        transport_distance_km=transport_distance,
        transport_mode=transport_mode,
        drying_method=drying_method,
        roast_level=roast_level,
    )


def build_row(scenario, result):
    """Merge a run_scenario() result dict with the raw random inputs that
    produced it into one flat row matching RANDOM_FIELDNAMES."""
    row = dict(result)
    row["area_ha"] = scenario.area_ha
    row["synthetic_n_kg_per_ha_yr"] = scenario.synthetic_n_kg_per_ha_yr
    row["organic_n_kg_per_ha_yr"] = scenario.organic_n_kg_per_ha_yr
    row["land_use_change"] = scenario.land_use_change
    row["canopy_cover_pct"] = scenario.canopy_cover_pct
    row["transport_distance_km"] = scenario.transport_distance_km
    return row


def generate_and_run(crop, n, roast_level_choices, index_offset=0):
    """Generate n random scenarios for one crop, run them, return CSV rows."""
    rows = []
    for i in range(n):
        roast_level = "none" if roast_level_choices == ["none"] else random.choice(roast_level_choices)
        scenario = make_random_scenario(index_offset + i, crop, roast_level)
        result = run_scenario(scenario)
        rows.append(build_row(scenario, result))
    return rows


def main():
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    n_per_crop_standard = N_STANDARD_TOTAL // len(CROPS)
    n_per_crop_roasted = N_ROASTED_TOTAL // len(CROPS)

    for crop in CROPS:
        # --- standard (unroasted) batch ---
        standard_rows = generate_and_run(crop, n_per_crop_standard, ["none"])
        standard_path = os.path.join(OUTPUT_DIR, f"{crop}_values.csv")
        write_csv(standard_rows, standard_path, RANDOM_FIELDNAMES)
        print(f"Wrote {len(standard_rows)} unroasted {crop} scenarios -> {standard_path}")

        # --- roasted batch (separate set, separate file) ---
        roasted_rows = generate_and_run(
            crop, n_per_crop_roasted, ROAST_LEVELS, index_offset=n_per_crop_standard
        )
        roasted_path = os.path.join(OUTPUT_DIR, f"{crop}_roasted_values.csv")
        write_csv(roasted_rows, roasted_path, RANDOM_FIELDNAMES)
        print(f"Wrote {len(roasted_rows)} roasted {crop} scenarios -> {roasted_path}")

    total = 2 * (n_per_crop_standard + n_per_crop_roasted)
    print(f"\nDone: {total} random scenarios written to '{OUTPUT_DIR}/'")


if __name__ == "__main__":
    main()