#!/usr/bin/env python3
"""Build a district-level research dataset from downloaded NSO tables."""

from __future__ import annotations

import csv
import math
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "nsonepal"
PROCESSED = ROOT / "data" / "processed"
OUTPUT = PROCESSED / "district_research_dataset.csv"


def norm(text: str) -> str:
    text = text.strip().lower().replace("_", " ")
    text = re.sub(r"[^a-z0-9 ]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


DISPLAY_FIXES = {
    norm("Manag"): "Manang",
    norm("Sirah"): "Siraha",
    norm("Terhthum"): "Terhathum",
    norm("Kavreplanchok"): "Kavrepalanchok",
    norm("Ramechap"): "Ramechhap",
    norm("Dailekha"): "Dailekh",
    norm("Kapilbastu"): "Kapilvastu",
}


def to_number(value: str) -> float | None:
    value = value.strip().replace(",", "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def safe_div(numerator: float | None, denominator: float | None) -> float | None:
    if numerator is None or denominator in (None, 0):
        return None
    return numerator / denominator


def format_number(value: float | None) -> str:
    if value is None:
        return ""
    if math.isfinite(value) and float(value).is_integer():
        return str(int(value))
    return f"{value:.6f}".rstrip("0").rstrip(".")


def load_long_table(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def build_canonical_districts() -> dict[str, str]:
    rows = load_long_table(RAW / "table_03_parcels_by_district.csv")
    canonical = {}
    for row in rows:
        district = row["Districts"].strip()
        district = DISPLAY_FIXES.get(norm(district), district)
        canonical[norm(district)] = district
    return canonical


CANONICAL = build_canonical_districts()
ALIASES = {
    norm("Manag"): "Manang",
    norm("Manang"): "Manang",
    norm("Sirah"): "Siraha",
    norm("Siraha"): "Siraha",
    norm("Terhthum"): "Terhathum",
    norm("Terhathum"): "Terhathum",
    norm("Kavreplanchok"): "Kavrepalanchok",
    norm("Kabhrepalanchok"): "Kavrepalanchok",
    norm("Ramechap"): "Ramechhap",
    norm("Ramechhap"): "Ramechhap",
    norm("Chitawan"): "Chitwan",
    norm("Chitwan"): "Chitwan",
    norm("Dailekha"): "Dailekh",
    norm("Dailekh"): "Dailekh",
    norm("Kapilbastu"): "Kapilvastu",
    norm("Kapilvastu"): "Kapilvastu",
    norm("Nawalparasi_E"): "Nawalparasi East",
    norm("Nawalparasi East"): "Nawalparasi East",
    norm("Nawalparasi_W"): "Nawalparasi West",
    norm("Nawalparasi West"): "Nawalparasi West",
    norm("Rukum_E"): "Rukum East",
    norm("Rukum East"): "Rukum East",
    norm("Rukum_W"): "Rukum West",
    norm("Rukum West"): "Rukum West",
}


def canonical_district(name: str) -> str:
    key = norm(name)
    if key in ALIASES:
        return ALIASES[key]
    if key in CANONICAL:
        return CANONICAL[key]
    raise KeyError(f"Unknown district label: {name!r}")


def load_wide_table(path: Path) -> dict[str, dict[str, float | None]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    header = [canonical_district(x) for x in rows[0][1:]]
    table: dict[str, dict[str, float | None]] = {}
    for row in rows[1:]:
        label = row[0].strip()
        values = {}
        for i, district in enumerate(header, start=1):
            values[district] = to_number(row[i] if i < len(row) else "")
        table[label] = values
    return table


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)

    parcels_rows = load_long_table(RAW / "table_03_parcels_by_district.csv")
    irrigation_rows = load_long_table(RAW / "table_04_1_irrigation_by_source.csv")

    loan = load_wide_table(RAW / "table_17_agricultural_loan.csv")
    subsidy = load_wide_table(RAW / "table_19_government_subsidy.csv")
    implements = load_wide_table(RAW / "table_14_implements_and_facilities.csv")
    climate = load_wide_table(RAW / "table_22_climate_impact.csv")
    income = load_wide_table(RAW / "table_35_income_and_sufficiency.csv")
    insuff = load_wide_table(RAW / "table_36_2_food_insufficiency_period.csv")
    market = load_wide_table(RAW / "table_38_1_market_access.csv")

    dataset: dict[str, dict[str, float | str | None]] = {}

    for row in parcels_rows:
        district = canonical_district(row["Districts"])
        total_holdings = to_number(row["Total holdings"])
        total_area = to_number(row["Total Area (ha)"])
        total_parcels = to_number(row["Total no. of parcels"])
        avg_parcels = to_number(row["Average no. of parcels"])
        dataset[district] = {
            "district": district,
            "total_holdings": total_holdings,
            "total_area_ha": total_area,
            "total_parcels": total_parcels,
            "avg_parcels_per_holding": avg_parcels,
        }

    for row in irrigation_rows:
        district = canonical_district(row["Districts"])
        entry = dataset[district]
        irrig_holdings = to_number(row["No. of holdings reporting irrigation"])
        irrig_area = to_number(row["Total area (ha) of irrigation"])
        entry["irrigated_holdings"] = irrig_holdings
        entry["irrigated_area_ha"] = irrig_area
        entry["irrigated_holdings_share"] = safe_div(irrig_holdings, entry["total_holdings"])  # type: ignore[arg-type]
        entry["irrigation_area_share"] = safe_div(irrig_area, entry["total_area_ha"])  # type: ignore[arg-type]

    row_specs = {
        "agriculture_main_income": (
            income,
            "Total number of household where agriculture is the main source of income",
        ),
        "agriculture_sufficient": (
            income,
            "Total number of households for which agricultural product were sufficient for household consumption",
        ),
        "agriculture_insufficient": (
            income,
            "Total number of households for which agricultural product were insufficient for household consumption",
        ),
        "loan_holdings": (
            loan,
            "Total number of holdings with agricultural loan",
        ),
        "subsidy_holdings": (
            subsidy,
            "Total number of holdings received government subsidy",
        ),
        "power_tiller_holdings": (
            implements,
            "Total number of holdings that use power tillers",
        ),
        "climate_impact_holdings": (
            climate,
            "Total number of holdings reporting impact on agriculture due to climate change",
        ),
        "insuff_10_12_months": (
            insuff,
            "Total number of holdings reporting insufficiency of their own produce for household consumption for 10 to 12 months",
        ),
        "market_next_household": (
            market,
            "Total number of holdings with an agricultural market next to their household",
        ),
        "market_foot_under_30": (
            market,
            "Total number of holdings that can reach the nearest agricultural market on foot in under 30 minutes",
        ),
    }

    for column, (table, label) in row_specs.items():
        values = table[label]
        for district, value in values.items():
            dataset[district][column] = value

    for district, entry in dataset.items():
        total_holdings = entry["total_holdings"]  # type: ignore[assignment]
        market_fast = None
        if entry.get("market_next_household") is not None or entry.get("market_foot_under_30") is not None:
            market_fast = (entry.get("market_next_household") or 0) + (entry.get("market_foot_under_30") or 0)

        entry["ag_main_income_share"] = safe_div(entry.get("agriculture_main_income"), total_holdings)  # type: ignore[arg-type]
        entry["ag_sufficiency_share"] = safe_div(entry.get("agriculture_sufficient"), total_holdings)  # type: ignore[arg-type]
        entry["ag_insufficiency_share"] = safe_div(entry.get("agriculture_insufficient"), total_holdings)  # type: ignore[arg-type]
        entry["loan_share"] = safe_div(entry.get("loan_holdings"), total_holdings)  # type: ignore[arg-type]
        entry["subsidy_share"] = safe_div(entry.get("subsidy_holdings"), total_holdings)  # type: ignore[arg-type]
        entry["power_tiller_share"] = safe_div(entry.get("power_tiller_holdings"), total_holdings)  # type: ignore[arg-type]
        entry["climate_impact_share"] = safe_div(entry.get("climate_impact_holdings"), total_holdings)  # type: ignore[arg-type]
        entry["severe_insuff_10_12_share"] = safe_div(entry.get("insuff_10_12_months"), total_holdings)  # type: ignore[arg-type]
        entry["market_access_fast_share"] = safe_div(market_fast, total_holdings)  # type: ignore[arg-type]

    fieldnames = [
        "district",
        "total_holdings",
        "total_area_ha",
        "total_parcels",
        "avg_parcels_per_holding",
        "irrigated_holdings",
        "irrigated_area_ha",
        "irrigated_holdings_share",
        "irrigation_area_share",
        "agriculture_main_income",
        "ag_main_income_share",
        "agriculture_sufficient",
        "ag_sufficiency_share",
        "agriculture_insufficient",
        "ag_insufficiency_share",
        "loan_holdings",
        "loan_share",
        "subsidy_holdings",
        "subsidy_share",
        "power_tiller_holdings",
        "power_tiller_share",
        "climate_impact_holdings",
        "climate_impact_share",
        "insuff_10_12_months",
        "severe_insuff_10_12_share",
        "market_next_household",
        "market_foot_under_30",
        "market_access_fast_share",
    ]

    with OUTPUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for district in sorted(dataset):
            row = {key: format_number(dataset[district].get(key)) if key != "district" else dataset[district][key] for key in fieldnames}
            writer.writerow(row)

    print(f"Wrote {len(dataset)} districts to {OUTPUT}")


if __name__ == "__main__":
    main()
