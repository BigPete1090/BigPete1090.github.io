// Initialize the map centered at (0, 0) with zoom level 2
const map = L.map('map', {
  center: [0, 0],  // Center the map at coordinates (0, 0)
  zoom: 2,  // Set the initial zoom level
  maxZoom: 3  // Set the maximum zoom out level (adjust this value as needed)
});

// Set the OpenStreetMap tiles for the map background
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Fetch satellite data from satellites.json
fetch('satellites.json')
  .then(response => response.json())
  .then(data => {
    data.satellites.forEach(satellite => {
      // Create a marker for each satellite, using latitude and longitude
      const marker = L.marker([satellite.lat, satellite.lon]).addTo(map);
      
      // Bind a popup with satellite information
      marker.bindPopup(`
        <h3>${satellite.name}</h3>
        <p>Launch Date: ${satellite.launch_date}</p>
        <p><a href="${satellite.details_url}" target="_blank">Learn More</a></p>
      `);
    });
  })
  .catch(error => console.error('Error loading satellite data:', error));

