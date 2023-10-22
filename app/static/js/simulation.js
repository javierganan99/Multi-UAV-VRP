import { globalElements } from './globals.js'
import { updatePoseMarkers } from './monitor.js'
import { addPoseMarker } from './drawing.js'
export { startSimulation, stopSimulation }
// To start the simulation
function startSimulation () {
  // Toggle the text of the Simulation button
  const simButton = document.getElementById('simulation')
  simButton.textContent = 'Stop Simulation'
  // Toggle function associated
  simButton.onclick = stopSimulation
  // Update poseMarkers of nVehicles
  updatePoseMarkers(globalElements.nVehicles)
  globalElements.eventSourcePose = new EventSource('/simulation')
  globalElements.eventSourcePose.onmessage = function (event) {
    if (event.data === 'None') {
      stopSimulation()
      return
    }
    const data = JSON.parse(event.data)
    for (let i = 0; i < data.length; i++) {
      const ml = globalElements.poseMarkers[i].length
      if (ml >= 1) {
        globalElements.poseMarkers[i].push(
          addPoseMarker(
            { lat: data[i].lat, lng: data[i].lon },
            globalElements.droneIcon
          )
        ) // Add new position
        globalElements.poseMarkers[i][ml - 1].setMap(null) // Oclude last marker
        globalElements.poseMarkers[i].slice(ml - 1, 1) // Eliminate marker from list
      } else {
        globalElements.poseMarkers[i].push(
          addPoseMarker(
            { lat: data[i].lat, lng: data[i].lon },
            globalElements.droneIcon
          )
        )
      }
    }
  }
}

// To stop the simulation
function stopSimulation () {
  // Toggle the text of the Simulation button
  const simButton = document.getElementById('simulation')
  simButton.textContent = 'Simulation'
  // Toggle function associated
  simButton.onclick = startSimulation
  if (globalElements.eventSourcePose) {
    globalElements.eventSourcePose.close()
  }
  // Delete the UAVs' markers
  for (let i = 0; i < Object.keys(globalElements.poseMarkers).length; i++) {
    for (let j = 0; j < globalElements.poseMarkers[i].length; j++) {
      globalElements.poseMarkers[i][j].setMap(null) // Oclude marker
    }
  }
  globalElements.poseMarkers = {}
  const xhr = new XMLHttpRequest()
  xhr.open('POST', '/stop-simulation', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        if (response.success) {
          console.log('Simulation stop signal sended!')
        } else {
          console.error(
            'Error stopping the simulation: ' +
            response.message
          )
        }
      } else {
        console.error('Failed to communicate with the server:', xhr.status)
      }
    }
  }
  xhr.send()
}
