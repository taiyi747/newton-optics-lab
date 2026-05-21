<template>
  <div class="slider-card" :style="{ '--slider-color': sliderColor }">
    <div class="flex justify-between items-center mb-1">
      <div class="flex items-center">
        <span class="color-dot"></span>
        <label class="font-semibold text-gray-700">{{ label }}</label>
      </div>
      <span class="slider-value">{{ displayValue }}</span>
    </div>
    <input
      type="range"
      :min="min"
      :max="max"
      :step="step"
      v-model.number="sliderValue"
      class="slider"
      :style="{ '--fill': fillPercent + '%' }"
    >
  </div>
</template>

<script setup>
import { computed } from 'vue'

const COLOR_MAP = {
  wavelength: '#3b82f6',
  radius: '#8b5cf6',
  convex1Radius: '#8b5cf6',
  convex2Radius: '#8b5cf6',
  convexRadius: '#8b5cf6',
  concaveRadius: '#8b5cf6',
  refractive: '#10b981',
  truncatedHeight: '#f59e0b',
  spacing: '#6366f1',
}

const props = defineProps({
  label: String,
  modelValue: Number,
  min: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  step: { type: Number, default: 1 },
  decimals: { type: Number, default: 1 },
  color: { type: String, default: '' },
  sliderKey: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

const displayValue = computed(() => props.modelValue.toFixed(props.decimals))

const fillPercent = computed(() =>
  ((props.modelValue - props.min) / (props.max - props.min)) * 100
)

const sliderValue = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const sliderColor = computed(() => {
  if (props.color) return props.color
  if (props.sliderKey && COLOR_MAP[props.sliderKey]) return COLOR_MAP[props.sliderKey]
  return '#3b82f6'
})
</script>

<style scoped>
.slider-card {
  border-radius: .625rem;
  padding: .38rem .65rem;
  background: #fff;
  border: 1px solid #f3f4f6;
  box-shadow: 0 1px 2px rgba(0,0,0,.04);
}

.color-dot {
  display: inline-block;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--slider-color);
  margin-right: 6px;
  flex-shrink: 0;
}

.slider-value {
  font-size: .8125rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  font-weight: 700;
  color: var(--slider-color);
  min-width: 50px;
  text-align: right;
}

/* Range input — thin track, colored fill, round thumb */
.slider {
  -webkit-appearance: none;
  appearance: none;
  width: 100%;
  height: 5px;
  border-radius: 999px;
  outline: none;
  border: 0;
  margin: 0;
  padding: 0;
  cursor: pointer;
  background: linear-gradient(
    to right,
    var(--slider-color) 0%,
    var(--slider-color) var(--fill, 50%),
    #e5e7eb var(--fill, 50%),
    #e5e7eb 100%
  );
}

/* Webkit thumb */
.slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--slider-color);
  border: 3px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,.18);
  cursor: pointer;
  transition: transform .15s ease, box-shadow .15s ease;
}
.slider::-webkit-slider-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 0 0 6px color-mix(in srgb, var(--slider-color) 18%, transparent),
              0 1px 4px rgba(0,0,0,.18);
}

/* Firefox track */
.slider::-moz-range-track {
  height: 5px;
  border-radius: 999px;
  background: #e5e7eb;
  border: 0;
}
.slider::-moz-range-progress {
  height: 5px;
  border-radius: 999px;
  background: var(--slider-color);
}
/* Firefox thumb */
.slider::-moz-range-thumb {
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--slider-color);
  border: 3px solid #fff;
  box-shadow: 0 1px 4px rgba(0,0,0,.18);
  cursor: pointer;
  transition: transform .15s ease, box-shadow .15s ease;
}
.slider::-moz-range-thumb:hover {
  transform: scale(1.15);
  box-shadow: 0 0 0 6px color-mix(in srgb, var(--slider-color) 18%, transparent),
              0 1px 4px rgba(0,0,0,.18);
}
</style>
