"""Тести очищують тільки окремі навчальні бази weather_test."""
import csv
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import MetaData, Table, select

from weather import repository, services
from weather.database import engine

ROOT = Path(__file__).resolve().parent.parent
URLS = [
    "postgresql+psycopg://weather:local_weather@127.0.0.1:55432/weather_test",
    "mysql+pymysql://weather:local_weather@127.0.0.1:3306/weather_test",
]


def dataset_count():
    with (ROOT / "data/GlobalWeatherRepository.csv").open(encoding="utf-8-sig", newline="") as file:
        return sum(1 for _ in csv.DictReader(file))


def reset(db):
    # Лише тестова база. Відновлює навіть частково перервану MySQL-міграцію.
    if db.url.database != "weather_test":
        raise ValueError("Очищення дозволене лише для weather_test")
    with db.begin() as connection:
        metadata = MetaData()
        metadata.reflect(bind=connection)
        metadata.drop_all(bind=connection)


def migrate(db, revision, down=False):
    config = Config(str(ROOT / "alembic.ini"))
    config.attributes["database_url"] = db.url
    if down:
        command.downgrade(config, revision)
    else:
        command.upgrade(config, revision)


def flat_rows(db):
    table = Table("weather", MetaData(), autoload_with=db)
    with db.connect() as connection:
        return [dict(row) for row in connection.execute(
            select(table).order_by(table.c.id)
        ).mappings()]


@pytest.mark.parametrize("url", URLS, ids=["postgres", "mysql"])
def test_import_migrations_and_rollback(url):
    db = engine(url)
    try:
        reset(db)
        migrate(db, "001")
        assert services.import_csv(db, ROOT / "data/GlobalWeatherRepository.csv", initial=True) == dataset_count()
        before = flat_rows(db)
        migrate(db, "head")
        first = before[0]
        rows = repository.find(db, first["country"], first["last_updated"].date())
        assert rows
        for weather, wind, air in rows:
            assert wind.go_outside == services.wind_is_safe(wind.wind_kph, wind.gust_kph)
            assert air.go_outside == services.air_is_safe(air.us_epa_index, air.gb_defra_index)
        migrate(db, "001", down=True)
        assert flat_rows(db) == before
        reset(db)
        migrate(db, "head")
        assert services.import_csv(db, ROOT / "data/GlobalWeatherRepository.csv") == dataset_count()
        with pytest.raises(ValueError, match="порожню"):
            services.import_csv(db, ROOT / "data/GlobalWeatherRepository.csv")
    finally:
        reset(db)
        db.dispose()


def test_transfer_both_directions():
    postgres, mysql = [engine(url) for url in URLS]
    try:
        for db in [postgres, mysql]:
            reset(db)
            migrate(db, "head")
        services.import_csv(postgres, ROOT / "data/GlobalWeatherRepository.csv")
        assert repository.copy(postgres, mysql) == dataset_count()
        assert repository.read_tables(postgres) == repository.read_tables(mysql)
        with pytest.raises(ValueError):
            repository.copy(postgres, mysql)
        reset(postgres)
        migrate(postgres, "head")
        assert repository.copy(mysql, postgres) == dataset_count()
        assert repository.read_tables(postgres) == repository.read_tables(mysql)
    finally:
        for db in [postgres, mysql]:
            reset(db)
            db.dispose()


def test_rules():
    assert services.wind_is_safe(36, 50)
    assert not services.wind_is_safe(37, 50)
    assert not services.wind_is_safe(36, 51)
    assert services.air_is_safe(2, 3)
    assert not services.air_is_safe(3, 3)
    assert not services.air_is_safe(2, 4)


def test_dataset_headers():
    with (ROOT / "data/GlobalWeatherRepository.csv").open(encoding="utf-8-sig", newline="") as file:
        row = next(csv.DictReader(file))
    weather, wind, air = services.parse(row)
    assert weather["country"] == row["country"].strip()
    assert wind["wind_kph"] == float(row["wind_kph"])
    assert air["pm2_5"] == float(row["air_quality_PM2.5"])


def test_reset_after_interrupted_mysql_migration():
    db = engine(URLS[1])
    try:
        reset(db)
        migrate(db, "head")
        migrate(db, "003", down=True)
        # Імітуємо переривання після ADD COLUMN, до завершення downgrade.
        with db.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE weather ADD COLUMN air_quality_carbon_monoxide DOUBLE"
            )
        reset(db)
        migrate(db, "head")
        assert repository.read_tables(db) == [[], [], []]
    finally:
        reset(db)
        db.dispose()
