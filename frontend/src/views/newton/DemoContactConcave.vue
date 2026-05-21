<template>
  <ExperimentPage v-bind="config" />
</template>

<script setup>
import ExperimentPage from './components/ExperimentPage.vue'
import { useI18n } from '../../utils/i18n.js'

const { t } = useI18n()

const config = {
  title: t('平凸透镜和平凹透镜 - 接触式'),
  intensityTitle: t('曲率差异分析图'),
  canvasPrefix: 'demo-concave',
  renderType: 'doubleLens',
  r1Key: 'convexRadius',
  r2Key: 'concaveRadius',
  principle: [
    t('平凸透镜与平凹透镜接触式牛顿环是由两种不同曲率的透镜接触形成的特殊干涉装置。'),
    t('两种透镜的曲率差异会影响空气薄膜的厚度分布，从而产生独特的干涉条纹。')
  ],
  principleImg: '/img/凸透镜和凹透镜接触式.png',
  sliders: [
    { key: 'wavelength', label: t('波长 (nm)'), min: 400, max: 760, step: 1, default: 589, decimals: 1 },
    { key: 'convexRadius', label: t('平凸透镜曲率半径R1 (m)'), min: 10, max: 20, step: 0.1, default: 10, decimals: 1 },
    { key: 'concaveRadius', label: t('平凹透镜曲率半径R2 (m)'), min: 10, max: 20, step: 0.1, default: 10, decimals: 1 },
    { key: 'refractive', label: t('折射率n'), min: 1, max: 1.5, step: 0.01, default: 1, decimals: 2 }
  ]
}
</script>
