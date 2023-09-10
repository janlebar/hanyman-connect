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

//     let marker = null;

//     // Function to add or replace the marker on the map at the clicked location
//     function addOrReplaceMarker(e) {
//         if (marker) {
//             // Remove the existing marker from the map
//             map.removeLayer(marker);
//         }
//         marker = L.marker(e.latlng).addTo(map);
//         marker.bindPopup("Marker at Clicked Location");
//     }

//     // Add a click event listener to the map
//     map.on('click', addOrReplaceMarker);
// });







// document.addEventListener("location", (event) => {
//     const { latitude, longitude } = event.detail;

//     var map = L.map('map').setView([latitude, longitude], 14);

//     L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
//         attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
//     }).addTo(map);

//     let marker = null;

//     // Function to add or replace the marker on the map at the clicked location
//     function addOrReplaceMarker(e) {
//         if (marker) {
//             // Remove the existing marker from the map
//             map.removeLayer(marker);
//         }
//         marker = L.marker(e.latlng).addTo(map);
//         marker.bindPopup("Marker at Clicked Location");

//         // Retrieve latitude and longitude of the clicked location
//         debugger
//         const clickedLatitude = e.latlng.lat;
//         const clickedLongitude = e.latlng.lng;
//         // alert(`Latitude: ${clickedLatitude}, Longitude: ${clickedLongitude}`);
//     }

//     // Add a click event listener to the map
//     map.on('click', addOrReplaceMarker);
// });








document.addEventListener("location", (event) => {
    const { latitude, longitude } = event.detail;

    var map = L.map('map').setView([latitude, longitude], 14);

    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);






debugger
    let clickedLatitude = null;
    let clickedLongitude = null;
    let marker = null;
    
    function addOrReplaceMarker(e) {
      if (marker) {
        // Remove the existing marker from the map
        map.removeLayer(marker);
      }
      
      marker = L.marker(e.latlng).addTo(map);
      marker.bindPopup("Marker at Clicked Location");
    
      // Update latitude and longitude
      clickedLatitude = e.latlng.lat;
      clickedLongitude = e.latlng.lng;
    
      // Call a function or perform any action you need with the updated values
      handleMarkerChange(clickedLatitude, clickedLongitude);
    }
debugger
    function handleMarkerChange(latitude, longitude) {
      // This function will be called whenever the marker location changes.
      // You can perform any actions here with the updated latitude and longitude.
      console.log(`Latitude: ${latitude}, Longitude: ${longitude}`);
    }
    
    // Add a click event listener to the map
    map.on('click', addOrReplaceMarker);

});



