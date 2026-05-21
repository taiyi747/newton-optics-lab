<template>
  <ExperimentPage v-bind="config" />
</template>

<script setup>
import ExperimentPage from './components/ExperimentPage.vue'
import { useI18n } from '../../utils/i18n.js'

const { t } = useI18n()

const config = {
  title: t('普通牛顿环'),
  intensityTitle: t('光强分布图'),
  canvasPrefix: 'demo-normal',
  ringCanvasSize: 0,
  renderType: 'normal',
  isNonContact: true,
  principle: [
    t('牛顿环是由一个平凸透镜与一个平面玻璃接触形成的空气薄膜产生的等厚干涉条纹。'),
    t('当单色光垂直入射时，在空气薄膜的上下表面反射的两束光发生干涉，形成明暗相间的环形条纹。')
  ],
  principleImg: '/img/普通牛顿环.png',
  sliders: [
    { key: 'wavelength', label: t('波长λ (nm)'), min: 400, max: 760, step: 1, default: 589, decimals: 1 },
    { key: 'radius', label: t('曲率半径R (m)'), min: 10, max: 20, step: 0.1, default: 10, decimals: 1 },
    { key: 'refractive', label: t('折射率n'), min: 1, max: 1.5, step: 0.01, default: 1, decimals: 2 },
    { key: 'spacing', label: t('间距h (nm)'), min: 0, max: 10000, step: 1, default: 0, decimals: 1 }
  ]
}
</script>
