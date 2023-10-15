var map // Map
var markers = [] // Markers of the locations
var pose_markers = {} // Markers of the pose of the drones
var infoWindow // Info of the markers
var paths = [] // Routes
var n_vehicles = 0 // Number of current vehicles
const drone_icon = 'images/drone.ico' // Icon for the drone pose
var eventSourcePose // The surce to stream the UAVs pose
const check_list = [
  'n_vehicles',
  'max_flight_time',
  'velocity',
  'start_nodes',
  'end_nodes'
] // Input fields to check
