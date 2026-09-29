"""
Fonctions génériques de tirage aléatoire pondéré, partagées par
generate_coords.py et generate_accounting_data.py.
"""

import random
from typing import Sequence, Tuple, TypeVar

T = TypeVar("T")


def weighted_choice(rng: random.Random, options: Sequence[Tuple[T, float]]) -> T:
    """
    Tire un élément parmi `options` (liste de tuples (valeur, poids)),
    proportionnellement à son poids.
    """
    labels = [o[0] for o in options]
    weights = [o[1] for o in options]
    return rng.choices(labels, weights=weights, k=1)[0]


def uniform_point_in_bbox(rng: random.Random,
                           lat_min: float, lat_max: float,
                           lon_min: float, lon_max: float,
                           precision: int = 6) -> Tuple[float, float]:
    """Tire un point (lat, lon) uniformément dans une bounding box."""
    lat = rng.uniform(lat_min, lat_max)
    lon = rng.uniform(lon_min, lon_max)
    return round(lat, precision), round(lon, precision)


def uniform_in_range(rng: random.Random, value_range: Tuple[float, float],
                      precision: int = 2) -> float:
    """Tire une valeur uniforme dans un intervalle (min, max), arrondie."""
    lo, hi = value_range
    return round(rng.uniform(lo, hi), precision)