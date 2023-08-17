// Adds a marker to the map
function addMarker(coordinates, index, color = "red") {
    let svgMarker = { // Style of the marker
        path: "M-1.547 12l6.563-6.609-1.406-1.406-5.156 5.203-2.063-2.109-1.406 1.406zM0 0q2.906 0 4.945 2.039t2.039 4.945q0 1.453-0.727 3.328t-1.758 3.516-2.039 3.070-1.711 2.273l-0.75 0.797q-0.281-0.328-0.75-0.867t-1.688-2.156-2.133-3.141-1.664-3.445-0.75-3.375q0-2.906 2.039-4.945t4.945-2.039z",
        fillColor: color,
        fillOpacity: 1,
        strokeWeight: 0,
        rotation: 0,
        scale: 2,
        anchor: new google.maps.Point(0, 20),
    };
    if (index === 0 && markers.length !== 0) {
        markers[index].setMap(null);
    }
    if (index < markers.length && index != 0) {
        console.log("Marker already added");
        return 0;
    }
    var marker = new google.maps.Marker({
        position: { lat: coordinates[0], lng: coordinates[1] },
        map,
        title: index.toString(),
        label: index.toString(),
        icon: svgMarker
    });
    if (index === 0) {
        markers.splice(index, 1, marker);
    } else {
        markers.splice(index, 0, marker);
    }

    // The content of each marker
    marker.addListener("mouseover", () => {
        infoWindow.close();
        var link = document.createElement("deleteLink");
        link.href = "#";
        link.textContent = "Delete";
        link.style.color = "blue"
        link.addEventListener("click", function () {
            deleteMarker(parseInt(marker.getTitle()))
        });
        var container = document.createElement("div");
        var text = document.createElement("p");
        text.textContent = "LAT: " + coordinates[0].toFixed(2).toString() + " LNG: " + coordinates[1].toFixed(2).toString();
        container.appendChild(text);
        container.appendChild(link);
        infoWindow.setContent(container);
        infoWindow.open(marker.getMap(), marker);
    });
}

// Deletes a marker from the map
function deleteMarker(index, coordinates = null) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/delete-address", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.onreadystatechange = function () {
        if (xhr.readyState === XMLHttpRequest.DONE) {
            if (xhr.status === 200) {
                var response = JSON.parse(xhr.responseText);
                if (response.success) {
                    console.log("Address deleted successfully");
                    markers[index].setMap(null);
                    if (index !== 0) {
                        markers = [markers[0]];
                        getMap(response.coordinates); // To reorder the indexes
                    }
                } else {
                    // Failed to convert address
                    console.error("Failed to convert address:", response.message);
                }
            } else {
                // Failed communication with the server
                console.error("Failed to delete address:", xhr.status);
            }
        }
    };
    // Send the index as the request body
    xhr.send("index=" + encodeURIComponent(index));
}

// Function to draw the routes
function drawRoutes(routes_info) {
    var routes = routes_info["routes"];
    Object.entries(routes).forEach(([v_number, v_route]) => {
        let coordinates = v_route.coordinates;
        var flightPlanCoordinates = [];
        for (var coordinate of coordinates) {
            flightPlanCoordinates.push({ lat: coordinate[0], lng: coordinate[1] })
        }
        paths.push(new google.maps.Polyline({
            path: flightPlanCoordinates,
            geodesic: true,
            strokeColor: v_route.color,
            strokeOpacity: 1.0,
            strokeWeight: 5,
        }));
        paths[v_number].setMap(map);
    });

}