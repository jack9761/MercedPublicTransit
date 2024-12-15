import osmnx
import geopandas
class Stop:
    def __init__(self, OSM_ID: str, times: [int]):
        self.OSM_ID = OSM_ID
        self.times = times
class Route:
   def __init__(self, operatingdays: str, route_name: str, operater: str, stops: [Stop]):
       self.operatingdays = operatingdays
       self.route_name = route_name
       self.operater = operater
       self.stops = stops

def compute_travel_time(graph, route):
    return osmnx.routing.route_to_gdf(graph, route)["travel_time"].sum()
def compute_travel_time_for_index_orgin(index, busdatabase, route, time_of_day, destination_node, gdfclean):
    return CalculateTravelTime(busdatabase, route, time_of_day, destination_node, gdfclean.loc[gdfclean.index[index], "element"][0] + str(gdfclean.loc[gdfclean.index[index], "id"]))
def compute_travel_time_for_index_destination(index, busdatabase, route, time_of_day, origin_node, gdfclean):
    return CalculateTravelTime(busdatabase, route, time_of_day, gdfclean.loc[gdfclean.index[index], "element"][0] + str(gdfclean.loc[gdfclean.index[index], "id"]), origin_node)
def CalculateTravelTime(busdatabase: geopandas.GeoDataFrame, currentroute: Route, time_of_day: float,
                        orginnode: str, destinationnode: str):
    besttraveltime =10000000000
    traveltime = 0
    for stopa in currentroute.stops:
        orginstop = stopa
        bestdeparturetime = 0
        for time in stopa.times:
            if time_of_day+(busdatabase.loc[(orginnode[0], int(orginnode[1:])), orginstop.OSM_ID]/60) < time:
                bestdeparturetime = time
                break
        for stopb in currentroute.stops:
            deststop = stopb
            bestarrivaltime = 0
            for time in stopb.times:
                if bestdeparturetime < time:
                    bestarrivaltime = time
                    break
            walktofirststoptime = busdatabase.loc[(orginnode[0], int(orginnode[1:])), orginstop.OSM_ID] / 60
            waitforbustime = bestdeparturetime - time_of_day - walktofirststoptime
            onthebustime = bestarrivaltime - bestdeparturetime
            walktodestinationtime = busdatabase.loc[(destinationnode[0], int(destinationnode[1:])), deststop.OSM_ID] / 60
            traveltime = walktofirststoptime+ waitforbustime + onthebustime + walktodestinationtime
            if traveltime < besttraveltime:
                besttraveltime = traveltime
    return besttraveltime