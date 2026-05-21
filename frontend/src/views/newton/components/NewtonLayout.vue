<template>
  <div class="flex min-h-screen">
    <TheSidebar @toggle-guide="guideVisible = !guideVisible" />
    <main class="flex-1 p-6">
      <router-view />
    </main>
    <GuideModal :visible="guideVisible" :content="GUIDE_CONTENT" @close="guideVisible = false" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import TheSidebar from '../TheSidebar-newton.vue'
import GuideModal from '../../../components/GuideModal.vue'
import { GUIDE_CONTENT } from '../../../utils/config.js'
import { initImageContextMenu, bindZoomGuards } from '../../../utils/image-tools.js'

const guideVisible = ref(false)

onMounted(() => {
  initImageContextMenu()
  bindZoomGuards()
})
</script>
