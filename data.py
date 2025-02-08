from sgp4.api import Satrec
from astropy.time import Time
from astropy.coordinates import CartesianRepresentation
from astropy import units as u
import requests

# URL of the CSV data
url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=csv"

# Send a request to download the CSV file
response = requests.get(url)

# Save the CSV file locally
if response.status_code == 200:
    with open("satellite_data.csv", "wb") as file:
        file.write(response.content)
    print("Download complete: satellite_data.csv")
else:
    print("Failed to download file, status code:", response.status_code)


# List of satellites with their TLE data
satellite_data = file

# Function to calculate position for each satellite
def calculate_position(satellite):
    # Create a Satrec object from TLE data
    sat = Satrec.twoline2rv(satellite["line1"], satellite["line2"])
    
    # Get the current time (or any desired time)
    current_time = Time.now()  # You can set any specific time here
    
    # Convert the time to Julian date
    jd = current_time.jd
    
    # Propagate the satellite's position and velocity at the given time
    e, r, v = sat.propagate(current_time.jd1, current_time.jd2)
    
    # Convert position to Cartesian representation
    position = CartesianRepresentation(r)
    
    # Convert to more user-friendly coordinates like latitude, longitude, altitude
    lat = position.lat
    lon = position.lon
    altitude = position.distance
    
    # Print or return the satellite's position
    return {
        "name": satellite["name"],
        "latitude": lat,
        "longitude": lon,
        "altitude": altitude
    }

# Process all satellites in the database
satellite_positions = []
for satellite in satellite_data:
    position = calculate_position(satellite)
    satellite_positions.append(position)

# Output all satellite positions
for position in satellite_positions:
    print(f"Satellite: {position['name']}")
    print(f"Latitude: {position['latitude']}, Longitude: {position['longitude']}, Altitude: {position['altitude']}")
    print("-" * 40)
