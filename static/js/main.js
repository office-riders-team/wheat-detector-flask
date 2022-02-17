"use strict"
const dropZones = $('.drop-zone')
const imgsDZ = dropZones[0]
const mapDZ = dropZones[1]
const fileForms = $('input[type="file"]')
const canvas = $('canvas')[0]
const ctx = canvas.getContext('2d')

const VERTICAL_ANGLE_OF_VIEW = 70
const HORIZONTAL_ANGLE_OF_VIEW = 120
const POPUP_ANIMATION_DURATION = 0.3

let wereImagesProcessed = false
let imgCoords = []
let mapContour = []

// Relatively to canvas!
let mouseX = 0
let mouseY = 0


function getTanDeg(deg) {
  var rad = deg * Math.PI/180;
  return Math.tan(rad);
}


function getNumbersFromText(str) {
  let nums = []
  let num = ''
  for (let i = 0; i < str.length; ++i) {
    if (!isNaN(str[i])) {
      num += str[i]
    } else if ($.trim(num)) {
      nums.push(parseInt(num))
      num = ''
    }
  }
  return nums
}


// ------------------------- Drop zones ---------------------
for (let i = 0; i < dropZones.length; ++i) {
  const dropZone = $(dropZones[i])

  if (typeof(window.FileReader) == 'undefined') {
      dropZone.text('Не поддерживается браузером!');
      dropZone.addClass('error');
  }


  dropZone.on('dragover', () => {
    event.preventDefault()
    dropZone.addClass('hover')
  })

  dropZone.on('dragleave', () => {
    event.preventDefault()
    dropZone.removeClass('hover')
  })

  dropZone.on('drop', (event) => {
      event.preventDefault()

      dropZone.removeClass('hover')
      dropZone.addClass('drop')

      event.originalEvent.dataTransfer.dropEffect = 'move'
      const files = event.originalEvent.dataTransfer.files
      fileForms[i].files = files

      const id = dropZone.attr('id')
      if (id == 'map-dz') {
        const file = files[0]
        let reader = new FileReader()

        reader.onload = (e) => {
          const file = e.target.result
          const nums = getNumbersFromText(file)
          console.log('Coords:', nums)
          mapContour = nums
        }
        reader.readAsText(file)
      } else {
        imgCoords = new Array(files.length)
        for (let i = 0; i < files.length; ++i) imgCoords[i] = getNumbersFromText(files[i].name)
        displayImageDots()
      }
  })

  dropZone.on('click', (event) => {
    const el = $(fileForms[i])
    el.trigger('click')
    el.on('change', () => {
      dropZone.addClass('drop')
      const files = fileForms[i].files

      const id = dropZone.attr('id')
      if (id == 'map-dz') {
        const file = files[0]
        let reader = new FileReader()

        reader.onload = (e) => {
          const file = e.target.result
          const nums = getNumbersFromText(file)
          console.log('Coords:', nums)
          mapContour = nums
          displayMapContour()
        }
        reader.readAsText(file)
      } else {
        imgCoords = new Array(files.length)
        for (let i = 0; i < files.length; ++i) imgCoords[i] = getNumbersFromText(files[i].name)
        displayImageDots()
      }
    })
  })
}

// Process button
$('.btn').on('click', (e) => {
  e.preventDefault() // XXX: STOPS FROM DEFAULT BEHAVIOUR
  $('html,body').animate({scrollTop: $('canvas').offset().top - 40}, 'slow')

  const formData = new FormData()

  const imgs = fileForms[0].files
  for (let i = 0; i < imgs.length; ++i) {
    formData.append(`${i}`, imgs[i])
  }

  drawTextOnCanvas('PROCESSING...', 80)

  fetch('http://127.0.0.1:5000/process/', {
    method: "POST",
    body: formData
  }).
  then(
    (response) => {
      response.text().then(
        (responseText) => {
          if (responseText != 'OK') {
            console.log('ERROR OCCURED! RESPONSE NOT OK')
          } else {
            console.log('OK')
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
}


function displayImageDots() {
  imgCoords.forEach((numbers, i) => {
    const xCenter = numbers[2]
    const yCenter = numbers[3]
    // const h = numbers[4] / 100
    ctx.fillStyle = 'red'
    ctx.beginPath()
    ctx.arc(xCenter, yCenter, 4, 0, 2 * Math.PI)
    ctx.fill()
  })
}


function displayMapContour() {
  const nums = mapContour
  ctx.strokeStyle = 'black'
  ctx.beginPath()
  ctx.moveTo(nums[0], nums[1])

  for (let i = 2; i < nums.length; i += 2) {
    ctx.lineTo(nums[i], nums[i + 1])
  }
  ctx.lineTo(nums[0], nums[1])
  ctx.stroke()
}


function isMouseHoveredOverPoint(points) {
  return imgCoords.some((numbers) => {
    const xCenter = numbers[2]
    const yCenter = numbers[3]

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
  const xOffset = 8
  const yOffest = 3
  ctx.fillRect(mouseX + xOffset - 3, mouseY + yOffest, 50, 20)
  ctx.fillStyle = 'white'
  ctx.font = '10px Roboto'
  ctx.fillText(`${mouseX}, ${mouseY}`, mouseX + xOffset + 20, mouseY + yOffest + 14)

  // If cursor is hovered over any point we should change the cursor style
  if (isMouseHoveredOverPoint()) {
    $('canvas').css('cursor', 'pointer')
  } else {
    $('canvas').css('cursor', 'auto')
  }
})


// If user clicked on a point
$('canvas').on('click', (e) => {
  if (!isMouseHoveredOverPoint()) return

  imgCoords.forEach((numbers, i) => {
    const xCenter = numbers[2]
    const yCenter = numbers[3]

    const radius = 10

    if (xCenter - radius <= mouseX && mouseX <= xCenter + radius && yCenter - radius <= mouseY && mouseY <= yCenter + radius) {
      $('.popup-background').css('display', 'flex')
      setTimeout(() => $('.popup-background').css('opacity', '1'), POPUP_ANIMATION_DURATION * 1000)

      // const reader = new FileReader()
      // reader.readAsDataURL(imgs[i])

      // reader.onload = function () {
        // const base64Image = reader.result
        // $('.popup-picture').attr('src', base64Image)
      // }
      $('.popup-picture').attr('src', `./static/results/${i}.jpg`)
    }
  });
})

$('canvas').on('mouseleave', (e) => {
  if (wereImagesProcessed) draw()
})


// ------------------------- POPUP --------------------------
$('.popup-close-btn').on('click', () => {
  $('.popup-background').css('opacity', '0')
  setTimeout(() => $('.popup-background').css('display', 'none'), POPUP_ANIMATION_DURATION * 1000)
})
