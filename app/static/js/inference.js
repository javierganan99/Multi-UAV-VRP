// Function to check if the depots are in the markers
function check_depots_in_markers(depots) {
    for (var depot of depots) {
        if (depot > (markers.length - 1) || depot < 0) {
            return false
        }
    }
    return true
}


// Function to check the values of the problem
// TODO: CHECK MIN VALUE
function no_warning(name, warning, min_value = 0) {
    if (name == "n_vehicles") {
         var numbers_to_load = 1;
    } else {
        numbers_to_load = n_vehicles;
    }
    var element = document.getElementById(name);
    var elementWarning = document.getElementById(warning);
    var new_element = stringNumbersToList(element.value, numbers_to_load);
    if ((!new_element) || (check_list.slice(3).includes(name) && !check_depots_in_markers(new_element))) {
        elementWarning.classList.remove('hidden');
        return false;
    } else {
        elementWarning.classList.add('hidden');
        if (name == "n_vehicles") {
            n_vehicles = new_element;
        }
        return new_element;
    }
}

// Function to generate the routes
function generateRoutes(event) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-routes", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    // Check for any invalid value
    var returned_param;
    for (let i = 0; i < check_list.length; i++) {
        returned_param = no_warning(check_list[i], check_list[i] + "-warning")
        if (!returned_param) {
            return false
        }
    }
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    // Delete the current problem data
                    deleteAllMarkers();
                    // Draw problem data
                    drawProblemData(response.problem_data);
                    // Draw the routes
                    drawRoutes(response.routes);
                } else {
                    console.error("Route generation failed:", response.message);
                }
            } else {
                console.error("Failed to communicate with the server:", xhr.status);
            }
        }
    };

    // Send the parameters
    url = ""
    for (let i = 0; i < check_list.length - 1; i++) {
        url += check_list[i] + "=" + encodeURIComponent(document.getElementById(check_list[i]).value) + "&";
    }
    url += check_list[check_list.length - 1] + "=" + encodeURIComponent(document.getElementById(check_list[check_list.length - 1]).value);
    xhr.send(url);
}