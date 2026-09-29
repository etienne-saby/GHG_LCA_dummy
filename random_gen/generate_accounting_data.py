#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
random_gen/generate_accounting_data.py

Génère, pour chaque scénario producteur (café ou cacao), un jeu de données
COMPTABLES ET COMMERCIALES crédibles mais SYNTHÉTIQUES, du point de vue d'un
trader agro-industriel (type ECOM) : prix de marché, devise, Incoterm,
financement, logistique jusqu'au FOB, marge de trading, couverture de
risque, BFR...

La liste des scénarios est déterminée automatiquement en lisant la colonne
"scenario" de tous les CSV de :
    data/output/random_tests/carbon_data/
(voir random_gen.src.config.discover_scenarios), comme pour
generate_coords.py, pour garantir un périmètre de scénarios identique.

Cohérence géographique :
    Si --geo-csv pointe vers le CSV produit par generate_coords.py, le
    pays retenu pour chaque scénario est repris de ce fichier (même
    origine -> devise, taxe export et logistique cohérentes). Sinon, un
    pays est tiré au hasard avec les pondérations de random_gen.src.countries.

AVERTISSEMENT : tous les montants, taux de change, primes qualité, taux
d'intérêt, taxes à l'export, marges de trading etc. sont des ORDRES DE
GRANDEUR ILLUSTRATIFS pour un jeu de données de démonstration. Ils ne
doivent pas être utilisés comme référence de marché réelle ou comptable.

Exécution :
    python random_gen/generate_coords.py -o coords.csv -s 42
    python random_gen/generate_accounting_data.py --geo-csv coords.csv -s 42
"""

import argparse
import csv
import random
import sys
from dataclasses import dataclass, fields, asdict
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from random_gen.src import config
from random_gen.src import market
from random_gen.src.sampling import weighted_choice, uniform_in_range
from random_gen.src.scenario_utils import detect_crop, is_roasted, scenario_suffix
from random_gen.src.countries import (
    COUNTRY_INFO,
    LANDLOCKED,
    COFFEE_VARIETY_WEIGHTS,
    country_weights_for_crop,
)


# ============================================================================
# Structure de sortie
# ============================================================================

@dataclass
class AccountingRecord:
    scenario_id: str
    crop: str
    processing_stage: str
    coffee_variety: Optional[str]
    producer_name: str
    country_iso3: str
    currency_local: str
    campaign_year: int
    contract_id: str
    contract_date: str
    delivery_date: str
    incoterm: str
    contract_type: str
    payment_terms_days: int

    volume_tons: float
    moisture_content_pct: float
    quality_grade: str
    certification: str
    certification_premium_usd_per_ton: float

    market_reference_price_usd_per_ton: float
    quality_differential_usd_per_ton: float
    purchase_price_usd_per_ton: float
    fx_rate_local_per_usd: float
    purchase_price_local_per_ton: float
    gross_purchase_value_usd: float
    gross_purchase_value_local: float

    advance_payment_pct: float
    advance_payment_usd: float
    advance_interest_rate_pct_annual: float

    inland_transport_cost_usd_per_ton: float
    warehousing_cost_usd_per_ton: float
    insurance_cost_usd_per_ton: float
    export_tax_pct: float
    export_tax_usd_per_ton: float
    fob_cost_usd_per_ton: float

    trader_margin_pct: float
    trader_margin_usd_per_ton: float
    selling_price_usd_per_ton: float
    total_contract_value_usd: float
    gross_margin_usd: float

    hedge_instrument: str
    hedge_ratio_pct: float
    counterparty_credit_rating: str

    accounts_receivable_days: int
    accounts_payable_days: int
    working_capital_usd: float

    roasting_cost_usd_per_ton: Optional[float]
    roasted_selling_price_usd_per_ton: Optional[float]


FIELDNAMES = [f.name for f in fields(AccountingRecord)]


# ============================================================================
# Tirages spécifiques
# ============================================================================

def pick_country(rng: random.Random, crop: str) -> str:
    return weighted_choice(rng, country_weights_for_crop(crop))


def pick_coffee_variety(rng: random.Random, country_iso3: str) -> str:
    weights = COFFEE_VARIETY_WEIGHTS.get(country_iso3, {"arabica": 1.0, "robusta": 0.0})
    return rng.choices(list(weights.keys()), weights=list(weights.values()), k=1)[0]


def pick_fx_rate(rng: random.Random, country_iso3: str) -> float:
    return uniform_in_range(rng, COUNTRY_INFO[country_iso3].fx_range, precision=4)


def pick_export_tax_pct(rng: random.Random, country_iso3: str) -> float:
    return uniform_in_range(rng, COUNTRY_INFO[country_iso3].export_tax_pct_range, precision=2)


def random_date_in_year(rng: random.Random, year: int) -> date:
    start = date(year, 1, 1)
    days_in_year = (date(year, 12, 31) - start).days
    return start + timedelta(days=rng.randint(0, days_in_year))


# ============================================================================
# Génération d'un enregistrement
# ============================================================================

def generate_record(scenario_id: str, rng: random.Random,
                     forced_country: Optional[str] = None) -> AccountingRecord:

    crop = detect_crop(scenario_id)
    roasted = is_roasted(scenario_id)
    country_iso3 = forced_country or pick_country(rng, crop)
    currency_local = COUNTRY_INFO[country_iso3].currency
    fx_rate = pick_fx_rate(rng, country_iso3)

    coffee_variety = pick_coffee_variety(rng, country_iso3) if crop == "coffee" else None

    # --- Campagne / contrat ---------------------------------------------
    campaign_year = weighted_choice(rng, market.CAMPAIGN_YEAR_WEIGHTS)
    contract_date = random_date_in_year(rng, campaign_year)
    delivery_date = contract_date + timedelta(days=rng.randint(30, 150))

    incoterm = weighted_choice(rng, market.INCOTERM_WEIGHTS)
    contract_type = weighted_choice(rng, market.CONTRACT_TYPE_WEIGHTS)

    if contract_type == "prepayment":
        advance_payment_pct = round(rng.uniform(30, 70), 1)
        payment_terms_days = rng.choice([0, 15, 30])
    elif contract_type == "forward":
        advance_payment_pct = round(rng.uniform(0, 30), 1) if rng.random() > 0.4 else 0.0
        payment_terms_days = rng.choice([30, 60, 90])
    else:  # spot
        advance_payment_pct = round(rng.uniform(0, 15), 1) if rng.random() > 0.6 else 0.0
        payment_terms_days = rng.choice([0, 7, 14, 30])

    advance_interest_rate_pct_annual = round(rng.uniform(6, 16), 2) if advance_payment_pct > 0 else 0.0

    contract_id = f"CTR-{crop[:3].upper()}-{scenario_suffix(scenario_id)}-{contract_date.year}"

    producer_type = weighted_choice(rng, market.PRODUCER_TYPE_WEIGHTS)
    producer_name = f"{producer_type} {country_iso3}-{scenario_suffix(scenario_id)}"

    # --- Volume et qualité -------------------------------------------------
    volume_tons = round(rng.uniform(5, 250) if crop == "cocoa" else rng.uniform(3, 180), 2)

    moisture_content_pct = (
        round(rng.uniform(6.5, 8.0), 2) if crop == "cocoa" else round(rng.uniform(9.5, 12.5), 2)
    )
    quality_grade = weighted_choice(rng, market.quality_grade_weights(crop, coffee_variety))

    certification = weighted_choice(rng, market.CERTIFICATION_WEIGHTS)
    cert_range = market.CERTIFICATION_PREMIUM_RANGES_USD_PER_TON[certification]
    certification_premium_usd_per_ton = (
        uniform_in_range(rng, cert_range, precision=2) if cert_range[1] > 0 else 0.0
    )

    # --- Prix ---------------------------------------------------------------
    price_range = (
        market.cocoa_price_range(campaign_year) if crop == "cocoa"
        else market.coffee_price_range(campaign_year, coffee_variety)
    )
    reference_price = uniform_in_range(rng, price_range, precision=2)
    quality_differential = uniform_in_range(rng, market.QUALITY_DIFFERENTIAL_RANGE_USD_PER_TON, precision=2)
    purchase_price_usd_per_ton = round(
        reference_price + quality_differential + certification_premium_usd_per_ton, 2
    )
    purchase_price_local_per_ton = round(purchase_price_usd_per_ton * fx_rate, 2)

    gross_purchase_value_usd = round(purchase_price_usd_per_ton * volume_tons, 2)
    gross_purchase_value_local = round(gross_purchase_value_usd * fx_rate, 2)
    advance_payment_usd = round(gross_purchase_value_usd * advance_payment_pct / 100, 2)

    # --- Logistique et coûts jusqu'au FOB -----------------------------------
    if country_iso3 in LANDLOCKED:
        inland_transport_cost_usd_per_ton = round(rng.uniform(60, 140), 2)
    else:
        inland_transport_cost_usd_per_ton = round(rng.uniform(15, 70), 2)

    warehousing_cost_usd_per_ton = round(rng.uniform(5, 20), 2)
    insurance_cost_usd_per_ton = round(purchase_price_usd_per_ton * rng.uniform(0.002, 0.006), 2)
    export_tax_pct = pick_export_tax_pct(rng, country_iso3)
    export_tax_usd_per_ton = round(purchase_price_usd_per_ton * export_tax_pct / 100, 2)

    fob_cost_usd_per_ton = round(
        purchase_price_usd_per_ton
        + inland_transport_cost_usd_per_ton
        + warehousing_cost_usd_per_ton
        + insurance_cost_usd_per_ton
        + export_tax_usd_per_ton,
        2,
    )

    # --- Économie du trade ---------------------------------------------------
    trader_margin_pct = round(rng.uniform(3, 9), 2)
    trader_margin_usd_per_ton = round(fob_cost_usd_per_ton * trader_margin_pct / 100, 2)
    selling_price_usd_per_ton = round(fob_cost_usd_per_ton + trader_margin_usd_per_ton, 2)

    total_contract_value_usd = round(selling_price_usd_per_ton * volume_tons, 2)
    total_logistics_cost_usd = round(
        (inland_transport_cost_usd_per_ton + warehousing_cost_usd_per_ton
         + insurance_cost_usd_per_ton + export_tax_usd_per_ton) * volume_tons,
        2,
    )
    gross_margin_usd = round(
        total_contract_value_usd - gross_purchase_value_usd - total_logistics_cost_usd, 2
    )

    # --- Gestion du risque -----------------------------------------------
    hedge_instrument = weighted_choice(rng, market.HEDGE_INSTRUMENT_WEIGHTS)
    hedge_ratio_pct = round(rng.uniform(20, 90), 1) if hedge_instrument != "none" else 0.0
    counterparty_credit_rating = weighted_choice(rng, market.CREDIT_RATING_WEIGHTS)

    # --- Créances / dettes ----------------------------------------------
    accounts_receivable_days = rng.randint(15, 60)
    accounts_payable_days = rng.randint(30, 90)
    working_capital_usd = round(
        (accounts_receivable_days - accounts_payable_days) / 365 * total_contract_value_usd, 2
    )

    # --- Extension torréfaction (si scénario *-ROASTED-*) ----------------
    if roasted:
        processing_stage = "roasted"
        roasting_cost_usd_per_ton = round(rng.uniform(400, 900), 2)
        roasting_margin_usd_per_ton = round(rng.uniform(100, 300), 2)
        roasted_selling_price_usd_per_ton = round(
            selling_price_usd_per_ton + roasting_cost_usd_per_ton + roasting_margin_usd_per_ton, 2
        )
    else:
        processing_stage = "green/dry beans"
        roasting_cost_usd_per_ton = None
        roasted_selling_price_usd_per_ton = None

    return AccountingRecord(
        scenario_id=scenario_id,
        crop=crop,
        processing_stage=processing_stage,
        coffee_variety=coffee_variety,
        producer_name=producer_name,
        country_iso3=country_iso3,
        currency_local=currency_local,
        campaign_year=campaign_year,
        contract_id=contract_id,
        contract_date=contract_date.isoformat(),
        delivery_date=delivery_date.isoformat(),
        incoterm=incoterm,
        contract_type=contract_type,
        payment_terms_days=payment_terms_days,
        volume_tons=volume_tons,
        moisture_content_pct=moisture_content_pct,
        quality_grade=quality_grade,
        certification=certification,
        certification_premium_usd_per_ton=certification_premium_usd_per_ton,
        market_reference_price_usd_per_ton=reference_price,
        quality_differential_usd_per_ton=quality_differential,
        purchase_price_usd_per_ton=purchase_price_usd_per_ton,
        fx_rate_local_per_usd=fx_rate,
        purchase_price_local_per_ton=purchase_price_local_per_ton,
        gross_purchase_value_usd=gross_purchase_value_usd,
        gross_purchase_value_local=gross_purchase_value_local,
        advance_payment_pct=advance_payment_pct,
        advance_payment_usd=advance_payment_usd,
        advance_interest_rate_pct_annual=advance_interest_rate_pct_annual,
        inland_transport_cost_usd_per_ton=inland_transport_cost_usd_per_ton,
        warehousing_cost_usd_per_ton=warehousing_cost_usd_per_ton,
        insurance_cost_usd_per_ton=insurance_cost_usd_per_ton,
        export_tax_pct=export_tax_pct,
        export_tax_usd_per_ton=export_tax_usd_per_ton,
        fob_cost_usd_per_ton=fob_cost_usd_per_ton,
        trader_margin_pct=trader_margin_pct,
        trader_margin_usd_per_ton=trader_margin_usd_per_ton,
        selling_price_usd_per_ton=selling_price_usd_per_ton,
        total_contract_value_usd=total_contract_value_usd,
        gross_margin_usd=gross_margin_usd,
        hedge_instrument=hedge_instrument,
        hedge_ratio_pct=hedge_ratio_pct,
        counterparty_credit_rating=counterparty_credit_rating,
        accounts_receivable_days=accounts_receivable_days,
        accounts_payable_days=accounts_payable_days,
        working_capital_usd=working_capital_usd,
        roasting_cost_usd_per_ton=roasting_cost_usd_per_ton,
        roasted_selling_price_usd_per_ton=roasted_selling_price_usd_per_ton,
    )


# ============================================================================
# Chargement des entrées
# ============================================================================

def load_scenarios_from_txt(path: Path) -> List[str]:
    return [l.strip() for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def load_geo_mapping(path: Path) -> Dict[str, str]:
    """Lit le CSV produit par generate_coords.py et retourne
    {scenario_id: country_iso3}."""
    mapping: Dict[str, str] = {}
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            mapping[row["scenario_id"]] = row["country_iso3"]
    return mapping


# ============================================================================
# Point d'entrée
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Génère des données comptables/commerciales synthétiques "
                    "pour des scénarios producteurs café/cacao (vision trader agro)."
    )
    parser.add_argument("-i", "--input", type=Path, default=None,
                         help="Fichier texte avec un scenario_id par ligne. "
                              "Par défaut, la liste est découverte automatiquement "
                              "depuis les CSV carbone (voir --carbon-data-dir).")
    parser.add_argument("--carbon-data-dir", type=Path, default=None,
                         help="Dossier contenant les CSV carbone (colonne 'scenario'), "
                              f"utilisé si --input n'est pas fourni. Défaut : "
                              f"{config.DEFAULT_CARBON_DATA_DIR}")
    parser.add_argument("-g", "--geo-csv", type=Path, default=None,
                         help="CSV produit par generate_coords.py (scenario_id, "
                              "country_iso3, ...) pour garder la même origine "
                              "géographique par scénario.")
    parser.add_argument("-o", "--output", default="scenarios_accounting.csv",
                         help="Fichier CSV de sortie.")
    parser.add_argument("-s", "--seed", type=int, default=None,
                         help="Graine aléatoire pour des résultats reproductibles.")
    args = parser.parse_args()

    geo_map: Dict[str, str] = {}
    if args.geo_csv:
        geo_map = load_geo_mapping(args.geo_csv)

    if args.input:
        scenarios = load_scenarios_from_txt(args.input)
    else:
        scenarios = config.discover_scenarios(args.carbon_data_dir)

    rng = random.Random(args.seed)

    rows = []
    for scenario_id in scenarios:
        forced_country = geo_map.get(scenario_id)
        record = generate_record(scenario_id, rng, forced_country=forced_country)
        rows.append(asdict(record))

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} scénarios traités -> {args.output}")


if __name__ == "__main__":
    main()