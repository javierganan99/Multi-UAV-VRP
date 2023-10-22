import { globalElements } from './globals.js'
import { addMarker } from './drawing.js'
// Function to get the initial globalElements.mapGoogle
export function getMap (coordinates = null) {
  if (coordinates == null) {
    const coordinatesList = document.getElementById('map-center')
    coordinates = JSON.parse(coordinatesList.getAttribute('coordinates'))
  }
  const mapOptions = {
    center: { lat: coordinates[0][0], lng: coordinates[0][1] },
    zoom: 12
  }
  // Create the map
  globalElements.mapGoogle = new google.maps.Map(document.getElementById('map'), mapOptions)
  // Info window to share between markers
  globalElements.infoWindow = new google.maps.InfoWindow()
  // Listener to add a marker when the map is clicked
  google.maps.event.addListener(globalElements.mapGoogle, 'click', event => {
    const xhr = new XMLHttpRequest()
    xhr.open('POST', '/handle-address', true)
    xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
    // Create the data to send with the request (if needed)
    const address = [event.latLng.lat(), event.latLng.lng()]
    // Send the address as the request body
    xhr.send(
      'address=' +
        encodeURIComponent(address) +
        '&depot=' +
        encodeURIComponent(false)
    )
    // Handle the response
    xhr.onreadystatechange = function () {
      if (xhr.readyState === XMLHttpRequest.DONE) {
        if (xhr.status === 200) {
          const response = JSON.parse(xhr.responseText)
          if (response.success) {
            console.log('Address registered successfully')
            // Draw the marker
            addMarker(response.coordinates, response.index)
          } else {
            // Failed to convert address
            console.error('Failed to convert address:', response.message)
          }
        } else {
          // Failed communication with the server
          console.error('Failed to execute frontend action:', xhr.status)
        }
      }
    }
  })
}
