import os, csv, sys
import pandas as pd
from ddmc.extractors.default_extractor import DefaultExtractor
from ddmc.extractors.osm import OSM as OSMExtractor
from ddmc.transformers.osm import OSM as OSMTransformer
from ddmc.transformers.trip_segments import TripSegments
from ddmc.loaders.csv import CSV as CSVLoader

class Pipeline():
    def __init__(self, file : str, working_dir : str, loader, silent : bool=False) -> None:
        self.file = file
        self.working_dir = working_dir
        self.silent = silent

        self.loader = loader

        self.data  = None
        self.current_step = 0
        self.steps = [
            {
                'name': 'extractCSV',
                'call': self.extractCSV,
                'checkpoint': False,
            },{
                'name': 'extractGraph',
                'call': self.extractGraph,
                'checkpoint': False,
            },{
                'name': 'transformCoordsToNodes',
                'call': self.transformCoordsToNodes,
                'checkpoint': True,
            },{
                'name': 'identifyTripSegments',
                'call': self.identifyTripSegments,
                'checkpoint': True,
            },{
                'name': 'evalDrivingDistances',
                'call': self.evalDrivingDistances,
                'checkpoint': True,
            },{
                'name': 'load',
                'call': self.load,
                'checkpoint': False,
            },
        ]

    def extractCSV(self) -> None:
        extractor = DefaultExtractor()
        self.data = extractor.extract(self.file)

    def extractGraph(self) -> None:
        max_lat, max_lon, min_lat, min_lon = self.data[['location_raw_lat', 'location_raw_lon']].agg(['max', 'min']).to_numpy().flatten().tolist()
        margin = 0.1
        bbox = (max_lat+margin, min_lat-margin, max_lon+margin, min_lon-margin)

        extractor = OSMExtractor(self.working_dir)
        G = extractor.extract(bbox)
        self.osm = OSMTransformer(G)
    
    def transformCoordsToNodes(self) -> None:
        self.data = self.osm.coordinatesToNodes(self.data)
        return self.data
    
    def identifyTripSegments(self) -> None:
        ts = TripSegments()
        self.data = ts.identify(self.data)

    def evalDrivingDistances(self) -> None:
        df = self.data[self.data['src_node'] == self.data['dest_node']]
        df = self.osm.geoDistances(df)
        df = df[['vehicle_id', 'day', 'km_driven']]

        self.data = self.data[self.data['src_node'] != self.data['dest_node']]
        self.data = self.osm.drivingDistances(self.data)
        self.data = self.data[['vehicle_id', 'day', 'km_driven']]

        self.data = pd.concat([self.data, df], ignore_index=True)
    
    def load(self) -> None:
        self.data = self.data.groupby(by=['vehicle_id', 'day']).agg('sum').reset_index()
        self.loader.load(self.data)

    def step(self) -> str:
        """Executes the next step in the pipeline."""
        if self.current_step >= len(self.steps):
            self.current_step = len(self.steps)
            return 'done'
        
        current = self.steps[self.current_step]
        current['call']()
        self.current_step += 1
        
        return current['name']

    def run(self) -> None:
        """Executes all the pipeline."""
        while self.current_step < len(self.steps):
            self.step()

class CheckpointedPipeline(Pipeline):
    def __init__(self, file : str, working_dir : str, loader, silent : bool=False, cleanCheckpoints : bool=False) -> None:
        super().__init__(file, working_dir, loader, silent)

        self.step_info = {
            'extractCSV': "Data extracted from CSV",
            'extractGraph': "OSM data extracted",
            'transformCoordsToNodes': "Coordinates transformed to graph nodes",
            'identifyTripSegments': "Trip segments identified",
            'evalDrivingDistances': "Driving distances evaluated",
            'load': "Data loaded",
        }

        file = os.path.basename(self.file)
        file = file.rsplit(".", 1)[0]
        self.filemask = '_checkpoint_' + file + '_%s.csv'
        self.cleanCheckpoints = cleanCheckpoints

    def step(self) -> str:
        """Executes the next step in the pipeline."""
        current = self.steps[self.current_step]        
        checkpoint_path = os.path.join(self.working_dir, self.filemask % current['name'])
        
        if os.path.isfile(checkpoint_path):
            self.data = pd.read_csv(checkpoint_path)
            self.current_step += 1
            print(self.step_info[current['name']])
            return current['name']

        result = super().step()

        if current['checkpoint']:
            self.data.to_csv(checkpoint_path, index=False, quoting=csv.QUOTE_NONNUMERIC)

        print(self.step_info[current['name']])
        return result

    def clean(self):
        """Removes checkpoint files."""
        for step in self.steps:
            recovery_path = os.path.join(self.working_dir, self.filemask % step['name'])
            if os.path.isfile(recovery_path):
                os.remove(recovery_path)

    def run(self) -> None:
        """Executes all the pipeline."""
        print('Pipeline execution started')

        super().run()
        if self.cleanCheckpoints:
            self.clean()
        
        print('Done!')