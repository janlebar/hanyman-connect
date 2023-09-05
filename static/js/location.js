window.onload = function() {
    const status = document.querySelector('.status');
    debugger
    const dispatchLocation = (longitude, latitude) => {
        const event = new CustomEvent("location", { detail: { latitude, longitude } });
        document.dispatchEvent(event);
    };

    const success = (position) => {
        dispatchLocation(position.coords.longitude, position.coords.latitude);
    };

    const error = () => {
        status.textContent = 'Unable to retrieve your location';
    };

    if (!longitude || !latitude) {
        navigator.geolocation.getCurrentPosition(success, error);
    } else {
        dispatchLocation(longitude, latitude);
    }
    
    debugger
    document.addEventListener("location", (event) => {
        document.getElementById("latitude").value = event.detail.latitude;
        document.getElementById("longitude").value = event.detail.longitude;

        // Store the location in the session
        sessionStorage.setItem('latitude', event.detail.latitude);
        sessionStorage.setItem('longitude', event.detail.longitude);
    });
};










