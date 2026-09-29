#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
random_gen/generate_coords.py

Génère des coordonnées (latitude, longitude) aléatoires pour chaque
scénario producteur (café ou cacao), en respectant les proportions
réelles de production mondiale par pays/région, et en tirant les points
dans des bounding boxes centrées sur les véritables bassins de
production.

La liste des scénarios est déterminée automatiquement en lisant la
colonne "scenario" de tous les CSV de :
    data/output/random_tests/carbon_data/
(voir random_gen.src.config.discover_scenarios). Elle peut être
surchargée via --input ou --carbon-data-dir.

Sortie : CSV avec scenario_id, crop, country_iso3, region, latitude, longitude.

Exécution :
    python random_gen/generate_coords.py
    python random_gen/generate_coords.py --carbon-data-dir /autre/chemin -s 42
    python random_gen/generate_coords.py --input mes_scenarios.txt
"""

import argparse
import csv
import random
import sys
from pathlib import Path
from typing import List

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from random_gen.src import config
from random_gen.src.sampling import weighted_choice, uniform_point_in_bbox
from random_gen.src.scenario_utils import detect_crop
from random_gen.src.geo_regions import regions_for_crop, ProductionRegion


def pick_region(rng: random.Random, crop: str) -> ProductionRegion:
    regions = regions_for_crop(crop)
    options = [(region, region.weight) for region in regions]
    return weighted_choice(rng, options)


def generate_row(scenario_id: str, rng: random.Random) -> dict:
    crop = detect_crop(scenario_id)
    region = pick_region(rng, crop)
    lat, lon = uniform_point_in_bbox(
        rng, region.lat_min, region.lat_max, region.lon_min, region.lon_max
    )
    return {
        "scenario_id": scenario_id,
        "crop": crop,
        "country_iso3": region.country_iso3,
        "region": region.region_label,
        "latitude": lat,
        "longitude": lon,
    }


def load_scenarios_from_txt(path: Path) -> List[str]:
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Génère des coordonnées lat/lon aléatoires pour des scénarios "
                    "café/cacao, pondérées par pays de production réel."
    )
    parser.add_argument("-o", "--output", default="scenarios_coordinates.csv",
                         help="Fichier CSV de sortie (défaut: scenarios_coordinates.csv)")
    parser.add_argument("-s", "--seed", type=int, default=None,
                         help="Graine aléatoire pour des résultats reproductibles")
    parser.add_argument("-i", "--input", type=Path, default=None,
                         help="Fichier texte optionnel avec un scenario_id par ligne "
                              "(remplace la découverte automatique depuis les CSV carbone)")
    parser.add_argument("--carbon-data-dir", type=Path, default=None,
                         help="Dossier contenant les CSV carbone (colonne 'scenario'). "
                              f"Défaut : {config.DEFAULT_CARBON_DATA_DIR}")
    args = parser.parse_args()

    if args.input:
        scenarios = load_scenarios_from_txt(args.input)
    else:
        scenarios = config.discover_scenarios(args.carbon_data_dir)

    rng = random.Random(args.seed)
    rows = [generate_row(scenario_id, rng) for scenario_id in scenarios]

    fieldnames = ["scenario_id", "crop", "country_iso3", "region", "latitude", "longitude"]
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} scénarios traités -> {args.output}")


if __name__ == "__main__":
    main()