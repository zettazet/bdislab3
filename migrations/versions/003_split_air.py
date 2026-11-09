"""Винести всі показники якості повітря без втрати даних."""
from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
FIELDS = [
    "carbon_monoxide", "ozone", "nitrogen_dioxide", "sulphur_dioxide",
    "pm2_5", "pm10", "us_epa_index", "gb_defra_index",
]


def upgrade():
    op.create_table(
        "air_quality",
        sa.Column("weather_id", sa.Integer, sa.ForeignKey("weather.id"), primary_key=True),
        *[sa.Column(name, sa.Integer if name.endswith("index") else sa.Double, nullable=False) for name in FIELDS],
    )
    # У старій таблиці назви мають префікс air_quality_.
    columns = ", ".join(FIELDS)
    old_columns = ", ".join("air_quality_" + name for name in FIELDS)
    op.execute(sa.text(f"INSERT INTO air_quality (weather_id, {columns}) SELECT id, {old_columns} FROM weather"))
    for name in FIELDS:
        op.drop_column("weather", "air_quality_" + name)


def downgrade():
    for name in FIELDS:
        column_type = sa.Integer() if name.endswith("index") else sa.Double()
        old_name = "air_quality_" + name
        op.add_column("weather", sa.Column(old_name, column_type, nullable=True))
        op.execute(sa.text(f"UPDATE weather SET {old_name} = (SELECT {name} FROM air_quality WHERE weather_id = weather.id)"))
        op.alter_column("weather", old_name, existing_type=column_type, nullable=False)
    op.drop_table("air_quality")
