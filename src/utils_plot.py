"""
utils_plot.py — Chart-generation helpers, crop-aware (cocoa/coffee).

Per-crop views (called once per crop by main.py, output_dir already scoped to
output/<crop>/):
  1. Overview      — all scenarios x all transport modes, grouped bars, stacked
                      by lifecycle-stage category. Each segment >= a minimum
                      share is annotated with its % of that bar's total.
  2. By mode        — one chart per transport mode, 6 farm profiles, stacked,
                      with % annotations. X-axis simplified to scenario
                      letters (A, B, ...); a separate "Scenario A : ..."
                      legend gives the full names.
  3. By farm type   — one chart per farm profile, N transport modes, stacked,
                      with % annotations.
  4. Yield effect   — one chart per transport mode: grouped bars (reference
                      yield vs actual yield PCF) with the yield-driven delta
                      annotated directly on the chart. X-axis simplified to
                      scenario letters, same "Scenario A : ..." legend as (2).

Plus one cross-crop view:
  5. write_chart_crop_comparison_truck — simple (non-stacked) grouped bars,
     cocoa vs coffee, truck mode only, matched by scenario letter (A-F), with
     the same letter + "Scenario A : ..." legend convention.

Legend convention: placed OUTSIDE the axes (right-hand side, bbox_to_anchor)
so it never overlaps tall stacked bars. When a chart has two legends (e.g.
category colours + scenario letters), the first is kept alive with
ax.add_artist() so both remain visible.

2026-09-24 fix: EVERY savefig() call now explicitly passes
`bbox_extra_artists=(...)` listing every legend object created for that
chart. `bbox_inches="tight"` alone does NOT reliably include legends added
via `ax.add_artist()` in its tight-bbox calculation — especially when that
legend is the ONLY legend on a narrow figure (e.g. the by-farmtype charts,
figsize=(7.5, 5)): the legend, anchored outside the axes at
bbox_to_anchor=(1.01, 1.0), was simply being cropped out of the saved PNG
entirely. Passing bbox_extra_artists is the standard matplotlib idiom to
force inclusion regardless of how the legend was attached.
"""

import os

import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.patheffects as pe

import src.factors as f

CATEGORIES = [
    "luc", "fertiliser_direct", "fertiliser_volatilisation", "fertiliser_leaching",
    "drying", "transport", "roasting",
]
CATEGORY_LABELS = {
    "fertiliser_direct": "Fertiliser N2O (direct)",
    "fertiliser_volatilisation": "Fertiliser N2O (volatilisation)",
    "fertiliser_leaching": "Fertiliser N2O (leaching)",
    "luc": "Land-use change (amortised)",
    "drying": "Drying (post-harvest)",
    "transport": "Transport",
    "roasting": "Roasting (high uncertainty, see SOURCES.md #13)",
}
CATEGORY_COLORS = {
    "fertiliser_direct": "#d62728",
    "fertiliser_volatilisation": "#ff7f0e",
    "fertiliser_leaching": "#bcbd22",
    "luc": "#9467bd",
    "drying": "#17becf",
    "transport": "#1f77b4",
    "roasting": "#e377c2",
}

MODE_COLORS = {"truck": "#b3542e", "rail": "#3f7d5c", "air": "#8f478f", "sea": "#3f6d9f"}
MODE_ORDER = ["truck", "rail", "sea", "air"]

COLOR_COUNTERFACTUAL = "#b0b0b0"
COLOR_PENALTY = "#c0392b"
COLOR_BONUS = "#2ca02c"

CROP_COLORS = {"cocoa": "#6b4423", "coffee": "#c08a4a"}


def _lit_band_for_crop(crop):
    if crop == "cocoa":
        return f.LIT_PCF_NO_LUC_DECILE_LOW, f.LIT_PCF_NO_LUC_DECILE_HIGH, "Literature range, no LUC (decile)"
    elif crop == "coffee":
        return f.LIT_PCF_COFFEE_NO_LUC_LOW, f.LIT_PCF_COFFEE_NO_LUC_HIGH, "Literature range, no LUC (median +/- IQR)"
    raise ValueError(f"Unknown crop: {crop!r}")


def _any_roasted(results):
    return any(r.get("roast_level", "none") != "none" for r in results)


def _add_literature_band_or_caveat(ax, crop, results):
    """
    Draws the literature comparison band ONLY if none of `results` are
    roasted (the band is sourced on an unroasted green/dry-bean basis — see
    SOURCES.md #9/#9b — and is NOT valid for a roasted-basis PCF). If any
    result is roasted, draws an explicit on-chart caveat instead and returns
    None (caller should skip adding a band legend entry).
    """
    if _any_roasted(results):
        ax.text(
            0.01, 0.99,
            "Literature band omitted: chart includes roasting (functional unit =\n"
            "roasted product, not green/dry beans) — see SOURCES.md #13.",
            transform=ax.transAxes, fontsize=6.5, va="top", ha="left",
            color="firebrick", style="italic",
        )
        return None
    low, high, label = _lit_band_for_crop(crop)
    ax.axhspan(low, high, color="grey", alpha=0.15, label=label)
    return label


def _category_intensity(r, category):
    return r[category] / r["final_product_kg_yr"]


def _stack_bar(ax, x, r, width, show_pct=True, min_pct_label=6, pct_fontsize=6.5):
    """
    Draw one stacked bar. If show_pct, annotate each segment whose share of
    the bar's total emissions is >= min_pct_label with its percentage, so
    only the main contributors get a label and small slivers don't clutter
    the chart.
    """
    bottom = 0.0
    total = sum(r[cat] for cat in CATEGORIES)
    for cat in CATEGORIES:
        height = _category_intensity(r, cat)
        if height == 0:
            continue
        ax.bar(x, height, bottom=bottom, width=width, color=CATEGORY_COLORS[cat])
        if show_pct and total > 0:
            pct = r[cat] / total * 100
            if pct >= min_pct_label:
                txt = ax.text(x, bottom + height / 2, f"{pct:.0f}%",
                               ha="center", va="center", fontsize=pct_fontsize, color="black")
                txt.set_path_effects([pe.withStroke(linewidth=2, foreground="white")])
        bottom += height
    return bottom


def _add_category_legend_outside(ax, extra_handles=None, extra_labels=None,
                                  bbox_to_anchor=(1.01, 1.0)):
    handles = [plt.Rectangle((0, 0), 1, 1, color=CATEGORY_COLORS[c]) for c in CATEGORIES]
    labels = [CATEGORY_LABELS[c] for c in CATEGORIES]
    if extra_handles:
        handles += list(extra_handles)
        labels += list(extra_labels)
    legend = ax.legend(handles, labels, loc="upper left", bbox_to_anchor=bbox_to_anchor,
                        borderaxespad=0, fontsize=8, frameon=True, title="Lifecycle stage")
    ax.add_artist(legend)  # keep alive if a second legend is added afterwards
    return legend


def _lit_band_handle(label):
    return plt.Rectangle((0, 0), 1, 1, color="grey", alpha=0.15), label


def _safe_filename(name):
    return name.replace(" ", "_").replace(".", "").replace(",", "").replace("/", "-")


def _ylabel(results):
    return f"kg CO2e / kg {results[0]['product_unit_label']}"


# --- Scenario letter/label helpers (used for simplified x-axes) ---

def _scenario_letter(name):
    return name.split(".")[0].strip()


def _scenario_letter_and_label(name):
    letter, _, rest = name.partition(".")
    return letter.strip(), rest.strip()


def _add_scenario_legend(ax, names, bbox_to_anchor=(1.01, 0.55)):
    """
    Second legend mapping each x-axis letter (A, B, ...) back to its full
    scenario name, e.g. "Scenario A : Conventional baseline". Uses invisible
    handles so it reads as a plain text key, not a colour legend.
    """
    pairs = [_scenario_letter_and_label(n) for n in names]
    handles = [plt.Line2D([], [], linestyle="none") for _ in pairs]
    labels = [f"Scenario {letter} : {label}" for letter, label in pairs]
    legend = ax.legend(handles, labels, loc="upper left", bbox_to_anchor=bbox_to_anchor,
                        borderaxespad=0, fontsize=7, frameon=True, handlelength=0,
                        handletextpad=0, title="Scenarios", title_fontsize=8)
    return legend


# --- Plot 1: overview ---

def write_chart_overview(results, path):
    crop = results[0]["crop"]
    scenario_names = sorted({r["scenario"] for r in results})
    by_key = {(r["scenario"], r["transport_mode"]): r for r in results}

    n_modes = len(MODE_ORDER)
    group_width = 0.8
    bar_width = group_width / n_modes

    fig, ax = plt.subplots(figsize=(15, 6.5))
    for gi, name in enumerate(scenario_names):
        for mi, mode in enumerate(MODE_ORDER):
            r = by_key.get((name, mode))
            if r is None:
                continue
            xpos = gi + (mi - (n_modes - 1) / 2) * bar_width
            total = _stack_bar(ax, xpos, r, bar_width, min_pct_label=12, pct_fontsize=5)
            ax.annotate(mode, xy=(xpos, 0), xytext=(0, -18), textcoords="offset points",
                        ha="center", fontsize=6.5, rotation=90, color=MODE_COLORS[mode])
            ax.text(xpos, total + 0.02 * total, f"{total:.2f}", ha="center", fontsize=6, rotation=90)

    ax.set_xticks(range(len(scenario_names)))
    ax.set_xticklabels(scenario_names, rotation=15, ha="right", fontsize=8)
    ax.set_ylabel(_ylabel(results))
    ax.set_title(f"{crop.capitalize()} PCF — all scenarios x all transport modes, by lifecycle stage")

    label = _add_literature_band_or_caveat(ax, crop, results)
    if label:
        extra_handle, extra_label = _lit_band_handle(label)
        legend = _add_category_legend_outside(ax, [extra_handle], [extra_label])
    else:
        legend = _add_category_legend_outside(ax)

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", bbox_extra_artists=(legend,))
    plt.close(fig)


# --- Plot 2: by mode ---

def write_charts_by_mode(results, output_dir):
    crop = results[0]["crop"]
    modes = sorted({r["transport_mode"] for r in results})
    for mode in modes:
        subset = sorted((r for r in results if r["transport_mode"] == mode), key=lambda r: r["scenario"])
        names = [r["scenario"] for r in subset]
        letters = [_scenario_letter(n) for n in names]

        fig, ax = plt.subplots(figsize=(9, 5.5))
        for i, r in enumerate(subset):
            total = _stack_bar(ax, i, r, 0.6, min_pct_label=5, pct_fontsize=7)
            ax.text(i, total + 0.02 * total, f"{total:.2f}", ha="center", fontsize=9)

        ax.set_xticks(range(len(letters)))
        ax.set_xticklabels(letters, fontsize=11)
        ax.set_ylabel(_ylabel(results))
        ax.set_title(f"{crop.capitalize()} PCF by farm scenario — transport mode: {mode}")

        label = _add_literature_band_or_caveat(ax, crop, subset)
        if label:
            extra_handle, extra_label = _lit_band_handle(label)
            legend1 = _add_category_legend_outside(ax, [extra_handle], [extra_label])
        else:
            legend1 = _add_category_legend_outside(ax)
        legend2 = _add_scenario_legend(ax, names, bbox_to_anchor=(1.01, 0.42))

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{crop}_footprint_{mode}.png"), dpi=150,
                    bbox_inches="tight", bbox_extra_artists=(legend1, legend2))
        plt.close(fig)


# --- Plot 3: by farm type ---

def write_charts_by_farmtype(results, output_dir):
    crop = results[0]["crop"]
    farm_types = sorted({r["scenario"] for r in results})
    for farm in farm_types:
        subset = sorted((r for r in results if r["scenario"] == farm),
                         key=lambda r: MODE_ORDER.index(r["transport_mode"]))
        modes = [r["transport_mode"] for r in subset]

        fig, ax = plt.subplots(figsize=(7.5, 5))
        for i, r in enumerate(subset):
            total = _stack_bar(ax, i, r, 0.6, min_pct_label=5, pct_fontsize=7)
            ax.text(i, total + 0.02 * total, f"{total:.2f}", ha="center", fontsize=9)

        ax.set_xticks(range(len(modes)))
        ax.set_xticklabels(modes, fontsize=9)
        ax.set_ylabel(_ylabel(results))
        ax.set_title(f"{crop.capitalize()} PCF by transport mode — {farm}")

        label = _add_literature_band_or_caveat(ax, crop, subset)
        if label:
            extra_handle, extra_label = _lit_band_handle(label)
            legend = _add_category_legend_outside(ax, [extra_handle], [extra_label])
        else:
            legend = _add_category_legend_outside(ax)

        plt.tight_layout()
        fname = f"{crop}_footprint_farmtype_{_safe_filename(farm)}.png"
        plt.savefig(os.path.join(output_dir, fname), dpi=150,
                    bbox_inches="tight", bbox_extra_artists=(legend,))
        plt.close(fig)


# --- Plot 4: yield-dilution effect ---

def write_charts_yield_effect(yield_analysis, output_dir):
    """
    Grouped-bar chart, one pair of bars per scenario:
      - grey bar  = "reference" PCF this scenario WOULD have if its yield
        were equal to the reference yield (baseline scenario A's yield),
        all other practices (fertiliser, LUC, transport, drying, roasting)
        unchanged;
      - coloured bar = the scenario's ACTUAL PCF, at its own real yield.

    Both bars are on the SAME functional unit (roasted or unroasted,
    whichever this scenario's roast_level implies) since
    compute_counterfactual_pcf() applies the identical roasting stage as
    run_scenario() — see main.py.

    The gap between the two bars is the pure "yield-dilution effect": how
    much of the actual PCF is explained just by this scenario's yield being
    below (red, penalty -> higher PCF) or above (green, bonus -> lower PCF)
    the reference yield, isolated from fertiliser/LUC/transport/processing
    differences. The delta is annotated directly above each pair of bars.
    """
    crop = yield_analysis[0]["crop"]
    modes = sorted({r["transport_mode"] for r in yield_analysis})
    for mode in modes:
        subset = sorted((r for r in yield_analysis if r["transport_mode"] == mode), key=lambda r: r["scenario"])
        names = [r["scenario"] for r in subset]
        letters = [_scenario_letter(n) for n in names]
        counterfactual = [r["counterfactual_pcf"] for r in subset]
        actual = [r["actual_pcf"] for r in subset]
        ref_yield = subset[0]["reference_yield_kg_ha"]
        ref_name = subset[0]["reference_scenario_name"]
        roasted = any(r.get("roast_level", "none") != "none" for r in subset)

        x = list(range(len(names)))
        width = 0.35

        fig, ax = plt.subplots(figsize=(9.5, 6))
        ax.bar([xi - width / 2 for xi in x], counterfactual, width=width, color=COLOR_COUNTERFACTUAL)
        actual_colors = [COLOR_PENALTY if a > c else COLOR_BONUS for a, c in zip(actual, counterfactual)]
        ax.bar([xi + width / 2 for xi in x], actual, width=width, color=actual_colors)

        for xi, c, a in zip(x, counterfactual, actual):
            ax.annotate(f"{c:.2f}", xy=(xi - width / 2, c), xytext=(0, 3),
                        textcoords="offset points", ha="center", fontsize=8)
            ax.annotate(f"{a:.2f}", xy=(xi + width / 2, a), xytext=(0, 3),
                        textcoords="offset points", ha="center", fontsize=8)
            delta = a - c
            if abs(delta) > 1e-9:
                sign = "+" if delta > 0 else "\u2212"
                word = "penalty" if delta > 0 else "bonus"
                color = COLOR_PENALTY if delta > 0 else COLOR_BONUS
                ax.annotate(f"{sign}{abs(delta):.2f} ({word})", xy=(xi, max(c, a)),
                            xytext=(0, 22), textcoords="offset points", ha="center",
                            fontsize=7, color=color)

        ax.set_xticks(x)
        ax.set_xticklabels(letters, fontsize=11)
        ax.set_ylabel("kg CO2e / kg product" + (" (roasted basis)" if roasted else ""))
        ax.set_title(
            f"{crop.capitalize()} — effect of yield on PCF — transport mode: {mode}\n"
            f"Grey = PCF at reference yield ({ref_yield:.0f} kg/ha/yr, scenario {ref_name}); "
            f"coloured = actual PCF at this scenario's own yield"
            + ("\n(includes roasting — see SOURCES.md #13)" if roasted else "")
        )

        grey_patch = plt.Rectangle((0, 0), 1, 1, color=COLOR_COUNTERFACTUAL)
        penalty_patch = plt.Rectangle((0, 0), 1, 1, color=COLOR_PENALTY)
        bonus_patch = plt.Rectangle((0, 0), 1, 1, color=COLOR_BONUS)
        legend1 = ax.legend(
            [grey_patch, penalty_patch, bonus_patch],
            [f"Reference-yield PCF ({ref_yield:.0f} kg/ha/yr, scenario {ref_name})",
             "Actual PCF — yield below reference (penalty: PCF higher)",
             "Actual PCF — yield at/above reference (bonus: PCF lower)"],
            loc="upper left", bbox_to_anchor=(1.01, 1.0), borderaxespad=0, fontsize=7.5, frameon=True,
        )
        ax.add_artist(legend1)
        legend2 = _add_scenario_legend(ax, names, bbox_to_anchor=(1.01, 0.55))

        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, f"{crop}_yield_effect_{mode}.png"), dpi=150,
                    bbox_inches="tight", bbox_extra_artists=(legend1, legend2))
        plt.close(fig)


# --- Plot 5: simple cocoa-vs-coffee comparison, truck only ---

def write_chart_crop_comparison_truck(truck_results_by_crop, path):
    """
    Simple (non-stacked) grouped-bar comparison of cocoa vs coffee PCF, truck
    mode only, matched by scenario letter (A-F). Transport is a minor share of
    total LCA PCF, so restricting to one mode avoids confounding the crop
    comparison with a transport-mode difference. X-axis is simplified to the
    scenario letter; a separate legend gives the full scenario names.

    Y-axis/title product-unit wording is generated dynamically from each
    result's product_unit_label, since roasting (if enabled) changes it from
    "dry cocoa beans"/"green coffee beans" to "roasted cocoa/coffee beans".
    """
    letters = sorted({
        _scenario_letter(r["scenario"])
        for results in truck_results_by_crop.values() for r in results
    })
    crops = list(truck_results_by_crop.keys())
    n_crops = len(crops)
    bar_width = 0.8 / n_crops

    product_labels = sorted({
        r["product_unit_label"]
        for results in truck_results_by_crop.values() for r in results
    })
    roasted = any(
        r.get("roast_level", "none") != "none"
        for results in truck_results_by_crop.values() for r in results
    )

    letter_labels = {}
    for letter in letters:
        for crop in crops:
            match = next((r for r in truck_results_by_crop[crop]
                          if _scenario_letter(r["scenario"]) == letter), None)
            if match:
                _, label = _scenario_letter_and_label(match["scenario"])
                letter_labels[letter] = label
                break

    fig, ax = plt.subplots(figsize=(9.5, 6))
    for ci, crop in enumerate(crops):
        by_letter = {_scenario_letter(r["scenario"]): r for r in truck_results_by_crop[crop]}
        for li, letter in enumerate(letters):
            r = by_letter.get(letter)
            if r is None:
                continue
            xpos = li + (ci - (n_crops - 1) / 2) * bar_width
            pcf = r["pcf_kg_co2e_per_kg"]
            ax.bar(xpos, pcf, width=bar_width, color=CROP_COLORS[crop])
            ax.text(xpos, pcf + 0.02 * pcf, f"{pcf:.2f}", ha="center", fontsize=8)

    ax.set_xticks(range(len(letters)))
    ax.set_xticklabels(letters, fontsize=11)
    ax.set_ylabel(f"kg CO2e / kg product ({' / '.join(product_labels)})")
    title = "Cocoa vs coffee PCF by scenario type — truck mode only\n(emissions intensity, excl. removals)"
    if roasted:
        title += "\n(includes roasting — high uncertainty, see SOURCES.md #13)"
    ax.set_title(title)

    handles = [plt.Rectangle((0, 0), 1, 1, color=CROP_COLORS[c]) for c in crops]
    legend1 = ax.legend(handles, [c.capitalize() for c in crops], loc="upper left",
                         bbox_to_anchor=(1.01, 1.0), borderaxespad=0, fontsize=9, frameon=True)
    ax.add_artist(legend1)
    legend2 = _add_scenario_legend(ax, [f"{letter}. {letter_labels[letter]}" for letter in letters],
                                    bbox_to_anchor=(1.01, 0.6))

    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight", bbox_extra_artists=(legend1, legend2))
    plt.close(fig)