"""
Bassins de production café/cacao : pondération (~ part de production
mondiale) et bounding box géographique resserrée sur le vrai bassin
agricole (et non le centre géographique du pays).

Sources d'ordre de grandeur : ICCO (cacao), ICO / USDA (café). Poids et
emprises sont ILLUSTRATIFS, destinés à un jeu de données de démonstration.
"""

from dataclasses import dataclass
from typing import List


@dataclass(frozen=True)
class ProductionRegion:
    country_iso3: str
    region_label: str
    weight: float          # poids relatif (~ % de production mondiale)
    lat_min: float
    lat_max: float
    lon_min: float
    lon_max: float


CACAO_REGIONS: List[ProductionRegion] = [
    ProductionRegion("CIV", "Sud-Ouest / Centre-Ouest (Abidjan-San Pedro-Daloa)", 38,
                      4.6, 8.8, -8.4, -3.0),
    ProductionRegion("GHA", "Ashanti / Western / Eastern", 13,
                      4.6, 7.6, -3.3, 0.6),
    ProductionRegion("IDN", "Sulawesi", 6,
                      -5.4, 1.4, 119.3, 123.5),
    ProductionRegion("ECU", "Côte (Guayas, Los Ríos, Manabí)", 6,
                      -3.4, 0.4, -80.5, -79.0),
    ProductionRegion("CMR", "Centre / Sud / Littoral", 6,
                      2.5, 6.3, 9.5, 14.5),
    ProductionRegion("NGA", "Sud-Ouest / Cross River", 5,
                      5.0, 8.0, 3.0, 9.0),
    ProductionRegion("BRA", "Bahia (Sud)", 5,
                      -16.0, -13.0, -40.0, -38.5),
    ProductionRegion("PER", "San Martín / Ucayali", 3,
                      -9.0, -6.0, -77.0, -74.0),
    ProductionRegion("DOM", "Nord / San Francisco de Macorís", 2,
                      18.6, 19.6, -71.0, -69.5),
    ProductionRegion("COL", "Santander / Arauca", 2,
                      5.0, 9.0, -75.0, -72.5),
    ProductionRegion("TGO", "Plateaux", 1,
                      6.6, 7.9, 0.3, 1.4),
    ProductionRegion("PNG", "East New Britain / Bougainville", 1,
                      -6.6, -4.0, 150.0, 155.5),
    ProductionRegion("UGA", "Ouest (Bundibugyo, Mukono)", 1,
                      -1.0, 3.0, 29.7, 34.0),
    ProductionRegion("MEX", "Chiapas / Tabasco", 1,
                      15.6, 18.0, -94.0, -91.5),
    ProductionRegion("SLE", "Est du pays", 1,
                      7.2, 9.3, -12.5, -10.3),
]

COFFEE_REGIONS: List[ProductionRegion] = [
    ProductionRegion("BRA", "Minas Gerais / São Paulo / Espírito Santo", 36,
                      -22.0, -15.0, -47.0, -39.5),
    ProductionRegion("VNM", "Hauts plateaux du centre (Dak Lak, Lam Dong)", 18,
                      10.5, 14.5, 105.5, 108.5),
    ProductionRegion("COL", "Eje Cafetero / Huila / Nariño", 8,
                      1.0, 6.5, -76.7, -74.5),
    ProductionRegion("IDN", "Sumatra (Nord/Sud)", 4,
                      -4.5, 4.0, 98.0, 103.5),
    ProductionRegion("IDN", "Java / Sulawesi", 3,
                      -8.2, -1.5, 105.0, 121.0),
    ProductionRegion("ETH", "Sidamo / Yirgacheffe / Oromia", 5,
                      5.0, 10.0, 36.0, 40.5),
    ProductionRegion("HND", "Ouest (Copán, Santa Bárbara, Comayagua)", 4,
                      13.5, 15.5, -89.0, -86.0),
    ProductionRegion("IND", "Karnataka / Kerala (Ghâts occidentaux)", 3,
                      9.5, 13.5, 75.0, 77.0),
    ProductionRegion("UGA", "Est / Ouest", 3,
                      -1.0, 2.5, 29.5, 34.5),
    ProductionRegion("MEX", "Chiapas / Veracruz / Oaxaca", 2.5,
                      15.5, 19.5, -97.0, -91.0),
    ProductionRegion("GTM", "Antigua / Huehuetenango", 2.5,
                      14.0, 16.0, -91.5, -89.0),
    ProductionRegion("PER", "San Martín / Cajamarca / Junín", 2.5,
                      -9.0, -5.0, -79.0, -73.0),
    ProductionRegion("NIC", "Jinotega / Matagalpa", 1.5,
                      12.5, 14.0, -86.5, -85.0),
    ProductionRegion("CRI", "Vallée centrale / Tarrazú", 1,
                      8.5, 10.5, -84.5, -83.0),
    ProductionRegion("TZA", "Kilimandjaro / Mbeya", 1,
                      -9.5, -2.8, 33.0, 37.5),
    ProductionRegion("KEN", "Centre (Nyeri, Kirinyaga)", 1,
                      -1.5, 0.5, 36.5, 37.5),
    ProductionRegion("PNG", "Hauts plateaux de l'Est", 1,
                      -7.0, -5.0, 143.0, 147.0),
    ProductionRegion("RWA", "Ouest / Sud", 0.5,
                      -2.5, -1.0, 29.0, 30.5),
    ProductionRegion("YEM", "Hauts plateaux (Haraaz, Bani Matar)", 0.5,
                      13.5, 15.5, 43.5, 44.5),
]


def regions_for_crop(crop: str) -> List[ProductionRegion]:
    if crop == "cocoa":
        return CACAO_REGIONS
    if crop == "coffee":
        return COFFEE_REGIONS
    raise ValueError(f"Culture inconnue : {crop!r} (attendu 'cocoa' ou 'coffee')")