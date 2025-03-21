#!/usr/bin/env python
import os
import sys
import transit_core
import geopandas
import networkx as nx
import osmnx
import re
from typing import Dict, List, Tuple, Optional, Union, Any, TypedDict, cast

class BoundingBox(TypedDict):
    xmin: float
    ymin: float
    xmax: float
    ymax: float

def print_banner() -> None:
    """Print a banner for the application"""
    print("="*80)
    print("Merced Public Transport Analysis Tool".center(80))
    print("="*80)
    print("This tool analyzes public transit in Merced County")
    print("="*80)

def validate_input(prompt: str, options: Optional[List[str]] = None, 
                  default: Optional[str] = None, allow_empty: bool = False) -> str:
    """Validate user input against a list of options
    
    Args:
        prompt (str): The prompt to display to the user
        options (list, optional): A list of valid options. If None, any input is valid.
        default (str, optional): Default value if user enters nothing
        allow_empty (bool): Whether empty input is allowed
        
    Returns:
        str: The validated user input
    """
    prompt_text = f"{prompt}"
    if options:
        prompt_text += f" [{'/'.join(options)}]"
    if default:
        prompt_text += f" (default: {default})"
    prompt_text += ": "
    
    while True:
        user_input = input(prompt_text).strip()
        
        if not user_input:
            if allow_empty:
                return ""
            if default:
                return default
            print("Input is required. Please try again.")
            continue
            
        if options and user_input not in options:
            print(f"Invalid input. Please choose from: {', '.join(options)}")
            continue
            
        return user_input

def validate_numeric_input(prompt: str, min_val: Optional[float] = None, 
                          max_val: Optional[float] = None, default: Optional[float] = None, 
                          allow_empty: bool = False) -> Optional[float]:
    """Validate numeric user input
    
    Args:
        prompt (str): The prompt to display to the user
        min_val (int/float, optional): Minimum valid value
        max_val (int/float, optional): Maximum valid value
        default (int/float, optional): Default value if user enters nothing
        allow_empty (bool): Whether empty input is allowed
        
    Returns:
        int/float: The validated numeric input
    """
    prompt_text = f"{prompt}"
    if default is not None:
        prompt_text += f" (default: {default})"
    prompt_text += ": "
    
    while True:
        user_input = input(prompt_text).strip()
        
        if not user_input:
            if allow_empty:
                return None
            if default is not None:
                return default
            print("Input is required. Please try again.")
            continue
            
        try:
            value = int(user_input)
            if min_val is not None and value < min_val:
                print(f"Value must be at least {min_val}")
                continue
            if max_val is not None and value > max_val:
                print(f"Value must be at most {max_val}")
                continue
            return float(value)
        except ValueError:
            try:
                value = float(user_input)
                if min_val is not None and value < min_val:
                    print(f"Value must be at least {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Value must be at most {max_val}")
                    continue
                return value
            except ValueError:
                print("Please enter a valid number")
                continue

def validate_file_path(prompt: str, must_exist: bool = True, 
                      default: Optional[str] = None, allow_empty: bool = False) -> Optional[str]:
    """Validate a file path
    
    Args:
        prompt (str): The prompt to display to the user
        must_exist (bool): Whether the file must exist
        default (str, optional): Default path if user enters nothing
        allow_empty (bool): Whether empty input is allowed
        
    Returns:
        str: The validated file path
    """
    prompt_text = f"{prompt}"
    if default:
        prompt_text += f" (default: {default})"
    prompt_text += ": "
    
    while True:
        user_input = input(prompt_text).strip()
        
        if not user_input:
            if allow_empty:
                return None
            if default:
                return default
            print("Input is required. Please try again.")
            continue
            
        if must_exist and not os.path.exists(user_input):
            print(f"File not found: {user_input}")
            continue
            
        return user_input

def validate_osm_id(prompt: str, default: Optional[str] = None, allow_empty: bool = False) -> Optional[str]:
    """Validate an OSM ID
    
    Args:
        prompt (str): The prompt to display to the user
        default (str, optional): Default OSM ID if user enters nothing
        allow_empty (bool): Whether empty input is allowed
        
    Returns:
        str: The validated OSM ID
    """
    prompt_text = f"{prompt}"
    if default:
        prompt_text += f" (default: {default})"
    prompt_text += ": "
    
    while True:
        user_input = input(prompt_text).strip()
        
        if not user_input:
            if allow_empty:
                return None
            if default:
                return default
            print("Input is required. Please try again.")
            continue
        
        # Validate OSM ID format (n for node, r for relation, w for way)
        if not re.match(r'^[nrw]\d+$', user_input):
            print("OSM ID must be in the format: n123456, r123456, or w123456")
            continue
            
        return user_input

def validate_bounding_box(prompt: str, default: Optional[BoundingBox] = None) -> BoundingBox:
    """Validate bounding box input
    
    Args:
        prompt (str): The prompt to display to the user
        default (dict, optional): Default bounding box
        
    Returns:
        dict: Dictionary with xmin, ymin, xmax, ymax
    """
    print(prompt)
    if default:
        print(f"Default: xmin={default['xmin']}, ymin={default['ymin']}, xmax={default['xmax']}, ymax={default['ymax']}")
    
    xmin = cast(float, validate_numeric_input("Enter minimum longitude (xmin)", -180, 180))
    ymin = cast(float, validate_numeric_input("Enter minimum latitude (ymin)", -90, 90))
    xmax = cast(float, validate_numeric_input("Enter maximum longitude (xmax)", -180, 180))
    ymax = cast(float, validate_numeric_input("Enter maximum latitude (ymax)", -90, 90))
    
    if xmin >= xmax:
        print("Warning: xmin must be less than xmax. Swapping values.")
        xmin, xmax = xmax, xmin
    
    if ymin >= ymax:
        print("Warning: ymin must be less than ymax. Swapping values.")
        ymin, ymax = ymax, ymin
    
    return {"xmin": xmin, "ymin": ymin, "xmax": xmax, "ymax": ymax}

def validate_multi_choice(prompt: str, options: List[str], 
                         default: Optional[List[str]] = None, allow_multiple: bool = True) -> List[str]:
    """Validate multi-choice input
    
    Args:
        prompt (str): The prompt to display to the user
        options (list): List of valid options
        default (list, optional): Default selections
        allow_multiple (bool): Whether multiple selections are allowed
        
    Returns:
        list: List of selected options
    """
    print(f"{prompt} [{', '.join(options)}]")
    if default:
        print(f"Default: {', '.join(default)}")
    
    if allow_multiple:
        print("Enter multiple selections separated by commas, or type 'all' for all options.")
        user_input = input("> ").strip()
        
        if not user_input and default:
            return default
        
        if user_input.lower() == 'all':
            return options
            
        selections = [s.strip() for s in user_input.split(',')]
        valid_selections = [s for s in selections if s in options]
        
        if not valid_selections:
            print("No valid selections made. Using default.")
            return default if default else []
            
        return valid_selections
    else:
        return [validate_input("Enter selection", options, default[0] if default else None)]

def main() -> None:
    """Main function to run the transit analysis tool"""
    print_banner()
    
    # Collect parameters from the user
    print("\nStep 1: Select the analysis mode")
    mode = validate_input(
        "Select the analysis mode", 
        options=["Fastest Mode", "Travel Time", "Public Transit Premium", "Transit Mode over Time", "Walking Score", "Precompute Table"],
        default="Fastest Mode"
    )
    
    print("\nStep 2: Define the region")
    region_mode = validate_input(
        "How do you want to define the region?",
        options=["Geocode Region", "Use Bounding Box", "Specify Node ID"],
        default="Use Bounding Box"
    )
    
    region_geocode: Optional[str] = None
    region_extent: Optional[BoundingBox] = None
    region_OSMID: Optional[str] = None
    
    if region_mode == "Geocode Region":
        region_geocode = validate_input(
            "Enter the region name to geocode",
            default="Merced, Merced County, California, USA"
        )
    elif region_mode == "Use Bounding Box":
        default_bbox: BoundingBox = {"xmin": -120.593, "ymin": 37.252, "xmax": -120.337, "ymax": 37.38}
        region_extent = validate_bounding_box(
            "Define the bounding box coordinates",
            default=default_bbox
        )
    elif region_mode == "Specify Node ID":
        region_OSMID = validate_osm_id(
            "Enter the OSM ID for the region boundary",
            default="r112291"
        )
    
    print("\nStep 3: Define the point of interest")
    POI_Mode = validate_input(
        "How do you want to define the point of interest?",
        options=["Geocode a Point of Interest", "Specify Node ID"],
        default="Specify Node ID"
    )
    
    POI_OSMID: Optional[str] = None
    POI_geocode: Optional[str] = None
    
    if POI_Mode == "Geocode a Point of Interest":
        POI_geocode = validate_input(
            "Enter the point of interest to geocode",
            default="UC Merced, Merced, California, USA"
        )
    elif POI_Mode == "Specify Node ID":
        POI_OSMID = validate_osm_id(
            "Enter the OSM Node ID for the point of interest",
            default="n12162711342"
        )
    
    print("\nStep 4: Configure additional parameters")
    origin_destination = validate_input(
        "Is the point of interest the origin or the destination?",
        options=["Origin", "Destination"],
        default="Origin"
    )
    
    modes_of_transportation = validate_multi_choice(
        "Select modes of transportation",
        options=["Walking", "UC Bus", "Merced Bus"],
        default=["Walking", "UC Bus", "Merced Bus"]
    )
    
    weekday_weekend: List[str] = []
    time_of_day: Optional[int] = None
    
    if "Walking" not in modes_of_transportation or len(modes_of_transportation) > 1:
        weekday_weekend = validate_multi_choice(
            "Select day type",
            options=["Weekday", "Weekend"],
            default=["Weekday"]
        )
        
        time_of_day = int(cast(float, validate_numeric_input(
            "Enter time of day (minutes since midnight, e.g. 720 for 12:00 PM)",
            min_val=0,
            max_val=1440,
            default=720
        )))
    
    print("\nStep 5: Configure caching options")
    use_caching = validate_input("Use cached data?", options=["yes", "no"], default="no") == "yes"
    
    clean_osm_database: Optional[str] = None
    precomputed_bus_database: Optional[str] = None
    graphml_file: Optional[str] = None
    
    if use_caching:
        clean_osm_database = validate_file_path(
            "Enter path to clean OSM database (.feather file)",
            must_exist=True,
            allow_empty=True
        )
        
        precomputed_bus_database = validate_file_path(
            "Enter path to precomputed bus database (.feather file)",
            must_exist=True,
            allow_empty=True
        )
        
        graphml_file = validate_file_path(
            "Enter path to GraphML file (.graphml file)",
            must_exist=True,
            allow_empty=True
        )
    
    output_path = validate_file_path(
        "Enter output directory for results",
        must_exist=False,
        default=os.getcwd(),
        allow_empty=False
    ) or os.getcwd()
    
    # If directory doesn't exist, create it
    if not os.path.exists(output_path):
        try:
            os.makedirs(output_path)
            print(f"Created output directory: {output_path}")
        except OSError:
            print(f"Failed to create output directory: {output_path}")
            output_path = os.getcwd()
            print(f"Using current directory instead: {output_path}")
    
    # Create parameters dictionary
    params: Dict[str, Any] = {
        "mode": mode,
        "region_mode": region_mode,
        "region_geocode": region_geocode,
        "region_extent": region_extent,
        "region_OSMID": region_OSMID,
        "POI_Mode": POI_Mode,
        "POI_OSMID": POI_OSMID,
        "POI_geocode": POI_geocode,
        "origin_destination": origin_destination,
        "modes_of_transportation": modes_of_transportation,
        "weekday_weekend": weekday_weekend,
        "time_of_day": time_of_day,
        "use_caching": use_caching,
        "clean_osm_database": clean_osm_database,
        "precomputed_bus_database": precomputed_bus_database,
        "graphml_file": graphml_file,
        "output_path": output_path
    }
    
    # Print configuration summary
    print("\nConfiguration Summary:")
    for key, value in params.items():
        if key != "output_path" and value is not None:
            print(f"{key}: {value}")
    print(f"Output path: {output_path}")
    
    # Confirm and run
    confirm = validate_input("Run analysis with these parameters?", options=["yes", "no"], default="yes")
    
    if confirm == "yes":
        print("\nRunning transit analysis. This may take a while...\n")
        result = transit_core.process_transit_data(params)
        print("\nAnalysis completed!")
        print(f"Results saved to: {output_path}")
    else:
        print("Analysis cancelled.")
        
if __name__ == "__main__":
    main()