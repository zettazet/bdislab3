import os

from sqlalchemy import create_engine


def database_url():
    return os.environ.get(
        "DATABASE_URL",
        "postgresql+psycopg://weather:local_weather@127.0.0.1:55432/weather",
    )


def engine(url=None):
    return create_engine(url or database_url(), pool_pre_ping=True)
