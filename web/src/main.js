import { createApp, ref } from 'vue'
import { createStore } from 'vuex'
import axios from "axios";
import App from './App.vue'
import router from './router'

import './assets/tailwind.css'

const app = createApp(App)
console.log("Loaded main.js")

// Create a new store instance.
export const store = createStore({
    state () {
      return {
        // count: 0,
        mountedPersonalities: [],
        settingsChanged:false,
        isConnected: false, // Add the isConnected property
        config:null,
        mountedPers:null,
        personalities:null,
      }
    },
    mutations: {
      setConfig(state, config) {
        state.config = config;
      },
      setPersonalities(state, personalities) {
        state.personalities = personalities;
      },
      setMountedPers(state, mountedPers) {
        state.mountedPers = mountedPers;
      },

      // increment (state) {
      //   state.count++
      // }    
    },
    getters: {
      getConfig(state) {
        return state.config
      },
      getIsConnected(state) {
        return state.isConnected
      },
      getMountedPers(state) {
        return state.mountedPers;
      }
    },
    actions: {
      async refreshConfig({ commit }) {
        console.log("Fetching configuration");
        try {
          const configFile = await api_get_req('get_config');
          commit('setConfig', configFile);
          console.log("Configurations recovered")
          console.log(configFile)
          console.log(this.state.config)
        } catch (error) {
          console.log(error.message, 'refreshConfig');
          // Handle error
        }
      },
      async refreshPersonalitiesArr({ commit }) {
          let personalities = []
          console.log("Getting personalities 0")
          const dictionary = await api_get_req("get_all_personalities")
          console.log("Getting personalities 2")
          const langkeys = Object.keys(dictionary); // returns languages folder names
          console.log("Getting personalities 3")
          for (let i = 0; i < langkeys.length; i++) {
              const langkey = langkeys[i];
              const catdictionary = dictionary[langkey];
              const catkeys = Object.keys(catdictionary); // returns categories

              for (let j = 0; j < catkeys.length; j++) {
                  const catkey = catkeys[j];
                  const personalitiesArray = catdictionary[catkey];
                  const modPersArr = personalitiesArray.map((item) => {

                      const isMounted = this.state.config.personalities.includes(langkey + '/' + catkey + '/' + item.folder)
                      // if (isMounted) {
                      //     console.log(item)
                      // }
                      let newItem = {}
                      newItem = item
                      newItem.category = catkey // add new props to items
                      newItem.language = langkey // add new props to items
                      newItem.full_path = langkey + '/' + catkey + '/' + item.folder // add new props to items
                      newItem.isMounted = isMounted // add new props to items
                      return newItem
                  })


                  if (personalities.length == 0) {
                      personalities = modPersArr
                  } else {
                      personalities = personalities.concat(modPersArr)
                  }
              }

          }
          console.log("Getting personalities 3")

          personalities.sort((a, b) => a.name.localeCompare(b.name))
          commit('setPersonalities',personalities)

          console.log("Done")
      },
      refreshMountedPersonalities({ commit }) {
          let mountedPersArr = []
          console.log(this.state.config.personalities.length)
          // console.log('perrs listo',this.state.personalities)
          for (let i = 0; i < this.state.config.personalities.length; i++) {
              const full_path_item = this.state.config.personalities[i]
              const index = this.state.personalities.findIndex(item => item.full_path == full_path_item)

              const pers = this.state.personalities[index]
              if (pers) {
                  mountedPersArr.push(pers)
              }
              else {
                  mountedPersArr.push(this.state.personalities[this.state.personalities.findIndex(item => item.full_path == "english/generic/lollms")])
              }
          }
          this.mountedPersArr = []
          this.state.mountedPersArr = mountedPersArr
          console.log('refreshMountedPersonalities', mountedPersArr)
          console.log('fig', this)

          this.state.mountedPers = this.state.personalities[this.state.personalities.findIndex(item => item.full_path == this.state.config.personalities[this.state.config.active_personality_id])]
      },
    }    
})
async function api_get_req(endpoint) {
  try {
    const res = await axios.get('/' + endpoint);

    if (res) {
      return res.data;
    }
  } catch (error) {
    console.log(error.message, 'api_get_req');
    throw error;
  }
}

let actionsExecuted = false;

app.mixin({
  beforeMount() {
    if (!actionsExecuted) {
      actionsExecuted = true;

      this.$store.dispatch('refreshConfig').then(() => {
        this.$store.dispatch('refreshPersonalitiesArr').then(() => {
          this.$store.dispatch('refreshMountedPersonalities');
          this.$store.dispatch('refreshPersonalityPath');
        });
      });
    }
  }
})

app.use(router)
app.use(store)

app.mount('#app')