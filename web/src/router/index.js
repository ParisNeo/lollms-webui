import { createRouter, createWebHistory } from 'vue-router'
import PlayGroundView from '../views/PlayGroundView.vue'
import ExtensionsView from '../views/ExtensionsView.vue'
import HelpView from '../views/HelpView.vue'
import SettingsView from '../views/SettingsView.vue'
import TrainingView from '../views/TrainingView.vue'
import QuantizingView from '../views/QuantizingView.vue'
import DiscussionsView from '../views/DiscussionsView.vue'
import InteractiveView from '../views/InteractiveView.vue'
import NodesView from '../views/NodesView.vue'
import ComfyuiView from '../views/ComfyuiView.vue'
import AutoSDView from '../views/AutoSDView.vue'
import AppsZoo from '../views/AppsZoo.vue'
import PersonalitiesZoo from '../views/PersonalitiesZoo.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/apps_view/',
      name: 'AppsZoo',
      component: AppsZoo
    },
    {
      path: '/personalities_view/',
      name: 'PersonalitiesZoo',
      component: PersonalitiesZoo
    },    
    {
      path: '/auto_sd_view/',
      name: 'AutoSD',
      component: AutoSDView
    },
    {
      path: '/comfyui_view/',
      name: 'ComfyUI',
      component: ComfyuiView
    },
    {
      path: '/playground/',
      name: 'playground',
      component: PlayGroundView
    },
    {
      path: '/extensions/',
      name: 'extensions',
      component: ExtensionsView
    },
    {
      path: '/help_view/',
      name: 'help_view',
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
      path: '/quantizing/',
      name: 'quantizing',
      component: QuantizingView
    },
    {
      path: '/',
      name: 'discussions',
      component: DiscussionsView
    },
    {
      path: '/interactive/',
      name: 'interactive',
      component: InteractiveView
    },
    {
      path: '/nodes/',
      name: 'nodes',
      component: NodesView
    },

  ],
  // scrollBehavior
 
})


export default router
