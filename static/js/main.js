"use strict"
const dropZone = $('.drop-zone')
const fileForm = $('input[type="file"]')
const canvas = $('canvas')[0]
const ctx = canvas.getContext('2d')

const SERVER_PORT = '5000'
const POPUP_ANIMATION_DURATION = 0.3

let wereImagesProcessed = false
let imgCoords = {}
let mapContour = []

let imageFiles = {}

// Relatively to canvas!
let mouseX = 0
let mouseY = 0

let totalWheat
let density
let totalArea


// ------------------------- Drop zones ---------------------

dropZone.on('dragover', (event) => {
  event.preventDefault()
  dropZone.addClass('hover')
})


dropZone.on('dragleave', (event) => {
  event.preventDefault()
  dropZone.removeClass('hover')
})


dropZone.on('drop', (event) => {
    event.preventDefault()

    dropZone.removeClass('hover')
    dropZone.addClass('drop')

    event.originalEvent.dataTransfer.dropEffect = 'move'
    const files = event.originalEvent.dataTransfer.files
    fileForm[0].files = files
    processFiles(files)
})


dropZone.on('click', () => {
  fileForm.trigger('click')
  fileForm.on('change', () => {
    dropZone.addClass('drop')
  })
})


fileForm.on('change', () => {
  processFiles(fileForm[0].files)
})


function processFiles(files) {
  imageFiles = {}

  for (let i = 0; i < files.length; ++i) {
    const file = files[i]
    if (file.name.endsWith('.png')) {
      imageFiles[file.name] = file
    } else if (file.name.endsWith('.json')) {
      parseJSON(file)
    }
  }
}


function parseJSON(jsonFile) {
  let reader = new FileReader()

  reader.onload = () => {
    const jsonData = JSON.parse(reader.result)

    mapContour = jsonData['mapContour']

    for (const [key, value] of Object.entries(jsonData)) {
      if (key == 'mapContour') continue
      imgCoords[key] = value
    }
  }

  reader.readAsText(jsonFile)
}


// Process button
$('.btn').on('click', (e) => {
  e.preventDefault() // XXX: STOPS FROM DEFAULT BEHAVIOUR

  // Create form data...
  const formData = new FormData()
  for (const [key, value] of Object.entries(imageFiles)) {
    formData.append(key, value)
  }
  for (const [key, value] of Object.entries(imgCoords)) {
    formData.append(key, value)
  }
  formData.append('mapContour', mapContour)

  // Process the data
  drawTextOnCanvas('PROCESSING...', 80)

  fetch(`process/`, {
    method: "POST",
    body: formData
  }).
  then(
    (response) => {
      response.text().then(
        (responseText) => {
          if (responseText == 'FAIL') {
            console.log('ERROR OCCURED! RESPONSE NOT OK')
            drawTextOnCanvas('NOTHING PROCESSED YET', 80)
          } else {
            // Scroll down to the canvas
            $('html,body').animate({scrollTop: $('canvas').offset().top - 40}, 'slow')

            const data = responseText.split(';')
            totalArea = data[0]
            totalWheat = data[1]
            density = data[2]
            
            wereImagesProcessed = true
            draw()
          }
        }
      )
    }
  )

})


//---------------------------- Canvas stuff --------------------------------
drawTextOnCanvas('NOTHING PROCESSED YET', 80)


function drawTextOnCanvas(text, fontSize) {
  ctx.fillStyle = 'black'
  ctx.fillRect(0, 0, canvas.width, canvas.height)
  
  ctx.textAlign = 'center'
  ctx.fillStyle = 'white'
  ctx.font = ('' + fontSize) + 'px Roboto'
  ctx.fillText(text, 500, 500)
}


function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height)
  displayImageDots()
  displayMapContour()
  drawFieldStats()
}


function drawFieldStats() { 
  ctx.textAlign = 'right'
  ctx.fillStyle = 'black'
  ctx.font =  '20px Roboto'
  const text = [`Field area: ${totalArea}`, `Total Wheat: ${totalWheat}`, `Density: ${density}`]
  for (let i = 0; i < text.length; ++i) {
    ctx.fillText(text[i], 1000, 20 + i * 20)
  }
}


function displayImageDots() {
  for (const [key, value] of Object.entries(imgCoords)) {
    const xCenter = value[0]
    const yCenter = value[1]

    ctx.fillStyle = 'red'
    ctx.beginPath()
    ctx.arc(xCenter, yCenter, 4, 0, 2 * Math.PI)
    ctx.fill()
  }
}


function displayMapContour() {
  ctx.strokeStyle = 'black'

  ctx.beginPath()
  ctx.moveTo(mapContour[0][0], mapContour[0][1])
  for (let i = 1; i < mapContour.length; ++i) {
    ctx.lineTo(mapContour[i][0], mapContour[i][1])
  }
  ctx.lineTo(mapContour[0][0], mapContour[0][1])
  ctx.stroke()
}


function wasMouseHoveredOverPoint() {
  return Object.values(imgCoords).some((i) => {
    const xCenter = i[0]
    const yCenter = i[1]

    const radius = 10

    return xCenter - radius <= mouseX && mouseX <= xCenter + radius && yCenter - radius <= mouseY && mouseY <= yCenter + radius
  })
}


const canvasOffset = $('canvas').offset()
$('canvas').on('mousemove', (e) => {
  if (!wereImagesProcessed) return

  draw()
  mouseX = Math.floor(e.pageX - canvasOffset.left)
  mouseY = Math.floor(e.pageY - canvasOffset.top)

  // Draw a rectangle near the cursor
  ctx.fillStyle = '#808080'
  ctx.textAlign = 'center'
  const xOffset = 8
  const yOffest = 3
  ctx.fillRect(mouseX + xOffset - 3, mouseY + yOffest, 50, 20)
  ctx.fillStyle = 'white'
  ctx.font = '10px Roboto'
  ctx.fillText(`${mouseX}, ${mouseY}`, mouseX + xOffset + 20, mouseY + yOffest + 14)

  // If cursor is hovered over any point we should change the cursor style
  if (wasMouseHoveredOverPoint()) {
    $('canvas').css('cursor', 'pointer')
  } else {
    $('canvas').css('cursor', 'auto')
  }
})


// If user clicked on a point
$('canvas').on('click', (e) => {
  if (!wasMouseHoveredOverPoint()) return

  for (const [filename, numbers] of Object.entries(imgCoords)) {
    const xCenter = numbers[0]
    const yCenter = numbers[1]

    const radius = 10

    if (xCenter - radius <= mouseX && mouseX <= xCenter + radius && yCenter - radius <= mouseY && mouseY <= yCenter + radius) {
      $('.popup-background').css('display', 'flex')
      setTimeout(() => $('.popup-background').css('opacity', '1'), POPUP_ANIMATION_DURATION * 1000)

      $('.popup-picture').attr('src', `./static/results/${filename}`)
    }
  }
})

$('canvas').on('mouseleave', (e) => {
  if (wereImagesProcessed) draw()
})


// ------------------------- POPUP --------------------------
$('.popup-close-btn').on('click', () => {
  $('.popup-background').css('opacity', '0')
  setTimeout(() => $('.popup-background').css('display', 'none'), POPUP_ANIMATION_DURATION * 1000)
})
