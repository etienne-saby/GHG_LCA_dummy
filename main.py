"""
main.py — Cocoa & coffee smallholder product carbon footprint prototype.

Entry point only. Wires together:
  - scenario data          (data/scenarios/<crop>/*.py)
  - the calculation engine (src/calculations.py)
  - reporting + CSV output (src/reporting.py)
  - chart generation       (src/utils_plot.py)
  - per-crop orchestration (src/pipeline.py)
then runs the verification test suite.

This is a Tier 1 demo tool, not an audited inventory. Every emission factor
is traceable to SOURCES.md.

Run: python main.py
  -> per crop, standard (unroasted) scenarios: console report + DQR +
     scenario_results.csv + yield_effect_analysis.csv + charts, written to
     data/output/<crop>/
  -> per crop, roasted scenarios (dark roast, sea only): the same
     outputs, written to a SEPARATE data/output/<crop>/roasted/ folder
     (roasting changes the functional unit, so it must never share a chart
     with unroasted results — see SOURCES.md #15)
  -> one cross-crop, truck-only comparison chart:
     data/output/cocoa_vs_coffee_truck_comparison.png
  -> runs test_calculations.py and prints pass/fail
"""

import unittest

from src.pipeline import run_crop, run_roasted, run_crop_comparison

from data.scenarios.cocoa.scenarios_truck import SCENARIOS_TRUCK as COCOA_TRUCK
from data.scenarios.cocoa.scenarios_truck_roasted import SCENARIOS_TRUCK_ROASTED as COCOA_TRUCK_ROASTED
from data.scenarios.cocoa.scenarios_sea import SCENARIOS_SEA as COCOA_SEA
from data.scenarios.cocoa.scenarios_sea_roasted import SCENARIOS_SEA_ROASTED as COCOA_SEA_ROASTED

from data.scenarios.coffee.scenarios_truck import SCENARIOS_TRUCK as COFFEE_TRUCK
from data.scenarios.coffee.scenarios_truck_roasted import SCENARIOS_TRUCK_ROASTED as COFFEE_TRUCK_ROASTED
from data.scenarios.coffee.scenarios_sea import SCENARIOS_SEA as COFFEE_SEA
from data.scenarios.coffee.scenarios_sea_roasted import SCENARIOS_SEA_ROASTED as COFFEE_SEA_ROASTED

# Re-exported for backward compatibility: test_calculations.py imports these
# names directly from `main` (e.g. `from main import fertiliser_n2o_co2e`).
# The actual implementations live in src/calculations.py; this re-export
# keeps that import working unchanged after the refactor.
from src.calculations import (  # noqa: F401
    fertiliser_n2o_co2e,
    luc_co2e,
    transport_co2e,
    drying_co2e,
    removal_co2e,
    run_scenario,
    compute_counterfactual_pcf,
    roasting_co2e_addon,
)

# Standard (unroasted) runs — truck + sea only; rail/air dropped (transport
# is a minor share of total PCF, so those modes added little signal).
CROP_SCENARIOS = {
    "cocoa": [COCOA_TRUCK, COCOA_SEA],
    "coffee": [COFFEE_TRUCK, COFFEE_SEA],
}

# Roasted runs (roast_level="dark", sea only) — see src/pipeline.py::run_roasted.
ROASTED_SCENARIOS = {
    "cocoa": [COCOA_TRUCK_ROASTED, COCOA_SEA_ROASTED],
    "coffee": [COFFEE_TRUCK_ROASTED, COFFEE_SEA_ROASTED],
}


def main():
    all_results = {crop: run_crop(crop, scenarios) for crop, scenarios in CROP_SCENARIOS.items()}
    for crop, scenarios in ROASTED_SCENARIOS.items():
        run_roasted(crop, scenarios)

    run_crop_comparison(all_results)

    print("\n" + "=" * 96)
    print("Running verification tests (test_calculations.py) ...")
    print("=" * 96)
    loader = unittest.TestLoader()
    suite = loader.discover(".", pattern="test_calculations.py")
    unittest.TextTestRunner(verbosity=2).run(suite)


if __name__ == "__main__":
    main()