<template>
  <dialog class="modal" :class="{ 'modal-open': visible }" @click.self="close">
    <div class="modal-box w-[90%] max-w-[680px] p-0 overflow-hidden">
      <!-- Header: gradient bar -->
      <div class="flex items-center justify-between px-5 py-3 bg-gradient-to-r from-blue-500 to-violet-500 text-white">
        <div class="flex items-center gap-2">
          <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
          <span class="font-bold">操作指南</span>
        </div>
        <button class="btn btn-ghost btn-xs btn-circle text-white hover:bg-white/20" @click="close" title="关闭">&times;</button>
      </div>

      <!-- Steps content -->
      <div class="p-4 overflow-y-auto max-h-[65vh] space-y-3">
        <div v-for="(step, idx) in steps.slice(1)" :key="idx"
             class="flex gap-3 rounded-lg border p-3 transition-colors"
             :class="stepColorClass(idx + 1)">
          <div class="step-dot shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-white text-xs font-bold"
               :style="{ background: dotColors[(idx + 1) % dotColors.length] }">
            {{ idx + 1 }}
          </div>
          <div class="min-w-0">
            <div class="font-semibold text-sm mb-1" :style="{ color: dotColors[(idx + 1) % dotColors.length] }">{{ step.title }}</div>
            <ul class="text-xs text-gray-600 space-y-0.5 list-none p-0 m-0">
              <li v-for="(line, j) in step.lines" :key="j">{{ line }}</li>
            </ul>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="flex justify-end gap-2 px-5 py-3 border-t border-base-200">
        <button class="btn btn-ghost btn-sm" @click="close">关闭</button>
        <button class="btn btn-primary btn-sm" @click="close">我知道了</button>
      </div>
    </div>
  </dialog>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
  content: { type: String, default: '' }
})
const emit = defineEmits(['close'])
function close() {
  emit('close')
}

const dotColors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#f43f5e']

function stepColorClass(i) {
  const maps = [
    'bg-blue-50/60 border-blue-200/60',
    'bg-violet-50/60 border-violet-200/60',
    'bg-emerald-50/60 border-emerald-200/60',
    'bg-amber-50/60 border-amber-200/60',
    'bg-rose-50/60 border-rose-200/60',
  ]
  return maps[i % maps.length]
}

const steps = computed(() => {
  const sections = props.content.split(/\n(?=[一二三四五六七八九十]+、)/).filter(s => s.trim())
  if (sections.length === 0) {
    const rawLines = props.content.split('\n').filter(l => l.trim())
    if (rawLines.length === 0) return []
    return [{ title: '操作指南', lines: rawLines }]
  }
  return sections.map(section => {
    const lines = section.split('\n').filter(l => l.trim())
    const titleLine = lines[0] || ''
    const title = titleLine.replace(/^[【\s]+/, '').replace(/[】\s]+$/, '').replace(/^[一二三四五六七八九十]+、/, '')
    const bulletLines = lines.slice(1).map(l => l.replace(/^[•\s]+/, '').trim()).filter(Boolean)
    return { title, lines: bulletLines }
  })
})
</script>
