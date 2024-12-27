from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path

import osmnx as ox

from .loaders import CSV, MySQL
from .pipeline import CheckpointedPipeline


@dataclass(frozen=True)
class _Config:
    db_table: str
    db_host: str
    db_database: str
    db_username: str
    db_password: str
    work_dir: str

    @classmethod
    def from_env(cls) -> _Config:
        return cls(
            os.getenv("DB_TABLE", ""),
            os.getenv("DB_HOST", ""),
            os.getenv("DB_DATABASE", ""),
            os.getenv("DB_USERNAME", ""),
            os.getenv("DB_PASSWORD", ""),
            os.getenv("WORK_DIR", ""),
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
    parser.add_argument("-o", "--output", help="Output path.", type=str, required=True)
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

    loader: CSV | MySQL
    if args.loader == "mysql":
        loader = MySQL(
            table=config.db_table,
            host_name=config.db_host,
            db_name=config.db_database,
            user=config.db_username,
            password=config.db_password,
        )
    else:
        loader = CSV(args.output)

    if (working_dir_str := config.work_dir) is None:
        raise KeyError("Work dir not defined in .env")

    work_dir = Path(working_dir_str)
    if not work_dir.exists():
        raise FileNotFoundError(f"Cant find {work_dir}")

    pipeline = CheckpointedPipeline(file=args.file, work_dir=work_dir, loader=loader)
    pipeline.run()
