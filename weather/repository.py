"""Шар даних: збереження, пошук і копіювання таблиць."""
from datetime import datetime, timedelta
from itertools import islice

from sqlalchemy import MetaData, Table, func, select
from sqlalchemy.orm import Session

from weather.models import AirQuality, Weather, Wind

TABLES = [Weather.__table__, Wind.__table__, AirQuality.__table__]


def save(db, rows, initial=False):
    # Початкова таблиця потрібна тільки для демонстрації міграції 001 -> 004.
    old_table = None
    if initial:
        old_table = Table("weather", MetaData(), autoload_with=db)

    with db.begin() as connection:
        if connection.scalar(select(func.count()).select_from(Weather)):
            raise ValueError("Імпорт виконується лише в порожню базу")
        next_id = 1
        count = 0
        rows = iter(rows)
        while batch := list(islice(rows, 1000)):
            weather_rows, wind_rows, air_rows = [], [], []
            for weather, wind, air in batch:
                weather["id"] = next_id
                if initial:
                    weather.update({name: value for name, value in wind.items()
                                    if name != "go_outside"})
                    weather.update({"air_quality_" + name: value for name, value in air.items()
                                    if name != "go_outside"})
                else:
                    wind_rows.append({"weather_id": next_id, **wind})
                    air_rows.append({"weather_id": next_id, **air})
                weather_rows.append(weather)
                next_id += 1
            # Пакети по 1000 рядків, але одна транзакція на весь CSV.
            connection.execute((old_table if initial else TABLES[0]).insert(), weather_rows)
            if not initial:
                connection.execute(TABLES[1].insert(), wind_rows)
                connection.execute(TABLES[2].insert(), air_rows)
            count += len(batch)
    return count


def find(db, country, day):
    start = datetime.combine(day, datetime.min.time())
    query = (
        select(Weather, Wind, AirQuality)
        .join(Wind, Weather.id == Wind.weather_id)
        .join(AirQuality, Weather.id == AirQuality.weather_id)
        .where(Weather.country == country,
               Weather.last_updated >= start,
               Weather.last_updated < start + timedelta(days=1))
        .order_by(Weather.id)
    )
    with Session(db) as session:
        return session.execute(query).all()




