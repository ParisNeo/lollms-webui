import { createApp, ref } from 'vue'
import { createStore } from 'vuex'
import App from './App.vue'
import router from './router'

import './assets/tailwind.css'

const app = createApp(App)

// Create a new store instance.
const store = createStore({
    state () {
      return {
        count: 0,
        mountedPersonalities: {}
      }
    },
    mutations: {
      increment (state) {
        state.count++
      }
    }
  })


app.use(router)
app.use(store)

app.mount('#app')