import { createRouter, createWebHistory } from 'vue-router'
import ExtensionsView from '../views/ExtensionsView.vue'
import HelpView from '../views/HelpView.vue'
import SettingsView from '../views/SettingsView.vue'
import TrainingView from '../views/TrainingView.vue'
import DiscussionsView from '../views/DiscussionsView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/extensions/',
      name: 'extensions',
      component: ExtensionsView
    },
    {
      path: '/help/',
      name: 'help',
      component: HelpView
    },
    {
      path: '/settings/',
      name: 'settings',
      component: SettingsView
    },
    {
      path: '/training/',
      name: 'training',
      component: TrainingView
    },
    {
      path: '/',
      name: 'discussions',
      component: DiscussionsView
    },

  ],
  // scrollBehavior
 
})


export default router
