// Input fields to check
let globalElements = {}

globalElements.mapGoogle = null // Map
globalElements.markers = [] // Markers of the locations
globalElements.poseMarkers = {} // Markers of the pose of the drones
globalElements.infoWindow = null // Info of the markers
globalElements.paths = [] // Routes
globalElements.nVehicles = 0 // Number of current vehicles
globalElements.droneIcon = 'images/drone.ico' // Icon for the drone pose
globalElements.eventSourcePose = null // The surce to stream the UAVs pose
globalElements.checkList = [
  'n_vehicles',
  'max_flight_time',
  'velocity',
  'start_nodes',
  'end_nodes'
]

export { globalElements }
