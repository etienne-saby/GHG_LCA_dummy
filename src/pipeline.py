"""
pipeline.py — Per-crop and cross-crop orchestration: flatten a crop's
scenario list, run the calculation engine, print the console report, write
CSVs, generate charts. Ties together src/calculations.py, src/reporting.py
and src/utils_plot.py — no calculation logic of its own.
"""

import os
from itertools import chain

from src.calculations import run_scenario, run_yield_effect_analysis
from src.reporting import (
    print_console_report,
    write_csv,
    RESULT_FIELDNAMES,
    YIELD_EFFECT_FIELDNAMES,
)
from src.utils_plot import (
    write_chart_overview,
    write_charts_by_mode,
    write_charts_by_farmtype,
    write_charts_yield_effect,
    write_chart_crop_comparison_truck,
)


def _run_and_write(crop, scenario_lists, output_dir, label=""):
    """Shared core: flatten scenarios, run calculations, print + write CSV + charts."""
    scenario_objs = list(chain(*scenario_lists))
    results = [run_scenario(s) for s in scenario_objs]

    print_console_report(crop, results, label=label)
    write_csv(results, os.path.join(output_dir, "scenario_results.csv"), RESULT_FIELDNAMES)

    write_chart_overview(results, os.path.join(output_dir, f"{crop}_footprint_overview.png"))
    write_charts_by_mode(results, output_dir)
    write_charts_by_farmtype(results, output_dir)

    yield_analysis = run_yield_effect_analysis(scenario_objs, results)
    write_csv(yield_analysis, os.path.join(output_dir, "yield_effect_analysis.csv"), YIELD_EFFECT_FIELDNAMES)
    write_charts_yield_effect(yield_analysis, output_dir)

    return results


def run_crop(crop, scenario_lists):
    """Standard (unroasted) pipeline for one crop -> data/output/<crop>/."""
    output_dir = os.path.join("data/output", crop)
    os.makedirs(output_dir, exist_ok=True)
    results = _run_and_write(crop, scenario_lists, output_dir)
    print(f"\nWrote {crop} outputs (CSV + charts) in '{output_dir}/'")
    return results


def run_roasted(crop, scenario_lists):
    """
    Roasted pipeline (roast_level='dark' scenarios only) -> a SEPARATE
    data/output/<crop>/roasted/ subfolder, so no chart ever mixes
    roasted and unroasted results (different functional units) — see
    SOURCES.md #15.
    """
    output_dir = os.path.join("data/output", crop, "roasted")
    os.makedirs(output_dir, exist_ok=True)

    scenario_objs = list(chain(*scenario_lists))
    modes_present = sorted({s.transport_mode for s in scenario_objs})
    label = f"ROASTED (dark roast, {'+'.join(modes_present)} transport)"

    results = _run_and_write(crop, scenario_lists, output_dir, label=label)
    print(f"\nWrote {crop} ROASTED outputs (CSV + charts) in '{output_dir}/'")
    return results


def run_crop_comparison(all_results, path="data/output/cocoa_vs_coffee_truck_comparison.png"):
    """
    Simple cross-crop comparison — truck mode only, ALWAYS unroasted (only
    ever called with standard/CROP_SCENARIOS' results, never roasted
    results). Transport is a minor share of total LCA PCF, so restricting to
    truck avoids confounding the crop comparison with a transport-mode
    difference.
    """
    os.makedirs("data/output", exist_ok=True)
    truck_by_crop = {
        crop: [r for r in results if r["transport_mode"] == "truck"]
        for crop, results in all_results.items()
    }
    write_chart_crop_comparison_truck(truck_by_crop, path)
    print(f"\nWrote {path}")