"""Сервісний шар: перетворення CSV та дві формули оцінювання."""
import csv
import math
from datetime import datetime

from weather import repository
from weather.models import DIRECTIONS


def wind_is_safe(speed, gust):
    return speed <= 36 and gust <= 50


def air_is_safe(epa, defra):
    return epa <= 2 and defra <= 3


def number(row, name, integer=False, nonnegative=True):
    value = int(row[name]) if integer else float(row[name])
    if not math.isfinite(value) or (nonnegative and value < 0):
        raise ValueError(f"Некоректне число: {name}")
    return value


def parse(row):
    # Наприклад: air_quality_PM2.5 -> air_quality_pm2_5.
    row = {name.strip().lower().replace("-", "_").replace(".", "_"): value
           for name, value in row.items() if name is not None}
    weather = {
        "country": row["country"].strip(),
        "location_name": row["location_name"].strip(),
        "last_updated": datetime.fromisoformat(row["last_updated"]),
        "sunrise": datetime.strptime(row["sunrise"].strip(), "%I:%M %p").time(),
    }
    if not weather["country"] or not weather["location_name"]:
        raise ValueError("Країна і місто не можуть бути порожніми")
    if weather["last_updated"].tzinfo is not None:
        raise ValueError("Очікується місцевий час без часового поясу")

    wind = {
        "wind_mph": number(row, "wind_mph"),
        "wind_kph": number(row, "wind_kph"),
        "wind_degree": number(row, "wind_degree", integer=True),
        "wind_direction": row["wind_direction"].strip(),
        "gust_mph": number(row, "gust_mph"),
        "gust_kph": number(row, "gust_kph"),
    }
    if wind["wind_direction"] not in DIRECTIONS or wind["wind_degree"] > 360:
        raise ValueError("Некоректний напрям вітру")
    air = {}
    for name in ["carbon_monoxide", "ozone", "nitrogen_dioxide",
                 "sulphur_dioxide", "pm2_5", "pm10"]:
        air[name] = number(row, "air_quality_" + name, nonnegative=False)
    air["us_epa_index"] = number(row, "air_quality_us_epa_index", integer=True)
    air["gb_defra_index"] = number(row, "air_quality_gb_defra_index", integer=True)
    if not 1 <= air["us_epa_index"] <= 6 or not 1 <= air["gb_defra_index"] <= 10:
        raise ValueError("Індекс EPA має бути 1–6, DEFRA — 1–10")
    wind["go_outside"] = wind_is_safe(wind["wind_kph"], wind["gust_kph"])
    air["go_outside"] = air_is_safe(air["us_epa_index"], air["gb_defra_index"])
    return weather, wind, air


def import_csv(db, path, initial=False):
    def rows():
        with open(path, encoding="utf-8-sig", newline="") as file:
            for line, row in enumerate(csv.DictReader(file), start=2):
                try:
                    yield parse(row)
                except (ValueError, KeyError, TypeError) as error:
                    raise ValueError(f"Рядок CSV {line}: {error}") from error
    return repository.save(db, rows(), initial)
