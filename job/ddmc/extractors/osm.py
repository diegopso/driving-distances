import os
import osmnx as ox

 # ShapelyDeprecationWarning unsolved in osmnx
import shapely
import warnings
from shapely.errors import ShapelyDeprecationWarning

class OSM():
    def __init__(self, working_dir : str) -> None:
        self.working_dir = working_dir
        warnings.filterwarnings("ignore", category=ShapelyDeprecationWarning)

    def extract(self, bbox : tuple) -> None:
        """Loads data from OSM to object. Caches data downloaded in file for future usage."""
        filename = '%d.graphml' % abs(hash(bbox))
        path = os.path.join(self.working_dir, filename)

        if os.path.isfile(path):
            return ox.load_graphml(path)
        
        G = ox.graph_from_bbox(*bbox, network_type='drive')
        G = ox.utils_graph.remove_isolated_nodes(G)
        G = ox.utils_graph.get_largest_component(G, strongly=True)

        ox.save_graphml(G, path)

        return G
    
    def clearCache(self, bbox : tuple) -> None:
        filename = '%d.graphml' % abs(hash(bbox))
        path = os.path.join(self.working_dir, filename)
        if os.path.isfile(path):
            os.remove(path)