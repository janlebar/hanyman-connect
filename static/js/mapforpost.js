// var map = L.map('map').setView([{{ longitude_localisation }}, {{ latitude_localisation }}], neki);

// document.addEventListener("location", (event) => {
//     const { latitude, longitude } = event.detail;
  
//     var map = L.map('map').setView([latitude, longitude], 14);
  
//     L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
//         attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
//     }).addTo(map);
  

//     });















    // var map = L.map('map').setView([{{ longitude_localisation }}, {{ latitude_localisation }}], neki);

// document.addEventListener("location", (event) => {
//     const { latitude, longitude } = event.detail;
  
//     var map = L.map('map').setView([latitude, longitude], 14);
  
//     L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
//         attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
//     }).addTo(map);
  
//             // Add a click event listener to the map
//             map.on('click', function (e) {
//                 const { lat, lng } = e.latlng;
//                 // Send the coordinates to the Flask backend
//                 fetch('/store_coordinates', {
//                     method: 'POST',
//                     headers: {
//                         'Content-Type': 'application/json',
//                     },
//                     body: JSON.stringify({ latitude: lat, longitude: lng }),
//                 })
//                 .then(response => response.json())
//                 .then(data => {
//                     console.log(data.message);
//                 })
//                 .catch(error => {
//                     console.error('Error:', error);
//                 });
//             });

//     });









// document.addEventListener("location", (event) => {
//     const { latitude, longitude } = event.detail;

//     var map = L.map('map').setView([latitude, longitude], 14);

//     L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
//         attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
//     }).addTo(map);

//     // Function to add a marker to the map at the clicked location
//     function addMarker(e) {
//         const marker = L.marker(e.latlng).addTo(map);
//         marker.bindPopup("Marker at Clicked Location");
//     }

//     // Add a click event listener to the map
//     map.on('click', addMarker);
// });







document.addEventListener("location", (event) => {
    const { latitude, longitude } = event.detail;

    var map = L.map('map').setView([latitude, longitude], 14);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    let marker = null;

    // Function to add or replace the marker on the map at the clicked location
    function addOrReplaceMarker(e) {
        if (marker) {
            // Remove the existing marker from the map
            map.removeLayer(marker);
        }
        marker = L.marker(e.latlng).addTo(map);
        marker.bindPopup("Marker at Clicked Location");
    }

    // Add a click event listener to the map
    map.on('click', addOrReplaceMarker);
});
