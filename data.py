import json
import requests
import pandas as pd
import numpy as np
from sgp4.api import Satrec
from astropy.time import Time

# URL of the CSV data from CelesTrak
url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv"

# Download and load CSV data
response = requests.get(url)
if response.status_code == 200:
    with open("satellite_data.csv", "wb") as file:
        file.write(response.content)
    print("Download complete: satellite_data.csv")
else:
    print("Failed to download file, status code:", response.status_code)
    exit()

# Load CSV into pandas DataFrame
df = pd.read_csv("satellite_data.csv")

# Function to calculate satellite position
def calculate_position(row):
    sat = Satrec()
    sat.sgp4init(
        72,  # Ephemeris type
        row["EPHEMERIS_TYPE"],
        row["NORAD_CAT_ID"],
        row["BSTAR"],
        row["MEAN_MOTION_DOT"],
        row["MEAN_MOTION_DDOT"],
        row["EPOCH"],
        row["INCLINATION"],
        row["RA_OF_ASC_NODE"],
        row["ECCENTRICITY"],
        row["ARG_OF_PERICENTER"],
        row["MEAN_ANOMALY"],
        row["MEAN_MOTION"]
    )

    # Get current time in Julian format
    current_time = Time.now()
    jd, fr = divmod(current_time.jd, 1)

    # Propagate the satellite position
    e, r, v = sat.sgp4(jd, fr)
    if e != 0:
        return None  # Skip if propagation fails

    x, y, z = r
    lat = np.degrees(np.arctan2(z, np.sqrt(x**2 + y**2)))
    lon = np.degrees(np.arctan2(y, x))
    altitude = np.linalg.norm(r) - 6371  # Earth radius correction

    return {
        "name": row["OBJECT_NAME"],
        "lat": round(lat, 6),
        "lon": round(lon, 6),
        "launch_date": row.get("EPOCH", "Unknown"),  # Approximate launch time
        "details_url": f"https://www.n2yo.com/satellite/?s={row['NORAD_CAT_ID']}"
    }

# Generate JSON structure
satellite_list = [calculate_position(row) for _, row in df.iterrows() if calculate_position(row)]
json_data = {"satellites": satellite_list[:10]}  # Limit to 10 satellites for readability

# Save to a JSON file
with open("satellites.json", "w") as json_file:
    json.dump(json_data, json_file, indent=2)

print("Updated JSON saved: satellites.json")
