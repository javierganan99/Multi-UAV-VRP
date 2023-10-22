import { globalElements } from './globals.js'
import { stringNumbersToList } from './auxiliary.js'
import { deleteAllMarkers, drawProblemData, drawRoutes } from './drawing.js'
export { generateRoutes }
// Function to check if the depots are in the markers
function checkDepotsInMarkers (depots) {
  for (const depot of depots) {
    if (depot > globalElements.markers.length - 1 || depot < 0) {
      return false
    }
  }
  return true
}

// Function to check the values of the problem
// TODO: CHECK MIN VALUE
function noWarning (name, warning, minValue = 0) {
  let numbers2load
  if (name === 'n_vehicles') {
    numbers2load = 1
  } else {
    numbers2load = globalElements.nVehicles[0]
  }
  const element = document.getElementById(name)
  const elementWarning = document.getElementById(warning)
  const newElement = stringNumbersToList(element.value, numbers2load)
  console.log('new element ' + newElement)
  if (
    newElement === false ||
    (globalElements.checkList.slice(3).includes(name) &&
      !checkDepotsInMarkers(newElement))
  ) {
    elementWarning.classList.remove('hidden')
    return false
  } else {
    elementWarning.classList.add('hidden')
    if (name === 'n_vehicles') {
      globalElements.nVehicles = newElement
    }
    return newElement
  }
}

// Function to generate the routes
function generateRoutes (event) {
  event.preventDefault()
  const xhr = new XMLHttpRequest()
  xhr.open('POST', '/create-routes', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  // Check for any invalid value
  let returnedParam
  for (let i = 0; i < globalElements.checkList.length; i++) {
    returnedParam = noWarning(globalElements.checkList[i], globalElements.checkList[i] + '-warning')
    if (!returnedParam) {
      return false
    }
  }
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        if (response.success) {
          // Delete the current problem data
          deleteAllMarkers()
          // Draw problem data
          drawProblemData(response.problem_data)
          // Draw the routes
          drawRoutes(response.routes)
        } else {
          console.error('Route generation failed:', response.message)
        }
      } else {
        console.error('Failed to communicate with the server:', xhr.status)
      }
    }
  }

  // Send the parameters
  let url = ''
  for (let i = 0; i < globalElements.checkList.length - 1; i++) {
    url +=
      globalElements.checkList[i] +
      '=' +
      encodeURIComponent(document.getElementById(globalElements.checkList[i]).value) +
      '&'
  }
  url +=
    'travel_mode' +
    '=' +
    encodeURIComponent(document.getElementById('travel_mode').value) +
    '&'
  url +=
    globalElements.checkList[globalElements.checkList.length - 1] +
    '=' +
    encodeURIComponent(
      document.getElementById(globalElements.checkList[globalElements.checkList.length - 1]).value
    )
  xhr.send(url)
}
