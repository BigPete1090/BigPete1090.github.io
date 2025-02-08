document.addEventListener("DOMContentLoaded", function () {
    let mapContainer = document.getElementById("map");
    mapContainer.style.display = "none";  // Hide the map initially

    // Add event listener to the "View Map" button
    document.getElementById("viewMapBtn").addEventListener("click", function () {
        mapContainer.style.display = "block";  // Show the map container
        initMap();  // Initialize the map when button is clicked
    });
});

function initMap() {
    // Initialize the map centered at (0, 0) with zoom level 2
    const map = L.map('map', {
        center: [0, 0],  
        zoom: 2,  
        maxZoom: 5,  
        worldCopyJump: false  // Prevents world duplication when zooming out
    });

    // Set the OpenStreetMap tiles for the map background
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        noWrap: true
    }).addTo(map);

    // Fetch satellite data from satellites.json
    fetch('satellites.json')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (!data.satellites || !Array.isArray(data.satellites)) {
                throw new Error("Invalid satellite data format.");
            }

            // Add markers for each satellite
            data.satellites.forEach(satellite => {
                if (typeof satellite.lat === 'number' && typeof satellite.lon === 'number') {
                    // Create a marker for each satellite
                    const marker = L.marker([satellite.lat, satellite.lon]).addTo(map);

                    // Bind a popup with satellite information
                    marker.bindPopup(`
                        <h3>${satellite.name}</h3>
                        <p>Launch Date: ${satellite.launch_date}</p>
                        <p><a href="${satellite.details_url}" target="_blank">Learn More</a></p>
                    `);
                } else {
                    console.warn(`Invalid coordinates for satellite: ${satellite.name}`);
                }
            });
        })
        .catch(error => console.error('Error loading satellite data:', error));
}
