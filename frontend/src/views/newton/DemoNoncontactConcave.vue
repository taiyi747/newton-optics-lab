<template>
  <ExperimentPage v-bind="config" />
</template>

<script setup>
import ExperimentPage from './components/ExperimentPage.vue'
import { useI18n } from '../../utils/i18n.js'

const { t } = useI18n()

const config = {
  title: t('平凸透镜和平凹透镜 - 非接触式'),
  intensityTitle: t('间距影响分析图'),
  canvasPrefix: 'demo-noncontact-concave',
  renderType: 'doubleLensNonContact',
  r1Key: 'convexRadius',
  r2Key: 'concaveRadius',
  principle: [
    t('平凸透镜与平凹透镜非接触式牛顿环是通过调节两透镜间的间距来观察干涉现象。')
  ],
  principleImg: '/img/凸透镜和凹透镜非接触.png',
  sliders: [
    { key: 'wavelength', label: t('波长 (nm)'), min: 400, max: 760, step: 1, default: 589, decimals: 1 },
    { key: 'convexRadius', label: t('平凸透镜曲率半径R1 (m)'), min: 10, max: 20, step: 0.1, default: 10, decimals: 1 },
    { key: 'concaveRadius', label: t('平凹透镜曲率半径R2 (m)'), min: 10, max: 20, step: 0.1, default: 10, decimals: 1 },
    { key: 'spacing', label: t('间距h (nm)'), min: 0, max: 10000, step: 1, default: 0, decimals: 1 },
    { key: 'refractive', label: t('折射率n'), min: 1, max: 1.5, step: 0.01, default: 1, decimals: 2 }
  ]
}
</script>
