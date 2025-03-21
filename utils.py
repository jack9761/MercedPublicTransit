import osmnx
import geopandas
import networkx as nx
from typing import List, Dict, Union, Tuple, Optional, Any

class Stop:
    def __init__(self, OSM_ID: str, times: List[int]):
        self.OSM_ID: str = OSM_ID
        self.times: List[int] = times

class Route:
   def __init__(self, operatingdays: str, route_name: str, operater: str, stops: List[Stop]):
       self.operatingdays: str = operatingdays
       self.route_name: str = route_name
       self.operater: str = operater
       self.stops: List[Stop] = stops

def compute_travel_time(graph: nx.MultiDiGraph, route: List) -> float:
    return osmnx.routing.route_to_gdf(graph, route)["travel_time"].sum()

def compute_travel_time_for_index_orgin(index: int, busdatabase: geopandas.GeoDataFrame, 
                                       route: Route, time_of_day: int, 
                                       destination_node: str, gdfclean: geopandas.GeoDataFrame) -> float:
    return CalculateTravelTime(busdatabase, route, time_of_day, destination_node, 
                             gdfclean.loc[gdfclean.index[index], "element"][0] + str(gdfclean.loc[gdfclean.index[index], "id"]))

def compute_travel_time_for_index_destination(index: int, busdatabase: geopandas.GeoDataFrame, 
                                            route: Route, time_of_day: int, 
                                            origin_node: str, gdfclean: geopandas.GeoDataFrame) -> float:
    return CalculateTravelTime(busdatabase, route, time_of_day, 
                             gdfclean.loc[gdfclean.index[index], "element"][0] + str(gdfclean.loc[gdfclean.index[index], "id"]), 
                             origin_node)

def CalculateTravelTime(busdatabase: geopandas.GeoDataFrame, currentroute: Route, time_of_day: float,
                        orginnode: str, destinationnode: str) -> float:
    besttraveltime: float = 10000000000
    traveltime: float = 0
    for stopa in currentroute.stops:
        orginstop: Stop = stopa
        bestdeparturetime: int = 0
        for time in stopa.times:
            if time_of_day+(busdatabase.loc[(orginnode[0], int(orginnode[1:])), orginstop.OSM_ID]/60) < time:
                bestdeparturetime = time
                break
        for stopb in currentroute.stops:
            deststop: Stop = stopb
            bestarrivaltime: int = 0
            for time in stopb.times:
                if bestdeparturetime < time:
                    bestarrivaltime = time
                    break
            walktofirststoptime: float = busdatabase.loc[(orginnode[0], int(orginnode[1:])), orginstop.OSM_ID] / 60
            waitforbustime: float = bestdeparturetime - time_of_day - walktofirststoptime
            onthebustime: float = bestarrivaltime - bestdeparturetime
            walktodestinationtime: float = busdatabase.loc[(destinationnode[0], int(destinationnode[1:])), deststop.OSM_ID] / 60
            traveltime = walktofirststoptime + waitforbustime + onthebustime + walktodestinationtime
            if traveltime < besttraveltime:
                besttraveltime = traveltime
    return besttraveltime