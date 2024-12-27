"""Module to host the API serving classes."""

from __future__ import annotations

import os
from dataclasses import dataclass

from flask import Flask, Response, jsonify, request  # type: ignore[import-not-found]

from .repositories import DrivenDistanceRepository
from .validator import GetDrivingDistancesRequest


@dataclass(frozen=True)
class _Config:
    db_host: str
    db_database: str
    db_username: str
    db_password: str

    @classmethod
    def from_env(cls) -> _Config:
        return cls(
            os.getenv("DB_HOST", ""),
            os.getenv("DB_DATABASE", ""),
            os.getenv("DB_USERNAME", ""),
            os.getenv("DB_PASSWORD", ""),
        )


def create_service() -> Flask:
    """Creates the REST API service."""
    service = Flask(__name__)

    config = _Config.from_env()
    repository = DrivenDistanceRepository(
        host_name=config.db_host,
        db_name=config.db_database,
        user=config.db_username,
        password=config.db_password,
    )

    @service.route("/", methods=["GET"])
    @service.route("/api", methods=["GET"])
    def index() -> Response:
        return jsonify("It Works!")

    @service.route("/api/driving-distances", methods=["GET"])
    def get_driving_distances() -> Response:
        try:
            return jsonify(
                repository.get_driving_distances(
                    GetDrivingDistancesRequest(
                        vehicle_id=request.args.get("vehicle_id", default="", type=str),
                        start_date=request.args.get("start_date", default=None),
                        end_date=request.args.get("end_date", default=None),
                    )
                )
            )
        except Exception as e:
            return jsonify({"error": str(e)})

    return service


def start() -> None:
    create_service().run()
