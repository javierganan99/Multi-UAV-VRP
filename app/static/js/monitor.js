// Load the monitor.js script after the simulation.js to load its functions previously

// Function to update image elements
function updateImageElements(numStreams) {
    var imageContainer = document.getElementById('image-container');

    // Remove excess images if number of streams is reduced
    for (var i = numStreams; i < vehicleImages.length; i++) {
        if (vehicleImages[i]) {
            imageContainer.removeChild(vehicleImages[i]);
            delete vehicleImages[i];
        }
    }

    // Add new images if number of streams is increased
    for (var i = 0; i < numStreams; i++) {
        if (!vehicleImages[i]) {
            var img = document.createElement('img');
            img.id = 'vehicle-image-' + i;
            imageContainer.appendChild(img);
            vehicleImages[i] = img;
        }
    }
}

// Function to connect to vehicles
function connectToVehicles(numStreams) {
    console.log("Connect to vehicles activated!")
    // Disconnect from vehicles if number of streams is reduced
    for (var i = numStreams; i < vehicleSockets.length; i++) {
        if (vehicleSockets[i]) {
            vehicleSockets[i].close();
            delete vehicleSockets[i];
        }
    }

    // Connect to vehicles and set up listeners for new images
    for (var i = 0; i < numStreams; i++) {
        if (!vehicleSockets[i]) {
            (function (i) {
                var socket = io.connect("/vehiclesns");
                socket.on('image_stream' + i.toString(), function (imageData) {
                    console.log("stream received " + i.toString())
                    var img = vehicleImages[i];
                    img.src = 'data:image/jpeg;base64,' + imageData.frame;
                    // Resize the image
                    img.onload = function () {
                        var MAX_WIDTH = 200;
                        var MAX_HEIGHT = 200;

                        // Maintain aspect ratio
                        var width = img.width;
                        var height = img.height;

                        if (width > height) {
                            if (width > MAX_WIDTH) {
                                height *= MAX_WIDTH / width;
                                width = MAX_WIDTH;
                            }
                        } else {
                            if (height > MAX_HEIGHT) {
                                width *= MAX_HEIGHT / height;
                                height = MAX_HEIGHT;
                            }
                        }

                        // Set the new dimensions
                        img.width = width;
                        img.height = height;
                    };
                });
                vehicleSockets[i] = socket;
            })(i);
        }
    }
}

// Function to update number of streams
function updateNumStreams(numStreams) {
    updateImageElements(numStreams);
    connectToVehicles(numStreams);
}


// Function to make the pop-up window draggable
function makeDraggable(element) {
    var pos1 = 0, pos2 = 0, pos3 = 0, pos4 = 0;
    element.onmousedown = dragMouseDown;

    function dragMouseDown(e) {
        e = e || window.event;
        e.preventDefault();
        pos3 = e.clientX;
        pos4 = e.clientY;
        document.onmouseup = closeDragElement;
        document.onmousemove = elementDrag;
    }

    function elementDrag(e) {
        e = e || window.event;
        e.preventDefault();
        pos1 = pos3 - e.clientX;
        pos2 = pos4 - e.clientY;
        pos3 = e.clientX;
        pos4 = e.clientY;
        element.style.top = (element.offsetTop - pos2) + "px";
        element.style.left = (element.offsetLeft - pos1) + "px";
    }

    function closeDragElement() {
        document.onmouseup = null;
        document.onmousemove = null;
    }
}

// Function to open the pop-up window
function openPopup() {

    startSimulation();
    // Display the pop-up window
    var popup = document.getElementById("popup");
    popup.style.display = "block";

    // Make the pop-up window draggable
    makeDraggable(popup);

    // Update the number of strings
    // Number of strings
    var numStreams = document.getElementById("n_vehicles").value;
    console.log("OPENED POP UP! The number of streams are " + numStreams.toString())
    updateNumStreams(numStreams);
}

// Function to close the pop-up window
function closePopup() {

    stopSimulation();
    // Hide the pop-up window
    var popup = document.getElementById("popup");
    popup.style.display = "none";

    // Clear the image container
    var imageContainer = document.getElementById("image-container");
    imageContainer.innerHTML = "";
}

// Event listener for the button click
document.getElementById("simulation").addEventListener("click", openPopup);

// Event listener for the close button click
document.getElementById("popup-close").addEventListener("click", closePopup);