// Load the monitor.js script after the simulation.js to load its functions previously

// Function to update pose markers
function updatePoseMarkers(numVehicles) {

    // Remove excess pose markers for non-existing vehicle
    for (var i = numVehicles; i < pose_markers.length; i++) {
        if (pose_markers[i]) {
            delete pose_markers[i];
        }
    }

    // Add new pose markers if number of vehicles increased
    for (var i = 0; i < numVehicles; i++) {
        if (!pose_markers[i]) {
            pose_markers[i] = [];
        }
    }
}