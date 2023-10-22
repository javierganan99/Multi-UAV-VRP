import { globalElements } from './globals.js'
import { deleteAllMarkers, drawProblemData } from './drawing.js'
export { loadProblemDefiniton }
// Load the problem definition from the yaml file and represent it in the frontend
function loadProblemDefiniton (event) {
  event.preventDefault()
  const xhr = new XMLHttpRequest()
  xhr.open('GET', '/load-problem', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        if (response.success) {
          console.log('Probem definition properly loaded')
          let toDisplay
          for (let i = 0; i < globalElements.checkList.length; i++) {
            if (globalElements.checkList.slice(1).includes(globalElements.checkList[i])) {
              if (Array.isArray(response.problem_data[globalElements.checkList[i]])) {
                toDisplay = response.problem_data[globalElements.checkList[i]].join(', ')
              }
              // TODO: Manage the error
            } else {
              toDisplay = response.problem_data[globalElements.checkList[i]]
            }
            document.getElementById(globalElements.checkList[i]).value = toDisplay
          }
          // Update number of vehicles
          globalElements.nVehicles = response.problem_data.n_vehicles
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
