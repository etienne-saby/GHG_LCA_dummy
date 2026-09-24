"""
main.py — Cocoa & coffee smallholder product carbon footprint prototype.

Tier 1, illustrative/demo tool — NOT an audited inventory. Every constant used
below is traceable to SOURCES.md; every formula names its source in a comment.

Run: python main.py
  -> for each crop (cocoa, coffee): prints console breakdown + DQR report,
     writes scenario_results.csv + yield_effect_analysis.csv,
     writes overview / per-mode / per-farm-type / yield-effect charts
     into data/output/<crop>/
  -> for each crop's ROASTED DEMO scenarios (roast_level="dark", air only):
     writes the SAME set of outputs into a SEPARATE data/output/<crop>/
     roasted_demo/ subfolder — kept fully apart from the main (unroasted)
     outputs above so no chart ever silently mixes two functional units
     (green/dry beans vs. roasted beans) in the same stacked bar.
  -> writes one simple cross-crop comparison chart (truck mode only, ALWAYS
     unroasted since only CROP_SCENARIOS feeds it) into
     data/output/cocoa_vs_coffee_truck_comparison.png

Boundary note (2026-09-24): drying is IN the farm-gate boundary (functional
unit is already post-drying, SOURCES.md #12); roasting, when a scenario opts
in via roast_level != "none", is MERGED into that scenario's headline PCF
(functional unit switches to roasted product) — see SOURCES.md #13/#15. The
demo scenario FILES that exercise roasting (*_air_roasted.py) are wired in
as their own separate run (see ROASTED_SCENARIOS below), never mixed
into CROP_SCENARIOS, precisely to keep every standard chart on one
consistent functional unit.
"""

import csv
import os
import unittest

import matplotlib
matplotlib.use("Agg")

from itertools import chain

import src.factors as f
from src.dqr import print_dqr_report
from src.utils_plot import (
    write_chart_overview,
    write_charts_by_mode,
    write_charts_by_farmtype,
    write_charts_yield_effect,
    write_chart_crop_comparison_truck,
)

from data.scenarios.cocoa.scenarios_truck import SCENARIOS_TRUCK as COCOA_TRUCK
from data.scenarios.cocoa.scenarios_truck_roasted import SCENARIOS_TRUCK_ROASTED as COCOA_TRUCK_ROASTED
from data.scenarios.cocoa.scenarios_air import SCENARIOS_AIR as COCOA_AIR
from data.scenarios.cocoa.scenarios_air_roasted import SCENARIOS_AIR_ROASTED as COCOA_AIR_ROASTED

from data.scenarios.coffee.scenarios_truck import SCENARIOS_TRUCK as COFFEE_TRUCK
from data.scenarios.coffee.scenarios_truck_roasted import SCENARIOS_TRUCK_ROASTED as COFFEE_TRUCK_ROASTED
from data.scenarios.coffee.scenarios_air import SCENARIOS_AIR as COFFEE_AIR
from data.scenarios.coffee.scenarios_air_roasted import SCENARIOS_AIR_ROASTED as COFFEE_AIR_ROASTED

# Standard (unroasted) runs — truck + air only; rail/sea dropped (transport
# is a minor share of total PCF, so those modes added little signal).
CROP_SCENARIOS = {
    "cocoa": [COCOA_TRUCK, COCOA_AIR],
    "coffee": [COFFEE_TRUCK, COFFEE_AIR],
}

# Separate roasted-demo runs (roast_level="dark", air only) — kept OUT of
# CROP_SCENARIOS and written to their own output subfolder, see run_roasted().
ROASTED_SCENARIOS = {
    "cocoa": [COCOA_TRUCK_ROASTED, COCOA_AIR_ROASTED],
    "coffee": [COFFEE_TRUCK_ROASTED, COFFEE_AIR_ROASTED],
}

# ---------------------------------------------------------------------------
# Calculation functions
# ---------------------------------------------------------------------------

def fertiliser_n2o_co2e(synthetic_n_kg_ha, organic_n_kg_ha, area_ha):
    """
    Direct + indirect N2O from N inputs, whole farm, kg CO2e/yr. Crop-agnostic:
    IPCC 2019 Refinement Vol.4 Ch.11 factors apply identically to cocoa/coffee
    in tropical-wet climates. See SOURCES.md #1-#4.
    """
    f_sn = synthetic_n_kg_ha * area_ha
    f_on = organic_n_kg_ha * area_ha

    n2o_n_direct = f_sn * f.EF1_SYNTHETIC_WET + f_on * f.EF1_ORGANIC_WET
    co2e_direct = n2o_n_direct * f.N2O_N_TO_N2O * f.GWP_N2O

    n_volatilised = f_sn * f.FRAC_GASF + f_on * f.FRAC_GASM
    n2o_n_volat = n_volatilised * f.EF4_WET
    co2e_volat = n2o_n_volat * f.N2O_N_TO_N2O * f.GWP_N2O

    n2o_n_leach = (f_sn + f_on) * f.FRAC_LEACH_WET * f.EF5
    co2e_leach = n2o_n_leach * f.N2O_N_TO_N2O * f.GWP_N2O

    return {
        "fertiliser_direct": co2e_direct,
        "fertiliser_volatilisation": co2e_volat,
        "fertiliser_leaching": co2e_leach,
    }


def _luc_delta_c_per_ha(crop):
    if crop == "cocoa":
        return f.LUC_DELTA_C_FOREST_TO_COCOA
    elif crop == "coffee":
        return f.LUC_DELTA_C_FOREST_TO_COFFEE
    raise ValueError(f"Unknown crop: {crop!r}")


def _removal_rates(crop):
    if crop == "cocoa":
        return f.REMOVAL_RATE_UNSHADED, f.REMOVAL_RATE_AGROFORESTRY
    elif crop == "coffee":
        return f.REMOVAL_RATE_UNSHADED_COFFEE, f.REMOVAL_RATE_AGROFORESTRY_COFFEE
    raise ValueError(f"Unknown crop: {crop!r}")


def _drying_ef(drying_method, crop):
    if drying_method == "sun":
        return f.DRYING_EF_SUN
    elif drying_method == "mechanical":
        if crop == "cocoa":
            return f.DRYING_EF_MECHANICAL_COCOA
        elif crop == "coffee":
            return f.DRYING_EF_MECHANICAL_COFFEE
        raise ValueError(f"Unknown crop: {crop!r}")
    raise ValueError(f"Unknown drying_method: {drying_method!r}")


def luc_co2e(land_use_change, area_ha, canopy_cover_pct, crop):
    """
    Amortised LUC emissions, whole farm, kg CO2e/yr. See SOURCES.md #5-#6/#10.

    The forest->crop delta-C is reduced linearly with canopy_cover_pct, since
    a conversion straight to shaded agroforestry retains more standing woody
    biomass on-site than a conversion to unshaded monoculture (SOURCES.md #X).
    At canopy_cover_pct=0 this reduces to the original unshaded calculation.
    """
    if not land_use_change:
        return 0.0
    delta_c_per_ha = _luc_delta_c_per_ha(crop)
    retained_frac = f.LUC_RETENTION_FRACTION_AGROFORESTRY * (canopy_cover_pct / 100)
    delta_c_per_ha_adjusted = delta_c_per_ha * (1 - retained_frac)
    delta_c_total = delta_c_per_ha_adjusted * area_ha
    co2_total_kg = delta_c_total * f.C_TO_CO2 * 1000
    return co2_total_kg / f.LUC_AMORTISATION_YEARS


def transport_co2e(yield_kg_ha, area_ha, distance_km, mode):
    """Farm-to-first-processing transport, whole farm, kg CO2e/yr. See SOURCES.md #7."""
    if mode == "truck":
        ef = f.TRANSPORT_EF_TRUCK
    elif mode == "rail":
        ef = f.TRANSPORT_EF_RAIL
    elif mode == "air":
        ef = f.TRANSPORT_EF_AIR_LONGHAUL
    elif mode == "sea":
        ef = f.TRANSPORT_EF_SEA_CONTAINER
    else:
        raise ValueError(f"Unknown transport mode: {mode!r}")
    tonnes_product = (yield_kg_ha * area_ha) * f.KG_TO_TONNE
    return tonnes_product * distance_km * ef


def drying_co2e(yield_kg_ha, area_ha, drying_method, crop):
    """
    Post-harvest drying, whole farm, kg CO2e/yr. IN the farm-gate boundary
    (functional unit is already post-drying). See SOURCES.md #12.
    """
    ef = _drying_ef(drying_method, crop)
    total_product_kg = yield_kg_ha * area_ha
    return ef * total_product_kg


def removal_co2e(canopy_cover_pct, area_ha, crop):
    """Agroforestry/shade CO2 removal credit, whole farm, kg CO2/yr. See SOURCES.md #8/#11."""
    rate_unshaded, rate_agroforestry = _removal_rates(crop)
    frac = canopy_cover_pct / 100
    rate_per_ha = rate_unshaded + (rate_agroforestry - rate_unshaded) * frac
    return rate_per_ha * area_ha


def roasting_co2e_addon(farm_product_kg, crop, roast_level):
    """
    Roasting emissions + mass-loss conversion, whole farm, kg CO2e/yr. See
    SOURCES.md #13 — this is the highest-uncertainty post in the model
    (~100-300x cross-study spread depending on fuel/technology/heat
    recovery), and it CHANGES THE FUNCTIONAL UNIT (green/dry beans ->
    roasted beans) via the mass-loss fraction. Returns
    (extra_co2e_kg_yr, roasted_product_kg_yr). `roast_level="none"` is
    handled by the caller (run_scenario), not here.
    """
    if roast_level not in f.ROAST_LEVEL_KWH_PER_KG:
        raise ValueError(f"Unknown roast_level: {roast_level!r}")
    kwh_per_kg = f.ROAST_LEVEL_KWH_PER_KG[roast_level]
    ef_per_kg = kwh_per_kg * f.GRID_EF_ROASTING_ILLUSTRATIVE * f.ROASTING_CROP_MULTIPLIER[crop]
    extra_co2e = ef_per_kg * farm_product_kg

    if crop == "cocoa":
        mass_loss = f.ROASTING_MASS_LOSS_FRACTION_COCOA
    elif crop == "coffee":
        mass_loss = f.ROASTING_MASS_LOSS_FRACTION_COFFEE
    else:
        raise ValueError(f"Unknown crop: {crop!r}")

    roasted_kg = farm_product_kg * (1 - mass_loss)
    return extra_co2e, roasted_kg


def _apply_roasting(farm_total_emissions, farm_product_kg, crop, roast_level, product_unit_label):
    """
    Shared helper: applies the roasting stage (or not) on top of a farm-gate
    total, returning (total_emissions, final_product_kg, product_label).
    Used by both run_scenario() and compute_counterfactual_pcf() so the two
    stay methodologically consistent.
    """
    if roast_level == "none":
        return farm_total_emissions, farm_product_kg, product_unit_label
    roasting, roasted_kg = roasting_co2e_addon(farm_product_kg, crop, roast_level)
    return farm_total_emissions + roasting, roasted_kg, f.ROASTED_LABEL[crop]


def run_scenario(s):
    """
    Run all calculations for one Scenario and return a results dict.

    Headline `pcf_kg_co2e_per_kg` INCLUDES roasting when
    `s.roast_level != "none"` (functional unit becomes roasted product,
    `product_unit_label` switches accordingly). `farm_gate_pcf_kg_co2e_per_kg`
    is ALWAYS the pre-roasting figure (green/dry bean basis), kept
    specifically so literature comparisons (SOURCES.md #9/#9b, which are on
    an unroasted basis) remain valid regardless of roast_level — see
    SOURCES.md #13.
    """
    fert = fertiliser_n2o_co2e(s.synthetic_n_kg_per_ha_yr, s.organic_n_kg_per_ha_yr, s.area_ha)
    luc = luc_co2e(s.land_use_change, s.area_ha, s.canopy_cover_pct, s.crop)
    transport = transport_co2e(
        s.yield_kg_per_ha_yr, s.area_ha, s.transport_distance_km, s.transport_mode
    )
    drying = drying_co2e(s.yield_kg_per_ha_yr, s.area_ha, s.drying_method, s.crop)
    removals = removal_co2e(s.canopy_cover_pct, s.area_ha, s.crop)

    farm_product_kg = s.yield_kg_per_ha_yr * s.area_ha
    farm_total_emissions = sum(fert.values()) + luc + drying + transport
    farm_gate_pcf = farm_total_emissions / farm_product_kg

    if s.roast_level == "none":
        roasting = 0.0
    else:
        roasting, _ = roasting_co2e_addon(farm_product_kg, s.crop, s.roast_level)

    total_emissions, final_product_kg, product_label = _apply_roasting(
        farm_total_emissions, farm_product_kg, s.crop, s.roast_level, s.product_unit_label
    )
    pcf = total_emissions / final_product_kg

    return {
        "scenario": s.name,
        "crop": s.crop,
        "product_unit_label": product_label,
        "transport_mode": s.transport_mode,
        "drying_method": s.drying_method,
        "roast_level": s.roast_level,
        "description": s.description,
        "fertiliser_direct": fert["fertiliser_direct"],
        "fertiliser_volatilisation": fert["fertiliser_volatilisation"],
        "fertiliser_leaching": fert["fertiliser_leaching"],
        "luc": luc,
        "drying": drying,
        "transport": transport,
        "roasting": roasting,
        "total_emissions_kg_co2e_yr": total_emissions,
        "total_removals_kg_co2_yr": removals,
        "farm_product_kg_yr": farm_product_kg,
        "final_product_kg_yr": final_product_kg,
        "yield_kg_per_ha_yr": s.yield_kg_per_ha_yr,
        "emissions_per_ha_kg_co2e_yr": total_emissions / s.area_ha,
        "farm_gate_pcf_kg_co2e_per_kg": farm_gate_pcf,
        "pcf_kg_co2e_per_kg": pcf,
    }


def compute_counterfactual_pcf(s, reference_yield_kg_ha):
    """
    PCF this scenario would have at `reference_yield_kg_ha`, practices
    unchanged — INCLUDING roasting if s.roast_level != "none", so the
    yield-dilution decomposition stays on a consistent functional unit with
    the scenario's actual PCF (both roasted, or both unroasted).
    """
    fert = fertiliser_n2o_co2e(s.synthetic_n_kg_per_ha_yr, s.organic_n_kg_per_ha_yr, s.area_ha)
    luc = luc_co2e(s.land_use_change, s.area_ha, s.canopy_cover_pct, s.crop)
    transport = transport_co2e(reference_yield_kg_ha, s.area_ha, s.transport_distance_km, s.transport_mode)
    drying = drying_co2e(reference_yield_kg_ha, s.area_ha, s.drying_method, s.crop)
    farm_total_emissions = sum(fert.values()) + luc + drying + transport
    farm_product_kg = reference_yield_kg_ha * s.area_ha

    total_emissions, final_product_kg, _ = _apply_roasting(
        farm_total_emissions, farm_product_kg, s.crop, s.roast_level, s.product_unit_label
    )
    return total_emissions / final_product_kg


def run_yield_effect_analysis(scenario_objs, results, reference_name_prefix="A."):
    """Yield-dilution decomposition, referenced against the 'A.' baseline's yield."""
    reference = next(s for s in scenario_objs if s.name.startswith(reference_name_prefix))
    ref_yield = reference.yield_kg_per_ha_yr

    analysis = []
    for s, r in zip(scenario_objs, results):
        counterfactual_pcf = compute_counterfactual_pcf(s, ref_yield)
        analysis.append({
            "scenario": s.name,
            "crop": s.crop,
            "transport_mode": s.transport_mode,
            "roast_level": s.roast_level,
            "reference_scenario_name": reference.name,
            "reference_yield_kg_ha": ref_yield,
            "actual_yield_kg_ha": s.yield_kg_per_ha_yr,
            "actual_pcf": r["pcf_kg_co2e_per_kg"],
            "counterfactual_pcf": counterfactual_pcf,
            "yield_effect_kg_co2e_per_kg": r["pcf_kg_co2e_per_kg"] - counterfactual_pcf,
        })
    return analysis


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

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


def run_crop(crop, scenario_lists):
    """Run the full pipeline (calc + console + CSV + charts) for one crop's
    STANDARD (unroasted) scenarios."""
    output_dir = os.path.join("data/output", crop)
    os.makedirs(output_dir, exist_ok=True)

    scenario_objs = list(chain(*scenario_lists))
    results = [run_scenario(s) for s in scenario_objs]

    print_console_report(crop, results)
    write_csv(results, os.path.join(output_dir, "scenario_results.csv"), RESULT_FIELDNAMES)

    write_chart_overview(results, os.path.join(output_dir, f"{crop}_footprint_overview.png"))
    write_charts_by_mode(results, output_dir)
    write_charts_by_farmtype(results, output_dir)

    yield_analysis = run_yield_effect_analysis(scenario_objs, results)
    write_csv(yield_analysis, os.path.join(output_dir, "yield_effect_analysis.csv"), YIELD_EFFECT_FIELDNAMES)
    write_charts_yield_effect(yield_analysis, output_dir)

    print(f"\nWrote {crop} outputs (CSV + charts) in '{output_dir}/'")
    return results


def run_roasted(crop, scenario_lists):
    """
    Run the SAME pipeline as run_crop(), but for the roast_level="dark"
    scenarios ONLY (truck + air), writing to a SEPARATE output subfolder
    (data/output/<crop>/roasted_demo/). Kept entirely apart from run_crop()'s
    output so that no chart ever combines roasted and unroasted results
    (different functional units) in the same stacked bar or grouped-bar
    comparison — see the module docstring and SOURCES.md #13/#15.

    `scenario_lists` is a LIST OF LISTS (e.g. [TRUCK_ROASTED, AIR_ROASTED]),
    same convention as run_crop()'s `scenario_lists` — must be flattened via
    chain() before use, exactly like run_crop() does. (2026-09-24 bugfix:
    an earlier version iterated over scenario_lists directly without
    flattening, which silently passed whole Scenario LISTS into
    run_scenario() instead of individual Scenario objects.)
    """
    output_dir = os.path.join("data/output", crop, "roasted_demo")
    os.makedirs(output_dir, exist_ok=True)

    scenario_objs = list(chain(*scenario_lists))
    results = [run_scenario(s) for s in scenario_objs]

    modes_present = sorted({s.transport_mode for s in scenario_objs})
    print_console_report(
        crop, results,
        label=f"ROASTED DEMO (dark roast, {'+'.join(modes_present)} transport)"
    )
    write_csv(results, os.path.join(output_dir, "scenario_results.csv"), RESULT_FIELDNAMES)

    write_chart_overview(results, os.path.join(output_dir, f"{crop}_footprint_overview.png"))
    write_charts_by_mode(results, output_dir)
    write_charts_by_farmtype(results, output_dir)

    yield_analysis = run_yield_effect_analysis(scenario_objs, results)
    write_csv(yield_analysis, os.path.join(output_dir, "yield_effect_analysis.csv"), YIELD_EFFECT_FIELDNAMES)
    write_charts_yield_effect(yield_analysis, output_dir)

    print(f"\nWrote {crop} ROASTED DEMO outputs (CSV + charts) in '{output_dir}/'")
    return results


def main():
    os.makedirs("data/output", exist_ok=True)

    all_results = {}
    for crop, scenario_lists in CROP_SCENARIOS.items():
        all_results[crop] = run_crop(crop, scenario_lists)

    roasted_results = {}
    for crop, scenario_list in ROASTED_SCENARIOS.items():
        roasted_results[crop] = run_roasted(crop, scenario_list)

    # Simple cross-crop comparison — truck mode only, ALWAYS unroasted since
    # only CROP_SCENARIOS (never ROASTED_SCENARIOS) feeds this dict.
    # Transport is a minor share of total LCA PCF, so restricting to truck
    # does not confound the crop comparison with a transport-mode difference.
    truck_by_crop = {
        crop: [r for r in results if r["transport_mode"] == "truck"]
        for crop, results in all_results.items()
    }
    write_chart_crop_comparison_truck(
        truck_by_crop, "data/output/cocoa_vs_coffee_truck_comparison.png"
    )
    print("\nWrote data/output/cocoa_vs_coffee_truck_comparison.png")

    print("\n" + "=" * 96)
    print("Running verification tests (test_calculations.py) ...")
    print("=" * 96)
    loader = unittest.TestLoader()
    suite = loader.discover(".", pattern="test_calculations.py")
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)


if __name__ == "__main__":
    main()