// Depends on monitor.js, that must be included before this file in index.html 
// Load the problem definition from the yaml file and represent it in the frontend
function loadProblemDefiniton(event, file = "cfg/problem_definition.yaml") {
    event.preventDefault();
    var check_list = ["n_vehicles", "max_flight_time", "capacity", "velocity"];
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/load-problem", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    console.log("Probem definition properly loaded");
                    for (let i = 0; i < check_list.length; i++) {
                        document.getElementById(check_list[i]).value = response.problem_data[check_list[i]];
                    }
                    addMarker(response.problem_data["coord_inds"][0][0], response.problem_data["coord_inds"][0][1], "blue")
                    // Update number of streams
                    updateNumStreams(response.problem_data["n_vehicles"]);
                    for (let i = 1; i < response.problem_data["addresses"].length; i++) {
                        addMarker(response.problem_data["coord_inds"][i][0], response.problem_data["coord_inds"][i][1], "red")
                    }
                } else {
                    // Some error in the definition of the problem
                    console.error(response.message);
                }
            } else {
                // Error when communicating with the server
                console.error("Failed communicate with server:", xhr.status);
            }
        }
    };
    // Send the file as the request body
    xhr.send("file=" + encodeURIComponent(file));
}

// Load the solver configuration defined in the yaml file
function loadSolverConfiguration(event, file = "cfg/solver_configuration.yaml") {
    event.preventDefault();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/load-solver", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    console.log("Solver parameters successfully registered");
                } else {
                    console.error("Solver parameters no valid, check the configuration file: " + file, response.message);
                }
            } else {
                console.error("Failed to communicate with the server:", xhr.status);
            }
        }
    };
    // Send the file as the request body
    xhr.send("file=" + encodeURIComponent(file));
}