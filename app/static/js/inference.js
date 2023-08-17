// Function to generate the routes
function generateRoutes(event) {
    event.preventDefault();
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/create-routes", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    var check_list = ["n_vehicles", "max_flight_time", "capacity", "velocity"]
    // Check for any invalid value
    for (let i = 0; i < check_list.length; i++) {
        if (warning(check_list[i], check_list[i] + "-warning")) {
            return false
        }
    }
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    let routes = response.routes;
                    drawRoutes(routes);
                    console.log("Route generation successful");
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