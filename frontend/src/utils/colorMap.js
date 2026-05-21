export function wavelengthToColor(wavelength) {
  if (wavelength <= 420) return '#9400d3'
  if (wavelength <= 450) return '#0000ff'
  if (wavelength <= 480) return '#0000ff'
  if (wavelength <= 490) return '#00bfff'
  if (wavelength <= 500) return '#00ced1'
  if (wavelength <= 530) return '#00ff7f'
  if (wavelength <= 560) return '#00ff00'
  if (wavelength <= 580) return '#90ee90'
  if (wavelength <= 595) return '#ffff00'
  if (wavelength <= 605) return '#ffa500'
  if (wavelength <= 650) return '#ff4500'
  return '#ff0000'
}

export function wavelengthToRgba(wavelength, alpha) {
  const hex = wavelengthToColor(wavelength)
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r}, ${g}, ${b}, ${alpha})`
}
