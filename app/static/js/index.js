import { handleAddress } from './addresses.js'
import { reset } from './auxiliary.js'
import { generateRoutes } from './inference.js'
import { startSimulation } from './simulation.js'
import { loadProblemDefiniton } from './load.js'
import { getMap } from './map_creation.js'
import { saveNodes, saveRoutes } from './save.js'

const exports = {
  handleAddress,
  reset,
  generateRoutes,
  startSimulation,
  loadProblemDefiniton,
  getMap,
  saveNodes,
  saveRoutes
}

const exportsArray = [
  'handleAddress', 'reset', 'generateRoutes', 'startSimulation',
  'loadProblemDefiniton', 'getMap', 'saveNodes', 'saveRoutes'
]

function main () {
  let script = document.createElement('script')
  // Get apiKey from server
  const xhr = new XMLHttpRequest()
  xhr.open('GET', '/maps-api-key', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  let apiKey = null
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        const response = JSON.parse(xhr.responseText)
        apiKey = response.apiKey
        script.src = 'https://maps.googleapis.com/maps/api/js?key=' + apiKey + '&callback=getMap'
        script.async = true
        document.head.appendChild(script)
      }
    }
  }
  xhr.send()
  // Declare the functions to be called in the app
  for (const exportItem of exportsArray) {
    if (Object.prototype.hasOwnProperty.call(exports, exportItem)) {
      window[exportItem] = exports[exportItem]
    }
  }
}

main()
