// var map = L.map('map').setView([{{ longitude_localisation }}, {{ latitude_localisation }}], neki);

document.addEventListener("location", (event) => {
    const { latitude, longitude } = event.detail;
  
    var map = L.map('map').setView([latitude, longitude], 14);
  
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
  

    });