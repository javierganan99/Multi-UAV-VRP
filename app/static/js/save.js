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