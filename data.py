import requests
import pandas as pd
import numpy as np
from sgp4.api import Satrec, WGS84
from astropy.time import Time
import json
from datetime import datetime, timedelta
import time

LAT_MIN = 34
LAT_MAX = 37
LON_MIN = -86  
LON_MAX = -74  

TIME_WINDOW = 180  
TIME_STEPS = 36    

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bool):
            return str(obj)  
        return super().default(obj)

def normalize_longitude(lon):
    """Normalize longitude to -180 to 180 range."""
    lon = lon % 360
    if lon > 180:
        lon -= 360
    return lon

def is_in_region(lat, lon):
    """Check if the position is within the specified geographic boundaries."""
    lon = normalize_longitude(lon)
    return (LAT_MIN <= lat <= LAT_MAX) and (LON_MIN <= lon <= LON_MAX)

def safe_float(value):
    try:
        return float(value.strip()) if isinstance(value, str) else float(value)
    except (ValueError, AttributeError):
        return 0.0

def safe_int(value):
    try:
        return int(float(value.strip())) if isinstance(value, str) else int(value)
    except (ValueError, AttributeError):
        return 0

def calculate_position(sat, jd, fr):
    """Calculate position for a satellite at a specific time."""
    try:
        e, r, v = sat.sgp4(jd, fr)
        
        if e != 0 or not r or not v:
            return None
            
        x, y, z = r
        lat = np.degrees(np.arctan2(z, np.sqrt(x**2 + y**2)))
        lon = np.degrees(np.arctan2(y, x))
        altitude = (np.sqrt(x**2 + y**2 + z**2) - 6371.0)
        
        return {
            "lat": round(lat, 6),
            "lon": normalize_longitude(lon),
            "altitude": round(altitude, 2)
        }
    except Exception:
        return None

def initialize_satellite(row):
    """Initialize a Satrec object with the satellite's parameters."""
    try:
        sat = Satrec()
        
        epoch_time = pd.to_datetime(row["EPOCH"])
        jd = Time(epoch_time).jd
        
        norad_id = safe_int(row["NORAD_CAT_ID"])
        bstar = safe_float(row["BSTAR"])
        ndot = safe_float(row["MEAN_MOTION_DOT"]) / (1440.0)
        nddot = safe_float(row["MEAN_MOTION_DDOT"]) / (1440.0 * 1440.0)
        ecco = safe_float(row["ECCENTRICITY"])
        argpo = safe_float(row["ARG_OF_PERICENTER"])
        inclo = safe_float(row["INCLINATION"])
        mo = safe_float(row["MEAN_ANOMALY"])
        no_kozai = safe_float(row["MEAN_MOTION"]) / (1440.0)
        nodeo = safe_float(row["RA_OF_ASC_NODE"])

        sat.sgp4init(
            WGS84,
            'a',
            norad_id,
            jd - 2433281.5,
            bstar,
            ndot,
            nddot,
            ecco,
            argpo,
            inclo,
            mo,
            no_kozai,
            nodeo
        )
        
        return sat, norad_id
    except Exception as e:
        print(f"Error initializing satellite {row['OBJECT_NAME']}: {str(e)}")
        return None, None

def predict_satellite_path(row):
    """Predict satellite positions over time window and check if it passes through region."""
    try:
        sat, norad_id = initialize_satellite(row)
        if not sat:
            return None

        current_time = Time.now()
        
        current_pos = calculate_position(sat, current_time.jd, 0.0)
        if not current_pos:
            return None

        time_step = TIME_WINDOW / TIME_STEPS
        future_positions = []
        
        for i in range(TIME_STEPS):
            minutes_from_now = i * time_step
            future_jd = current_time.jd + (minutes_from_now / 1440.0)
            
            pos = calculate_position(sat, future_jd, 0.0)
            if pos:
                future_positions.append({
                    "lat": pos["lat"],
                    "lon": pos["lon"],
                    "altitude": pos["altitude"],
                    "minutes_from_now": round(minutes_from_now, 1)
                })

        positions_in_region = [pos for pos in future_positions if is_in_region(pos["lat"], pos["lon"])]
        
        if positions_in_region or is_in_region(current_pos["lat"], current_pos["lon"]):
            return {
                "name": row["OBJECT_NAME"],
                "norad_id": norad_id,
                "current_position": {
                    "lat": current_pos["lat"],
                    "lon": current_pos["lon"],
                    "altitude": current_pos["altitude"],
                    "timestamp": current_time.iso,
                    "in_region": str(is_in_region(current_pos["lat"], current_pos["lon"]))  
                },
                "future_passes": positions_in_region,
                "details_url": f"https://www.n2yo.com/satellite/?s={norad_id}"
            }
        
        return None

    except Exception as e:
        print(f"Error processing {row['OBJECT_NAME']}: {str(e)}")
        return None

if __name__ == "__main__":
    print(f"Starting download of satellite data...")
    response = requests.get("https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv")
    
    if response.status_code != 200:
        print(f"Failed to download file, status code: {response.status_code}")
        exit()
    
    with open("satellite_data.csv", "wb") as file:
        file.write(response.content)
    print("Download complete: satellite_data.csv")
    
    print("Loading CSV data into DataFrame...")
    df = pd.read_csv("satellite_data.csv")
    print(f"Loaded {len(df)} rows from the CSV file.")
    
    print(f"\nCalculating satellite positions and predicting paths over {TIME_WINDOW} minutes...")
    satellite_list = []
    total_satellites = len(df)
    start_time = time.time()
    
    for idx, row in df.iterrows():
        sat_data = predict_satellite_path(row)
        
        if sat_data:
            satellite_list.append(sat_data)
        
        if (idx + 1) % max(1, total_satellites // 20) == 0:
            progress = (idx + 1) / total_satellites * 100
            print(f"Progress: {progress:.1f}% ({idx + 1}/{total_satellites})")
            print(f"Satellites found that pass through region: {len(satellite_list)}")
    
    if satellite_list:
        final_data = {
            "satellites": satellite_list,
            "timestamp": datetime.utcnow().isoformat(),
            "total_processed": total_satellites,
            "satellites_in_region": len(satellite_list),
            "region": {
                "lat_min": LAT_MIN,
                "lat_max": LAT_MAX,
                "lon_min": LON_MIN,
                "lon_max": LON_MAX
            },
            "prediction_window_minutes": TIME_WINDOW,
            "processing_time": round(time.time() - start_time, 2)
        }
        
        print(f"\nFinal Results:")
        print(f"Total satellites processed: {total_satellites}")
        print(f"Satellites passing through region: {len(satellite_list)}")
        print(f"Processing time: {final_data['processing_time']} seconds")
        
        print("\nSaving satellite data to satellites.json...")
        with open("satellites.json", "w") as json_file:
            json.dump(final_data, json_file, indent=2, cls=CustomJSONEncoder)
        print("Final results saved: satellites.json")
    else:
        print("No satellites found in the specified region. Exiting...")
        exit()
