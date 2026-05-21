export const X_MIN = -5
export const X_MAX = 5
export const X_STEP = 0.005

export function generateX() {
  const arr = []
  for (let x = X_MIN; x <= X_MAX; x += X_STEP) {
    arr.push(x)
  }
  return arr
}

const xCache = generateX()
export function getXValues() {
  return xCache
}

export function doubleSlitIntensity(wavelengthNm, D_mm, d_mm) {
  const lambda = wavelengthNm * 1e-6
  const I = []
  for (const x of xCache) {
    const phase = (Math.PI * d_mm * x) / (lambda * D_mm)
    I.push(4 * Math.cos(phase) ** 2)
  }
  return I
}

export function stripeSpacing(wavelengthNm, D_mm, d_mm) {
  const lambda = wavelengthNm * 1e-6
  return (lambda * D_mm) / d_mm
}
