import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import { createStore } from 'vuex'
import App from './App.vue';
import Install from './views/Install.vue';
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


// Create a new store instance.
export const store = createStore({
  state () {
    return {
      // count: 0,
    }
  },
  mutations: {      
     
  },
  getters: {
  },
  actions: {
  }    
})

createApp(App).use(router).mount('#app');
