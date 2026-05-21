<template>
  <div class="page-content">
    <div class="bg-white rounded-lg shadow-md card-container flex flex-col h-[calc(100vh-140px)]">
      <h3 class="text-gray-800 mb-4">{{ title }}</h3>
      <div ref="containerRef" class="pdf-container w-full flex-1 rounded-lg overflow-auto bg-gray-50 flex flex-col items-center p-4 gap-0.5">
        <div class="loading-text text-gray-500">正在加载...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const props = defineProps({
  title: { type: String, required: true },
  pdfName: { type: String, required: true }
})

const containerRef = ref(null)

async function loadPdfImages(pdfName, container) {
  if (!container || container.querySelector('img')) return

  try {
    const pdfjsLib = window.pdfjsLib
    if (!pdfjsLib) {
      throw new Error('PDF.js 库未加载')
    }
    pdfjsLib.GlobalWorkerOptions.workerSrc = '/js/pdf.worker.min.js'

    const pdfData = await new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest()
      xhr.open('GET', `/pdfs/${pdfName}.pdf`, true)
      xhr.responseType = 'arraybuffer'
      xhr.onload = () => {
        if (xhr.status < 200 || xhr.status >= 300) {
          reject(new Error(`无法加载PDF文件: HTTP ${xhr.status}`))
          return
        }
        resolve(xhr.response)
      }
      xhr.onerror = () => reject(new Error('无法加载PDF文件'))
      xhr.send()
    })

    const header = new TextDecoder('ascii').decode(new Uint8Array(pdfData, 0, 5))
    if (header !== '%PDF-') {
      throw new Error('加载到的文件不是有效PDF，请检查PDF路径')
    }

    const pdf = await pdfjsLib.getDocument({ data: pdfData }).promise
    container.innerHTML = ''

    for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
      const page = await pdf.getPage(pageNumber)
      const viewport = page.getViewport({ scale: 2.5 })
      const canvas = document.createElement('canvas')
      const context = canvas.getContext('2d')
      canvas.height = viewport.height
      canvas.width = viewport.width
      await page.render({ canvasContext: context, viewport }).promise
      const image = document.createElement('img')
      image.src = canvas.toDataURL()
      image.alt = `第${pageNumber}页`
      image.className = 'pdf-page-image'
      container.appendChild(image)
    }
  } catch (error) {
    console.error('加载PDF出错:', error)
    container.innerHTML = `<div class="text-red-500">PDF加载失败: ${error.message}<br>请确保PDF文件存在于 /pdfs/ 目录</div>`
  }
}

onMounted(() => {
  if (containerRef.value) {
    loadPdfImages(props.pdfName, containerRef.value)
  }
})
</script>
