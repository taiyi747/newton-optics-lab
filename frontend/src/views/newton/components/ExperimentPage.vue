<template>
  <div class="page-content" :class="{ 'compact-display': compactDisplay }">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div class="space-y-4">
        <div class="card bg-base-100 border border-base-content/10 shadow-sm card-container">
          <div class="card-body p-3">
            <h3 class="card-title text-gray-800">{{ t('物理参数设置') }}</h3>
            <div class="space-y-2">
              <ParamSlider
                v-for="s in sliders"
                :key="s.key"
                :label="s.label"
                :min="s.min"
                :max="s.max"
                :step="s.step"
                :decimals="s.decimals"
                :slider-key="s.key"
                v-model="params[s.key]"
              />
            </div>
          </div>
        </div>
        <div class="card bg-base-100 border border-base-content/10 shadow-sm card-container">
          <div class="card-body p-3">
            <h3 class="card-title text-gray-800">{{ t('实验原理') }}</h3>
            <div class="principle-text text-gray-600 leading-relaxed">
              <p v-for="(p, i) in principle" :key="i" class="mb-3">{{ p }}</p>
            </div>
            <div v-if="principleImg" class="principle-image mt-3 p-3 bg-base-200 rounded-lg flex items-center justify-center overflow-hidden">
              <img :src="principleImg" :alt="title + '原理图'" class="max-w-full max-h-48 object-contain rounded-lg">
            </div>
          </div>
        </div>
      </div>
      <div class="space-y-4">
        <div class="card bg-base-100 border border-base-content/10 shadow-sm card-container">
          <div class="card-body p-3">
            <h3 class="card-title text-gray-800">{{ title }} {{ t('演示图像') }}</h3>
            <div class="demo-ring-container bg-base-200 rounded-xl flex items-center justify-center"
              :class="{ 'demo-ring-container-fixed': ringCanvasSize }"
              :style="ringCanvasStyle">
              <canvas :id="canvasPrefix + '-ring-canvas'" ref="ringCanvas" class="w-full h-full rounded-xl"></canvas>
            </div>
          </div>
        </div>
        <div class="card bg-base-100 border border-base-content/10 shadow-sm card-container">
          <div class="card-body p-3">
            <h3 class="card-title text-gray-800">{{ intensityTitle }} <span class="text-xs text-gray-500">({{ t('可左右拖动') }})</span></h3>
            <div class="demo-intensity-container bg-base-200 rounded-xl flex items-center justify-center cursor-grab active:cursor-grabbing"
              :id="canvasPrefix + '-intensity-wrapper'">
              <canvas :id="canvasPrefix + '-intensity-canvas'" ref="intensityCanvas" class="w-full h-full rounded-xl"></canvas>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div id="experiment-formula" class="mt-4 bg-gradient-to-r from-blue-50 to-sky-50 rounded-2xl border border-blue-100 p-5">
      <h3 class="formula-title text-blue-700">{{ t('牛顿环公式') }}</h3>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <div class="rounded-xl border border-blue-100 bg-white/75 p-4 text-center shadow-sm">
          <div class="formula-subtitle text-blue-600">{{ t('光强分布') }}</div>
          <div ref="katexIntensityFormula" class="formula-box text-blue-950"></div>
          <div class="formula-note text-blue-600">{{ t('反射光干涉强度随半径 r 与空气膜间距 h 变化') }}</div>
        </div>
        <div class="rounded-xl border border-blue-100 bg-white/75 p-4 text-center shadow-sm">
          <div class="formula-subtitle text-blue-600">{{ t('明环与暗环半径') }}</div>
          <div ref="katexRingFormula" class="formula-box text-blue-950"></div>
          <div class="formula-note text-blue-600">{{ t('k 为环序数，R 为曲率半径，λ 为入射光波长') }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onUnmounted, nextTick, computed } from 'vue'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import ParamSlider from './ParamSlider.vue'
import ringRenderer from '../../../utils/renderer.js'
import { useI18n } from '../../../utils/i18n.js'

const { t } = useI18n()

let renderTimer = null

const props = defineProps({
  title: String,
  intensityTitle: { type: String, default: '' },
  canvasPrefix: String,
  sliders: { type: Array, required: true },
  principle: { type: Array, default: () => [] },
  principleImg: { type: String, default: '' },
  ringCanvasSize: { type: Number, default: 0 },
  isNonContact: { type: Boolean, default: false },
  // 渲染类型: normal | truncated | doubleLens
  renderType: { type: String, default: 'normal' },
  // 双透镜参数名映射
  r1Key: { type: String, default: 'radius' },
  r2Key: { type: String, default: '' },
})

const ringCanvas = ref(null)
const intensityCanvas = ref(null)
const compactDisplay = ref(false)
const katexIntensityFormula = ref(null)
const katexRingFormula = ref(null)
const ringCanvasStyle = computed(() => {
  if (!props.ringCanvasSize) return {}
  const size = `${props.ringCanvasSize}px`
  return {
    width: size,
    height: size,
    minHeight: size,
    maxHeight: size,
  }
})

const params = reactive({})
props.sliders.forEach(s => { params[s.key] = s.default })

function renderKatexFormulas() {
  if (katexIntensityFormula.value) {
    katex.render(
      'I = 4I_0 \\sin^2\\left[\\frac{\\pi n r^2}{R\\lambda}+\\frac{2\\pi n h}{\\lambda}\\right]',
      katexIntensityFormula.value,
      { throwOnError: false, displayMode: true },
    )
  }
  if (katexRingFormula.value) {
    katex.render(
      '\\begin{aligned} r_{\\text{明}} &= \\sqrt{\\frac{(2k-1)R\\lambda}{2n}-2Rh} \\\\ r_{\\text{暗}} &= \\sqrt{\\frac{kR\\lambda}{n}-2Rh} \\end{aligned}',
      katexRingFormula.value,
      { throwOnError: false, displayMode: true },
    )
  }
}

function render() {
  const ringCanvasId = props.canvasPrefix + '-ring-canvas'
  const intensityCanvasId = props.canvasPrefix + '-intensity-canvas'
  renderTimer = null

  const wavelength = params.wavelength || 589
  const refractive = params.refractive || 1
  const spacing = params.spacing || 0
  const isNonContact = props.isNonContact || props.renderType === 'doubleLensNonContact' || props.renderType === 'nonContact'

  // 根据渲染类型调用不同的 renderer 方法
  if (props.renderType === 'normal') {
    const radius = params.radius || 10
    ringRenderer.drawNewtonRing(ringCanvasId, wavelength, radius, spacing, refractive, isNonContact)
    ringRenderer.drawIntensityPlot(intensityCanvasId, wavelength, radius, refractive, isNonContact, spacing, false, 0)
  } else if (props.renderType === 'truncated') {
    const radius = params.radius || 10
    const truncatedHeight = params.truncatedHeight || 5000
    ringRenderer.drawTruncatedRing(ringCanvasId, wavelength, radius, truncatedHeight, refractive)
    ringRenderer.drawIntensityPlot(intensityCanvasId, wavelength, radius, refractive, false, 0, false, 0)
  } else if (props.renderType === 'doubleLens' || props.renderType === 'doubleLensNonContact') {
    const r1 = params[props.r1Key] || 10
    const r2 = params[props.r2Key] || 10
    const nc = props.renderType === 'doubleLensNonContact'
    ringRenderer.drawDoubleLensRing(ringCanvasId, wavelength, r1, r2, refractive, nc, spacing)
    ringRenderer.drawIntensityPlot(intensityCanvasId, wavelength, r1, refractive, nc, spacing, true, r2)
  } else if (props.renderType === 'nonContact') {
    const radius = params.radius || 10
    ringRenderer.drawNewtonRing(ringCanvasId, wavelength, radius, spacing, refractive, true)
    ringRenderer.drawIntensityPlot(intensityCanvasId, wavelength, radius, refractive, true, spacing, false, 0)
  }
}

let stopWatch = null
let dragCleanup = null
let resizeObserver = null
let resizeCleanup = null

function scheduleRender() {
  if (renderTimer) cancelAnimationFrame(renderTimer)
  renderTimer = requestAnimationFrame(render)
}

function updateCompactDisplay() {
  const dpr = window.devicePixelRatio || 1
  const physicalScreenHeight = Math.round((window.screen?.height || window.innerHeight) * dpr)
  compactDisplay.value = physicalScreenHeight <= 1080
}

onMounted(async () => {
  await nextTick()
  updateCompactDisplay()
  renderKatexFormulas()

  stopWatch = watch(params, () => {
    scheduleRender()
  }, { deep: true })

  // 持续监听 canvas 容器尺寸，宽度或高度变化都重新渲染。
  const ringEl = document.getElementById(props.canvasPrefix + '-ring-canvas')
  const intensityEl = document.getElementById(props.canvasPrefix + '-intensity-canvas')
  const observedElements = [
    ringEl?.parentElement || ringEl,
    intensityEl?.parentElement || intensityEl,
  ].filter(Boolean)

  if (observedElements.length && typeof ResizeObserver !== 'undefined') {
    resizeObserver = new ResizeObserver(() => {
      scheduleRender()
    })
    observedElements.forEach(el => resizeObserver.observe(el))
    scheduleRender()
  } else {
    setTimeout(() => {
      render()
    }, 200)
  }

  const onWindowResize = () => {
    updateCompactDisplay()
    scheduleRender()
  }
  window.addEventListener('resize', onWindowResize)
  resizeCleanup = () => {
    window.removeEventListener('resize', onWindowResize)
  }

  // 绑定光强图拖动
  dragCleanup = bindIntensityDrag()
})

onUnmounted(() => {
  if (stopWatch) stopWatch()
  if (dragCleanup) dragCleanup()
  if (resizeObserver) resizeObserver.disconnect()
  if (resizeCleanup) resizeCleanup()
  if (renderTimer) cancelAnimationFrame(renderTimer)
})

// 光强图拖动逻辑，返回清理函数
function bindIntensityDrag() {
  const wrapperId = props.canvasPrefix + '-intensity-wrapper'
  const intensityCanvasId = props.canvasPrefix + '-intensity-canvas'

  let isDragging = false
  let startX = 0
  let startXlim = [-4, 4]
  let wrapper = null

  const getX = (e) => e.touches ? e.touches[0].clientX : e.clientX

  const onDragStart = (e) => {
    isDragging = true
    startX = getX(e)
    const state = ringRenderer.getCanvasState(intensityCanvasId)
    startXlim = state.currentXlim ? [...state.currentXlim] : [-4, 4]
  }

  const onDragMove = (e) => {
    if (!isDragging) return
    const clientX = getX(e)
    const dx = clientX - startX
    const state = ringRenderer.getCanvasState(intensityCanvasId)
    if (!state.width) return
    const padding = 50
    const plotWidth = state.width - padding * 2
    const rangePerPx = (startXlim[1] - startXlim[0]) / plotWidth
    const shift = -dx * rangePerPx
    const newXlim = [startXlim[0] + shift, startXlim[1] + shift]
    const maxR = state.maxR ? state.maxR * 1000 : 7
    newXlim[0] = Math.max(-maxR, newXlim[0])
    newXlim[1] = Math.min(maxR, newXlim[1])
    ringRenderer.redrawIntensityPlotWithXlim(intensityCanvasId, newXlim)
  }

  const onDragEnd = () => { isDragging = false }

  nextTick(() => {
    wrapper = document.getElementById(wrapperId)
    if (!wrapper) return
    wrapper.addEventListener('mousedown', onDragStart)
    window.addEventListener('mousemove', onDragMove)
    window.addEventListener('mouseup', onDragEnd)
    wrapper.addEventListener('touchstart', onDragStart, { passive: true })
    window.addEventListener('touchmove', onDragMove, { passive: true })
    window.addEventListener('touchend', onDragEnd)
  })

  // 返回清理函数
  return () => {
    if (wrapper) {
      wrapper.removeEventListener('mousedown', onDragStart)
      wrapper.removeEventListener('touchstart', onDragStart)
    }
    window.removeEventListener('mousemove', onDragMove)
    window.removeEventListener('mouseup', onDragEnd)
    window.removeEventListener('touchmove', onDragMove)
    window.removeEventListener('touchend', onDragEnd)
  }
}
</script>

<style scoped>
.formula-box {
  min-height: 4.2rem;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  font-size: 1rem;
}

.formula-box::-webkit-scrollbar {
  display: none;
}

.formula-box :deep(.katex-display) {
  margin: .35rem 0;
}

.formula-subtitle {
  margin-bottom: .35rem;
  font-size: .875rem;
  font-weight: 700;
}

.formula-note {
  margin-top: .35rem;
  font-size: .75rem;
  line-height: 1.35;
}

.formula-title {
  margin-bottom: .75rem;
  font-size: .875rem;
  font-weight: 700;
  line-height: 1.25;
}
</style>

<style scoped>
@media (min-width: 1024px) {
  .compact-display :deep(.card-container) {
    padding: 0.55rem 0.8rem !important;
  }

  .compact-display :deep(.card-container h3) {
    margin-bottom: 0.45rem !important;
    font-size: clamp(1rem, 2.3cqi, 1.35rem);
  }

  .compact-display :deep(.slider-container) {
    margin: 12px 0 8px;
  }

  .compact-display .demo-ring-container {
    height: clamp(250px, 34vh, 340px);
    min-height: 250px;
    max-height: 340px;
    aspect-ratio: unset;
  }

  .compact-display .demo-intensity-container {
    height: clamp(175px, 24vh, 220px);
    min-height: 175px;
    max-height: 220px;
    aspect-ratio: unset;
  }

  .compact-display .principle-image {
    max-height: 150px;
  }

  .compact-display .principle-image img {
    max-height: 130px;
  }
}
</style>
