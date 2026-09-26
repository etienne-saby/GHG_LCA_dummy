# Cocoa & Coffee Carbon Footprint Prototype

A Tier 1 **demo** tool estimating the product carbon footprint (PCF, kg CO2e / kg product)
of smallholder cocoa and coffee farms, from farm-gate inputs (fertiliser, land-use history,
drying, transport, optional roasting) plus an agroforestry CO2-removal co-benefit.

**This is not an audited inventory.** Every factor is traceable to a named source with an
explicit confidence tier — see [`SOURCES.md`](./SOURCES.md). Where no defensible source could
be found, the value is flagged `# ILLUSTRATIVE - unverified` directly in the code.

## Quick start

```bash
python main.py