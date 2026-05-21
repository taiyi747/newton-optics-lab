<template>
  <PdfViewer :title="t('牛顿环演示实验结果分析')" pdfName="newton_demo_analysis" />
</template>

<script setup>
import PdfViewer from './components/PdfViewer.vue'
import { useI18n } from '../../utils/i18n.js'

const { t } = useI18n()
</script>
