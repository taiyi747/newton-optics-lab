import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/', redirect: '/newton/demo-normal' },
  {
    path: '/newton',
    component: () => import('../views/newton/components/NewtonLayout.vue'),
    children: [
      { path: 'demo-normal', name: 'DemoNormal', component: () => import('../views/newton/DemoNormal.vue') },
      { path: 'demo-principle', name: 'NewtonDemoPrinciple', component: () => import('../views/newton/DemoPrinciple.vue') },
      { path: 'result-analysis', name: 'NewtonDemoResultAnalysis', component: () => import('../views/newton/DemoResultAnalysis.vue') },
      { path: 'demo-contact-truncated', name: 'DemoContactTruncated', component: () => import('../views/newton/DemoContactTruncated.vue') },
      { path: 'demo-contact-concave', name: 'DemoContactConcave', component: () => import('../views/newton/DemoContactConcave.vue') },
      { path: 'demo-contact-convex', name: 'DemoContactConvex', component: () => import('../views/newton/DemoContactConvex.vue') },
      { path: 'demo-noncontact-concave', name: 'DemoNoncontactConcave', component: () => import('../views/newton/DemoNoncontactConcave.vue') },
      { path: 'demo-noncontact-convex', name: 'DemoNoncontactConvex', component: () => import('../views/newton/DemoNoncontactConvex.vue') },
      { path: 'simulation-manual', name: 'SimulationManual', component: () => import('../views/newton/SimulationManual.vue') },
      { path: 'simulation-guide', name: 'SimulationGuide', component: () => import('../views/newton/SimulationGuide.vue') },
      { path: 'data-normal', name: 'DataNormal', component: () => import('../views/newton/DataNormal.vue') },
      { path: 'ai-chat', name: 'AiChat', component: () => import('../views/AiChat.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
