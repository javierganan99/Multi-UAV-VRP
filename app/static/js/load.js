// Depends on monitor.js, that must be included before this file in index.html
// Load the problem definition from the yaml file and represent it in the frontend
function loadProblemDefiniton (event) {
  event.preventDefault()
  var xhr = new XMLHttpRequest()
  xhr.open('POST', '/load-problem', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText)
        if (response.success) {
          console.log('Probem definition properly loaded')
          for (let i = 0; i < check_list.length; i++) {
            if (check_list.slice(1).includes(check_list[i])) {
              if (Array.isArray(response.problem_data[check_list[i]])) {
                to_display = response.problem_data[check_list[i]].join(', ')
              }
              // TODO: Manage the error
            } else {
              to_display = response.problem_data[check_list[i]]
            }
            document.getElementById(check_list[i]).value = to_display
          }
          // Update number of vehicles
          n_vehicles = response.problem_data['n_vehicles']
          // Delete the current problem data
          deleteAllMarkers()
          // Draw problem data
          drawProblemData(response.problem_data)
        } else {
          // Some error in the definition of the problem
          console.error(response.message)
        }
      } else {
        // Error when communicating with the server
        console.error('Failed communicate with server:', xhr.status)
      }
    }
  }
  // Send the file as the request body
  xhr.send()
}

// Load the solver configuration defined in the yaml file
function loadSolverConfiguration (
  event,
  file = 'cfg/solver_configuration.yaml'
) {
  event.preventDefault()
  var xhr = new XMLHttpRequest()
  xhr.open('POST', '/load-solver', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        var response = JSON.parse(xhr.responseText)
        if (response.success) {
          console.log('Solver parameters successfully registered')
        } else {
          console.error(
            'Solver parameters no valid, check the configuration file: ' + file,
            response.message
          )
        }
      } else {
        console.error('Failed to communicate with the server:', xhr.status)
      }
    }
  }
  // Send the file as the request body
  xhr.send('file=' + encodeURIComponent(file))
}
