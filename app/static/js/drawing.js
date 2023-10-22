import { globalElements } from './globals.js'
import { changeAddressAltitude } from './addresses.js'
export { drawRoutes, addMarker, addPoseMarker, deleteMarker, deleteAllMarkers, drawProblemData }
// Adds a marker to the globalElements.mapGoogle
function addMarker (coordinates, index, color = 'red') {
  const svgMarker = {
    // Style of the marker
    path: 'M-1.547 12l6.563-6.609-1.406-1.406-5.156 5.203-2.063-2.109-1.406 1.406zM0 0q2.906 0 4.945 2.039t2.039 4.945q0 1.453-0.727 3.328t-1.758 3.516-2.039 3.070-1.711 2.273l-0.75 0.797q-0.281-0.328-0.75-0.867t-1.688-2.156-2.133-3.141-1.664-3.445-0.75-3.375q0-2.906 2.039-4.945t4.945-2.039z',
    fillColor: color,
    fillOpacity: 1,
    strokeWeight: 0,
    rotation: 0,
    scale: 2,
    anchor: new google.maps.Point(0, 20)
  }
  if (index < globalElements.markers.length && index !== 0) {
    console.log('Marker already added')
    return 0
  }
  const marker = new google.maps.Marker({
    position: {
      lat: coordinates[0],
      lng: coordinates[1],
      alt: coordinates.length === 3 ? coordinates[3] : 40
    },
    map: globalElements.mapGoogle,
    title: index.toString(),
    label: index.toString(),
    icon: svgMarker
  })
  globalElements.markers.push(marker) // Add marker
  // The content of each marker
  marker.addListener('mouseover', () => {
    globalElements.infoWindow.close()
    const deleteButton = document.createElement('button')
    deleteButton.classList.add('small-blue-button')
    deleteButton.textContent = 'Delete'
    deleteButton.addEventListener('click', function () {
      deleteMarker(parseInt(marker.getTitle()))
    })
    const textContainer = document.createElement('div')
    textContainer.style.display = 'flex'
    const text = document.createElement('p')
    text.style.marginRight = '4px'
    text.textContent =
      'LAT: ' +
      coordinates[0].toFixed(2).toString() +
      ' LNG: ' +
      coordinates[1].toFixed(2).toString() +
      ' ALT: '
    const inputAlt = document.createElement('input')
    inputAlt.style.width = '50px'
    inputAlt.style.padding = 0
    inputAlt.type = 'number'
    inputAlt.step = 0.1
    inputAlt.value = coordinates.length === 3 ? coordinates[2] : 40
    // Event listener to change the altitude
    inputAlt.addEventListener('input', function () {
      changeAddressAltitude(index, inputAlt.value)
      if (coordinates.length === 2) {
        coordinates.push(inputAlt.value)
      } else {
        coordinates[2] = inputAlt.value
      }
    })
    textContainer.appendChild(text)
    textContainer.appendChild(inputAlt)
    const deleteButtonContainer = document.createElement('div')
    deleteButtonContainer.appendChild(deleteButton)
    const container = document.createElement('div')
    container.appendChild(textContainer)
    container.appendChild(deleteButtonContainer)
    container.style.display = 'flex'
    container.style.flexDirection = 'column'
    globalElements.infoWindow.setContent(container)
    globalElements.infoWindow.open(marker.getMap(), marker)
  })
}

// Deletes a marker from the globalElements.mapGoogle
function deleteMarker (index) {
  const xhr = new XMLHttpRequest()
  xhr.open('POST', '/delete-address', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        if (response.success) {
          console.log('Address deleted successfully')
          for (let i = 0; i < globalElements.markers.length; i++) {
            globalElements.markers[i].setMap(null)
          }
          globalElements.markers = []
          drawProblemData(response.problem_data) // To reorder the indexes
        } else {
          // Failed to convert address
          console.error('Failed to convert address:', response.message)
        }
      } else {
        // Failed communication with the server
        console.error('Failed to delete address:', xhr.status)
      }
    }
  }
  // Send the index as the request body
  xhr.send('index=' + encodeURIComponent(index))
}

function deleteAllMarkers () {
  for (let i = 0; i < globalElements.markers.length; i++) {
    globalElements.markers[i].setMap(null)
  }
  globalElements.markers = []
}

// Function to draw the routes
function drawRoutes (routesInfo) {
  const routes = routesInfo.routes
  Object.entries(routes).forEach(([vNumber, vRoute]) => {
    const coordinates = vRoute.coordinates
    const flightPlanCoordinates = []
    for (const coordinate of coordinates) {
      flightPlanCoordinates.push({ lat: coordinate[0], lng: coordinate[1] })
    }
    globalElements.paths.push(
      new google.maps.Polyline({
        path: flightPlanCoordinates,
        geodesic: true,
        strokeColor: vRoute.color,
        strokeOpacity: 1.0,
        strokeWeight: 5
      })
    )
    globalElements.paths[vNumber].setMap(globalElements.mapGoogle)
  })
}

// Adds a drone pose marker to the map
function addPoseMarker (coordinates, icon) {
  return new google.maps.Marker({
    position: coordinates,
    map: globalElements.mapGoogle,
    icon
  })
}

// Display markers
function drawProblemData (problemData) {
  for (let i = 0; i < problemData.addresses.length; i++) {
    if (
      problemData.start_nodes.includes(i) &&
      problemData.end_nodes.includes(i)
    ) {
      // Both Departure and Arrival Depot
      addMarker(problemData.addresses[i], i, 'black')
    } else if (problemData.start_nodes.includes(i)) {
      // Departure depot
      addMarker(problemData.addresses[i], i, 'blue')
    } else if (problemData.end_nodes.includes(i)) {
      // Arrival depot
      addMarker(problemData.addresses[i], i, 'purple')
    } else {
      // To visit node
      addMarker(problemData.addresses[i], i, 'red')
    }
  }
}
