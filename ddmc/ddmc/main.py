from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from pathlib import Path

from .loaders import CSV, MySQL
from .pipeline import CheckpointedPipeline


@dataclass(frozen=True)
class _Config:
    db_table: str
    db_host: str
    db_database: str
    work_dir: str
    db_username: str
    db_password: str

    @classmethod
    def from_env(cls) -> _Config:
        return cls(
            os.getenv("DB_TABLE", ""),
            os.getenv("DB_HOST", ""),
            os.getenv("DB_DATABASE", ""),
            os.getenv("WORK_DIR", ""),
            os.getenv("DB_USERNAME", ""),
            os.getenv("DB_PASSWORD", ""),
        )

    def __str__(self):
        return repr(
            _Config(
                self.db_table,
                self.db_host,
                self.db_database,
                self.work_dir,
                "***",
                "***",
            )
        )


@dataclass()
class _ArgumentBag:
    loader: str = ""
    output: str = ""
    file: str = ""


def start() -> None:
    """Main entrypoint of the program."""
    parser = argparse.ArgumentParser(
        prog="Eval driving distances",
        description="Evaluate driving distances of vehicles per day.",
    )

    parser.add_argument(
        "-f",
        "--file",
        help="A file to be extracted.",
        type=str,
        required=True,
    )
    parser.add_argument("-o", "--output", help="Output path.", type=str, default="")
    parser.add_argument(
        "-l",
        "--loader",
        help="Data loader to be used.",
        type=str,
        required=False,
        default="csv",
    )

    args = _ArgumentBag()
    parser.parse_args(namespace=args)

    config = _Config.from_env()

    logging.getLogger(__name__).info(f"Startign pipeline for: {args}.")
    logging.getLogger(__name__).info(f"Using config: {config}.")

    loader: CSV | MySQL
    if args.loader == "mysql":
        logging.getLogger(__name__).info("Selected MySQL loader.")
        loader = MySQL(
            table=config.db_table,
            host_name=config.db_host,
            db_name=config.db_database,
            user=config.db_username,
            password=config.db_password,
        )
    else:
        if not args.output:
            raise ValueError("output must be provided for CSV loader.")
        logging.getLogger(__name__).info("Selected CSV loader.")
        loader = CSV(args.output)

    if (working_dir_str := config.work_dir) is None:
        raise KeyError("Work dir not defined in .env")

    work_dir = Path(working_dir_str)
    if not work_dir.exists():
        raise FileNotFoundError(f"Cant find {work_dir}")

    logging.getLogger(__name__).info(f"Processing file {args.file}.")
    pipeline = CheckpointedPipeline(file=args.file, work_dir=work_dir, loader=loader)
    pipeline.run()
    logging.getLogger(__name__).info("Done!")
