"""Початкова таблиця: погода і всі показники вітру разом."""
from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None


def upgrade():
    op.create_table(
        "weather",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=False),
        sa.Column("country", sa.String(100), nullable=False),
        sa.Column("location_name", sa.String(150), nullable=False),
        sa.Column("last_updated", sa.DateTime, nullable=False),
        sa.Column("sunrise", sa.Time, nullable=False),
        sa.Column("wind_mph", sa.Double, nullable=False),
        sa.Column("wind_kph", sa.Double, nullable=False),
        sa.Column("wind_degree", sa.Integer, nullable=False),
        sa.Column("wind_direction", sa.String(3), nullable=False),
        sa.Column("gust_mph", sa.Double, nullable=False),
        sa.Column("gust_kph", sa.Double, nullable=False),
        sa.Column("air_quality_carbon_monoxide", sa.Double, nullable=False),
        sa.Column("air_quality_ozone", sa.Double, nullable=False),
        sa.Column("air_quality_nitrogen_dioxide", sa.Double, nullable=False),
        sa.Column("air_quality_sulphur_dioxide", sa.Double, nullable=False),
        sa.Column("air_quality_pm2_5", sa.Double, nullable=False),
        sa.Column("air_quality_pm10", sa.Double, nullable=False),
        sa.Column("air_quality_us_epa_index", sa.Integer, nullable=False),
        sa.Column("air_quality_gb_defra_index", sa.Integer, nullable=False),
    )


def downgrade():
    op.drop_table("weather")
