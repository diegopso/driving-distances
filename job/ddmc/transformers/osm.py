import osmnx as ox
import pandas as pd
import networkx as nx

class OSM():
    def __init__(self, G) -> None:
        self.G = G

    def coordinatesToNodes(
        self,
        df: pd.DataFrame,
        lat_col : str = 'location_raw_lat',
        lon_col : str = 'location_raw_lon'
    ) -> pd.DataFrame:
        """Converts a series of lat and lon coordinates in a dataframe to nodes in the OSM graph."""
        if self.G is None:
            raise Exception("Load graph before using OSM class methods.")
        
        nodes = ox.nearest_nodes(self.G, Y=df[lat_col], X=df[lon_col])
        df['nodes'] = nodes
        return df
    
    def geoDistances(self, df):
        distances = ox.distance.great_circle_vec(df['src_lat'], df['src_lon'], df['dest_lat'], df['dest_lon'])
        
        if isinstance(distances, float):
            return distances / 1000
        
        df = pd.concat([df, pd.DataFrame({'km_driven': distances})], axis=1)
        df['km_driven'] = df['km_driven'].divide(1000)
        return df
    
    def drivingDistances(self, df : pd.DataFrame, src_col : str = 'src_node', dest_col : str = 'dest_node') -> pd.DataFrame:
        """Evaluates the driving distance between 2 nodes in the OSM graph."""
        if self.G is None:
            raise Exception("Load graph before using OSM class methods.")

        df['km_driven'] = df.apply(lambda r: nx.shortest_path_length(self.G, r[src_col], r[dest_col], weight='length'), axis=1)
        df['km_driven'] = df['km_driven'].divide(1000)
                
        return df

