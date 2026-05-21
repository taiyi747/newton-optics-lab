<template>
  <PdfViewer :title="t('牛顿环演示实验原理')" pdfName="newton_demo_principle" />
</template>

<script setup>
import PdfViewer from './components/PdfViewer.vue'
import { useI18n } from '../../utils/i18n.js'

const { t } = useI18n()
</script>
