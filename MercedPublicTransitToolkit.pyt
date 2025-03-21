import arcpy
import os
import transit_core

arcpy.env.addOutputsToMap = True
class Toolbox(object):
    def __init__(self):
        self.label = "Merced Public Transit Toolkit"
        self.alias = "Merced Public Transit Toolkit"
        self.tools = [MercedPublicTransitMap]

class MercedPublicTransitMap(object):
    def __init__(self):
        self.label = "Merced Public Transit Map"
        self.description = "This tool creates a map of public transit in Merced County."
        self.canRunInBackground = False
        self.params = arcpy.GetParameterInfo()

    def getParameterInfo(self):
        param0 = arcpy.Parameter(
            displayName = "Mode",
            name = "mode",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param0.filter.type = "ValueList"
        param0.filter.list = ["Fastest Mode", "Travel Time", "Public Transit Premium", "Transit Mode over Time","Walking Score", "Precompute Table"]
        param1 = arcpy.Parameter(
            displayName = "Geocode a region, use bounding box, or specify a node id for the bounding box",
            name = "region_mode",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param1.filter.type = "ValueList"
        param1.filter.list = ["Geocode Region", "Use Bounding Box", "Specify Node ID"]
        param1.value = "Use Bounding Box"
        param2 = arcpy.Parameter(
            displayName = "Region (Geocode)",
            name = "region_geocode",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input"
        )
        param2.value = "Merced, Merced County, California, USA"
        param3 = arcpy.Parameter(
            displayName = "Bounding Box",
            name = "region_extent",
            datatype = "GPExtent",
            parameterType = "Optional",
            direction = "Input"
        )
        param3.value = arcpy.Extent(-120.593,37.252, -120.337,37.38)
        param4 = arcpy.Parameter(
            displayName="Region Boundary (OSM ID)",
            name="region_OSMID",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"
        )
        param4.value= "r112291"
        param5 = arcpy.Parameter(
            displayName="Geocode a node, specify Lat,Long, or specify a node id for the point of interest",
            name="POI_Mode",
            datatype= "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param5.filter.type = "ValueList"
        param5.filter.list = ["Geocode a Point of Interest", "Specify Node ID"]
        param5.value = "Specify Node ID"
        param6 = arcpy.Parameter(
            displayName = "Point of Interest (OSM ID)",
            name = "POI_OSMID",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input",
            multiValue=False
        )
        param6.value = "n12162711342"
        param7 = arcpy.Parameter(
            displayName = "Point of Interest (Lat, Long)",
            name = "POI_lat_long",
            datatype = "GPPoint",
            parameterType = "Optional",
            direction = "Input",
        )
        param7.enabled = False
        param8 = arcpy.Parameter(
            displayName = "Point of Interest (Geocode)",
            name = "POI_geocode",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input",
        )
        param9 = arcpy.Parameter(
            displayName = "Origin or Destination",
            name = "origin_destination",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input"
        )
        param9.filter.type = "ValueList"
        param9.filter.list = ["Origin", "Destination"]
        param10 = arcpy.Parameter(
            displayName = "Modes of Transportation",
            name = "modes_of_transportation",
            datatype = "GPString",
            parameterType = "Required",
            direction = "Input",
            multiValue = True
        )
        param10.filter.type = "ValueList"
        param10.filter.list = ["Walking", "UC Bus", "Merced Bus"]
        param10.value = ["Walking", "UC Bus", "Merced Bus"]
        param11 = arcpy.Parameter(
            displayName = "Weekday or Weekend",
            name = "weekday_weekend",
            datatype = "GPString",
            parameterType = "Optional",
            direction = "Input",
            multiValue = True
        )
        param11.filter.type = "ValueList"
        param11.filter.list = ["Weekday", "Weekend"]
        param11.value = "Weekday"
        param12 = arcpy.Parameter(
            displayName = "Time of Day (Minutes Since Midnight)",
            name = "time_of_day",
            datatype = "GPLong",
            parameterType = "Optional",
            direction = "Input"
        )
        param12.value = 720
        param13 = arcpy.Parameter(
            displayName = "Use Caching",
            name = "use_caching",
            datatype = "GPBoolean",
            parameterType = "Optional",
            direction = "Input"
        )
        param13.value = False
        param14 = arcpy.Parameter(
            displayName = "Clean OSM Database",
            name = "clean_osm_database",
            datatype = "DEFile",
            parameterType = "Optional",
            direction = "Input"
        )
        param15 = arcpy.Parameter(
            displayName = "Precomputed Bus Database",
            name = "precomputed_bus_database",
            datatype = "DEFile",
            parameterType = "Optional",
            direction = "Input"
        )
        param15.filter.list = ["feather"]
        param16 = arcpy.Parameter(
            displayName="GraphML File",
            name="graphml_file",
            datatype="DEFile",
            parameterType="Optional",
            direction="Input"
        )
        param16.filter.list = ["graphml"]
        param17 = arcpy.Parameter(
            displayName = "Output Map",
            name = "output_map",
            datatype = "GPFeatureLayer",
            parameterType = "Derived",
            direction = "Output"
        )
        return [param0, param1, param2, param3, param4, param5, param6, param7, param8, param9, param10, param11, param12, param13, param14, param15,param16, param17]
    
    def isLicensed(self):
        return True
    
    def updateParameters(self, params):
        if params[0].value == "Precompute Table":
            params[13].enabled = False
            params[14].enabled = False
            params[15].enabled = False
            params[16].enabled = False
        if params[13].value == True:
            params[2].enabled = False
            params[3].enabled = False
            params[4].enabled = False
        if params[1].value == "Geocode Region":
            params[2].enabled = True
            params[3].enabled = False
            params[4].enabled = False
        elif params[1].value == "Use Bounding Box":
            params[2].enabled = False
            params[3].enabled = True
            params[4].enabled = False
        elif params[1].value == "Specify Node ID":
            params[2].enabled = False
            params[3].enabled = False
            params[4].enabled = True
        if params[5].value == "Geocode a Node":
            params[8].enabled = True
            #params[7].enabled = False
            params[6].enabled = False
        elif params[5].value == "Specify Lat,Long":
            params[6].enabled = False
            #params[7].enabled = True
            params[8].enabled = False
        elif params[5].value == "Specify Node ID":
            params[8].enabled = False
            #params[7].enabled = False
            params[6].enabled = True
        if params[10].values == ["Walking"]:
            params[11].enabled = False
            params[12].enabled = False
        else:
            params[11].enabled = True
            params[12].enabled = True
        return
    
    def updateMessages(self, params):
        if params[1].value == "Geocode Region" and params[2].value is None:
            params[2].setIDMessage("ERROR", 530)
        elif params[1].value == "Use Bounding Box" and params[3].value is None:
            params[3].setIDMessage("ERROR", 530)
        elif params[1].value == "Specify Node ID" and params[4].value is None:
            params[4].setIDMessage("ERROR", 530)
        if params[5].value == "Geocode a Node" and params[6].value is None:
            params[8].setIDMessage("ERROR", 530)
        elif params[5].value == "Specify Lat,Long" and params[7].value is None:
            params[7].setIDMessage("ERROR", 530)
        elif params[6].value == "Specify Node ID" and params[8].value is None:
            params[8].setIDMessage("ERROR", 530)
        if params[13].value == True and params[14].value:
            if not os.path.isfile(str(params[14].value)):
                params[14].setErrorMessage("File does not exist.", 1)
        if params[13].value == True and params[15].value:
            if not os.path.isfile(str(params[15].value)):
                params[15].setErrorMessage("File does not exist.", 1)
        if params[13].value == True and params[16].value:
            if not os.path.isfile(str(params[16].value)):
                params[16].setErrorMessage("File does not exist.", 1)
        return

    def execute(self, params, messages):
        """Execute the ArcPy toolbox by converting parameters and calling the core functionality"""
        
        # Log the parameters
        arcpy.AddMessage(f"Mode of transportation: {params[10].valueAsText}")
        
        # Convert ArcPy parameters to a dictionary for transit_core
        param_dict = {
            "mode": params[0].valueAsText,
            "region_mode": params[1].valueAsText,
            "region_geocode": params[2].valueAsText if params[2].enabled and params[2].value else None,
            "region_extent": {
                "xmin": params[3].value.XMin, 
                "ymin": params[3].value.YMin,
                "xmax": params[3].value.XMax,
                "ymax": params[3].value.YMax
            } if params[3].enabled and params[3].value else None,
            "region_OSMID": params[4].valueAsText if params[4].enabled and params[4].value else None,
            "POI_Mode": params[5].valueAsText,
            "POI_OSMID": params[6].valueAsText if params[6].enabled and params[6].value else None,
            "POI_lat_long": (params[7].value.X, params[7].value.Y) if params[7].enabled and params[7].value else None,
            "POI_geocode": params[8].valueAsText if params[8].enabled and params[8].value else None,
            "origin_destination": params[9].valueAsText,
            "modes_of_transportation": params[10].valueAsText.split(";") if params[10].value else [],
            "weekday_weekend": params[11].valueAsText.split(";") if params[11].value else [],
            "time_of_day": params[12].value if params[12].value else 720,
            "use_caching": params[13].value,
            "clean_osm_database": str(params[14].valueAsText) if params[14].value else None,
            "precomputed_bus_database": str(params[15].valueAsText) if params[15].value else None,
            "graphml_file": str(params[16].valueAsText) if params[16].value else None,
            "output_path": "E:/"  # Default output path - you might want to make this configurable
        }
        
        # Call the core functionality with ArcPy logging
        result = transit_core.process_transit_data(param_dict, logger_func=arcpy.AddMessage)
        
        return