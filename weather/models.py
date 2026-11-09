"""Три таблиці фінальної схеми погодної бази."""
from sqlalchemy import Boolean, Column, DateTime, Enum, Double, ForeignKey, Integer, String, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()

DIRECTIONS = ("N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
              "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW")


class Weather(Base):
    __tablename__ = "weather"

    id = Column(Integer, primary_key=True, autoincrement=False)
    country = Column(String(100), nullable=False)
    location_name = Column(String(150), nullable=False)
    last_updated = Column(DateTime, nullable=False)
    sunrise = Column(Time, nullable=False)


class Wind(Base):
    __tablename__ = "wind"

    weather_id = Column(Integer, ForeignKey("weather.id"), primary_key=True)
    wind_mph = Column(Double, nullable=False)
    wind_kph = Column(Double, nullable=False)
    wind_degree = Column(Integer, nullable=False)
    wind_direction = Column(
        Enum(*DIRECTIONS, native_enum=False, create_constraint=True,
             name="wind_direction", length=3), nullable=False,
    )
    gust_mph = Column(Double, nullable=False)
    gust_kph = Column(Double, nullable=False)
    go_outside = Column(Boolean, nullable=False)


class AirQuality(Base):
    __tablename__ = "air_quality"

    weather_id = Column(Integer, ForeignKey("weather.id"), primary_key=True)
    carbon_monoxide = Column(Double, nullable=False)
    ozone = Column(Double, nullable=False)
    nitrogen_dioxide = Column(Double, nullable=False)
    sulphur_dioxide = Column(Double, nullable=False)
    pm2_5 = Column(Double, nullable=False)
    pm10 = Column(Double, nullable=False)
    us_epa_index = Column(Integer, nullable=False)
    gb_defra_index = Column(Integer, nullable=False)
    go_outside = Column(Boolean, nullable=False)
