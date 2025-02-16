<template>
  <div class="app-card flex flex-col h-full"
    :class="selected_computed ? 'border-primary-light' : 'border-transparent', isMounted ? 'bg-blue-200 dark:bg-blue-700' : ''"
    :title="!personality.installed ? 'Not installed' : ''">
    <div class="flex-grow">
      <div class="flex items-center mb-4">
        <img :src="getImgUrl()" @error="defaultImg($event)" alt="Personality Icon" 
          class="w-16 h-16 rounded-full border border-gray-300 mr-4 cursor-pointer"
          @click="toggleSelected"
          @mouseover="showThumbnail" @mousemove="updateThumbnailPosition" @mouseleave="hideThumbnail" />
        <div>
          <h3 class="font-bold text-xl text-gray-800 cursor-pointer" @click="toggleSelected">{{ personality.name }}</h3>
          <p class="text-sm text-gray-600">Author: {{ personality.author }}</p>
          <p class="text-sm text-gray-600">Version: {{ personality.version }}</p>
          <p class="text-sm text-gray-600">Category: {{ personality.category }}</p>
          <p v-if="personality.creation_date" class="text-sm text-gray-600">Creation Date: {{ formatDate(personality.creation_date) }}</p>
          <p v-if="personality.last_update_date" class="text-sm text-gray-600">Last update Date: {{ formatDate(personality.last_update_date) }}</p>
        </div>
        <!-- Add the help icon if help is available -->
        <button v-if="personality.help" @click="showHelp" class="ml-2 text-blue-500 hover:text-blue-600 transition duration-300 ease-in-out" title="Help">
          <i data-feather="help-circle" class="h-6 w-6"></i>
        </button>
      </div>

      <div class="mb-4">
        <h4 class="font-semibold mb-1 text-gray-700">Description:</h4>
        <p class="text-sm text-gray-600 h-20 overflow-y-auto" v-html="personality.description"></p>
      </div>

    </div>

    <div class="mt-auto pt-4 border-t">
      <div class="flex justify-between items-center flex-wrap">
        <button @click="toggleFavorite" class="text-yellow-500 hover:text-yellow-600 transition duration-300 ease-in-out" :title="isFavorite ? 'Remove from favorites' : 'Add to favorites'">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" :fill="isFavorite ? 'currentColor' : 'none'" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
          </svg>
        </button>
        <button v-if="isMounted" @click="toggleSelected" class="text-blue-500 hover:text-blue-600 transition duration-300 ease-in-out" title="Select">
          <i data-feather="check" class="h-6 w-6"></i>
        </button>
        <button v-if="isMounted" @click="toggleTalk" class="text-green-500 hover:text-green-600 transition duration-300 ease-in-out" title="Talk">
          <i data-feather="send" class="h-6 w-6"></i>
        </button>
        <button @click="showFolder" class="text-purple-500 hover:text-purple-600 transition duration-300 ease-in-out" title="Show Folder">
          <i data-feather="folder" class="h-6 w-6"></i>
        </button>
        <InteractiveMenu :commands="commandsList" :force_position="2" title="Menu" class="text-gray-500 hover:text-gray-600 transition duration-300 ease-in-out">
        </InteractiveMenu>
      </div>
    </div>

    <div v-if="thumbnailVisible" :style="{ top: thumbnailPosition.y + 'px', left: thumbnailPosition.x + 'px' }"
      class="fixed z-50 w-20 h-20 rounded-full overflow-hidden">
      <img :src="getImgUrl()" class="w-full h-full object-fill">
    </div>

    <!-- Help Popup -->
    <div v-if="showHelpPopup" class="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center">
      <div class="bg-white p-4 rounded-lg shadow-lg w-[500px] h-[400px] flex flex-col">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-lg font-bold">Help</h2>
          <button @click="closeHelp" class="text-red-500 hover:text-red-600">Close</button>
        </div>
        <div class="flex-grow overflow-auto">
          <div v-html="renderedHelp"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { nextTick } from "vue";
import feather from "feather-icons";
import { marked } from "marked"; // Correct import for marked
import botImgPlaceholder from "../assets/logo.png";
import userImgPlaceholder from "../assets/default_user.svg";
import InteractiveMenu from "@/components/InteractiveMenu.vue";

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
    onCopyPersonalityName: Function,
    onToggleFavorite: Function
  },
  components:{
    InteractiveMenu
  },
  data() {
    return {
      isMounted: false,
      name: this.personality.name,
      thumbnailVisible: false,
      thumbnailPosition: { x: 0, y: 0 },
      showHelpPopup: false, // State for help popup visibility
      renderedHelp: '' // Rendered markdown content
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
    console.log(this.personality)

    nextTick(() => {
      feather.replace()
    })
  },
  methods: {
    formatDate(dateString) {
        const options = { year: 'numeric', month: 'short', day: 'numeric' };
        return new Date(dateString).toLocaleDateString(undefined, options);
    },    
    showThumbnail() {
      this.thumbnailVisible = true;
    },
    hideThumbnail() {
      this.thumbnailVisible = false;
    },
    updateThumbnailPosition(event) {
      this.thumbnailPosition = {
        x: event.clientX + 10, // 10px offset to avoid cursor overlap
        y: event.clientY + 10
      };
    },    
    getImgUrl() {
      return bUrl + this.personality.avatar
    },
    defaultImg(event) {
      event.target.src = botImgPlaceholder
    },
    toggleFavorite() {
      this.onToggleFavorite(this)
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
    showHelp() {
      this.renderedHelp = marked(this.personality.help); // Render markdown
      this.showHelpPopup = true;
    },
    closeHelp() {
      this.showHelpPopup = false;
    }
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
