"""Створити wind, скопіювати дані, потім прибрати старі колонки."""
from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
FIELDS = ["wind_mph", "wind_kph", "wind_degree", "wind_direction", "gust_mph", "gust_kph"]


def upgrade():
    op.create_table(
        "wind",
        sa.Column("weather_id", sa.Integer, sa.ForeignKey("weather.id"), primary_key=True),
        sa.Column("wind_mph", sa.Double, nullable=False),
        sa.Column("wind_kph", sa.Double, nullable=False),
        sa.Column("wind_degree", sa.Integer, nullable=False),
        sa.Column(
            "wind_direction",
            sa.Enum(
                "N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
                "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW",
                native_enum=False, length=3, create_constraint=True,
                name="wind_direction",
            ),
            nullable=False,
        ),
        sa.Column("gust_mph", sa.Double, nullable=False),
        sa.Column("gust_kph", sa.Double, nullable=False),
    )
    # Спочатку копіюємо значення, тільки потім прибираємо старі колонки.
    columns = ", ".join(FIELDS)
    op.execute(sa.text(f"INSERT INTO wind (weather_id, {columns}) SELECT id, {columns} FROM weather"))
    for name in FIELDS:
        op.drop_column("weather", name)


def downgrade():
    types = [sa.Double(), sa.Double(), sa.Integer(), sa.String(3), sa.Double(), sa.Double()]
    for name, column_type in zip(FIELDS, types):
        op.add_column("weather", sa.Column(name, column_type, nullable=True))
        op.execute(sa.text(f"UPDATE weather SET {name} = (SELECT {name} FROM wind WHERE wind.weather_id = weather.id)"))
        op.alter_column("weather", name, existing_type=column_type, nullable=False)
    op.drop_table("wind")
