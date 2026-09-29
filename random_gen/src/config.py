"""
random_gen.src.config
======================

Point d'entrée unique pour la configuration de random_gen :
  - chemins et découverte des scénarios (SCENARIOS_RAW)
  - ré-export des données de référence (pays, régions de production, marché)

Usage typique :

    from random_gen.src.config import SCENARIOS_RAW, COUNTRY_INFO, CACAO_REGIONS

`SCENARIOS_RAW` est calculé PARESSEUSEMENT (au premier accès) en lisant la
colonne "scenario" de tous les CSV du dossier :

    data/output/random_tests/carbon_data/

Cette approche est plus robuste qu'une liste recopiée à la main : elle
reste synchronisée avec les fichiers réellement présents sur disque.
"""

import csv
import os
import sys
from pathlib import Path
from typing import List, Optional, Set, Union

# Ré-exports pour un point d'accès unique (cf. docstring ci-dessus) --------
from .countries import (        # noqa: F401
    COUNTRY_INFO,
    LANDLOCKED,
    CACAO_COUNTRY_WEIGHTS,
    COFFEE_COUNTRY_WEIGHTS,
    COFFEE_VARIETY_WEIGHTS,
    country_weights_for_crop,
)
from .geo_regions import (      # noqa: F401
    CACAO_REGIONS,
    COFFEE_REGIONS,
    ProductionRegion,
    regions_for_crop,
)
from .market import (           # noqa: F401
    COCOA_PRICE_RANGES_USD_PER_TON,
    COFFEE_ARABICA_PRICE_RANGES_USD_PER_TON,
    COFFEE_ROBUSTA_PRICE_RANGES_USD_PER_TON,
    QUALITY_DIFFERENTIAL_RANGE_USD_PER_TON,
    CAMPAIGN_YEAR_WEIGHTS,
    CERTIFICATION_WEIGHTS,
    CERTIFICATION_PREMIUM_RANGES_USD_PER_TON,
    INCOTERM_WEIGHTS,
    CONTRACT_TYPE_WEIGHTS,
    PRODUCER_TYPE_WEIGHTS,
    HEDGE_INSTRUMENT_WEIGHTS,
    CREDIT_RATING_WEIGHTS,
    cocoa_price_range,
    coffee_price_range,
    quality_grade_weights,
)

# ---------------------------------------------------------------------------
# Chemins
# ---------------------------------------------------------------------------

# random_gen/src/config.py -> on remonte de 2 crans pour la racine du projet.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_CARBON_DATA_DIR = PROJECT_ROOT / "data" / "output" / "random_tests" / "carbon_data"

# Permet un override sans toucher au code, ex :
#   export RANDOM_GEN_CARBON_DATA_DIR=/chemin/vers/carbon_data
ENV_OVERRIDE_VAR = "RANDOM_GEN_CARBON_DATA_DIR"

SCENARIO_COLUMN = "scenario"
CSV_GLOB_PATTERN = "*.csv"


def resolve_carbon_data_dir(carbon_data_dir: Optional[Union[str, Path]] = None) -> Path:
    """Détermine le dossier de données carbone à utiliser, par ordre de
    priorité : argument explicite > variable d'environnement > défaut."""
    if carbon_data_dir is not None:
        return Path(carbon_data_dir).expanduser().resolve()
    env_value = os.environ.get(ENV_OVERRIDE_VAR)
    if env_value:
        return Path(env_value).expanduser().resolve()
    return DEFAULT_CARBON_DATA_DIR.resolve()


def discover_scenarios(carbon_data_dir: Optional[Union[str, Path]] = None,
                        column: str = SCENARIO_COLUMN,
                        pattern: str = CSV_GLOB_PATTERN) -> List[str]:
    """
    Parcourt tous les CSV de `carbon_data_dir`, lit la colonne `column`
    et retourne la liste TRIÉE des identifiants de scénario uniques.

    Robustesse :
      - les fichiers sans la colonne attendue sont ignorés (avertissement),
        plutôt que de faire échouer tout le traitement ;
      - les valeurs vides sont ignorées ;
      - lève une erreur explicite si le dossier est introuvable ou si
        aucun scénario n'a pu être extrait.
    """
    directory = resolve_carbon_data_dir(carbon_data_dir)

    if not directory.is_dir():
        raise FileNotFoundError(
            f"Dossier de données carbone introuvable : {directory}\n"
            f"-> Vérifiez le chemin, définissez {ENV_OVERRIDE_VAR}, "
            f"ou passez --carbon-data-dir explicitement."
        )

    csv_files = sorted(directory.glob(pattern))
    if not csv_files:
        raise FileNotFoundError(f"Aucun fichier '{pattern}' trouvé dans {directory}")

    scenario_ids: Set[str] = set()
    files_without_column: List[str] = []

    for csv_path in csv_files:
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            fieldnames = reader.fieldnames or []
            if column not in fieldnames:
                files_without_column.append(csv_path.name)
                continue
            for row in reader:
                value = (row.get(column) or "").strip()
                if value:
                    scenario_ids.add(value)

    if files_without_column:
        preview = ", ".join(files_without_column[:5])
        suffix = " ..." if len(files_without_column) > 5 else ""
        print(
            f"[random_gen.config] Avertissement : colonne '{column}' absente dans "
            f"{len(files_without_column)} fichier(s) ignoré(s) : {preview}{suffix}",
            file=sys.stderr,
        )

    if not scenario_ids:
        raise ValueError(
            f"Aucun scenario_id trouvé dans la colonne '{column}' des fichiers de {directory}"
        )

    return sorted(scenario_ids)


_scenarios_cache: Optional[List[str]] = None


def get_scenarios(carbon_data_dir: Optional[Union[str, Path]] = None,
                   force_reload: bool = False) -> List[str]:
    """
    Retourne la liste des scénarios.

    Le résultat est mis en cache UNIQUEMENT pour l'emplacement par défaut
    (aucun argument) afin d'éviter de rescanner le disque inutilement.
    Un chemin explicite déclenche toujours un scan frais.
    """
    global _scenarios_cache
    if carbon_data_dir is not None:
        return discover_scenarios(carbon_data_dir)
    if force_reload or _scenarios_cache is None:
        _scenarios_cache = discover_scenarios()
    return _scenarios_cache


def __getattr__(name: str):
    """
    Permet `from random_gen.src.config import SCENARIOS_RAW` : la liste est
    calculée paresseusement, au premier accès, plutôt qu'à l'import du
    module (PEP 562).
    """
    if name == "SCENARIOS_RAW":
        return get_scenarios()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")