"""
Utilitaires communs pour interpréter un scenario_id (ex: "RANDOM-COCOA-0003",
"RANDOM-COFFEE-ROASTED-0201") : culture, étape de transformation, suffixe
numérique. Partagé par generate_coords.py et generate_accounting_data.py.
"""

import re


def detect_crop(scenario_id: str) -> str:
    """Retourne 'cocoa' ou 'coffee' selon le contenu de l'identifiant."""
    upper = scenario_id.upper()
    if "COCOA" in upper:
        return "cocoa"
    if "COFFEE" in upper:
        return "coffee"
    raise ValueError(f"Impossible de déterminer la culture pour '{scenario_id}'")


def is_roasted(scenario_id: str) -> bool:
    """True si le scénario correspond à un produit torréfié (*-ROASTED-*)."""
    return "ROASTED" in scenario_id.upper()


def scenario_suffix(scenario_id: str, default: str = "0000") -> str:
    """Extrait le suffixe numérique final de l'identifiant (ex: '0003')."""
    match = re.search(r"(\d+)$", scenario_id)
    return match.group(1) if match else default