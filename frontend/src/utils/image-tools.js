export function getImageSource(target) {
  const now = new Date()
  const dateStr = now.getFullYear()
    + String(now.getMonth() + 1).padStart(2, '0')
    + String(now.getDate()).padStart(2, '0') + '_'
    + String(now.getHours()).padStart(2, '0')
    + String(now.getMinutes()).padStart(2, '0')
    + String(now.getSeconds()).padStart(2, '0')

  if (target.tagName === 'IMG') {
    const srcParts = target.src.split('/')
    const baseName = srcParts[srcParts.length - 1] || 'image.png'
    const dotIndex = baseName.lastIndexOf('.')
    const name = dotIndex > 0 ? baseName.substring(0, dotIndex) : baseName
    const ext = dotIndex > 0 ? baseName.substring(dotIndex) : '.png'
    return { url: target.src, filename: `${name}_${dateStr}${ext}` }
  }

  if (target.tagName === 'CANVAS') {
    try {
      const canvasId = target.id || 'canvas'
      const name = canvasId.replace('-canvas', '')
      return { url: target.toDataURL('image/png'), filename: `${name}_${dateStr}.png` }
    } catch (error) {
      console.error('Canvas转换失败:', error)
      return null
    }
  }

  const container = target.closest('div')
  const canvas = target.querySelector?.('canvas') || container?.querySelector('canvas')
  const image = target.querySelector?.('img') || container?.querySelector('img')

  if (canvas) return getImageSource(canvas)
  if (image) return getImageSource(image)
  return null
}

function fallbackSaveImage(imageUrl, filename) {
  const link = document.createElement('a')
  link.href = imageUrl
  link.download = filename
  link.style.display = 'none'
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

async function saveImage(target) {
  const source = getImageSource(target)
  if (!source) {
    alert('无法获取图像')
    return
  }

  try {
    const tauri = window.__TAURI__
    const dialog = tauri ? (tauri.dialog || tauri.dialogs) : null
    const fs = tauri ? (tauri.fs || tauri.filesystem) : null

    let bytes
    if (source.url.startsWith('data:')) {
      const base64 = source.url.split(',')[1]
      const binaryString = atob(base64)
      bytes = new Uint8Array(binaryString.length)
      for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i)
      }
    } else {
      const response = await fetch(source.url)
      const blob = await response.blob()
      bytes = new Uint8Array(await blob.arrayBuffer())
    }

    if (dialog?.save && fs) {
      const filePath = await dialog.save({
        defaultPath: source.filename,
        filters: [{ name: 'PNG', extensions: ['png'] }]
      })
      if (filePath) {
        const writeBinary = fs.writeFile || fs.writeBinaryFile
        if (writeBinary) {
          await writeBinary(filePath, bytes)
          return
        }
      }
    }
    fallbackSaveImage(source.url, source.filename)
  } catch (error) {
    console.error('保存图像失败:', error)
    fallbackSaveImage(source.url, source.filename)
  }
}

function openImageZoom(target) {
  const source = getImageSource(target)
  if (!source) return

  const overlay = document.createElement('div')
  overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.9);display:flex;align-items:center;justify-content:center;z-index:10001;overflow:hidden;'

  const container = document.createElement('div')
  container.style.cssText = 'position:relative;display:flex;align-items:center;justify-content:center;width:100%;height:100%;'

  const zoomedImg = document.createElement('img')
  zoomedImg.src = source.url
  zoomedImg.style.cssText = 'max-width:90%;max-height:90%;object-fit:contain;border-radius:4px;transition:transform .1s ease-out;cursor:grab;'

  let scale = 1
  let translateX = 0
  let translateY = 0
  let isDragging = false
  let lastX = 0
  let lastY = 0

  const updateTransform = () => {
    zoomedImg.style.transform = `translate(${translateX}px,${translateY}px) scale(${scale})`
  }

  const onMouseMove = (event) => {
    if (!isDragging) return
    translateX += event.clientX - lastX
    translateY += event.clientY - lastY
    lastX = event.clientX
    lastY = event.clientY
    updateTransform()
  }

  const onMouseUp = () => {
    isDragging = false
    zoomedImg.style.cursor = scale > 1 ? 'grab' : 'zoom-out'
  }

  const closeOnEsc = (event) => {
    if (event.key === 'Escape') cleanup()
  }

  const cleanup = () => {
    overlay.remove()
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    document.removeEventListener('keydown', closeOnEsc)
  }

  container.addEventListener('wheel', (event) => {
    event.preventDefault()
    const delta = event.deltaY > 0 ? 0.9 : 1.1
    const nextScale = scale * delta
    if (nextScale >= 0.5 && nextScale <= 5) {
      scale = nextScale
      updateTransform()
    }
  }, { passive: false })

  zoomedImg.addEventListener('mousedown', (event) => {
    if (scale <= 1) return
    isDragging = true
    lastX = event.clientX
    lastY = event.clientY
    zoomedImg.style.cursor = 'grabbing'
    event.preventDefault()
  })

  zoomedImg.addEventListener('dblclick', () => {
    scale = 1; translateX = 0; translateY = 0; updateTransform()
  })

  overlay.addEventListener('click', (event) => {
    if (event.target === overlay || event.target === container) cleanup()
  })

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  document.addEventListener('keydown', closeOnEsc)

  container.appendChild(zoomedImg)
  overlay.appendChild(container)
  document.body.appendChild(overlay)
}

export function initImageContextMenu() {
  document.addEventListener('contextmenu', (event) => {
    const target = event.target
    const isImageElement = target.tagName === 'IMG' || target.tagName === 'CANVAS'
    const isInImageContainer = target.closest('.demo-ring-container')
      || target.closest('.demo-intensity-container')
      || target.closest('[id$="-canvas"]')
      || target.closest('img')

    event.preventDefault()

    if (!isImageElement && !isInImageContainer) return

    const existingMenu = document.getElementById('image-zoom-menu')
    if (existingMenu) existingMenu.remove()

    const menu = document.createElement('div')
    menu.id = 'image-zoom-menu'
    menu.style.cssText = `position:fixed;background:white;border:1px solid #ccc;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,0.15);padding:8px 0;z-index:10000;min-width:150px;left:${event.clientX}px;top:${event.clientY}px;`

    const makeItem = (label, onClick, withBorder = false) => {
      const item = document.createElement('div')
      item.textContent = label
      item.style.cssText = `padding:10px 16px;cursor:pointer;font-size:14px;color:#333;transition:background .2s;${withBorder ? 'border-bottom:1px solid #eee;' : ''}`
      item.onmouseover = () => { item.style.background = '#f0f0f0' }
      item.onmouseout = () => { item.style.background = 'transparent' }
      item.onclick = () => { menu.remove(); onClick() }
      return item
    }

    menu.appendChild(makeItem('查看放大图像', () => openImageZoom(target), true))
    menu.appendChild(makeItem('图像另存为', () => saveImage(target)))
    document.body.appendChild(menu)

    setTimeout(() => {
      const closeMenu = () => { menu.remove(); document.removeEventListener('click', closeMenu) }
      document.addEventListener('click', closeMenu)
    }, 100)
  })
}

export function bindZoomGuards() {
  document.addEventListener('wheel', (event) => {
    if (event.ctrlKey || event.metaKey) event.preventDefault()
  }, { passive: false })

  document.addEventListener('touchmove', (event) => {
    if (event.scale !== 1) event.preventDefault()
  }, { passive: false })

  let lastTouchEnd = 0
  document.addEventListener('touchend', (event) => {
    const now = Date.now()
    if (now - lastTouchEnd <= 300) event.preventDefault()
    lastTouchEnd = now
  }, { passive: false })
}
