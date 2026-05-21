<template>
  <nav id="sidebar" class="flex flex-col h-screen overflow-hidden fixed lg:static inset-y-0 left-0 z-40 border-r border-gray-200 bg-white shadow-lg transition-transform duration-300" :class="sidebarOpen ? 'translate-x-0 lg:translate-x-0' : '-translate-x-full lg:translate-x-0'">
    <!-- Top bar: title + toggle button -->
    <div class="shrink-0 border-b border-gray-100 px-4 pt-4 pb-3">
      <div class="flex items-center gap-2.5">
        <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-blue-500 to-violet-500 flex items-center justify-center shrink-0 shadow-md shadow-blue-500/20">
          <svg width="21" height="21" viewBox="0 0 24 24" fill="none" class="text-white"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.5" opacity=".5"/><circle cx="12" cy="12" r="7" stroke="currentColor" stroke-width="1.5" opacity=".7"/><circle cx="12" cy="12" r="4" stroke="currentColor" stroke-width="1.5" opacity=".9"/><circle cx="12" cy="12" r="1.5" fill="currentColor"/></svg>
        </div>
        <div>
          <h1 class="nav-title text-base font-bold" :title="t('牛顿环')">{{ t('牛顿环') }}</h1>
          <p class="text-xs text-gray-500 leading-tight tracking-wide font-semibold">{{ t('综合实验平台') }}</p>
        </div>
      </div>
      <button class="nav-toggle-btn absolute top-1/2 right-3 -translate-y-1/2 z-10 btn btn-ghost btn-sm btn-square" title="收起/展开导航" @click="sidebarOpen = !sidebarOpen">
        <svg class="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
      </button>
    </div>

    <!-- Scrollable nav content -->
    <div class="sidebar-content flex-1 overflow-y-auto overflow-x-hidden px-2.5 py-3 space-y-2.5">
      <!-- Experiment content section (blue) -->
      <section class="sidebar-group section-blue">
        <div class="group-head">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
            <span class="gradient-underline">{{ t('实验内容') }}</span>
          </div>
        </div>
        <div class="group-body">
          <a href="#" class="menu-entry" :class="route.path === '/newton/demo-normal' ? 'menu-entry-primary active-entry' : 'menu-entry-default'" @click.prevent="navigateTo('/newton/demo-normal')">
            <span class="entry-left">
              <span class="entry-icon">
                <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
              </span>
              <span>
                <span class="entry-title">{{ t('实验演示') }}</span>
                <span class="entry-subtitle">{{ t('Demo') }}</span>
              </span>
            </span>
            <span v-if="route.path === '/newton/demo-normal' && currentLanguage === 'zh'" class="badge badge-primary badge-sm">{{ t('当前') }}</span>
          </a>
          <a href="#" class="menu-entry" :class="route.path === '/newton/demo-principle' ? 'menu-entry-primary active-entry' : 'menu-entry-default'" @click.prevent="navigateTo('/newton/demo-principle')">
            <span class="entry-left">
              <span class="entry-icon">
                <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
              </span>
              <span>
                <span class="entry-title">{{ t('实验原理') }}</span>
                <span class="entry-subtitle">{{ t('Principle') }}</span>
              </span>
            </span>
            <span v-if="route.path === '/newton/demo-principle' && currentLanguage === 'zh'" class="badge badge-primary badge-sm">{{ t('当前') }}</span>
          </a>
          <a href="#" class="menu-entry" :class="route.path === '/newton/result-analysis' ? 'menu-entry-primary active-entry' : 'menu-entry-default'" @click.prevent="navigateTo('/newton/result-analysis')">
            <span class="entry-left">
              <span class="entry-icon">
                <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
              </span>
              <span>
                <span class="entry-title">{{ t('结果分析') }}</span>
                <span class="entry-subtitle">{{ t('Analysis') }}</span>
              </span>
            </span>
            <span v-if="route.path === '/newton/result-analysis' && currentLanguage === 'zh'" class="badge badge-primary badge-sm">{{ t('当前') }}</span>
          </a>
        </div>
      </section>

      <!-- Simulation section (violet) -->
      <section class="sidebar-group section-violet">
        <div class="group-head">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-violet-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
            <span class="gradient-underline">{{ t('仿真实验') }}</span>
          </div>
        </div>
        <div class="group-body">
          <button class="menu-entry menu-entry-secondary justify-between" @click="toggleDropdown('simulation')">
            <span class="entry-left">
              <span class="entry-icon">
                <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>
              </span>
              <span>
                <span class="entry-title">{{ t('普通牛顿环') }}</span>
                <span class="entry-subtitle">Simulation</span>
              </span>
            </span>
            <svg class="submenu-arrow w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4" :class="{ 'rotate-180': dropdownStates.simulation }"><path d="m6 9 6 6 6-6"/></svg>
          </button>
          <div class="submenu-wrap" :class="{ 'submenu-open': dropdownStates.simulation }">
            <a href="#" class="sub-entry sub-entry-violet" :class="{ 'active-sub-entry': route.path === '/newton/simulation-manual' }" @click.prevent="navigateTo('/newton/simulation-manual')">
              <svg viewBox="0 0 24 24" class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
              {{ t('实验原理') }}
              <span v-if="route.path === '/newton/simulation-manual' && currentLanguage === 'zh'" class="badge badge-secondary badge-sm ml-auto">{{ t('当前') }}</span>
            </a>
            <a href="#" class="sub-entry sub-entry-violet" :class="{ 'active-sub-entry': route.path === '/newton/simulation-guide' }" @click.prevent="navigateTo('/newton/simulation-guide')">
              <svg viewBox="0 0 24 24" class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14,2 14,8 20,8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
              {{ t('操作手册') }}
              <span v-if="route.path === '/newton/simulation-guide' && currentLanguage === 'zh'" class="badge badge-secondary badge-sm ml-auto">{{ t('当前') }}</span>
            </a>
            <a href="#" class="sub-entry sub-entry-violet" @click.prevent="openSimulationWindow">
              <svg viewBox="0 0 24 24" class="w-3.5 h-3.5 shrink-0" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5,3 19,12 5,21"/></svg>
              {{ t('开始实验') }}
            </a>
          </div>
        </div>
      </section>

      <!-- Data processing section (emerald) -->
      <section class="sidebar-group section-emerald">
        <div class="group-head">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4"/><polyline points="7,10 12,15 17,10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>
            <span class="gradient-underline">{{ t('数据处理') }}</span>
          </div>
        </div>
        <div class="group-body">
          <a href="#" class="menu-entry" :class="route.path === '/newton/data-normal' ? 'menu-entry-accent active-entry' : 'menu-entry-default'" @click.prevent="navigateTo('/newton/data-normal')">
            <span class="entry-left">
              <span class="entry-icon">
                <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 20V10M12 20V4M6 20v-6"/></svg>
              </span>
              <span>
                <span class="entry-title">{{ t('普通牛顿环') }}</span>
                <span class="entry-subtitle">Data</span>
              </span>
            </span>
            <span v-if="route.path === '/newton/data-normal' && currentLanguage === 'zh'" class="badge badge-accent badge-sm">{{ t('当前') }}</span>
          </a>
        </div>
      </section>

      <!-- AI assistant section (amber) -->
      <section class="sidebar-group section-amber">
        <div class="group-head">
          <div class="flex items-center gap-2">
            <svg class="w-4 h-4 text-amber-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2a7 7 0 017 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 01-2 2h-4a2 2 0 01-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 017-7z"/><line x1="9" y1="21" x2="15" y2="21"/></svg>
            <span class="gradient-underline">{{ t('AI 助手') }}</span>
          </div>
        </div>
        <div class="group-body">
          <a href="#" class="menu-entry" :class="route.path === '/newton/ai-chat' ? 'menu-entry-warning active-entry' : 'menu-entry-default'" @click.prevent="navigateTo('/newton/ai-chat')">
            <span class="entry-left">
              <span class="entry-icon">
                <svg viewBox="0 0 24 24" class="w-4 h-4" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>
              </span>
              <span>
                <span class="entry-title">{{ t('开始对话') }}</span>
                <span class="entry-subtitle">AI Chat</span>
              </span>
            </span>
            <span v-if="route.path === '/newton/ai-chat' && currentLanguage === 'zh'" class="current-badge badge-amber">{{ t('当前') }}</span>
          </a>
        </div>
      </section>
    </div>

    <!-- Bottom buttons -->
    <div class="shrink-0 px-3 py-2.5 border-t border-gray-100 space-y-1.5">
      <button class="btn btn-ghost btn-sm w-full gap-2" @click="$emit('toggle-guide')">
        <svg class="w-4 h-4 text-blue-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        {{ t('操作指南') }}
      </button>
    </div>
  </nav>

  <!-- Float button when sidebar closed -->
  <button v-if="!sidebarOpen" class="nav-float-btn fixed top-1/2 left-0 -translate-y-1/2 z-50 bg-white/85 border border-gray-200 border-l-none rounded-r-md py-3 px-2 cursor-pointer shadow-[2px_0_6px_rgba(0,0,0,0.08)] flex flex-col items-center transition-all duration-250 hover:bg-blue-500 hover:text-white hover:border-blue-500" title="展开导航" @click="sidebarOpen = true">
    <svg class="w-6 h-6 stroke-current stroke-2 fill-none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7" /></svg>
  </button>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useI18n } from '../../utils/i18n.js'

const router = useRouter()
const route = useRoute()
const { t, currentLanguage } = useI18n()
const sidebarOpen = ref(true)
const emit = defineEmits(['toggle-guide'])

const dropdownStates = ref({
  simulation: false,
})

function navigateTo(path) {
  router.push(path)
}

function toggleDropdown(key) {
  dropdownStates.value[key] = !dropdownStates.value[key]
}

function openSimulationWindow() {
  const tauri = window.__TAURI__
  if (tauri) {
    let WebviewWindow = null
    if (tauri.window && tauri.window.WebviewWindow) {
      WebviewWindow = tauri.window.WebviewWindow
    } else if (tauri.webviewWindow && tauri.webviewWindow.WebviewWindow) {
      WebviewWindow = tauri.webviewWindow.WebviewWindow
    } else if (tauri.WebviewWindow) {
      WebviewWindow = tauri.WebviewWindow
    }
    if (WebviewWindow) {
      try {
        new WebviewWindow('simulationWindow', {
          url: 'pages/simulation.html',
          title: '牛顿环仿真实验',
          width: 1280,
          height: 800,
          center: true,
          resizable: true,
        })
        return
      } catch (error) {
        console.error('Tauri创建窗口失败:', error)
      }
    }
  }
  window.open('pages/simulation.html', 'simulationWindow', 'width=1280,height=800,menubar=no,toolbar=no,location=no,status=no')
}
</script>

<style scoped>
/* Container query — must preserve */
#sidebar {
  container-type: inline-size;
  container-name: sidebar;
}

/* Scrollbar hiding */
.sidebar-content {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.sidebar-content::-webkit-scrollbar { display: none; }

/* cqi typography — must preserve */
.nav-title {
  font-size: clamp(.95rem, 3cqi, 1.25rem);
  font-weight: 700;
  line-height: 1.2;
  color: #1f2937;
  display: block;
  transition: none !important;
  transform: none !important;
}

/* Sidebar group cards */
.sidebar-group {
  overflow: hidden;
  border-radius: .5rem;
  border: 1px solid #f3f4f6;
  background: #fff;
  box-shadow: 0 1px 2px rgba(0,0,0,.04);
  transition: box-shadow .18s ease;
}
.sidebar-group:hover {
  box-shadow: 0 2px 8px rgba(0,0,0,.06);
}

/* Colored left borders */
.section-blue { border-left: 3px solid #3b82f6; }
.section-violet { border-left: 3px solid #8b5cf6; }
.section-emerald { border-left: 3px solid #10b981; }
.section-amber { border-left: 3px solid #f59e0b; }

/* Group layout */
.group-head { padding: .68rem .72rem .4rem; }
.group-body { display: grid; gap: .38rem; padding: 0 .42rem .48rem; }

/* Gradient underlines */
.gradient-underline {
  position: relative;
  display: inline-block;
  padding-bottom: 4px;
  font-size: .8rem;
  font-weight: 800;
  color: #374151;
}
.gradient-underline::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: 0;
  height: 2px;
  width: 100%;
  border-radius: 999px;
}
.section-blue .gradient-underline::after { background: linear-gradient(90deg, #3b82f6, #93c5fd); }
.section-violet .gradient-underline::after { background: linear-gradient(90deg, #8b5cf6, #c4b5fd); }
.section-emerald .gradient-underline::after { background: linear-gradient(90deg, #10b981, #6ee7b7); }
.section-amber .gradient-underline::after { background: linear-gradient(90deg, #f59e0b, #fcd34d); }

/* Menu entries — compact nav items matching original size */
.menu-entry {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: .45rem;
  width: 100%;
  border: 1px solid transparent;
  border-radius: .45rem;
  padding: .38rem .48rem;
  text-decoration: none;
  cursor: pointer;
  font-size: .82rem;
  font-weight: 600;
  color: #4b5563;
  white-space: nowrap;
  user-select: none;
  transition: transform .18s ease, background .18s ease, color .18s ease;
}
.menu-entry:hover { transform: translateX(4px); }

.menu-entry-default {
  color: #4b5563;
  background: transparent;
}
.menu-entry-default:hover {
  background: rgb(243 244 246);
}

.menu-entry-primary {
  color: #2563eb;
  background: #eff6ff;
  font-weight: 700;
}
.menu-entry-secondary {
  color: #374151;
  background: #f9fafb;
  font-weight: 600;
}
.menu-entry-secondary:hover {
  color: #7c3aed;
  background: #f5f3ff;
}
.menu-entry-accent {
  color: #059669;
  background: #ecfdf5;
  font-weight: 700;
}
.menu-entry-warning {
  color: #d97706;
  background: #fffbeb;
  font-weight: 700;
}

.entry-left { display: flex; align-items: center; gap: .42rem; min-width: 0; flex: 1 1 0; overflow: hidden; }
.entry-left > span:not(.entry-icon) { min-width: 0; flex: 1 1 0; overflow: hidden; }
.entry-icon {
  display: grid;
  place-items: center;
  width: 1.35rem;
  height: 1.35rem;
  border-radius: .35rem;
  flex-shrink: 0;
}
.menu-entry-primary .entry-icon { background: rgba(59,130,246,.12); color: #3b82f6; }
.menu-entry-secondary .entry-icon { background: rgba(107,114,128,.08); color: #6b7280; }
.menu-entry-accent .entry-icon { background: rgba(16,185,129,.12); color: #10b981; }
.menu-entry-warning .entry-icon { background: rgba(245,158,11,.12); color: #f59e0b; }
.menu-entry-default .entry-icon { background: rgba(107,114,128,.08); color: #6b7280; }
.entry-title { display: block; max-width: 100%; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; font-size: .82rem; font-weight: 700; line-height: 1.2; }
.entry-subtitle { display: none; }
.section-amber .entry-subtitle {
  display: block;
  font-size: .65rem;
  font-weight: 500;
  color: #9ca3af;
  line-height: 1;
}

.current-badge {
  font-size: .6rem;
  font-weight: 700;
  line-height: 1;
  padding: 2px 6px;
  border-radius: 999px;
  color: #fff;
  white-space: nowrap;
  flex-shrink: 0;
}
.badge-amber { background: #f59e0b; }

/* Sub entries — small capsule links */
.sub-entry {
  display: flex;
  align-items: center;
  gap: .45rem;
  min-height: 2.25rem;
  border-radius: .5rem;
  padding: .52rem .62rem;
  border: 1px solid transparent;
  font-size: .8rem;
  font-weight: 700;
  text-decoration: none;
  transition: transform .18s ease, box-shadow .18s ease, background .18s ease;
}
.sub-entry:hover { transform: translateX(4px); box-shadow: 0 8px 16px rgb(15 23 42 / .05); }

.sub-entry-violet {
  color: #374151;
  background: #f9fafb;
}
.sub-entry-violet:hover {
  color: #7c3aed;
  background: #f5f3ff;
}
.active-sub-entry { font-weight: 900; box-shadow: inset 0 0 0 1px rgba(139,92,246,.18); }

/* Submenu animation */
.submenu-wrap {
  overflow: hidden;
  display: grid;
  gap: .35rem;
  margin-left: .18rem;
  padding-left: .3rem;
  max-height: 0;
  opacity: 0;
  transition: max-height .28s ease, opacity .28s ease, margin-top .28s ease;
}
.submenu-wrap.submenu-open {
  max-height: 200px;
  opacity: 1;
  margin-top: .25rem;
}

.submenu-arrow { transition: transform .28s ease; }

.active-entry { font-weight: 800; box-shadow: inset 0 0 0 1px rgba(0,0,0,.06); }

/* Float button fix */
#sidebar * { max-width: none; }

/* Responsive — cqi/cqw and container queries (must preserve) */
@media (min-width: 1024px) {
  #sidebar { width: max-content; min-width: 236px; max-width: none; flex-shrink: 0; position: relative; transform: none !important; height: auto; min-height: 100vh; overflow: visible; }
  .nav-toggle-btn { display: none !important; }
  .nav-float-btn { display: none !important; }
  .sidebar-content { overflow-y: auto; height: auto; }
  .nav-title { font-size: clamp(.95rem, 2.5vw, 1.25rem); }
}
@media (max-width: 1023px) {
  #sidebar { width: max-content; min-width: 264px; max-width: none; overflow-y: auto; scrollbar-width: none; -ms-overflow-style: none; }
  #sidebar::-webkit-scrollbar { display: none; }
}
@media (max-width: 768px) {
  #sidebar { width: max-content; max-width: none; }
  .nav-title { font-size: clamp(.875rem, 4vw, 1.125rem); }
}
</style>
