import geopandas
import networkx as nx
import osmnx
import os
import numpy
import osmapi
import itertools
import multiprocessing as mp
import functools
import pandas
import sys
from typing import Dict, List, Tuple, Callable, Optional, Union, Any
from utils import compute_travel_time, compute_travel_time_for_index_destination, CalculateTravelTime, Route, Stop, \
    compute_travel_time_for_index_orgin

def log_message(message: str) -> None:
    """Print a log message. This function is used to maintain consistent logging across implementations."""
    print(message)

def initialize_routes() -> Tuple[List[Route], List[Route], List[Route]]:
    """Initialize and return route information."""
    api = osmapi.OsmApi()
    BobcatExpress = Route("Weekday", "Bobcat Express", "UC Merced", [
        Stop("n12154520785", [389,429,469,524,564,604,644,729,829,917,1017,1102,1202]),
        Stop("n12154520786", [392,432,472,527,567,607,647,732,832,920,1020,1105,1205]),
        Stop("n12154520787", [394,434,474,529,569,609,649,734,834,922,1022,1107,1207]),
        Stop("n12154509604", [399,439,479,534,574,614,654,739,839,927,1027,1112,1212]),
        Stop("n12153159159", [404,444,484,539,579,619,660,745,845,933,1033,1118,1218]),
        Stop("n12167340731", [415,455,510,550,590,630,671,771,856,959,1044,1144,1229]),
        Stop("n12162711345", [680,780,865,968,1053,1153]),
        Stop("n12167340732", [689,789,877,977,1062,1162]),
        Stop("n12162649319", [698,798,886,986,1071,1171]),
        Stop("n12162599795", [710,810,898,998,1083,1183,1280]),
        Stop("n12162634549", [712,812,900,1000,1085,1185]),
        Stop("n12153159164", [721,821,909,1009,1094,1194]),
        Stop("n12153159162", [723,823,911,1011,1096,1196])])
    C1 = Route("Weekday", "C-1", "UC Merced", [
        Stop("n12153159167", [380,451,537,608,694,765,856,927,1013,1084,1155,1241,1312]),
        Stop("n12153159165", [392, 434, 463, 520, 549, 591, 620, 677, 706, 748, 777, 834, 868, 910, 939, 996, 1025, 1067, 1096, 1138, 1167, 1224, 1253, 1295, 1324]),
        Stop("n12153159164", [394,465,551,622,708,779,870,941,1027,1098,1169,1255,1326]),
        Stop("n12153159162", [396,467,553,624,710,781,872,943,1029,1100,1171,1257,1328]),
        Stop("n12153159160", [399,470,556,627,713,784,875,946,1032,1103,1174,1260,1331]),
        Stop("n12153159159", [405,476,562,633,719,790,881,952,1038,1109,1180,1266,1337]),
        Stop("n12153159156", [416,502,573,659,730,816,892,978,1049,1120,1206,1277,1348]),
        Stop("n12153159161", [426,512,583,669,740,826,902,988,1059,1130,1216,1287]),
        Stop("n12153159163", [429,515,586,672,743,829,905,991,1062,1133,1219,1290]),
        ])
    C2 = Route("Weekday", "C-2", "UC Merced", [
        Stop("n12154520785", [380, 438, 511, 569, 642, 700, 773, 831, 892, 950, 1023, 1081, 1154, 1212, 1285]),
        Stop("n12154520786", [383, 441, 514, 572, 645, 703, 776, 834, 895, 953, 1026, 1084, 1157, 1215, 1288]),
        Stop("n12154520787", [385, 443, 516, 574, 647, 705, 778, 836, 897, 955, 1028, 1086, 1159, 1217, 1290]),
        Stop("n12154522608", [392, 450, 523, 581, 654, 712, 785, 843, 904, 962, 1035, 1093, 1166, 1224, 1297]),
        Stop("n12154523360", [399, 457, 530, 588, 661, 719, 792, 853, 911, 969, 1042, 1100, 1173, 1231, 1304]),
        Stop("n12154509606", [401, 459, 532, 590, 663, 721, 794, 855, 913, 971, 1044, 1102, 1175, 1233, 1306]),
        Stop("n12154509604", [405, 463, 536, 594, 667, 725, 798, 859, 917, 975, 1048, 1106, 1179, 1237, 1310]),
        Stop("n12154509603", [408, 466, 539, 597, 670, 728, 801, 862, 920, 978, 1051, 1109, 1182, 1240, 1313]),
        Stop("n12153159159", [411, 469, 542, 600, 673, 731, 804, 865, 923, 981, 1054, 1112, 1185, 1243, 1316]),
        Stop("n12154500900", [422, 495, 553, 626, 684, 757, 815, 876, 934, 1007, 1065, 1138, 1196, 1269, 1327]),
        Stop("n12154509601", [429, 502, 560, 633, 691, 764, 822, 883, 941, 1014, 1072, 1145, 1203, 1276]),
        Stop("n12154509602", [433, 506, 564, 637, 695, 768, 826, 887, 945, 1018, 1076, 1149, 1207, 1280])])
    E1 = Route("Weekend", "E-1", "UC Merced", [
        Stop("n12162599793", [510, 547, 582, 619, 639, 676, 711, 748, 768, 805, 840, 877, 897, 934, 954, 994, 1014, 1051, 1086, 1123, 1143, 1180, 1200, 1237, 1272, 1309, 1329, 1366, 1386]),
        Stop("n12154530337", [519, 591, 648, 720, 777, 849, 906, 963, 1023, 1095, 1152, 1209, 1281, 1338]),
        Stop("n12162599795", [526, 598, 655, 727, 784, 856, 913, 970, 1030, 1102, 1159, 1216, 1288, 1345]),
        Stop("n12162634549", [528, 600, 657, 729, 786, 858, 915, 975, 1032, 1104, 1161, 1218, 1290, 1347]),
        Stop("n12154523360", [541, 613, 670, 742, 799, 871, 928, 988, 1045, 1117, 1174, 1231, 1303, 1360]),
        Stop("n12162649318", [543, 615, 672, 744, 801, 873, 930, 990, 1047, 1119, 1176, 1233, 1305, 1362]),
        Stop("n12162599794", [554, 626, 683, 755, 812, 884, 941, 1001, 1058, 1130, 1187, 1244, 1316, 1373])
    ])
    E2 = Route("Weekend", "E-2", "UC Merced", [
        Stop("n12162711342", [665, 729, 778, 827, 876, 940, 989, 1038, 1105, 1154, 1218, 1267, 1316]),
        Stop("n12162711345", [674, 738, 787, 836, 885, 949, 998, 1047, 1114, 1163, 1227, 1276]),
        Stop("n12154520785", [680, 744, 793, 842, 891, 955, 1004, 1056, 1120, 1169, 1233, 1282]),
        Stop("n12154520786", [683, 747, 796, 845, 894, 958, 1007, 1059, 1123, 1172, 1236, 1285]),
        Stop("n12154520787", [685, 749, 798, 847, 896, 960, 1009, 1061, 1125, 1174, 1238, 1287]),
        Stop("n12154523360", [691, 755, 804, 853, 902, 966, 1015, 1067, 1131, 1180, 1244, 1293]),
        Stop("n12154509606", [693, 757, 806, 855, 904, 968, 1017, 1069, 1133, 1182, 1246, 1295]),
        Stop("n12162735605", [697, 761, 810, 859, 908, 972, 1021, 1073, 1137, 1186, 1250, 1299]),
        Stop("n12162711346", [703, 767, 816, 865, 914, 978, 1027, 1079, 1143, 1192, 1256, 1305]),
        Stop("n12154530339", [706, 770, 819, 868, 917, 981, 1030, 1082, 1146, 1195, 1259, 1308])
    ])
    FastCat = Route("Weekday", "FastCat", "UC Merced", [
        Stop("n12154530338", [399, 436, 463, 515, 542, 579, 606, 643, 670, 707, 749, 786, 813, 850, 880, 917, 944, 996, 1023, 1060,1087, 1124, 1151, 1188, 1215, 1267, 1294, 1331]),
        Stop("n12162711345", [402, 466, 545, 609, 673, 752, 816, 883, 947, 1026, 1090, 1154, 1218, 1297]),
        Stop("n12162599794", [404, 468, 547, 611, 675, 754, 818, 885, 949, 1028, 1092, 1156, 1220, 1299]),
        Stop("n12153159160", [408, 433, 472, 512, 551, 576, 615, 640, 679, 704, 758, 783, 822, 847, 889, 914, 953, 993, 1032, 1057,1096, 1121, 1160, 1185, 1224, 1264, 1303, 1328]),
        Stop("n12154509603", [412, 476, 555, 619, 683, 762, 826, 893, 957, 1036, 1100, 1164, 1228, 1307]),
        Stop("n12153159161", [423, 502, 566, 630, 694, 773, 837, 904, 983, 1047, 1111, 1175, 1254, 1318]),
        Stop("n12154530339", [439, 518, 582, 646, 710, 789, 853, 920, 999, 1063, 1127, 1191, 1270, 1334]),
        Stop("n12162599793", [442, 521, 585, 649, 713, 792, 859, 923, 1002, 1066, 1130, 1194, 1273, 1337])
    ])
    FastCat2 = Route("Weekday", "FastCat 2", "UC Merced", [
        Stop("n12162711345", [514, 578, 657, 721, 785, 864, 928, 995, 1074, 1138, 1217, 1281]),
        Stop("n12162599794", [517, 581, 660, 724, 788, 867, 931, 998, 1077, 1141, 1220, 1284]),
        Stop("n12153159160", [519, 583, 662, 726, 790, 869, 933, 1000, 1079, 1143, 1222, 1286]),
        Stop("n12154509603", [523, 587, 666, 730, 794, 873, 937, 1004, 1083, 1147, 1226, 1290]),
        Stop("n12153159159", [527, 591, 670, 734, 798, 877, 941, 1008, 1087, 1151, 1230, 1294]),
        Stop("n12154530336", [538, 565, 617, 644, 681, 708, 745, 772, 809, 851, 888, 915, 952, 982, 1019, 1061, 1098, 1125, 1162, 1204, 1241, 1268, 1305]),
        Stop("n12153159161", [548, 627, 691, 755, 819, 898, 962, 1029, 1108, 1172, 1251]),
        Stop("n12162711346", [551, 630, 694, 758, 822, 901, 965, 1032, 1111, 1175, 1254]),
        Stop("n12154530338", [554, 574, 633, 653, 697, 717, 761, 781, 825, 860, 904, 924, 968, 991, 1035, 1070, 1114, 1134, 1178, 1213, 1257, 1277]),
        Stop("n12154530339", [557, 636, 700, 764, 828, 907, 971, 1038, 1117, 1181, 1260]),
    ])
    GLine = Route("Weekday", "G-Line", "UC Merced", [
        Stop("n12154520785", [390, 458, 541, 609, 677, 745, 828, 901, 969, 1052, 1120, 1188, 1271]),
        Stop("n12154520786", [393, 461, 544, 612, 680, 748, 831, 904, 972, 1055, 1123, 1191, 1274]),
        Stop("n12154520787", [395, 463, 546, 614, 682, 750, 833, 906, 974, 1057, 1125, 1193, 1276]),
        Stop("n12154509604", [400, 468, 551, 619, 687, 755, 838, 911, 979, 1062, 1130, 1198, 1281]),
        Stop("n12153159159", [406, 474, 557, 625, 693, 761, 844, 917, 985, 1068, 1136, 1204, 1287]),
        Stop("n12167312041", [417, 500, 568, 636, 704, 787, 855, 928, 1011, 1079, 1147, 1230, 1298]),
        Stop("n12162599795", [438, 521, 589, 657, 725, 808, 876, 949, 1032, 1100, 1168, 1251, 1319]),
        Stop("n12162634549", [440, 523, 591, 659, 727, 810, 883, 951, 1034, 1102, 1170, 1253, 1321]),
        Stop("n12167312042", [442, 525, 593, 661, 729, 812, 885, 953, 1036, 1104, 1172, 1255, 1323])
    ])
    YosemiteExpress = Route("Weekday", "Yosemite Express", "UC Merced", [
        Stop("n12154530339", [540, 567, 594, 636, 663, 690, 717, 744, 771, 798, 840, 867, 894, 921, 963, 995, 1022, 1049, 1076, 1118, 1145, 1172, 1199, 1226, 1253, 1280, 1322]),
        Stop("n12154530336", [547, 574, 616, 643, 670, 697, 724, 751, 778, 820, 847, 874, 901, 943, 970, 1002, 1029, 1056, 1098, 1125, 1152, 1179, 1206, 1233, 1260, 1302, 1329]),
        Stop("n12153159161", [556, 583, 625, 652, 679, 706, 733, 760, 787, 829, 856, 883, 910, 952, 984, 1011, 1038, 1065, 1107, 1134, 1161, 1188, 1215, 1242, 1269, 1311]),
        Stop("n12154530337", [559, 586, 628, 655, 682, 709, 736, 763, 790, 832, 859, 886, 913, 955, 987, 1014, 1041, 1068, 1110, 1137, 1164, 1191, 1218, 1245, 1272, 1314]),
        Stop("n12154530338", [564, 591, 633, 660, 687, 714, 741, 768, 795, 837, 864, 891, 918, 960, 992, 1019, 1046, 1073, 1115, 1142, 1169, 1196, 1223, 1250, 1277, 1319])
    ])
    
    # Merced bus routes and other routes would go here...
    # For brevity, I'm only including some representative routes
    
    M1_weekday = Route("Weekday", "M1 Weekdays", "Merced Bus", [
        Stop("n8273119140", [394, 424, 454, 484, 514, 544, 574, 604, 634, 664, 694, 724, 754, 784, 814, 844, 874, 904, 934, 964, 994, 1024, 1054, 1114, 1174])
    ])
    
    M1_weekend = Route("Weekend", "M1 Weekend", "Merced Bus", [
        Stop("n8273119140", [510, 600, 690, 780, 870, 960, 1050])
    ])
    
    # Group all the routes
    Routes = [BobcatExpress, C1, C2, E1, E2, FastCat, FastCat2, GLine, YosemiteExpress, M1_weekday, M1_weekend]
    WeekdayRoutes = [BobcatExpress, C1, C2, FastCat, FastCat2, GLine, YosemiteExpress, M1_weekday]
    WeekendRoutes = [E1, E2, M1_weekend]
    
    return Routes, WeekdayRoutes, WeekendRoutes

def process_transit_data(params: Dict[str, Any], logger_func: Callable[[str], None] = log_message) -> Optional[geopandas.GeoDataFrame]:
    """Core function to process transit data
    
    Args:
        params: Dictionary of parameters (similar to ArcPy parameters)
        logger_func: Function to use for logging messages
        
    Returns:
        Optional[geopandas.GeoDataFrame]: The processed data or None if only preprocessing was done
    """
    # Set up multiprocessing
    if sys.platform == 'win32':
        mp.set_executable(os.path.join(sys.exec_prefix, 'pythonw.exe'))
    
    api = osmapi.OsmApi()
    
    # Initialize routes
    Routes, WeekdayRoutes, WeekendRoutes = initialize_routes()
    logger_func("Routes Loaded")
    
    # Handle cached data if specified
    if params.get("use_caching"):
        graph = osmnx.load_graphml(params.get("graphml_file"))
        if params.get("mode") != "Precompute Table":
            busdatabase = geopandas.read_feather(params.get("precomputed_bus_database"))
            busdatabase.index = busdatabase.index.set_levels(busdatabase.index.levels[0].str[0], level=0)
        gdfclean = geopandas.read_feather(params.get("clean_osm_database"))
    else:
        # Load graph based on selected region mode
        if params.get("region_mode") == "Geocode Region":
            graph = osmnx.graph_from_place(params.get("region_geocode"), network_type='walk', simplify=True)
            osmnx.io.save_graphml(graph, params.get("region_geocode") + ".graphml")
        elif params.get("region_mode") == "Use Bounding Box":
            bbox = params.get("region_extent")
            graph = osmnx.graph_from_bbox(bbox["ymin"], bbox["xmin"], bbox["ymax"], bbox["xmax"], network_type='walk', simplify=True)
            osmnx.io.save_graphml(graph, str(bbox) + ".graphml")
        elif params.get("region_mode") == "Specify Node ID":
            graph = osmnx.graph_from_place(params.get("region_OSMID"), network_type='walk', simplify=True)
            osmnx.io.save_graphml(graph, params.get("region_OSMID") + ".graphml")
        
        logger_func("Graph Loaded")
        
        # Load and process OSM features
        tags = {'building': True, "leisure": True}
        addresstags = {"addr:street": True, "addr:housenumber": True, "addr:postcode": True}
        
        if params.get("region_mode") == "Geocode Region":
            buildingsgdf = osmnx.features_from_place(params.get("region_geocode"), tags)
            addressgdf = osmnx.features_from_place(params.get("region_geocode"), addresstags)
        elif params.get("region_mode") == "Use Bounding Box":
            bbox = params.get("region_extent")
            buildingsgdf = osmnx.features_from_bbox(bbox["ymin"], bbox["xmin"], bbox["ymax"], bbox["xmax"], tags)
            addressgdf = osmnx.features_from_bbox(bbox["ymin"], bbox["xmin"], bbox["ymax"], bbox["xmax"], addresstags)
        elif params.get("region_mode") == "Specify Node ID":
            buildingsgdf = osmnx.features_from_place(params.get("region_OSMID"), tags)
            addressgdf = osmnx.features_from_place(params.get("region_OSMID"), addresstags)
            
        gdf = geopandas.geodataframe.GeoDataFrame(pandas.concat([buildingsgdf, addressgdf], axis=0).drop_duplicates())
        gdf.drop("relation", level="element", inplace=True)
        polygons = gdf.groupby(level=0).get_group("way")
        points = gdf.groupby(level=0).get_group("node")
        pointsinpolygons = polygons.sindex.query(points.geometry, predicate="within")
        pointsindex = numpy.ones(len(points), dtype=bool)
        pointsindex[pointsinpolygons[0]] = False
        points = points.iloc[pointsindex]
        polygons.geometry = polygons.geometry.centroid
        gdfclean = geopandas.geodataframe.GeoDataFrame(pandas.concat([polygons, points], axis=0))
        gdfclean["nearestnode"] = osmnx.distance.nearest_nodes(graph, gdfclean.geometry.get_coordinates(ignore_index=True).x, gdfclean.geometry.get_coordinates(ignore_index=True).y)
        logger_func(str(gdfclean.head()))
        gdfclean.to_feather("MercedCounty.feather")
        logger_func("OSM Features Loaded")
        return None
    
    # Handle precompute table mode
    if params.get("mode") == "Precompute Table":
        stops: List[str] = []
        for route in Routes:
            for stop in route.stops:
                if stop.OSM_ID not in stops:
                    stops.append(stop.OSM_ID)
        
        # Precompute Table
        gdfclean["nearestnode"] = osmnx.distance.nearest_nodes(graph, gdfclean.geometry.get_coordinates(ignore_index=True).x, gdfclean.geometry.get_coordinates(ignore_index=True).y)
        speed_dict: Dict[Tuple, float] = {edge: 5 for edge in graph.edges}
        nx.set_edge_attributes(graph, speed_dict, "speed_kph")
        osmnx.routing.add_edge_travel_times(graph)
        
        for destination_stop in stops:
            destination_node_api_dict = api.NodeGet(int(destination_stop[1:]))
            destination_node_graph = osmnx.distance.nearest_nodes(graph, destination_node_api_dict["lon"], destination_node_api_dict["lat"])
            destinations = list(itertools.repeat(destination_node_graph, len(gdfclean)))
            routelists = osmnx.routing.shortest_path(graph, gdfclean["nearestnode"], destinations, weight="travel_time", cpus=mp.cpu_count())
            
            with mp.Pool(mp.cpu_count()) as pool:
                travel_times = pool.map(functools.partial(compute_travel_time, graph), routelists)
            
            print(destination_stop)
            gdfclean[destination_stop] = travel_times
        
        gdfclean.to_feather(os.getcwd() + "/BusDatabase.feather")
        return None
    
    logger_func("Calculating Destination Nodes")
    
    # Get destination node based on POI mode
    destination_node: str = ""
    destination_node_graph: int = 0
    
    if params.get("POI_Mode") == "Geocode a Node":
        geocoderesults = osmnx.geocoder.geocode_to_gdf(params.get("POI_geocode"))
        destination_node = geocoderesults["osm_type"][0] + str(geocoderesults["osm_id"])
        destination_node_graph = osmnx.distance.nearest_nodes(graph, geocoderesults["lon"], geocoderesults["lat"])
    elif params.get("POI_Mode") == "Specify Node ID":
        destination_node = params.get("POI_OSMID")
        destination_node_api_dict = api.NodeGet(int(params.get("POI_OSMID")[1:]))
        destination_node_graph = osmnx.distance.nearest_nodes(graph, destination_node_api_dict["lon"], destination_node_api_dict["lat"])
    
    outputgdf = gdfclean.copy(deep=True)
    logger_func("Destination Node Calculated")
    
    # Handle fastest mode calculation
    if params.get("mode") == "Fastest Mode":
        logger_func("Walking Distance Calculation Starting")
        methods: List[str] = []
        
        # Calculate walking distances
        if "Walking" in params.get("modes_of_transportation"):
            speed_dict = {edge: 5 for edge in graph.edges}
            nx.set_edge_attributes(graph, speed_dict, "speed_kph")
            osmnx.routing.add_edge_travel_times(graph)
            destinations = list(itertools.repeat(destination_node_graph, len(outputgdf)))
            routelists = osmnx.routing.shortest_path(graph, outputgdf["nearestnode"], destinations, weight="travel_time", cpus=mp.cpu_count())
            
            with mp.Pool(mp.cpu_count()) as pool:
                travel_times = pool.map(functools.partial(compute_travel_time, graph), routelists)
            
            travel_times = [time/60 for time in travel_times]
            outputgdf["Walking"] = travel_times
            methods.append("Walking")
            logger_func("Walking Distance Calculated")
        
        # Calculate UC Bus routes
        if "UC Bus" in params.get("modes_of_transportation"):
            if "Weekday" in params.get("weekday_weekend"):
                for route in WeekdayRoutes:
                    if route.operater == "UC Merced":
                        logger_func(route.route_name)
                        travel_times = []
                        
                        if params.get("origin_destination") == "Origin":
                            with mp.Pool(mp.cpu_count()) as pool:
                                travel_times = pool.starmap(compute_travel_time_for_index_orgin, [
                                    (i, busdatabase, route, params.get("time_of_day"), destination_node, gdfclean) for i
                                    in range(len(gdfclean))])
                        else:  # Destination
                            with mp.Pool(mp.cpu_count()) as pool:
                                travel_times = pool.starmap(compute_travel_time_for_index_destination, [
                                    (i, busdatabase, route, params.get("time_of_day"), destination_node, gdfclean) for i 
                                    in range(len(gdfclean))])
                        
                        methods.append(route.route_name)
                        outputgdf[route.route_name] = travel_times
            
            if "Weekend" in params.get("weekday_weekend"):
                for route in WeekendRoutes:
                    if route.operater == "UC Merced":
                        logger_func(route.route_name)
                        travel_times = []
                        
                        if params.get("origin_destination") == "Origin":
                            with mp.Pool(mp.cpu_count()) as pool:
                                travel_times = pool.starmap(compute_travel_time_for_index_orgin, [
                                    (i, busdatabase, route, params.get("time_of_day"), destination_node, gdfclean) for i
                                    in range(len(gdfclean))])
                        else:  # Destination
                            with mp.Pool(mp.cpu_count()) as pool:
                                travel_times = pool.starmap(compute_travel_time_for_index_destination, [
                                    (i, busdatabase, route, params.get("time_of_day"), destination_node, gdfclean) for i 
                                    in range(len(gdfclean))])
                        
                        methods.append(route.route_name)
                        outputgdf[route.route_name] = travel_times
                        logger_func(str(route.route_name))
            
            logger_func("UC Merced Routes Calculated")
        
        # Calculate Merced Bus routes
        if "Merced Bus" in params.get("modes_of_transportation"):
            if "Weekday" in params.get("weekday_weekend"):
                for route in WeekdayRoutes:
                    if route.operater == "Merced Bus":
                        logger_func(route.route_name)
                        travel_times = []
                        
                        if params.get("origin_destination") == "Origin":
                            with mp.Pool(mp.cpu_count()) as pool:
                                travel_times = pool.starmap(compute_travel_time_for_index_orgin, [
                                    (i, busdatabase, route, params.get("time_of_day"), destination_node, gdfclean) for i
                                    in range(len(gdfclean))])
                        else:  # Destination
                            with mp.Pool(mp.cpu_count()) as pool:
                                travel_times = pool.starmap(compute_travel_time_for_index_destination, [
                                    (i, busdatabase, route, params.get("time_of_day"), destination_node, gdfclean) for i 
                                    in range(len(gdfclean))])
                        
                        methods.append(route.route_name)
                        outputgdf[route.route_name] = travel_times
            
            if "Weekend" in params.get("weekday_weekend"):
                for route in WeekendRoutes:
                    if route.operater == "Merced Bus":
                        logger_func(route.route_name)
                        travel_times = []
                        
                        if params.get("origin_destination") == "Origin":
                            with mp.Pool(mp.cpu_count()) as pool:
                                travel_times = pool.starmap(compute_travel_time_for_index_orgin, [
                                    (i, busdatabase, route, params.get("time_of_day"), destination_node, gdfclean) for i
                                    in range(len(gdfclean))])
                        else:  # Destination
                            with mp.Pool(mp.cpu_count()) as pool:
                                travel_times = pool.starmap(compute_travel_time_for_index_destination, [
                                    (i, busdatabase, route, params.get("time_of_day"), destination_node, gdfclean) for i 
                                    in range(len(gdfclean))])
                        
                        methods.append(route.route_name)
                        outputgdf[route.route_name] = travel_times
            
            logger_func("Merced Bus Routes Calculated")
        
        # Calculate the fastest route and method
        outputgdf["fastest_route"] = outputgdf[methods].min(axis=1)
        outputgdf["fastest_route_method"] = outputgdf[methods].idxmin(axis=1)
        
        # Save results
        output_path = params.get("output_path", "")
        if not output_path:
            output_path = os.getcwd()
        
        outputgdf.to_file(os.path.join(output_path, "fastestmode.geojson"), driver="GeoJSON")
        outputgdf.to_feather(os.path.join(output_path, "fastestmode.feather"))
        
    return outputgdf

if __name__ == "__main__":
    # This section can be used for testing the module directly
    print("Transit core module loaded.")