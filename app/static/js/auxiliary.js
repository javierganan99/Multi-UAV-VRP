import { globalElements } from './globals.js'
export { stringNumbersToList, reset }
function stringNumbersToList (str, numbers2load) {
  const parts = str.split(/[,\s]+/).filter(part => part !== '')
  console.log(numbers2load)
  if (parts.length === 1 && numbers2load === 1) {
    const singleNumber = parseFloat(parts[0])
    return isNaN(singleNumber)
      ? 'Invalid input: Not a valid number'
      : [singleNumber]
  } else if (parts.length > 1) {
    const numbers = parts.map(part => parseFloat(part))
    console.log('NUMBERS ' + numbers)
    const allNumbers = numbers.every(num => !isNaN(num))
    if (allNumbers && numbers.length === numbers2load) {
      return numbers
    } else {
      return false
    }
  } else {
    return false
  }
}

// Function to reset the problem information
function reset (event) {
  event.preventDefault()
  const xhr = new XMLHttpRequest()
  xhr.open('DELETE', '/reset', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        // Reset parameters
        for (let i = 0; i < globalElements.checkList.length; i++) {
          document.getElementById(globalElements.checkList[i]).value = 0
        }
        // Delete markers
        for (let i = 0; i < globalElements.markers.length; i++) {
          globalElements.markers[i].setMap(null)
        }
        globalElements.markers = [globalElements.markers[0]]
        // Delete routes
        for (let i = 0; i < globalElements.paths.length; i++) {
          globalElements.paths[i].setMap(null)
        }
        globalElements.paths = []
        console.log('Reset done.')
      } else {
        console.error('Failed to reset:', xhr.status)
      }
    }
  }
  xhr.send()
}
