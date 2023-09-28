export function resetSize (vm) {
  let imgWidth, imgHeight, barWidth, barHeight

  const parentWidth =
    vm.$el.parentNode.offsetWidth || (window).offsetWidth
  const parentHeight =
    vm.$el.parentNode.offsetHeight || (window).offsetHeight
  if (vm.imgSize.width.indexOf('%') !== -1) {
    imgWidth = (parseInt(vm.imgSize.width) / 100) * parentWidth + 'px'
  } else {
    imgWidth = vm.imgSize.width
  }

  if (vm.imgSize.height.indexOf('%') !== -1) {
    imgHeight = (parseInt(vm.imgSize.height) / 100) * parentHeight + 'px'
  } else {
    imgHeight = vm.imgSize.height
  }

  if (vm.barSize.width.indexOf('%') !== -1) {
    barWidth = (parseInt(vm.barSize.width) / 100) * parentWidth + 'px'
  } else {
    barWidth = vm.barSize.width
  }

  if (vm.barSize.height.indexOf('%') !== -1) {
    barHeight = (parseInt(vm.barSize.height) / 100) * parentHeight + 'px'
  } else {
    barHeight = vm.barSize.height
  }

  return {
    imgWidth: imgWidth,
    imgHeight: imgHeight,
    barWidth: barWidth,
    barHeight: barHeight
  }
}
