const dropZones = $('.drop-zone')
const btn = $('.btn')
const MAX_FILE_SIZE = 1000000; // максимальный размер файла - 1 мб.

for (let i = 0; i < dropZones.length; ++i) {
  let dropZone = $(dropZones[i])

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

      $('input[type="file"]')[i].files = files
  })

  dropZone.on('click', (event) => {
    const el = $($('input[type="file"]')[i])
    el.trigger('click')
    el.on('change', () => {
      dropZone.addClass('drop')
    })

  })

}


btn.on('click', (e) => {
  e.preventDefault() // XXX: STOPS FROM DEFAULT BEHAVIOUR
  $('html,body').animate({scrollTop: $('#ans-text').offset().top}, 'slow')

})
