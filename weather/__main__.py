"""Консольний шар. Міграції запускаються окремо через Alembic."""
import argparse
import json
from datetime import date

from sqlalchemy.exc import SQLAlchemyError

from weather import repository, services
from weather.database import engine


def main():
    parser = argparse.ArgumentParser(description="Погода: вітер та якість повітря")
    commands = parser.add_subparsers(dest="command", required=True)
    importer = commands.add_parser("import-csv")
    importer.add_argument("path", nargs="?", default="data/GlobalWeatherRepository.csv")
    importer.add_argument("--initial", action="store_true", help="Імпорт у схему 001")
    show = commands.add_parser("show")
    show.add_argument("country")
    show.add_argument("day", type=date.fromisoformat)
    transfer = commands.add_parser("transfer")
    transfer.add_argument("target", help="URL порожньої БД зі схемою 004")
    args = parser.parse_args()
    db = engine()
    try:
        if args.command == "import-csv":
            print("Додано спостережень:", services.import_csv(db, args.path, args.initial))
        elif args.command == "show":
            output = []
            for weather, wind, air in repository.find(db, args.country, args.day):
                row = {}
                for name, obj in [("weather", weather), ("wind", wind), ("air", air)]:
                    row[name] = {column.name: getattr(obj, column.name)
                                 for column in obj.__table__.columns}
                row["go_outside"] = wind.go_outside and air.go_outside
                output.append(row)
            print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
        else:
            target = engine(args.target)
            try:
                print("Перенесено спостережень:", repository.copy(db, target))
            finally:
                target.dispose()
    except (ValueError, OSError, SQLAlchemyError) as error:
        parser.exit(1, f"Помилка: {error}\n")
    finally:
        db.dispose()


if __name__ == "__main__":
    main()
