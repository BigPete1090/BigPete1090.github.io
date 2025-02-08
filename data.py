from sgp4.api import Satrec
from astropy.time import Time
from astropy.coordinates import CartesianRepresentation
from astropy import units as u

# List of satellites with their TLE data
satellite_data = [
    {
        "name": "ISS (ZARYA)",
        "line1": "1 25544U 98067A   22314.22666767  .00002799  00000-0  62276-4 0  9993",
        "line2": "2 25544  51.6414  17.2241 0004257  68.3855 291.6687 15.50106675465559"
    },
    {
        "name": "Hubble Space Telescope",
        "line1": "1 20580U 90037B   22314.24960123  .00003884  00000-0  81076-4 0  9995",
        "line2": "2 20580  28.4722  79.3312 0009789  53.6154  35.6976 15.42456725838984"
    }
    # Add more satellites here...
]

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
