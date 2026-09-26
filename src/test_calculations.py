"""
test_calculations.py — Required sanity-check tests (stdlib unittest, no new
dependency), per the carbon-footprint-methodology skill. A calculation "looks
plausible" is not evidence — these are the actual checks, and main.py reports
their real pass/fail output, not a description of what they're supposed to do.

2026-09-24 update: roasting is now MERGED into run_scenario()'s headline PCF
(main.py: _apply_roasting) whenever a scenario's roast_level != "none". The
order-of-magnitude checks below import the plain (unroasted) truck scenario
files, where `Scenario.roast_level` defaults to "none" (src/config.py), so
`pcf_kg_co2e_per_kg` and `farm_gate_pcf_kg_co2e_per_kg` are identical for
every scenario tested here in practice. The checks still deliberately read
`farm_gate_pcf_kg_co2e_per_kg` rather than `pcf_kg_co2e_per_kg`, since the
literature bands (SOURCES.md #9/#9b/#11c) are sourced on an unroasted
green/dry-bean basis and this keeps the check correct even if a roasted
scenario set is ever substituted in.

2026-09-26 audit: this file's order-of-magnitude check previously covered
cocoa only. `CoffeeOrderOfMagnitudeCheck` was added below to close that gap
— see SOURCES.md #17 for the rationale behind its wider with-LUC margin.
"""

import unittest

import src.factors as f
from main import (
    fertiliser_n2o_co2e,
    luc_co2e,
    transport_co2e,
    drying_co2e,
    removal_co2e,
    run_scenario,
    roasting_co2e_addon,
)
from data.scenarios.cocoa.scenarios_truck import SCENARIOS_TRUCK as COCOA_SCENARIOS
from data.scenarios.coffee.scenarios_truck import SCENARIOS_TRUCK as COFFEE_SCENARIOS

# Kept as an alias so the existing hand-computed / zero-input / monotonicity
# checks below (which predate the cocoa+coffee split and only ever need "a
# representative scenario list", not crop-specific values) don't need to
# change: they use SCENARIOS[0] etc. purely as a generic cocoa fixture.
SCENARIOS = COCOA_SCENARIOS


class ZeroInputSanityChecks(unittest.TestCase):
    def test_zero_fertiliser_gives_zero_fertiliser_emissions(self):
        result = fertiliser_n2o_co2e(0, 0, area_ha=3.0)
        self.assertEqual(sum(result.values()), 0.0)

    def test_zero_transport_distance_gives_zero_transport_emissions(self):
        self.assertEqual(transport_co2e(400, 3.0, distance_km=0, mode="truck"), 0.0)

    def test_no_land_use_change_gives_zero_luc_emissions(self):
        self.assertEqual(
            luc_co2e(land_use_change=False, area_ha=3.0, canopy_cover_pct=0, crop="cocoa"),
            0.0,
        )

    def test_sun_drying_gives_zero_drying_emissions(self):
        self.assertEqual(
            drying_co2e(yield_kg_ha=400, area_ha=3.0, drying_method="sun", crop="cocoa"),
            0.0,
        )


class MonotonicityChecks(unittest.TestCase):
    def test_increasing_fertiliser_increases_fertiliser_emissions(self):
        low = sum(fertiliser_n2o_co2e(30, 0, area_ha=3.0).values())
        high = sum(fertiliser_n2o_co2e(90, 0, area_ha=3.0).values())
        self.assertGreater(high, low)

    def test_increasing_shade_increases_removal_credit_not_emissions(self):
        low_shade = removal_co2e(canopy_cover_pct=0, area_ha=3.0, crop="cocoa")
        high_shade = removal_co2e(canopy_cover_pct=80, area_ha=3.0, crop="cocoa")
        self.assertGreater(high_shade, low_shade)

        # Canopy cover must NOT change the farm-gate emissions total — only removals.
        fert = sum(fertiliser_n2o_co2e(60, 0, area_ha=3.0).values())
        transport = transport_co2e(400, 3.0, 150, "truck")
        drying = drying_co2e(400, 3.0, "mechanical", "cocoa")
        emissions_low_shade = fert + transport + drying
        emissions_high_shade = fert + transport + drying
        self.assertEqual(emissions_low_shade, emissions_high_shade)

    def test_mechanical_drying_emits_more_than_sun_drying(self):
        sun = drying_co2e(yield_kg_ha=400, area_ha=3.0, drying_method="sun", crop="cocoa")
        mechanical = drying_co2e(yield_kg_ha=400, area_ha=3.0, drying_method="mechanical", crop="cocoa")
        self.assertGreater(mechanical, sun)

    def test_darker_roast_emits_more_than_lighter_roast(self):
        light_co2e, _ = roasting_co2e_addon(1000, "coffee", "light")
        dark_co2e, _ = roasting_co2e_addon(1000, "coffee", "dark")
        self.assertGreater(dark_co2e, light_co2e)


class UnitConversionChecks(unittest.TestCase):
    def test_fertiliser_n2o_hand_computed_round_numbers(self):
        """
        Hand-computed check, 100 kg synthetic N/ha on 1 ha, organic=0:
          N2O-N direct = 100 * 0.016 = 1.6 kg N2O-N
          N2O direct   = 1.6 * 44/28 = 2.514285... kg N2O
          CO2e direct  = 2.514285... * 273 = 686.4 kg CO2e (rounded)
        """
        result = fertiliser_n2o_co2e(100, 0, area_ha=1.0)
        expected_direct = 100 * f.EF1_SYNTHETIC_WET * f.N2O_N_TO_N2O * f.GWP_N2O
        self.assertAlmostEqual(result["fertiliser_direct"], expected_direct, places=6)
        self.assertAlmostEqual(result["fertiliser_direct"], 686.4, delta=1.0)

    def test_transport_kg_to_tonne_km_conversion(self):
        result = transport_co2e(yield_kg_ha=1000, area_ha=1.0, distance_km=100, mode="truck")
        self.assertAlmostEqual(result, 7.547, places=3)

    def test_roasting_addon_hand_computed_coffee_medium(self):
        """
        Hand-computed check, coffee, medium roast, 1000 kg green coffee:
          kWh/kg = 5.04, grid EF = 0.3 kg CO2e/kWh, crop multiplier = 1.0
          -> 5.04 * 0.3 * 1.0 = 1.512 kg CO2e/kg -> 1512 kg CO2e total.
          Mass loss 16% -> roasted mass = 1000 * 0.84 = 840 kg.
        """
        extra_co2e, roasted_kg = roasting_co2e_addon(
            farm_product_kg=1000, crop="coffee", roast_level="medium"
        )
        self.assertAlmostEqual(extra_co2e, 1512.0, places=3)
        self.assertAlmostEqual(roasted_kg, 840.0, places=3)

    def test_run_scenario_farm_gate_pcf_excludes_roasting(self):
        """
        farm_gate_pcf_kg_co2e_per_kg must equal (fert+luc+drying+transport)/
        farm_product_kg — i.e. NOT include the roasting addon, regardless of
        the scenario's roast_level.
        """
        r = run_scenario(SCENARIOS[0])
        farm_only = (
            r["fertiliser_direct"] + r["fertiliser_volatilisation"]
            + r["fertiliser_leaching"] + r["luc"] + r["drying"] + r["transport"]
        )
        recomputed_farm_gate_pcf = farm_only / r["farm_product_kg_yr"]
        self.assertAlmostEqual(r["farm_gate_pcf_kg_co2e_per_kg"], recomputed_farm_gate_pcf, places=6)

    def test_run_scenario_total_pcf_includes_roasting_when_opted_in(self):
        r = run_scenario(SCENARIOS[0])
        if SCENARIOS[0].roast_level == "none":
            self.assertEqual(r["pcf_kg_co2e_per_kg"], r["farm_gate_pcf_kg_co2e_per_kg"])
        else:
            all_posts = (
                r["fertiliser_direct"] + r["fertiliser_volatilisation"]
                + r["fertiliser_leaching"] + r["luc"] + r["drying"]
                + r["transport"] + r["roasting"]
            )
            recomputed_pcf = all_posts / r["final_product_kg_yr"]
            self.assertAlmostEqual(r["pcf_kg_co2e_per_kg"], recomputed_pcf, places=6)
            # Roasted basis must strictly differ from farm-gate basis (mass
            # loss + added emissions) whenever roasting is active.
            self.assertNotAlmostEqual(
                r["pcf_kg_co2e_per_kg"], r["farm_gate_pcf_kg_co2e_per_kg"], places=3
            )


class CocoaOrderOfMagnitudeCheck(unittest.TestCase):
    """
    Checked against SOURCES.md #9/#9b (peer-reviewed cacao meta-analysis;
    Becker et al. 2024 Ghana/Côte d'Ivoire figures) — flag loudly, don't just
    trust the output, if a scenario's PCF lands outside a defensible range.

    IMPORTANT: these bands are sourced on an UNROASTED (green/dry bean)
    basis. These tests deliberately check `farm_gate_pcf_kg_co2e_per_kg`
    (pre-roasting), NOT the headline `pcf_kg_co2e_per_kg` — comparing a
    roasted-basis PCF against an unroasted literature band would be an
    invalid, misleading check (see SOURCES.md #13). In practice the two are
    equal here since these scenarios' roast_level defaults to "none".
    """

    def test_no_luc_scenarios_within_literature_decile_range(self):
        for s in COCOA_SCENARIOS:
            if s.land_use_change:
                continue
            result = run_scenario(s)
            pcf = result["farm_gate_pcf_kg_co2e_per_kg"]
            self.assertGreaterEqual(
                pcf, f.LIT_PCF_NO_LUC_DECILE_LOW,
                f"{s.name}: farm-gate PCF {pcf:.2f} below literature 1st-decile floor "
                f"({f.LIT_PCF_NO_LUC_DECILE_LOW})",
            )
            self.assertLessEqual(
                pcf, f.LIT_PCF_NO_LUC_DECILE_HIGH,
                f"{s.name}: farm-gate PCF {pcf:.2f} above literature 8th-decile ceiling "
                f"({f.LIT_PCF_NO_LUC_DECILE_HIGH})",
            )

    def test_luc_scenario_shows_order_of_magnitude_jump(self):
        luc_scenarios = [s for s in COCOA_SCENARIOS if s.land_use_change]
        self.assertTrue(luc_scenarios, "No LUC scenario found to test")
        for s in luc_scenarios:
            result = run_scenario(s)
            pcf = result["farm_gate_pcf_kg_co2e_per_kg"]
            self.assertGreater(
                pcf, f.LIT_PCF_NO_LUC_DECILE_HIGH,
                f"{s.name}: LUC scenario farm-gate PCF {pcf:.2f} did not exceed the "
                f"no-LUC literature ceiling — LUC penalty looks too small",
            )
            self.assertLess(
                pcf, f.LIT_PCF_CIV_LUC * 2,
                f"{s.name}: LUC scenario farm-gate PCF {pcf:.2f} implausibly far above "
                f"even the Côte d'Ivoire with-LUC benchmark",
            )


class CoffeeOrderOfMagnitudeCheck(unittest.TestCase):
    """
    Coffee counterpart to CocoaOrderOfMagnitudeCheck, added 2026-09-26 to
    close a coverage gap: this tool previously had no automated check of
    coffee's calculated PCFs against literature at all (SOURCES.md #17).

    Checked against SOURCES.md #11c: Cornelius et al. 2025 (no-LUC,
    median +/- IQR) and Chéron-Bessou et al. 2024 Table 2 (with-LUC range,
    the ground-truth coffee review supplied with this tool).

    The with-LUC ceiling uses a wide (x3) margin, not the raw 10.52 figure —
    see SOURCES.md #17 for why: Scenario E is a known, deliberately extreme
    combination (large, differently-sourced coffee LUC delta-C + an
    unsourced/illustrative canopy retention discount + this crop's
    lowest-yield scenario) that legitimately lands above the raw literature
    range. The margin is still tight enough to catch a genuine gross error
    (e.g. a 10x unit-conversion mistake).
    """

    def test_no_luc_scenarios_within_literature_range(self):
        for s in COFFEE_SCENARIOS:
            if s.land_use_change:
                continue
            result = run_scenario(s)
            pcf = result["farm_gate_pcf_kg_co2e_per_kg"]
            self.assertGreaterEqual(
                pcf, f.LIT_PCF_COFFEE_NO_LUC_LOW,
                f"{s.name}: farm-gate PCF {pcf:.2f} below literature floor "
                f"({f.LIT_PCF_COFFEE_NO_LUC_LOW})",
            )
            self.assertLessEqual(
                pcf, f.LIT_PCF_COFFEE_NO_LUC_HIGH,
                f"{s.name}: farm-gate PCF {pcf:.2f} above literature ceiling "
                f"({f.LIT_PCF_COFFEE_NO_LUC_HIGH})",
            )

    def test_luc_scenario_shows_order_of_magnitude_jump(self):
        luc_scenarios = [s for s in COFFEE_SCENARIOS if s.land_use_change]
        self.assertTrue(luc_scenarios, "No LUC scenario found to test")
        for s in luc_scenarios:
            result = run_scenario(s)
            pcf = result["farm_gate_pcf_kg_co2e_per_kg"]
            self.assertGreater(
                pcf, f.LIT_PCF_COFFEE_NO_LUC_HIGH,
                f"{s.name}: LUC scenario farm-gate PCF {pcf:.2f} did not exceed the "
                f"no-LUC literature ceiling — LUC penalty looks too small",
            )
            self.assertLess(
                pcf, f.LIT_PCF_COFFEE_LUC_HIGH * 3,
                f"{s.name}: LUC scenario farm-gate PCF {pcf:.2f} implausibly far above "
                f"even a x3 margin on the sourced coffee with-LUC ceiling "
                f"({f.LIT_PCF_COFFEE_LUC_HIGH}) — see SOURCES.md #17 before assuming "
                f"this is 'just' the known Scenario E outlier",
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)