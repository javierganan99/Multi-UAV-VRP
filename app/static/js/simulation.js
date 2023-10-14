// To start the simulation
function startSimulation() {
    // Toggle the text of the Simulation button
    var sim_button = document.getElementById("simulation");
    sim_button.textContent = "Stop Simulation";
    // Toggle function associated
    sim_button.onclick = stopSimulation;
    // Update pose_markers of n_vehicles
    updatePoseMarkers(n_vehicles);
    eventSourcePose = new EventSource('/simulation');
    eventSourcePose.onmessage = function(event) {
        const data = JSON.parse(event.data);
        if (data === null) {
            // TODO: SOLVE!
            console.log(data);
            stopSimulation();
        }
        for (let i = 0; i < data.length; i++) {
            ml = pose_markers[i].length;
            if (ml >= 1){
                pose_markers[i].push(addPoseMarker({lat: data[i]["lat"], lng: data[i]["lon"]}, drone_icon)); // Add new position
                pose_markers[i][ml - 1].setMap(null); // Oclude last marker
                pose_markers[i].slice(ml - 1, 1); // Eliminate marker from list
            } else {
                pose_markers[i].push(addPoseMarker({lat: data[i]["lat"], lng: data[i]["lon"]}, drone_icon));
            }
          }
    };
}

// To stop the simulation
function stopSimulation() {
    // Toggle the text of the Simulation button
    var sim_button = document.getElementById("simulation");
    sim_button.textContent = "Simulation";
    // Toggle function associated
    sim_button.onclick = startSimulation;
    if (eventSourcePose) {
        eventSourcePose.close();
    }
    // Delete the UAVs' markers
    pml = Object.keys(pose_markers).length;
    for (let i = 0; i < Object.keys(pose_markers).length; i++) {
        for (let j = 0; j < pose_markers[i].length; j++) {
            pose_markers[i][j].setMap(null); // Oclude marker
        }
    }
    pose_markers = {}
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/stop-simulation", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    console.log("Simulation stop signal sended!");
                } else {
                    console.error("Error stopping the simulation: " + file, response.message);
                }
            } else {
                console.error("Failed to communicate with the server:", xhr.status);
            }
        }
    };
    xhr.send();
}