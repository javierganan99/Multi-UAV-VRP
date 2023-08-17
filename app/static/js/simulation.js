// To start the simulation
function startSimulation() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/start-simulation", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    // Reset the elements of the streaming
                    vehicleImages = {};
                    vehicleSockets = {};
                    console.log("Simulation ended successfully!")
                } else {
                    console.error("Error starting the simulation: " + file, response.message);
                }
            } else {
                console.error("Failed to communicate with the server:", xhr.status);
            }
        }
    };
    xhr.send();
}

// To stop the simulation
function stopSimulation() {
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