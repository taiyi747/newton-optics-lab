<template>
  <div id="data-normal-page" class="page-content">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
      <!-- 拟合曲线 -->
      <div class="card bg-base-100 border border-base-content/10 shadow-sm card-container">
        <div class="card-body p-3">
          <h3 class="card-title text-gray-800">{{ t('拟合曲线') }}</h3>
          <div class="demo-ring-container bg-base-200 rounded-xl flex items-center justify-center">
            <canvas id="data-fit-canvas" ref="fitCanvas" class="w-full h-full rounded-xl"></canvas>
          </div>
        </div>
      </div>

      <!-- 牛顿环模拟 -->
      <div class="card bg-base-100 border border-base-content/10 shadow-sm card-container">
        <div class="card-body p-3">
          <h3 class="card-title text-gray-800">{{ t('牛顿环模拟图像') }}</h3>
          <div class="demo-ring-container bg-base-200 rounded-xl flex items-center justify-center">
            <canvas id="data-raw-canvas" ref="rawCanvas" class="w-full h-full rounded-xl"></canvas>
          </div>
          <div class="flex items-center justify-between mt-3 px-3 py-2 rounded-lg bg-primary/5 border border-primary/10">
            <span class="text-sm font-semibold text-primary/70">{{ t('计算得到的曲率半径 R') }}</span>
            <span id="data-calculated-R" class="font-bold text-primary">{{ calculatedR }}</span>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <!-- 文件导入 -->
      <div class="card bg-base-100 border border-base-content/10 shadow-sm card-container">
        <div class="card-body p-3">
          <h3 class="card-title text-gray-800">{{ t('文件导入') }}</h3>
          <div class="flex flex-col gap-2 mt-1">
            <label class="file-input file-input-bordered file-input-primary file-input-sm w-full cursor-pointer">
              <input type="file" accept=".csv,.txt" @change="onFileSelect" class="hidden" />
              <span class="flex-1 truncate">{{ fileName || t('未选择任何文件') }}</span>
              <span class="btn btn-primary btn-sm">{{ t('选择文件') }}</span>
            </label>
            <button class="btn btn-accent btn-sm w-fit" @click="downloadTemplate">
              {{ t('下载模板') }}
            </button>
            <div class="text-xs text-gray-400">{{ t('支持 CSV、TXT 格式，文件大小不超过 10MB') }}</div>
          </div>
        </div>
      </div>

      <!-- 物理参数 -->
      <div class="card bg-base-100 border border-base-content/10 shadow-sm card-container">
        <div class="card-body p-3">
          <h3 class="card-title text-gray-800">{{ t('物理参数设置') }}</h3>
          <div class="space-y-3 mt-1">
            <div class="number-input-wrapper" data-param="data-wavelength">
              <div class="flex justify-between items-center mb-1">
                <label class="font-medium text-gray-700">{{ t('波长λ (nm)') }}</label>
              </div>
              <div class="join w-full">
                <button class="btn btn-sm join-item" @click="adjustParam('wavelength', -0.1)">−</button>
                <input type="text" class="input input-bordered input-sm join-item flex-1 text-center font-mono font-semibold text-primary" v-model="params.wavelength" @change="onParamChange">
                <button class="btn btn-sm join-item" @click="adjustParam('wavelength', 0.1)">+</button>
              </div>
            </div>
            <div class="number-input-wrapper" data-param="data-refractive">
              <div class="flex justify-between items-center mb-1">
                <label class="font-medium text-gray-700">{{ t('折射率n') }}</label>
              </div>
              <div class="join w-full">
                <button class="btn btn-sm join-item" @click="adjustParam('refractive', -0.01)">−</button>
                <input type="text" class="input input-bordered input-sm join-item flex-1 text-center font-mono font-semibold text-primary" v-model="params.refractive" @change="onParamChange">
                <button class="btn btn-sm join-item" @click="adjustParam('refractive', 0.01)">+</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import ringRenderer from '../../utils/renderer.js'
import { useI18n } from '../../utils/i18n.js'

const { t } = useI18n()

const fitCanvas = ref(null)
const rawCanvas = ref(null)
const calculatedR = ref('--')
const fileName = ref('')
const currentDataFile = ref(null)
const importedData = ref(null)

const params = reactive({
  wavelength: '589.3',
  refractive: '1.00'
})

function adjustParam(key, delta) {
  const val = parseFloat(params[key]) + delta
  const min = key === 'wavelength' ? 400 : 1
  const max = key === 'wavelength' ? 760 : 1.5
  params[key] = Math.max(min, Math.min(max, val)).toFixed(key === 'wavelength' ? 1 : 2)
  onParamChange()
}

function onParamChange() {
  if (currentDataFile.value) {
    processDataFile(currentDataFile.value)
  } else {
    ringRenderer.drawEmptyDataMessage('data-fit-canvas', t('请先导入CSV数据文件'))
    ringRenderer.drawEmptyDataMessage('data-raw-canvas', t('无数据'))
  }
}

function onFileSelect(e) {
  const file = e.target.files?.[0]
  if (file) {
    fileName.value = file.name
    currentDataFile.value = file
    processDataFile(file)
  }
}

function readFileAsText(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (event) => resolve(event.target.result)
    reader.onerror = reject
    reader.readAsText(file)
  })
}

function parseCSVData(fileContent) {
  const lines = fileContent.trim().split('\n')
  if (lines.length < 3) {
    throw new Error('CSV文件至少需要3行数据')
  }

  const kRow = lines[0].split(',').slice(1).map(v => parseInt(v.trim(), 10)).filter(v => !isNaN(v))
  const leftRow = lines[1].split(',').slice(1).map(v => parseFloat(v.trim())).filter(v => !isNaN(v))
  const rightRow = lines[2].split(',').slice(1).map(v => parseFloat(v.trim())).filter(v => !isNaN(v))

  const minLength = Math.min(kRow.length, leftRow.length, rightRow.length)
  if (minLength < 3) {
    throw new Error('有效数据点太少，至少需要3个数据点')
  }

  const k = kRow.slice(0, minLength)
  const diameterMm = leftRow.slice(0, minLength).map((left, idx) => Math.abs(left - rightRow[idx]))
  const dSq = diameterMm.map(d => (d * 1e-3) ** 2)

  return { k, dSq }
}

function linearRegression(x, y) {
  const n = x.length
  let sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0
  for (let i = 0; i < n; i++) {
    sumX += x[i]
    sumY += y[i]
    sumXY += x[i] * y[i]
    sumX2 += x[i] * x[i]
  }
  const a = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX)
  const b = (sumY - a * sumX) / n
  return { a, b }
}

function updateDataImages() {
  const wavelength = parseFloat(params.wavelength) || 589.3
  const refractive = parseFloat(params.refractive) || 1.0

  if (!importedData.value) {
    ringRenderer.drawEmptyDataMessage('data-fit-canvas', t('请先导入CSV数据文件'))
    ringRenderer.drawEmptyDataMessage('data-raw-canvas', t('无数据'))
    calculatedR.value = '--'
    return
  }

  const { a, b } = linearRegression(importedData.value.k, importedData.value.dSq)
  const wlM = wavelength * 1e-9
  const R = a / (4 * (wlM / refractive))
  ringRenderer.drawDataFitCurve('data-fit-canvas', importedData.value.k, importedData.value.dSq, a, b, wavelength, refractive)
  ringRenderer.drawDataNewtonRing('data-raw-canvas', wavelength, R)
  calculatedR.value = R.toFixed(2) + ' m'
}

async function processDataFile(file) {
  currentDataFile.value = file
  try {
    importedData.value = parseCSVData(await readFileAsText(file))
    updateDataImages()
  } catch (error) {
    console.error('数据处理失败:', error)
    ringRenderer.drawEmptyDataMessage('data-fit-canvas', `数据解析失败: ${error.message}`)
    ringRenderer.drawEmptyDataMessage('data-raw-canvas', '无数据')
    calculatedR.value = '--'
  }
}

function downloadTemplate() {
  const template = `k,1,2,3,4,5,6,7,8,9,10
左读数(mm),5.123,5.234,5.345,5.456,5.567,5.678,5.789,5.890,6.001,6.112
右读数(mm),15.123,15.234,15.345,15.456,15.567,15.678,15.789,15.890,16.001,16.112`
  const blob = new Blob([template], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = '牛顿环数据模板.csv'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

onMounted(() => {
  setTimeout(() => {
    ringRenderer.drawEmptyDataMessage('data-fit-canvas', t('请先导入CSV数据文件'))
    ringRenderer.drawEmptyDataMessage('data-raw-canvas', t('无数据'))
  }, 500)
})
</script>
