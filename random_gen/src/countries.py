"""
Référentiel pays pour la génération comptable : devise locale, taux de
change USD (fourchette), taxe/prélèvement à l'export, accès à la mer, et
poids de production (café/cacao) et répartition Arabica/Robusta.

Ordres de grandeur ILLUSTRATIFS (~2024-2026), à ne pas utiliser comme
référence de marché réelle.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple


@dataclass(frozen=True)
class CountryInfo:
    currency: str
    fx_range: Tuple[float, float]           # unités de devise locale pour 1 USD
    export_tax_pct_range: Tuple[float, float]


COUNTRY_INFO: Dict[str, CountryInfo] = {
    "CIV": CountryInfo("XOF", (580, 620), (12, 16)),
    "GHA": CountryInfo("GHS", (14, 17), (0, 2)),
    "IDN": CountryInfo("IDR", (15300, 16500), (0, 5)),
    "ECU": CountryInfo("USD", (1, 1), (0, 0)),
    "CMR": CountryInfo("XAF", (580, 620), (5, 10)),
    "NGA": CountryInfo("NGN", (1450, 1650), (0, 0)),
    "BRA": CountryInfo("BRL", (4.9, 5.6), (0, 0)),
    "PER": CountryInfo("PEN", (3.6, 3.85), (0, 0)),
    "DOM": CountryInfo("DOP", (58, 61), (0, 0)),
    "COL": CountryInfo("COP", (3900, 4300), (0, 0)),
    "TGO": CountryInfo("XOF", (580, 620), (8, 12)),
    "PNG": CountryInfo("PGK", (3.7, 4.0), (0, 0)),
    "UGA": CountryInfo("UGX", (3650, 3800), (0, 0)),
    "MEX": CountryInfo("MXN", (17, 19.5), (0, 0)),
    "SLE": CountryInfo("SLE", (19, 23), (0, 0)),
    "VNM": CountryInfo("VND", (24300, 25700), (0, 0)),
    "ETH": CountryInfo("ETB", (110, 145), (0, 1)),
    "HND": CountryInfo("HNL", (24.5, 25.5), (0, 0)),
    "IND": CountryInfo("INR", (83, 85.5), (0, 0)),
    "GTM": CountryInfo("GTQ", (7.7, 7.9), (0, 0)),
    "NIC": CountryInfo("NIO", (36.4, 37.1), (0, 0)),
    "CRI": CountryInfo("CRC", (500, 535), (0, 0)),
    "TZA": CountryInfo("TZS", (2500, 2750), (0, 0)),
    "KEN": CountryInfo("KES", (128, 158), (0, 0)),
    "RWA": CountryInfo("RWF", (1300, 1420), (0, 0)),
    "YEM": CountryInfo("YER", (250, 530), (0, 0)),
}

# Pays enclavés : coûts de transport intérieur plus élevés (pas d'accès
# direct à la mer -> transbordement, routes plus longues).
LANDLOCKED = {"UGA", "RWA", "ETH"}

# Pondérations pays ~ part de production mondiale (mêmes ordres de
# grandeur que random_gen.src.geo_regions, simplifiées au niveau pays).
CACAO_COUNTRY_WEIGHTS: List[Tuple[str, float]] = [
    ("CIV", 38), ("GHA", 13), ("IDN", 6), ("ECU", 6), ("CMR", 6),
    ("NGA", 5), ("BRA", 5), ("PER", 3), ("DOM", 2), ("COL", 2),
    ("TGO", 1), ("PNG", 1), ("UGA", 1), ("MEX", 1), ("SLE", 1),
]

COFFEE_COUNTRY_WEIGHTS: List[Tuple[str, float]] = [
    ("BRA", 36), ("VNM", 18), ("COL", 8), ("IDN", 7), ("ETH", 5),
    ("HND", 4), ("IND", 3), ("UGA", 3), ("MEX", 2.5), ("GTM", 2.5),
    ("PER", 2.5), ("NIC", 1.5), ("CRI", 1), ("TZA", 1), ("KEN", 1),
    ("PNG", 1), ("RWA", 0.5), ("YEM", 0.5),
]

# Répartition Arabica / Robusta par pays producteur de café (ILLUSTRATIF).
COFFEE_VARIETY_WEIGHTS: Dict[str, Dict[str, float]] = {
    "BRA": {"arabica": 0.70, "robusta": 0.30},
    "VNM": {"arabica": 0.05, "robusta": 0.95},
    "COL": {"arabica": 1.00, "robusta": 0.00},
    "IDN": {"arabica": 0.30, "robusta": 0.70},
    "ETH": {"arabica": 1.00, "robusta": 0.00},
    "HND": {"arabica": 1.00, "robusta": 0.00},
    "IND": {"arabica": 0.40, "robusta": 0.60},
    "UGA": {"arabica": 0.20, "robusta": 0.80},
    "MEX": {"arabica": 1.00, "robusta": 0.00},
    "GTM": {"arabica": 1.00, "robusta": 0.00},
    "PER": {"arabica": 1.00, "robusta": 0.00},
    "NIC": {"arabica": 1.00, "robusta": 0.00},
    "CRI": {"arabica": 1.00, "robusta": 0.00},
    "TZA": {"arabica": 0.75, "robusta": 0.25},
    "KEN": {"arabica": 1.00, "robusta": 0.00},
    "PNG": {"arabica": 0.90, "robusta": 0.10},
    "RWA": {"arabica": 1.00, "robusta": 0.00},
    "YEM": {"arabica": 1.00, "robusta": 0.00},
}


def country_weights_for_crop(crop: str) -> List[Tuple[str, float]]:
    if crop == "cocoa":
        return CACAO_COUNTRY_WEIGHTS
    if crop == "coffee":
        return COFFEE_COUNTRY_WEIGHTS
    raise ValueError(f"Culture inconnue : {crop!r} (attendu 'cocoa' ou 'coffee')")