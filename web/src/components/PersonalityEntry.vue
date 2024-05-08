<template>
  <div
    class=" min-w-96 items-start p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer  select-none"
    tabindex="-1" 
    :class="selected_computed ? 'border-2 border-primary-light' : 'border-transparent', isMounted ? 'bg-blue-200 dark:bg-blue-700':''"
    :title="!personality.installed ? 'Not installed' : ''">

    <div :class="!personality.installed ? 'border-red-500' : ''">

      <div class="flex flex-row items-center  flex-shrink-0 gap-3">
        <img @click="toggleSelected" ref="imgElement" :src="getImgUrl()" @error="defaultImg($event)"
          class="w-10 h-10 rounded-full object-fill text-red-700 cursor-pointer">
        <!-- :class="personality.installed ? 'grayscale-0':'grayscale'" -->
        <h3 @click="toggleSelected" class="font-bold font-large text-lg line-clamp-3 cursor-pointer">
          {{ personality.name }}
        </h3>
        <button
              class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center "
              title="Copy link to clipboard" @click.stop="toggleCopyLink()">
              <i data-feather="clipboard" class="w-5"></i>
            </button>        
      </div>
      <div class="">
        <div class="">

          <div class="flex items-center">
            <i data-feather="user" class="w-5 m-1"></i>
            <b>Author:&nbsp;</b>

            {{ personality.author }}
          </div>
          <div class="flex items-center">
            <i data-feather="git-commit" class="w-5 m-1"></i>
            <b>Version:&nbsp;</b>

            {{ personality.version }}
          </div>
          
          <div v-if="personality.languages && select_language" class="flex items-center">
            <i data-feather="globe" class="w-5 m-1"></i>
            <b>Languages:&nbsp;</b>
            <select v-if="!isMounted" id="languages" v-model ="personality.language"
                class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                <option v-for="(item, index) in personality.languages" :key="index"
                    :selected="item == personality.languages[0]">{{
                        item
                    }}

                </option>

            </select>
          </div>
          <div v-if="personality.language" class="flex items-center">
            <i data-feather="globe" class="w-5 m-1"></i>
            <b>Language:&nbsp;</b>
            {{ personality.language }}
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
        <p class="mx-1 opacity-80 h-20  overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary" :title="personality.description"  v-html="personality.description"></p>
      </div>
      <div class="rounded bg-blue-300">
          <button v-if="isMounted" type="button" title="Select"
            @click="toggleSelected"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="">
            <i 
            data-feather="check"  
            ></i>
            <span class="sr-only">Select</span>
        </button>        
        <button v-if="isMounted" type="button" title="Talk"
            @click="toggleTalk"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="">
            <i data-feather="send" class="w-5"></i>
            <span class="sr-only">Talk</span>
        </button>      
        <button type="button" title="Show_folder"
            @click="showFolder"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="">
            <i data-feather="folder" class="w-5"></i>
            <span class="sr-only">Show Folder</span>
        </button>      

          
        <InteractiveMenu  :commands="commandsList" :force_position=2 title="Menu">
        
        </InteractiveMenu>

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
    select_language: Boolean,
    selected: Boolean,
    full_path: String,
    onTalk:Function,
    onOpenFolder:Function,
    onSelected: Function,
    onMount: Function,
    onUnMount: Function,
    onRemount: Function,
    onCopyToCustom: Function,
    onEdit: Function,
    onReinstall: Function,
    onSettings: Function,
    onCopyPersonalityName: Function
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
                {name:this.isMounted?"unmount":"mount", icon: "feather:settings", is_file:false, value:this.isMounted?this.unmount:this.mount},
                {name:"reinstall", icon: "feather:terminal", is_file:false, value:this.toggleReinstall},
              ];
        console.log("this.category",this.personality.category)
        if(this.personality.category=="custom_personalities"){
          main_menu.push({name:"edit", icon: "feather:settings", is_file:false, value:this.edit})
        }
        else{
          main_menu.push({name:"Copy to custom personas folder for editing", icon: "feather:copy", is_file:false, value:this.copyToCustom})
        }
        if(this.isMounted){
          main_menu.push({name:"remount", icon: "feather:refresh-ccw", is_file:false, value:this.reMount})
        }
        if(this.selected && this.personality.has_scripts){
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
    showFolder() {
      this.onOpenFolder(this)
    },
    toggleTalk() {
      this.onTalk(this)
    },
    toggleCopyLink() {
      this.onCopyPersonalityName(this)
      //navigator.clipboard.writeText(this.path)
    },
    toggleSelected() {
      if(this.isMounted){
        this.onSelected(this)
      }
    },
    edit(){
      this.onEdit(this)
    },
    copyToCustom(){
      this.onCopyToCustom(this)
    },
    reMount(){
      this.onRemount(this)
    },
    mount() {
      console.log("Mounting")
      this.onMount(this)
    },
    unmount() {
      console.log("Unmounting")
      console.log(this.onUnMount)
      this.onUnMount(this)
      this.isMounted=false
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
