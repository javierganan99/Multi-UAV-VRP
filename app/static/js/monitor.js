import { globalElements } from './globals.js'
export { updatePoseMarkers }
// Function to update pose markers
function updatePoseMarkers (numVehicles) {
  // Remove excess pose markers for non-existing vehicle
  for (let i = numVehicles; i < globalElements.poseMarkers.length; i++) {
    if (globalElements.poseMarkers[i]) {
      delete globalElements.poseMarkers[i]
    }
  }
  // Add new pose markers if number of vehicles increased
  for (let i = 0; i < numVehicles; i++) {
    if (!globalElements.poseMarkers[i]) {
      globalElements.poseMarkers[i] = []
    }
  }
}
