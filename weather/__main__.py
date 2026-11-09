"""Консольний імпорт погодного CSV."""
import argparse
from sqlalchemy.exc import SQLAlchemyError
from weather import services
from weather.database import engine


def main():
    parser = argparse.ArgumentParser(description="Імпорт погодного CSV")
    commands = parser.add_subparsers(dest="command", required=True)
    importer = commands.add_parser("import-csv")
    importer.add_argument("path", nargs="?", default="data/GlobalWeatherRepository.csv")
    importer.add_argument("--initial", action="store_true", help="Імпорт у схему 001")
    args = parser.parse_args()
    db = engine()
    try:
        print("Додано спостережень:", services.import_csv(db, args.path, args.initial))
    except (ValueError, OSError, SQLAlchemyError) as error:
        parser.exit(1, f"Помилка: {error}\n")
    finally:
        db.dispose()


if __name__ == "__main__":
    main()
