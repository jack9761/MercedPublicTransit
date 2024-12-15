# Merced Public Transit
This repository contains code to calculate statistics about Merced's public transit system. The main product of this is a ArcGis Pro toolkit (MercedPublicTransitToolkit.pyt). 

Right now this project is incomplete, the project likely will not work without modification. The project will be updated to improve functionality and fix bugs. 

To install, first create a conda environment based on environment.yml
Next you can open the toolkit in ArcGis Pro. Right now only "fastest mode" is implemented.
The road network, graphml, and feature databases are provided as feathes, use those to prevent having to recompute them. 
Make sure to select a building that would be in a database when selecting the point of interest.
The output is a geojson and feather file on your E drive. You should change this to a better location. 
You can then import the geojson file into ArcGIS. 