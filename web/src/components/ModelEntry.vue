<template>
  <div
    class="relative items-start p-4 hover:bg-primary-light  rounded-lg mb-2 shadow-lg border-2 select-none"
    :class="computed_classes" 
    :title="model.name">
    <!-- CUSTOM MODEL VIEW -->
    <div class="flex flex-row" v-if="model.isCustomModel">
      <div class="max-w-[300px] overflow-x-auto">
        <div class="flex gap-3 items-center grow">
          <a :href="model.model_creator_link" target="_blank">
            <img :src="getImgUrl()" @error="defaultImg($event)" class="w-10 h-10 rounded-lg object-fill">
          </a>
          <div class="flex-1 overflow-hidden">
            <h3 class="font-bold font-large text-lg truncate">
              {{ model.name }}
            </h3>
          </div>
        </div>
      </div>


    </div>

    <div v-if="model.isCustomModel" class="flex items-center flex-row gap-2 my-1">
      <!-- CONTROLS -->
      <div class="flex grow items-center">
        <button type="button" title="Custom model / local model"
          class="font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="">
          <i data-feather="box" class="w-5"></i>
          <span class="sr-only">Custom model / local model</span>
        </button>
        Custom model
      </div>
      <input v-model="model.selected" @click.stop="toggleSelected" type="checkbox" class='cursor-pointer border-2 border-blue-300 rounded w-10 h-10'>
      <div>
        <button v-if="model.isInstalled" title="Delete file from disk" type="button" @click.stop="toggleInstall"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300  rounded-lg  dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900">
          Uninstall
          <span class="sr-only">Remove</span>
        </button>
      </div>




    </div>
    <div v-if="installing"
      class="absolute z-10 -m-4 p-5 shadow-md text-center rounded-lg w-full h-full bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel bg-opacity-70 dark:bg-opacity-70 flex justify-center items-center">
      <!-- DOWNLOAD MODEL PANEL SPINNER -->
      <div class="relative flex flex-col items-center justify-center flex-grow h-full">
        <div role="status" class=" justify-center ">
          <!-- SPINNER -->
          <svg aria-hidden="true" class="w-24 h-24 mr-2 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600"
            viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
              fill="currentColor" />
            <path
              d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
              fill="currentFill" />
          </svg>
          <span class="sr-only">Loading...</span>
        </div>
        <div class="relative flex flex-row flex-grow items-center w-full h-full bottom-0">
          <!-- PROGRESS BAR -->
          <div class="w-full bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel  rounded-lg p-2">


            <div class="flex justify-between mb-1">
              <span class="text-base font-medium text-blue-700 dark:text-white">Downloading</span>
              <span class="text-sm font-medium text-blue-700 dark:text-white">{{ Math.floor(progress) }}%</span>
            </div>
            <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
              <div class="bg-blue-600 h-2.5 rounded-full" :style="{ width: progress + '%' }"></div>
            </div>
            <div class="flex justify-between mb-1">
              <span class="text-base font-medium text-blue-700 dark:text-white">Download speed: {{ speed_computed
              }}/s</span>
              <span class="text-sm font-medium text-blue-700 dark:text-white">{{ downloaded_size_computed }}/{{
                total_size_computed }}</span>
            </div>
          </div>
        </div>
        <div class="flex flex-grow">
          <!-- CANCEL BUTTON -->

          <div class="flex  flex-row flex-grow gap-3">
            <div class="p-2 text-center grow">
              <!-- <button @click.stop="hide(true)" type="button"
                                class="mr-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm  sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                                {{ ConfirmButtonText }}
                            </button> -->
              <button @click.stop="toggleCancelInstall" type="button" title="Cancel download"
                class="text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-gray-200 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-10 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600">
                Cancel
              </button>
            </div>

          </div>
        </div>
      </div>

    </div>
    <div v-if="!model.isCustomModel">
      <div class="flex flex-row items-center   gap-3 ">
        <img ref="imgElement" :src="getImgUrl()" @error="defaultImg($event)" class="w-10 h-10 rounded-lg object-fill"
          :class="linkNotValid ? 'grayscale' : ''">
        <h3 class="font-bold font-large text-lg truncate">
          {{ model.name }}
        </h3>
        <div class="grow">
          <!-- EMPTY SPACE FILLER -->
        </div>
        <input v-model="model.selected" @click.stop="toggleSelected" type="checkbox" class='cursor-pointer border-2 border-blue-300 rounded w-10 h-10'>

        <InteractiveMenu  :commands="commandsList" :force_position=2 title="Menu">
        
        </InteractiveMenu>

      </div>
      <div class="flex items-center flex-row-reverse gap-2 my-1">
        <!-- CONTROLS -->

        <div class="flex flex-row  items-center ">

          <div v-if="linkNotValid" class="text-base text-red-600 flex  items-center mt-1 ">
            <i data-feather="alert-triangle" class="flex-shrink-0 mx-1"></i>
            Link is not valid
          </div>
        </div>


      </div>
      <div class="" :title="!model.isInstalled ? 'Not installed' : model.name">
        <div class="">
          <!-- <div class="flex flex-row  items-center ">

            <div v-if="linkNotValid" class="text-base text-red-600 flex  items-center mt-1 ">
              <i data-feather="alert-triangle" class="flex-shrink-0 mx-1"></i>
              Link is not valid
            </div>
          </div> -->
          <div class="flex flex-row  items-center ">

            <i data-feather="download" class="w-5 m-1 flex-shrink-0"></i>
            <b>Card:&nbsp;</b>

            <a :href="'https://huggingface.co/'+model.quantizer+'/'+model.name" target="_blank" @click.stop
              class="m-1 flex items-center  hover:text-secondary duration-75 active:scale-90 truncate"
              :title="linkNotValid ? 'Link is not valid' : 'Download this manually (faster) and put it in the models/<current binding> folder then refresh'">

              View full model card

            </a>
            <div class="grow"></div>
            <button
              class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center "
              title="Copy link to clipboard" @click.stop="toggleCopyLink()">
              <i data-feather="clipboard" class="w-5"></i>
            </button>

          </div>

          <div class="flex items-center">
            <div class="flex flex-shrink-0 items-center" :class="linkNotValid ? 'text-red-600' : ''">
              <i data-feather="file" class="w-5 m-1"></i>

              <b>File size:&nbsp;</b>

              {{ fileSize }}
            </div>

          </div>
          <div class="flex items-center">
            <i data-feather="key" class="w-5 m-1"></i>
            <b>License:&nbsp;</b>
            {{ model.license }}
          </div>
          <div class="flex items-center">
            <i data-feather="user" class="w-5 m-1"></i>
            <b>quantizer:&nbsp;</b>
            <a :href="'https://huggingface.co/'+model.quantizer" target="_blank" rel="noopener noreferrer" @click.stop
              class="flex hover:text-secondary duration-75 active:scale-90" title="quantizer's profile">

              {{ model.quantizer }}
            </a>
          </div>
          <div class="flex items-center">
            <i data-feather="user" class="w-5 m-1"></i>
            <b>Model creator:&nbsp;</b>
            <a :href="model.model_creator_link" target="_blank" rel="noopener noreferrer" @click.stop
              class="flex hover:text-secondary duration-75 active:scale-90" title="quantizer's profile">

              {{ model.model_creator }}
            </a>
          </div>
          <div class="flex items-center">
            <i data-feather="clock" class="w-5 m-1"></i>
            <b>Release date:&nbsp;</b>
              {{ model.last_commit_time }}
          </div>
          <div class="flex items-center">
            <i data-feather="grid" class="w-5 m-1"></i>
            <b>Category:&nbsp;</b>
            <a :href="'https://huggingface.co/'+model.model_creator" target="_blank" rel="noopener noreferrer" @click.stop
              class="flex hover:text-secondary duration-75 active:scale-90" title="quantizer's profile">

              {{ model.category }}
            </a>
          </div>          
          <div class="flex items-center">
            <i data-feather="user" class="w-5 m-1"></i>
            <b>Hugging face rank:&nbsp;</b>
            <a href="https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard" target="_blank" rel="noopener noreferrer" @click.stop
              class="flex hover:text-secondary duration-75 active:scale-90" title="quantizer's profile">

              {{ model.rank }}
            </a>
          </div>          
        </div>
        

      </div>
    </div>
  </div>

</template>



<script>
import filesize from '../plugins/filesize'
import axios from "axios";
import { nextTick } from 'vue'
import feather from 'feather-icons'
import defaultImgPlaceholder from "../assets/default_model.png"
import InteractiveMenu from "@/components/InteractiveMenu.vue"

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
export default {
  components:{InteractiveMenu},
  props: {
    isInstalled: Boolean,
    onInstall: Function,
    onCancelInstall: Function,
    onUninstall: Function,
    onSelected: Function,
    onCopy: Function,
    onCopyLink: Function,
    selected: Boolean,
    model: Object,
    model_type: String
  },
  data() {
    return {
      progress: 0,
      speed: 0,
      total_size: 0,
      downloaded_size: 0,
      start_time: '',
      installing: false,
      uninstalling: false,
      failedToLoad: false,
      linkNotValid: false,
      selected_variant: ''
    };
  },
  async mounted() {
    nextTick(() => {
      feather.replace()


    })
  },
  methods: {
    formatFileSize(sizeInBytes) {
    if (sizeInBytes < 1024) {
      return sizeInBytes + " bytes";
    } else if (sizeInBytes < 1024 * 1024) {
      return (sizeInBytes / 1024).toFixed(2) + " KB";
    } else if (sizeInBytes < 1024 * 1024 * 1024) {
      return (sizeInBytes / (1024 * 1024)).toFixed(2) + " MB";
    } else {
      return (sizeInBytes / (1024 * 1024 * 1024)).toFixed(2) + " GB";
    }
  },    
    computedFileSize(size) {
      return filesize(size)
    },
    getImgUrl() {

      if(this.model.icon==undefined){
        return defaultImgPlaceholder
      }
      if (this.model.icon === '/images/default_model.png') {
        return defaultImgPlaceholder
      }

      return this.model.icon
    },
    defaultImg(event) {
      event.target.src = defaultImgPlaceholder
    },
    toggleInstall() {

      if (this.isInstalled) {
        this.uninstalling = true;
        // Simulate uninstallation delay (replace this with your WebSocket logic)
        this.onUninstall(this);
      } else {
        //this.installing = true;
        this.onInstall(this);
      }
    },
    toggleSelected(force=false) {
      this.onSelected(this,force)
    },
    toggleCopy() {

      this.onCopy(this)
    },
    toggleCopyLink() {
      this.onCopyLink(this)
      //navigator.clipboard.writeText(this.path)
    },
    toggleCancelInstall() {
      this.onCancelInstall(this)

    },
    handleSelection() {
      if (this.isInstalled && !this.selected) {
        this.onSelected(this);
      }
    },
    copyContentToClipboard() {
      this.$emit('copy', 'this.message.content')

    },
  },
  computed: {
    computed_classes(){
      if(!this.model.isInstalled){
        return 'border-transparent'
      }
      if(this.selected){
        return 'border-4 border-gray-200 bg-primary'
      }      
      return 'border-0 border-primary bg-primary'
    },
    commandsList(){
      let main_menu = [
                {name:this.model.isInstalled?"Uninstall":"Install", icon: "feather:settings", is_file:false, value:this.toggleInstall},
                {name:"Copy model info to clipboard", icon: "feather:settings", is_file:false, value:this.toggleCopy},
              ];
        if(this.selected){
          main_menu.push({name:"Reload", icon: "feather:refresh-ccw", is_file:false, value:this.toggleSelected})
        }
        return main_menu
      },  
      selected_computed(){
        return this.selected
    },    
    fileSize: {
        get() {
          // console.log(this.model)
          if (this.model && this.model.variants && this.model.variants.length > 0) {
            const sizeInBytes = this.model.variants[0]["size"];
            return this.formatFileSize(sizeInBytes);
          }
          return null; // Return null if the conditions are not met
        },
    },
    speed_computed() {
      return filesize(this.speed)
    },
    total_size_computed() {
      return filesize(this.total_size)
    },
    downloaded_size_computed() {
      return filesize(this.downloaded_size)
    },

  },
  watch: {
    linkNotValid() {
      nextTick(() => {
        feather.replace()


      })
    }
  }
};
</script>
