<template>
  <ExperimentPage v-bind="config" />
</template>

<script setup>
import ExperimentPage from './components/ExperimentPage.vue'
import { useI18n } from '../../utils/i18n.js'

const { t } = useI18n()

const config = {
  title: t('截顶式近切割牛顿环'),
  intensityTitle: t('截顶效应分析图'),
  canvasPrefix: 'demo-truncated',
  renderType: 'truncated',
  principle: [
    t('截顶式近切割牛顿环是在普通牛顿环基础上，通过切割部分透镜形成的特殊干涉装置。'),
    t('截顶高度的变化会影响干涉条纹的分布和形状，产生独特的光学现象。')
  ],
  principleImg: '/img/截顶式.png',
  sliders: [
    { key: 'wavelength', label: t('波长 (nm)'), min: 400, max: 760, step: 1, default: 589, decimals: 1 },
    { key: 'radius', label: t('曲率半径 (m)'), min: 10, max: 20, step: 0.1, default: 10, decimals: 1 },
    { key: 'truncatedHeight', label: t('截顶高度 (nm)'), min: 0, max: 10000, step: 1, default: 5000, decimals: 1 },
    { key: 'refractive', label: t('折射率n'), min: 1, max: 1.5, step: 0.01, default: 1, decimals: 2 }
  ]
}
</script>
