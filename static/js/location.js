  window.onload = function() {
    const status = document.querySelector('.status');




    const dispatchLocation = (longitude, latitude) => {
        const event = new CustomEvent("location", {detail: { latitude, longitude }});

        document.dispatchEvent(event);
    };

    const success = (position) => {
        dispatchLocation(position.coords.longitude, position.coords.latitude);
    }

    const error = () => {
        status.textContent = 'Unable to retrieve your location';
    }

    if (!longitude || !latitude) {
        navigator.geolocation.getCurrentPosition(success, error);
    } else {
        dispatchLocation(longitude, latitude);
    }
};
