import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import Install from './components/Install.vue';
import './style.css';
const routes = [
  {
    path: '/',
    name: 'Install',
    component: Install,
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

createApp(App).use(router).mount('#app');
