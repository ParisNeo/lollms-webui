<template>
  <div
    class=" min-w-96 items-start p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer  select-none"
    tabindex="-1" :class="selected_computed ? 'border-primary-light' : 'border-transparent'"
    :title="!personality.installed ? 'Not installed' : ''">

    <div :class="!personality.installed ? 'opacity-50' : ''">

      <div class="flex flex-row items-center  flex-shrink-0 gap-3">
        <img ref="imgElement" :src="getImgUrl()" @error="defaultImg($event)"
          class="w-10 h-10 rounded-full object-fill text-red-700">
        <!-- :class="personality.installed ? 'grayscale-0':'grayscale'" -->
        <h3 class="font-bold font-large text-lg line-clamp-3">
          {{ personality.name }}
        </h3>
        <button type="button" title="Talk"
            @click="toggleSelected"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="">
            <i data-feather="check" class="w-5"></i>
            <span class="sr-only">Select</span>
        </button>        
        <button type="button" title="Talk"
            @click="toggleTalk"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="">
            <i data-feather="send" class="w-5"></i>
            <span class="sr-only">Talk</span>
        </button>        
        <InteractiveMenu  :commands="commandsList" :force_position=2>
        
        </InteractiveMenu>
  
      </div>
      <div class="">
        <div class="">

          <div class="flex items-center">
            <i data-feather="user" class="w-5 m-1"></i>
            <b>Author:&nbsp;</b>

            {{ personality.author }}
          </div>
          <div v-if="personality.languages" class="flex items-center">
            <i data-feather="globe" class="w-5 m-1"></i>
            <b>Languages:&nbsp;</b>
            <select id="languages" v-model ="personality.lang"
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                <option v-for="(item, index) in personality.languages" :key="index"
                    :selected="item == personality.languages[0]">{{
                        item
                    }}

                </option>

            </select>
          </div>          
          <div class="flex items-center">
            <i data-feather="bookmark" class="w-5 m-1"></i>
            <b>Category:&nbsp;</b>

            {{ personality.category }}
          </div>

        </div>
        <div class="flex items-center">
          <i data-feather="info" class="w-5 m-1"></i>
          <b>Description:&nbsp;</b><br>
        </div>
        <p class="mx-1 opacity-80 line-clamp-3" :title="personality.description">{{ personality.description }}</p>


      </div>
    </div>
  </div>
</template>

<script>
import { nextTick } from 'vue'
import feather from 'feather-icons'
import botImgPlaceholder from "../assets/logo.svg"
import userImgPlaceholder from "../assets/default_user.svg"
import InteractiveMenu from "@/components/InteractiveMenu.vue"

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
export default {
  props: {
    personality: {},
    selected: Boolean,
    full_path: String,
    onTalk:Function,
    onSelected: Function,
    onMounted: Function,
    onRemount: Function,
    onReinstall: Function,
    onSettings: Function
  },
  components:{
    InteractiveMenu
  },
  data() {
    return {
      isMounted: false,
      name: this.personality.name,
    };
  },
  computed:{
    commandsList(){
      let main_menu = [
                {name:this.isMounted?"unmount":"mount", icon: "feather:settings", is_file:false, value:this.toggleMounted},
                {name:"reinstall", icon: "feather:terminal", is_file:false, value:this.toggleReinstall},
              ];
        if(this.selected){
          main_menu.push({name:"settings", icon: "feather:settings", is_file:false, value:this.toggleSettings})
        }
        return main_menu
      },  
      selected_computed(){
        return this.selected
    }
  },
  mounted() {

    this.isMounted = this.personality.isMounted

    nextTick(() => {
      feather.replace()


    })
  },
  methods: {
    getImgUrl() {
      return bUrl + this.personality.avatar
    },
    defaultImg(event) {
      event.target.src = botImgPlaceholder
    },
    toggleTalk() {
      this.onTalk(this)
    },
    toggleSelected() {
      if(this.isMounted){
        this.onSelected(this)
      }
    },
    reMount(){
      this.onRemount(this)
    },
    toggleMounted() {
      this.onMounted(this)
    },
    toggleSettings() {
      this.onSettings(this)
    },
    toggleReinstall() {
      this.onReinstall(this)
    },

  },
  watch: {
    selected() {
      nextTick(() => {
        feather.replace()


      })
    }
  }
};
</script>
