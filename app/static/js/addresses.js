// To handle the address and depot boxes
function handleAddress (event, depot = false) {
  event.preventDefault()
  // Get the address value from the input field
  if (depot) {
    var addressInput = document.getElementById('depot')
    var color = 'blue'
  } else {
    var addressInput = document.getElementById('address')
    var color = 'red'
  }
  var address = addressInput.value
  addAddress(address, color, depot)
  // Clear the input field
  addressInput.value = ''
}

// To register an addres both in front and back ends
function addAddress (address, color, depot = false) {
  var xhr = new XMLHttpRequest()
  xhr.open('POST', '/handle-address', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText)
        if (response.success) {
          // Draw the marker
          if (response.index == 0 || response.index == markers.length) {
            addMarker(response.coordinates, response.index, color)
          } else {
          }
        } else {
          // Failed to convert address
          console.error('Failed to convert address:', response.message)
        }
      } else {
        console.error('Failed to register address:', xhr.status)
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
