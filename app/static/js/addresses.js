import { addMarker } from './drawing.js'
import { globalElements } from './globals.js'
export { handleAddress, addAddress, changeAddressAltitude }
// To handle the address and depot boxes
function handleAddress (event, depot = false) {
  event.preventDefault()
  // Get the address value from the input field
  let addressInput, color
  if (depot) {
    addressInput = document.getElementById('depot')
    color = 'blue'
  } else {
    addressInput = document.getElementById('address')
    color = 'red'
  }
  const address = addressInput.value
  addAddress(address, color, depot)
  // Clear the input field
  addressInput.value = ''
}

// To register an addres both in front and back ends
function addAddress (address, color, depot = false) {
  const xhr = new XMLHttpRequest()
  xhr.open('POST', '/handle-address', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        if (response.success && (response.index === 0 || response.index === globalElements.markers.length)) {
          // Draw the marker
          addMarker(response.coordinates, response.index, color)
        } else {
          // Failed to convert address
          console.error('Failed to convert address:', response.message)
        }
      } else {
        console.error('Failed to communicate with the server:', xhr.status)
      }
    }
  }
  // Send the address as the request body
  xhr.send(
    'address=' +
      encodeURIComponent(address) +
      '&depot=' +
      encodeURIComponent(depot)
  )
}

function changeAddressAltitude (index, altitude) {
  const xhr = new XMLHttpRequest()
  xhr.open('POST', '/change-altitude', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        if (response.success) {
          console.log('Altitude of index ' + index + ' changed to ' + altitude)
        } else {
          // Failed to convert address
          console.error('Failed to change altitude:', response.message)
        }
      } else {
        console.error('Failed to communicate with the server:', xhr.status)
      }
    }
  }
  // Send the address as the request body
  xhr.send(
    'index=' +
      encodeURIComponent(index) +
      '&altitude=' +
      encodeURIComponent(altitude)
  )
}
