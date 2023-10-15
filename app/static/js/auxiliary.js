function stringNumbersToList (str, numbers_to_load) {
  const parts = str.split(/[,\s]+/).filter(part => part !== '')
  if (parts.length === 1 && numbers_to_load == 1) {
    const singleNumber = parseFloat(parts[0])
    return isNaN(singleNumber)
      ? 'Invalid input: Not a valid number'
      : singleNumber
  } else if (parts.length > 1) {
    const numbers = parts.map(part => parseFloat(part))
    const allNumbers = numbers.every(num => !isNaN(num))
    if (allNumbers && numbers.length == numbers_to_load) {
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
  var xhr = new XMLHttpRequest()
  xhr.open('POST', '/reset', true)
  xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded')
  xhr.onreadystatechange = function () {
    if (xhr.readyState === XMLHttpRequest.DONE) {
      if (xhr.status === 200) {
        // Reset parameters
        for (let i = 0; i < check_list.length; i++) {
          document.getElementById(check_list[i]).value = 0
        }
        // Delete markers
        for (let i = 0; i < markers.length; i++) {
          markers[i].setMap(null)
        }
        markers = [markers[0]]
        // Delete routes
        for (let i = 0; i < paths.length; i++) {
          paths[i].setMap(null)
        }
        paths = []
        console.log('Reset done.')
      } else {
        console.error('Failed to reset:', xhr.status)
      }
    }
  }
  xhr.send()
}
