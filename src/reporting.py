"""
reporting.py — Console report + CSV writers for scenario results and the
yield-effect decomposition. Pure I/O layer: takes already-computed result
dicts (see src/calculations.py::run_scenario) and formats/writes them.
Never computes anything itself.
"""

import csv

from src.dqr import print_dqr_report

RESULT_FIELDNAMES = [
    "scenario", "crop", "product_unit_label", "transport_mode", "drying_method",
    "roast_level", "description", "fertiliser_direct", "fertiliser_volatilisation",
    "fertiliser_leaching", "luc", "drying", "transport", "roasting",
    "total_emissions_kg_co2e_yr", "total_removals_kg_co2_yr",
    "farm_product_kg_yr", "final_product_kg_yr", "yield_kg_per_ha_yr",
    "emissions_per_ha_kg_co2e_yr", "farm_gate_pcf_kg_co2e_per_kg", "pcf_kg_co2e_per_kg",
]

YIELD_EFFECT_FIELDNAMES = [
    "scenario", "crop", "transport_mode", "roast_level", "reference_scenario_name",
    "reference_yield_kg_ha", "actual_yield_kg_ha", "actual_pcf",
    "counterfactual_pcf", "yield_effect_kg_co2e_per_kg",
]


def print_console_report(crop, results, label=""):
    banner = f"{crop.upper()}{(' — ' + label) if label else ''}"
    print("=" * 96)
    print(f"{banner} SMALLHOLDER PRODUCT CARBON FOOTPRINT — Tier 1 demo, not an")
    print("audited inventory. Every factor sourced in SOURCES.md; illustrative farm-")
    print("profile inputs are flagged as such in scenarios/<crop>/*.py.")
    roasted_any = any(r["roast_level"] != "none" for r in results)
    if roasted_any:
        print(
            "NOTE: roasting is INCLUDED in the PCF below for scenarios with roast_level != "
            "'none' (functional unit = roasted product, see product_unit_label column). "
            "Roasting is the highest-uncertainty post in this model (~100-300x cross-study "
            "spread — SOURCES.md #13). The pre-roasting farm-gate PCF (green/dry bean basis, "
            "comparable to published literature ranges) is reported separately as "
            "farm_gate_pcf_kg_co2e_per_kg."
        )
    print("=" * 96)

    header = f"{'Scenario':38}{'Mode':>7}{'Roast':>8}{'Emissions':>14}{'Removals':>14}{'FarmGatePCF':>13}{'TotalPCF':>10}"
    print(f"\n{header}")
    print(f"{'':38}{'':>7}{'':>8}{'(kgCO2e/yr)':>14}{'(kgCO2/yr)':>14}{'(kgCO2e/kg)':>13}{'(kgCO2e/kg)':>10}")
    print("-" * 96)
    for r in results:
        print(
            f"{r['scenario']:38}{r['transport_mode']:>7}{r['roast_level']:>8}"
            f"{r['total_emissions_kg_co2e_yr']:>14,.0f}"
            f"{r['total_removals_kg_co2_yr']:>14,.0f}"
            f"{r['farm_gate_pcf_kg_co2e_per_kg']:>13.2f}"
            f"{r['pcf_kg_co2e_per_kg']:>10.2f}"
        )

    print("\nBreakdown by source category (kg CO2e/yr, whole farm):")
    print(
        f"{'Scenario':38}{'Mode':>7}{'Fert.direct':>13}{'Fert.volat':>12}"
        f"{'Fert.leach':>12}{'LUC':>10}{'Drying':>10}{'Transport':>11}{'Roasting':>10}"
    )
    for r in results:
        print(
            f"{r['scenario']:38}{r['transport_mode']:>7}"
            f"{r['fertiliser_direct']:>13,.0f}{r['fertiliser_volatilisation']:>12,.0f}"
            f"{r['fertiliser_leaching']:>12,.0f}{r['luc']:>10,.0f}"
            f"{r['drying']:>10,.0f}{r['transport']:>11,.0f}{r['roasting']:>10,.0f}"
        )

    print(
        "\nNote: emissions and removals are reported separately and never "
        "pre-netted into one number."
    )
    print_dqr_report()


def write_csv(results, path, fieldnames):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            writer.writerow(r)