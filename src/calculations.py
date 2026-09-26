"""
calculations.py — Core calculation engine: every function here computes one
lifecycle-stage's emissions (or removals), whole farm, kg CO2/CO2e per year,
from a Scenario's inputs and the constants in src/factors.py. Crop-specific
behaviour (which ΔC, which removal-rate pair, which drying/roasting factor
applies) is isolated in the small `_...` dispatch helpers below.

Every formula names its SOURCES.md section in a comment. This module has no
I/O — see src/reporting.py for console/CSV output and src/pipeline.py for
per-crop orchestration.
"""

import src.factors as f


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
    Amortised LUC emissions, whole farm, kg CO2e/yr. See SOURCES.md #5-#6/#11
    (mechanism / cocoa magnitude / coffee magnitude).

    The forest->crop delta-C is reduced linearly with canopy_cover_pct, since
    a conversion straight to shaded agroforestry retains more standing woody
    biomass on-site than a conversion to unshaded monoculture. This retention
    discount is itself an ILLUSTRATIVE, unsourced modelling choice — see
    SOURCES.md #16. At canopy_cover_pct=0 this reduces to the original
    unshaded calculation.
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
    """Agroforestry/shade CO2 removal credit, whole farm, kg CO2/yr. See SOURCES.md #8/#11b.
    Reported separately, never netted against emissions — see SOURCES.md #8."""
    rate_unshaded, rate_agroforestry = _removal_rates(crop)
    frac = canopy_cover_pct / 100
    rate_per_ha = rate_unshaded + (rate_agroforestry - rate_unshaded) * frac
    return rate_per_ha * area_ha


def roasting_co2e_addon(farm_product_kg, crop, roast_level):
    """
    Roasting emissions + mass-loss conversion, whole farm, kg CO2e/yr. See
    SOURCES.md #13 for factor sourcing (highest-uncertainty post in the
    model, ~100-300x cross-study spread) and #15 for the boundary/merge
    decision. Returns (extra_co2e_kg_yr, roasted_product_kg_yr).
    `roast_level="none"` is handled by the caller (run_scenario), not here.
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
    stay methodologically consistent. See SOURCES.md #15.
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
    specifically so literature comparisons (SOURCES.md #9/#9b/#11c, which
    are on an unroasted basis) remain valid regardless of roast_level — see
    SOURCES.md #15.
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