// Function to save the nodes
function saveNodes(event) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/save-nodes", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                console.log("Nodes saved")
            } else {
                console.error("Failed to save:", xhr.status);
            }
        }
    };
    xhr.send();
}

// Function to save the routes
function saveRoutes(event) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/save-routes", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                console.log("Routes saved")
            } else {
                console.error("Failed to save:", xhr.status);
            }
        }
    };
    xhr.send();
}

// Load the solver configuration defined in the yaml file
function saveTravelMode() {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/travel-mode", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    console.log("Travel mode successfully stored");
                } else {
                    console.error("Travel mode not valid: " + file, response.message);
                }
            } else {
                console.error("Failed to communicate with the server:", xhr.status);
            }
        }
    };
    // Send the file as the request body
    xhr.send("travelmode=" + encodeURIComponent(document.getElementById("travelmode").value));
}

saveTravelMode(); // At the start to load the default