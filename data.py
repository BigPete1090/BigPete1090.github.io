from sgp4.api import Satrec
from sgp4.api import SatrecArray
from astropy.time import Time
import requests
import pandas as pd
import numpy as np

# URL of the CSV data
url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv"

# Download the CSV file
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

# Function to calculate position for a satellite
def calculate_position(row):
    # Create a Satrec object using the TLE parameters
    sat = Satrec()
    sat.sgp4init(
        72,  # Ephemeris type (72 = standard SGP4)
        row["EPHEMERIS_TYPE"],  # Ephemeris type from dataset
        row["NORAD_CAT_ID"],  # NORAD catalog ID
        row["BSTAR"],  # Drag term
        row["MEAN_MOTION_DOT"],  # First derivative of mean motion
        row["MEAN_MOTION_DDOT"],  # Second derivative of mean motion
        row["EPOCH"],  # Epoch time in Julian format
        row["INCLINATION"],  # Inclination (degrees)
        row["RA_OF_ASC_NODE"],  # Right Ascension of Ascending Node (degrees)
        row["ECCENTRICITY"],  # Eccentricity (unitless)
        row["ARG_OF_PERICENTER"],  # Argument of Perigee (degrees)
        row["MEAN_ANOMALY"],  # Mean Anomaly (degrees)
        row["MEAN_MOTION"],  # Mean Motion (revolutions per day)
    )
    
    # Get current time in Julian format
    current_time = Time.now()
    jd, fr = divmod(current_time.jd, 1)  # Separate Julian date and fraction

    # Propagate the satellite
    e, r, v = sat.sgp4(jd, fr)  # Returns position (r) and velocity (v)

    if e != 0:
        print(f"Error computing satellite position: {e}")
        return None

    # Convert position from km to more readable format
    x, y, z = r  # Position vector in km
    lat = np.degrees(np.arctan2(z, np.sqrt(x**2 + y**2)))  # Approximate latitude
    lon = np.degrees(np.arctan2(y, x))  # Approximate longitude
    altitude = np.linalg.norm(r) - 6371  # Subtract Earth's radius (6371 km)

    return {
        "name": row["OBJECT_NAME"],
        "latitude": lat,
        "longitude": lon,
        "altitude": altitude
    }

# Process all satellites
satellite_positions = []
for _, row in df.iterrows():
    pos = calculate_position(row)
    if pos:
        satellite_positions.append(pos)

# Output all satellite positions
for position in satellite_positions[:10]:  # Show only the first 10 for brevity
    print(f"Satellite: {position['name']}")
    print(f"Latitude: {position['latitude']:.2f}, Longitude: {position['longitude']:.2f}, Altitude: {position['altitude']:.2f} km")
    print("-" * 40)
