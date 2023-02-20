var map = L.map('map').setView([46.056946, 14.505751], 8);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

// Fetch the coordinates from the server
fetch('/coords')
  .then(response => response.json())
  .then(coords => {


    // Loop through the coordinates and create a marker for each one
    coords.forEach(coord => {
      const { id, title, latitude, longitude } = coord;
      const marker = L.marker([latitude, longitude]).addTo(map);
      marker.bindPopup(`${title}`).openPopup();
    });
  });








//link
//   marker.bindPopup(`<a href="/post/${id}">Marker ${id}</a>`).openPopup();