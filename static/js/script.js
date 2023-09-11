// This script fetches the user's GPS coordinates and fills in the location field.
window.addEventListener('load', () => {
    if ('geolocation' in navigator) {
        navigator.geolocation.getCurrentPosition(function (position) {
            var latitude = position.coords.latitude;
            var longitude = position.coords.longitude;
            var locationField = document.getElementById('location');
            locationField.value = latitude + ', ' + longitude;
        });
    } else {
        console.error('Geolocation is not supported by this browser.');
    }
});

m.on('zoomend', function() {
    var currentZoom = m.getZoom();
    if (currentZoom >= someZoomThreshold) {
        // Remove clustered markers and add individual markers
    } else {
        // Remove individual markers and add clustered markers
    }
});