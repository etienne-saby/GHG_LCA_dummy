"""
dqr.py — Data Quality Rating.

Per the carbon-footprint-methodology skill: each input category is scored on
five separate dimensions (not one gut-feel number), then combined into a single
per-category rating. Combination rule used here: the OVERALL rating for a
category is its WEAKEST dimension (the "weak link" convention) — a category is
only as trustworthy as its least-representative dimension, so averaging would
hide a real weakness. This rule is a modelling choice, not itself sourced.

The five dimensions, per SOURCES.md's category write-ups:
  - Technological representativeness
  - Geographical representativeness
  - Temporal representativeness
  - Completeness
  - Reliability of source
Each is rated Poor / Fair / Good / Very Good.

2026-09-24 update: added Drying (SOURCES.md #12) and Roasting (SOURCES.md #13)
categories. Roasting is rated even though it is an OPTIONAL, out-of-boundary
extension (main.py: run_roasting_extension) — it is only ever computed for
scenarios that opt in via roast_level != "none", but when it IS computed its
data quality still needs to be visible to the user.
"""

RATING_ORDER = ["Poor", "Fair", "Good", "Very Good"]


def _combine(dimensions: dict) -> str:
    """Overall category rating = its weakest (lowest-ranked) dimension."""
    return min(dimensions.values(), key=lambda r: RATING_ORDER.index(r))


# Ratings and the one-line reasoning behind each, drawn directly from the
# category write-ups in SOURCES.md.
DQR_RATINGS = {
    "Fertiliser N2O (IPCC 2019 Refinement, Tier 1, wet-climate)": {
        "dimensions": {
            "Technological representativeness": "Good",
            "Geographical representativeness": "Fair",
            "Temporal representativeness": "Good",
            "Completeness": "Very Good",
            "Reliability of source": "Very Good",
        },
        "note": (
            "Global Tier 1 default disaggregated only by wet/dry climate, not "
            "West-Africa-specific; otherwise a current, complete, peer-consensus "
            "IPCC default covering direct + both indirect pathways."
        ),
    },
    "Land-use change (Becker et al. 2024 + PAS2050/SBTi FLAG amortisation)": {
        "dimensions": {
            "Technological representativeness": "Fair",
            "Geographical representativeness": "Very Good",
            "Temporal representativeness": "Very Good",
            "Completeness": "Fair",
            "Reliability of source": "Fair",
        },
        "note": (
            "Geographically exact (Ghana/Côte d'Ivoire) and recent, but "
            "aboveground-biomass only (excludes belowground biomass and soil "
            "organic carbon) and drawn from an arXiv preprint of unconfirmed "
            "peer-review status."
        ),
    },
    "Transport (UK DESNZ Conversion Factors 2024)": {
        "dimensions": {
            "Technological representativeness": "Fair",
            "Geographical representativeness": "Poor",
            "Temporal representativeness": "Good",
            "Completeness": "Good",
            "Reliability of source": "Fair",
        },
        "note": (
            "UK generic freight default standing in for West African transport; "
            "sourced via a secondary aggregator, not independently re-verified "
            "against the primary DESNZ spreadsheet cell."
        ),
    },
    "Agroforestry removal credit (peer-reviewed cacao/coffee meta-analyses)": {
        "dimensions": {
            "Technological representativeness": "Fair",
            "Geographical representativeness": "Fair",
            "Temporal representativeness": "Good",
            "Completeness": "Good",
            "Reliability of source": "Very Good",
        },
        "note": (
            "Peer-reviewed systematic reviews, but global (not West-Africa/origin- "
            "specific) medians, and this tool's linear interpolation between the "
            "two reported endpoints by % canopy cover is our own simplifying "
            "assumption, not itself drawn from the reviews."
        ),
    },
    "Drying, coffee (Honduras biomass-dryer field study)": {
        "dimensions": {
            "Technological representativeness": "Fair",
            "Geographical representativeness": "Fair",
            "Temporal representativeness": "Fair",
            "Completeness": "Good",
            "Reliability of source": "Fair",
        },
        "note": (
            "Single-country field study of biomass dryers; the 'mechanical' "
            "default reuses the vertical-dryer figure (mid-point of three dryer "
            "types measured) rather than a broader technology sample."
        ),
    },
    "Drying, cocoa (cross-crop proxy from coffee study)": {
        "dimensions": {
            "Technological representativeness": "Poor",
            "Geographical representativeness": "Poor",
            "Temporal representativeness": "Fair",
            "Completeness": "Fair",
            "Reliability of source": "Poor",
        },
        "note": (
            "No cocoa-specific mechanical-drying LCA factor found; reuses the "
            "coffee (Honduras) vertical-dryer value as an ILLUSTRATIVE, "
            "unverified proxy — flagged as the weakest input in the model."
        ),
    },
        "Roasting, merged into headline PCF when opted-in (SOURCES.md #13)": {
        "dimensions": {
            "Technological representativeness": "Poor",
            "Geographical representativeness": "Poor",
            "Temporal representativeness": "Fair",
            "Completeness": "Poor",
            "Reliability of source": "Poor",
        },
        "note": (
            "Documented ~100-300x cross-study spread depending on fuel/roaster "
            "technology/heat recovery; cocoa uses an unverified 0.5x multiplier "
            "and an unverified 4% mass-loss placeholder. Now MERGED into the "
            "headline pcf_kg_co2e_per_kg whenever roast_level != 'none' — the "
            "pre-roasting farm-gate figure is kept separately as "
            "farm_gate_pcf_kg_co2e_per_kg specifically so literature checks "
            "and cross-scenario comparisons on an unroasted basis remain valid."
        ),
    },
}


def print_dqr_report():
    print("\n=== DATA QUALITY RATING (multi-dimensional) ===")
    for category, info in DQR_RATINGS.items():
        overall = _combine(info["dimensions"])
        print(f"\n{category}")
        print(f"  Overall (weakest dimension): {overall}")
        for dim, rating in info["dimensions"].items():
            print(f"    - {dim}: {rating}")
        print(f"  Note: {info['note']}")


if __name__ == "__main__":
    print_dqr_report()