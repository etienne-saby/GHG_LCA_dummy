"""
Données de marché et de contrat pour la génération comptable synthétique :
prix de référence (ICE Cocoa / ICE Coffee C / ICE Robusta), grades qualité,
primes de certification, et distributions utilisées pour tirer les
caractéristiques de contrat (Incoterm, type de contrat, couverture...).

Ordres de grandeur ILLUSTRATIFS (~2024-2026), à but de démonstration.
"""

from typing import Dict, List, Optional, Tuple

# --- Prix de référence marché ($/tonne), par année de campagne -------------

COCOA_PRICE_RANGES_USD_PER_TON: Dict[int, Tuple[float, float]] = {
    2024: (6000, 11500),
    2025: (3800, 7500),
    2026: (3200, 6200),
}
COCOA_PRICE_DEFAULT_RANGE: Tuple[float, float] = (3500, 6500)

COFFEE_ARABICA_PRICE_RANGES_USD_PER_TON: Dict[int, Tuple[float, float]] = {
    2024: (6500, 9500),
    2025: (5200, 8200),
    2026: (4500, 7200),
}
COFFEE_ROBUSTA_PRICE_RANGES_USD_PER_TON: Dict[int, Tuple[float, float]] = {
    2024: (3800, 5600),
    2025: (3200, 5200),
    2026: (3000, 4800),
}
COFFEE_PRICE_DEFAULT_YEAR = 2025

QUALITY_DIFFERENTIAL_RANGE_USD_PER_TON: Tuple[float, float] = (-300, 300)

# --- Campagnes ---------------------------------------------------------------

CAMPAIGN_YEAR_WEIGHTS: List[Tuple[int, float]] = [(2024, 20), (2025, 45), (2026, 35)]

# --- Grades qualité ------------------------------------------------------------

COCOA_QUALITY_GRADE_WEIGHTS: List[Tuple[str, float]] = [
    ("Grade I", 35), ("Grade II", 35), ("FAQ (Fair Average Quality)", 25), ("Below FAQ", 5),
]

COFFEE_ROBUSTA_GRADE_WEIGHTS: List[Tuple[str, float]] = [
    ("Grade 1 (Screen 18)", 20), ("Grade 2 (Screen 16)", 40),
    ("Grade 3", 30), ("Below Grade", 10),
]

COFFEE_ARABICA_GRADE_WEIGHTS: List[Tuple[str, float]] = [
    ("Specialty (85+)", 10), ("Premium (80-84)", 35),
    ("Exchange Grade", 45), ("Below Grade", 10),
]

# --- Certifications et primes ($/tonne) ----------------------------------------

CERTIFICATION_WEIGHTS: List[Tuple[str, float]] = [
    ("none", 50), ("organic", 12), ("fairtrade", 12),
    ("rainforest_alliance", 14), ("utz", 7), ("4c", 5),
]

CERTIFICATION_PREMIUM_RANGES_USD_PER_TON: Dict[str, Tuple[float, float]] = {
    "none": (0, 0),
    "organic": (150, 400),
    "fairtrade": (100, 250),
    "rainforest_alliance": (50, 150),
    "utz": (40, 120),
    "4c": (20, 60),
}

# --- Contrat -------------------------------------------------------------------

INCOTERM_WEIGHTS: List[Tuple[str, float]] = [
    ("FOB", 50), ("FCA", 20), ("EXW", 15), ("CIF", 10), ("FAS", 5),
]

CONTRACT_TYPE_WEIGHTS: List[Tuple[str, float]] = [
    ("spot", 40), ("forward", 35), ("prepayment", 25),
]

PRODUCER_TYPE_WEIGHTS: List[Tuple[str, float]] = [
    ("Coopérative", 45), ("Ferme", 25), ("Exploitation", 15), ("Groupement de producteurs", 15),
]

# --- Risque ---------------------------------------------------------------------

HEDGE_INSTRUMENT_WEIGHTS: List[Tuple[str, float]] = [
    ("futures", 35), ("options", 15), ("none", 50),
]

CREDIT_RATING_WEIGHTS: List[Tuple[str, float]] = [
    ("A", 10), ("B", 35), ("C", 40), ("D", 15),
]


def cocoa_price_range(campaign_year: int) -> Tuple[float, float]:
    return COCOA_PRICE_RANGES_USD_PER_TON.get(campaign_year, COCOA_PRICE_DEFAULT_RANGE)


def coffee_price_range(campaign_year: int, variety: Optional[str]) -> Tuple[float, float]:
    table = (COFFEE_ROBUSTA_PRICE_RANGES_USD_PER_TON if variety == "robusta"
             else COFFEE_ARABICA_PRICE_RANGES_USD_PER_TON)
    return table.get(campaign_year, table[COFFEE_PRICE_DEFAULT_YEAR])


def quality_grade_weights(crop: str, coffee_variety: Optional[str] = None) -> List[Tuple[str, float]]:
    if crop == "cocoa":
        return COCOA_QUALITY_GRADE_WEIGHTS
    if crop == "coffee":
        return COFFEE_ROBUSTA_GRADE_WEIGHTS if coffee_variety == "robusta" else COFFEE_ARABICA_GRADE_WEIGHTS
    raise ValueError(f"Culture inconnue : {crop!r}")