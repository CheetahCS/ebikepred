import requests as r
from datetime import datetime, timezone 
import json
BIKEPOINTS_URL = "https://api.tfl.gov.uk/BikePoint"

def get_bike_points():
    response = r.get(BIKEPOINTS_URL)
    response.raise_for_status()
    return response.json()

def process_bike_point(bikepoint, current_time):

    raw_add_props = bikepoint.get('additionalProperties', [])

    add_props = {}
    for item in raw_add_props:
        if isinstance(item, dict) and 'key' in item and 'value' in item:
            add_props[item['key']] = item['value']

    def safe_int(value, default=0):
        try:
            if value is None or str(value).strip() == "":
                return default
            return int(float(value))
        except (ValueError, TypeError):
            return default

    processed = {
        "timestamp": current_time,
        "station_id": bikepoint.get('id', 'UNKNOWN'),
        "station_name": bikepoint.get('commonName', 'Unknown Station'),
        "latitude": bikepoint.get('lat', 0.0),
        "longitude": bikepoint.get('lon', 0.0),
        "total_bikes": safe_int(add_props.get('NbBikes', 0)),
        "ebikes": safe_int(add_props.get('NbEBikes', 0)),
        "standard_bikes": safe_int(add_props.get('NbStandardBikes', 0)),
        "total_docks": safe_int(add_props.get('NbDocks', 0)),
        "empty_docks": safe_int(add_props.get('NbEmptyDocks', 0))
    }

    processed["broken_docks"] = processed["total_docks"] - (processed["empty_docks"] + processed["total_bikes"])

    # Prevent negative broken docks
    processed["broken_docks"] = max(0, processed["broken_docks"])

    return processed

def process_bike_points(bike_points):
    current_time = datetime.now(timezone.utc).isoformat()
    processed = [process_bike_point(point, current_time) for point in bike_points]
    return processed


