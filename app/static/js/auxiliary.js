// Function to check the values of the problem
function warning(name, warning, min_value = 0) {
    var element = document.getElementById(name);
    var elementWarning = document.getElementById(warning);
    if (element.value.trim() === '' || isNaN(parseInt(element.value.trim())) || parseInt(element.value.trim()) <= min_value) {
        elementWarning.classList.remove('hidden');
        event.preventDefault();
        return true;
    } else {
        elementWarning.classList.add('hidden');
        return false;
    }
}

// Function to reset the problem information
function reset(event) {
    event.preventDefault();
    var check_list = ["n_vehicles", "max_flight_time", "capacity", "velocity"];
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/reset", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                // Reset parameters
                for (let i = 0; i < check_list.length; i++) {
                    document.getElementById(check_list[i]).value = 0;
                }
                // Delete markers
                for (let i = 0; i < markers.length; i++) {
                    markers[i].setMap(null);
                }
                markers = [markers[0]];
                // Delete routes
                for (let i = 0; i < paths.length; i++) {
                    paths[i].setMap(null);
                }
                paths = [];
                console.log("Reset done.")
            } else {
                console.error("Failed to reset:", xhr.status);
            }
        }
    };
    xhr.send();
}