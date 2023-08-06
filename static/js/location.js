  window.onload = function() {
    const status = document.querySelector('.status');
    let longitude;
    let latitude;

    const success = (position) => {
        longitude = position.coords.longitude;
        latitude = position.coords.latitude;
        document.getElementById("longitude").value = longitude;
        document.getElementById("latitude").value = latitude;
    }

    const error = () => {
        status.textContent = 'Unable to retrieve your location';
    }

    navigator.geolocation.getCurrentPosition(success, error);
};




