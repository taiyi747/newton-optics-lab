<template>
  <ExperimentPage v-bind="config" />
</template>

<script setup>
import ExperimentPage from './components/ExperimentPage.vue'
import { useI18n } from '../../utils/i18n.js'

const { t } = useI18n()

const config = {
  title: t('平凸透镜和平凸透镜 - 接触式'),
  intensityTitle: t('双凸面干涉分析图'),
  canvasPrefix: 'demo-convex',
  renderType: 'doubleLens',
  r1Key: 'convex1Radius',
  r2Key: 'convex2Radius',
  principle: [
    t('两个平凸透镜接触式牛顿环是由两个平凸透镜接触形成的特殊干涉装置。'),
    t('两个凸面之间的空气薄膜会产生独特的干涉条纹，其分布与两个透镜的曲率半径都有关系。')
  ],
  principleImg: '/img/凸透镜和凸透镜接触式.png',
  sliders: [
    { key: 'wavelength', label: t('波长 (nm)'), min: 400, max: 760, step: 1, default: 589, decimals: 1 },
    { key: 'convex1Radius', label: t('平凸透镜曲率半径R1 (m)'), min: 10, max: 20, step: 0.1, default: 10, decimals: 1 },
    { key: 'convex2Radius', label: t('平凸透镜曲率半径R2 (m)'), min: 10, max: 20, step: 0.1, default: 10, decimals: 1 },
    { key: 'refractive', label: t('折射率n'), min: 1, max: 1.5, step: 0.01, default: 1, decimals: 2 }
  ]
}
</script>
