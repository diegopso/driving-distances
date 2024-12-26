import csv
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pandas as pd

from .extractors import CSV
from .extractors import OSM as OSMExtractor
from .loaders import Loader
from .transformers import OSM as OSMTransformer
from .transformers import TripSegments


@dataclass
class _Step:
    run: Callable
    checkpoint: bool

    @property
    def name(self):
        return self.run.__name__


class Pipeline:
    def __init__(
        self,
        place: str,
        file: str | Path,
        working_dir: str | Path,
        loader: Loader,
        silent: bool = False,
    ) -> None:
        self._file = file
        self._place = place
        self._working_dir = working_dir
        self._silent = silent

        self._loader = loader

        self._data: pd.DataFrame | None = None
        self._current_step = 0
        self._steps = [
            _Step(run=self.extract_csv, checkpoint=False),
            _Step(run=self.extract_graph, checkpoint=False),
            _Step(
                run=self.transform_coords_to_nodes,
                checkpoint=True,
            ),
            _Step(
                run=self.identify_trip_segments,
                checkpoint=True,
            ),
            _Step(
                run=self.eval_driving_distances,
                checkpoint=True,
            ),
            _Step(run=self.load, checkpoint=False),
        ]

    @property
    def data(self):
        if self._data is None:
            raise RuntimeError("You must load the data before working with it.")
        return self._data

    def extract_csv(self) -> None:
        extractor = CSV()
        self._data = extractor.extract(self._file)

    def extract_graph(self) -> None:
        extractor = OSMExtractor(str(self._working_dir))
        G = extractor.extract(self._place)
        self._osm = OSMTransformer(G)

    def transform_coords_to_nodes(self) -> None:
        self._data = self._osm.coordinatesToNodes(self.data)
        return self.data

    def identify_trip_segments(self) -> None:
        ts = TripSegments()
        self._data = ts.identify(self.data)

    def eval_driving_distances(self) -> None:
        df = self.data[self.data["src_node"] == self.data["dest_node"]]
        df = self._osm.geo_distances(df)
        df = df[["vehicle_id", "day", "km_driven"]]

        self._data = self.data[self.data["src_node"] != self.data["dest_node"]]
        self._data = self._osm.driving_distances(self.data)
        self._data = self.data[["vehicle_id", "day", "km_driven"]]

        self._data = pd.concat([self.data, df], ignore_index=True)

    def load(self) -> None:
        self._data = (
            self.data.groupby(by=["vehicle_id", "day"]).agg("sum").reset_index()
        )
        self._loader.load(self.data)

    def step(self) -> str:
        """Executes the next step in the pipeline."""
        if self._current_step >= len(self._steps):
            self._current_step = len(self._steps)
            return "done"

        current_step = self._steps[self._current_step]
        current_step.run()
        self._current_step += 1

        return current_step.name

    def run(self) -> None:
        """Executes all the pipeline."""
        while self._current_step < len(self._steps):
            self.step()


class CheckpointedPipeline(Pipeline):
    def __init__(
        self,
        place: str,
        file: str | Path,
        work_dir: str | Path,
        loader,
        silent: bool = False,
        cleanCheckpoints: bool = False,
    ) -> None:
        super().__init__(place, file, work_dir, loader, silent)

        self.step_info = {
            "extract_csv": "Data extracted from CSV",
            "extract_graph": "OSM data extracted",
            "transform_coords_to_nodes": "Coordinates transformed to graph nodes",
            "identify_trip_segments": "Trip segments identified",
            "eval_driving_distances": "Driving distances evaluated",
            "load": "Data loaded",
        }

        file = os.path.basename(self._file)
        file = file.rsplit(".", 1)[0]
        self.filemask = "_checkpoint_" + file + "_%s.csv"
        self.cleanCheckpoints = cleanCheckpoints

    def step(self) -> str:
        """Executes the next step in the pipeline."""
        current_step = self._steps[self._current_step]
        checkpoint_path = os.path.join(
            self._working_dir, self.filemask % current_step.name
        )

        if os.path.isfile(checkpoint_path):
            self._data = pd.read_csv(checkpoint_path)
            self._current_step += 1
            logging.getLogger(__name__).info(self.step_info[current_step.name])
            return current_step.name

        result = super().step()

        if current_step.checkpoint:
            self.data.to_csv(checkpoint_path, index=False, quoting=csv.QUOTE_NONNUMERIC)

        logging.getLogger(__name__).info(self.step_info[current_step.name])
        return result

    def clean(self):
        """Removes checkpoint files."""
        for step in self._steps:
            recovery_path = os.path.join(
                self._working_dir, self.filemask % step["name"]
            )
            if os.path.isfile(recovery_path):
                os.remove(recovery_path)

    def run(self) -> None:
        """Executes all the pipeline."""
        logging.getLogger(__name__).info("Pipeline execution started")

        super().run()
        if self.cleanCheckpoints:
            self.clean()

        logging.getLogger(__name__).info("Done!")
