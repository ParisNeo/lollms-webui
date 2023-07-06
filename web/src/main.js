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
        // count: 0,
        mountedPersonalities: [],
        settingsChanged:false,
        isConnected: false, // Add the isConnected property
      }
    },
    mutations: {
      // increment (state) {
      //   state.count++
      // }
      setConnectionStatus(state, status) {
        state.isConnected = status;
      },      
    }
  })


app.use(router)
app.use(store)

app.mount('#app')