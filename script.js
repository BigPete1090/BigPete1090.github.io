// Initialize the map
const map = L.map('map').setView([0, 0], 2); // Default view set to 0,0 (center of the world)

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Fetch satellite data from the JSON file (or API)
fetch('satellites.json')
  .then(response => response.json())
  .then(data => {
    data.satellites.forEach(satellite => {
      // Add a marker for each satellite
      const marker = L.marker([satellite.lat, satellite.lon]).addTo(map);
      
      // When a marker is clicked, show a popup with satellite details
      marker.bindPopup(`
        <h3>${satellite.name}</h3>
        <p>Launch Date: ${satellite.launch_date}</p>
        <p>Details: <a href="${satellite.details_url}" target="_blank">Learn More</a></p>
      `);
    });
  })
  .catch(error => console.error('Error loading satellite data:', error));

