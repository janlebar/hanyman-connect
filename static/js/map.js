// var map = L.map('map').setView([{{ longitude_localisation }}, {{ latitude_localisation }}], neki);

document.addEventListener("location", (event) => {
  const { latitude, longitude } = event.detail;

  var map = L.map('map').setView([latitude, longitude], 14);

  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  // Fetch the coordinates from the server
  //fetch('/coords')
  //  .then(response => response.json())
  //  .then(coords => {
  //
  //
  //    // Loop through the coordinates and create a marker for each one
  //    coords.forEach(coord => {
  //      const { id, title, latitude, longitude } = coord;
  //      const marker = L.marker([latitude, longitude]).addTo(map);
  //      marker.bindPopup(`${title}`).openPopup();
  //    });
  //  });

  // Loop through the coordinates and create a marker for each one
  coords.forEach(coord => {
  const { id, title, latitude, longitude } = coord;
  const marker = L.marker([latitude, longitude]).addTo(map);
  marker.bindPopup(`<a href="/post/${id}">${title}</a>`).openPopup();
  // marker.bindPopup(`<a href="/search?query=${title}">${title}</a>`).openPopup();
  });








  //link
  //   marker.bindPopup(`<a href="/post/${id}">Marker ${id}</a>`).openPopup();
}, false);