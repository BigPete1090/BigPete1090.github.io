function initMap() {
    const map = L.map('map', {
        center: [35.5, -79.0],
        zoom: 4,
        maxZoom: 10,
        minZoom: 2
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        noWrap: true
    }).addTo(map);

    fetch('https://raw.githubusercontent.com/BigPete1090/BigPete1090/main/satellites.json')
        .then(response => response.json())
        .then(data => {
            if (!data.satellites || !Array.isArray(data.satellites)) {
                throw new Error("Invalid satellite data format.");
            }

            console.log("Satellite data loaded successfully.");

            data.satellites.forEach(satellite => {
                if (satellite.current_position && satellite.future_passes) {
                    let marker = L.marker([
                        satellite.current_position.lat,
                        satellite.current_position.lon
                    ]).addTo(map);
                    
                    marker.bindPopup(`
                        <h3>${satellite.name}</h3>
                        <p>Altitude: ${Math.round(satellite.current_position.altitude)} km</p>
                        <p>Timestamp: ${satellite.current_position.timestamp}</p>
                        <p><a href="${satellite.details_url}" target="_blank">Learn More</a></p>
                    `);

                    let pathCoordinates = [
                        [satellite.current_position.lat, satellite.current_position.lon]
                    ];

                    satellite.future_passes.forEach(pass => {
                        pathCoordinates.push([pass.lat, pass.lon]);
                    });

                    let lastPoints = pathCoordinates.slice(-2);
                    if (lastPoints.length === 2) {
                        let dx = lastPoints[1][1] - lastPoints[0][1];
                        let dy = lastPoints[1][0] - lastPoints[0][0];
                        
                        for (let i = 1; i <= 5; i++) {
                            pathCoordinates.push([
                                lastPoints[1][0] + dy * i,
                                lastPoints[1][1] + dx * i
                            ]);
                        }
                    }

                    let pathLine = L.polyline(pathCoordinates, {
                        color: 'blue',
                        weight: 2,
                        opacity: 0.8,
                        dashArray: '5, 10' 
                    }).addTo(map);

                    animateSatellite(marker, pathLine, pathCoordinates);
                }
            });
        })
        .catch(error => {
            console.error('Error loading satellite data:', error);
        });
}

function animateSatellite(marker, pathLine, pathCoords, index = 0) {
    if (index >= pathCoords.length) index = 0;

    marker.setLatLng(pathCoords[index]);
    pathLine.setLatLngs(pathCoords.slice(0, index + 1));

    setTimeout(() => {
        animateSatellite(marker, pathLine, pathCoords, index + 1);
    }, 100);
}
