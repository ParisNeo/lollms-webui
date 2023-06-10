<template>

  <div class="flex items-center p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer  active:opacity-80 duration-75 "
    @click.stop="toggleSelected" :class="selected ? ' border-primary-light' : 'border-transparent'">


    <div class="flex-1" v-if="model.isCustomModel">
      <div class="flex gap-3 items-center">
        <img :src="getImgUrl()" @error="defaultImg($event)" class="w-10 h-10 rounded-lg object-fill">
        <h3 class="font-bold font-large text-lg">
          {{ title }}
        </h3>
      </div>

    </div>
    <div class="flex-1" v-if="!model.isCustomModel">
      <div class="flex flex-row gap-3 items-center ">
        <img ref="imgElement" :src="getImgUrl()" @error="defaultImg($event)" class="w-10 h-10 rounded-lg object-fill" :class="linkNotValid ? 'grayscale':''">
        <h3 class="font-bold font-large text-lg">
          {{ title }}
        </h3>
        <div class="flex-grow">

        </div>

      </div>
      <div class="flex flex-shrink-0 items-center ">
        <i  data-feather="download" class="w-5 m-1" ></i>
        <b>Manual download:&nbsp;</b>
        
        <a :href="path" @click.stop class="flex items-center  hover:text-secondary duration-75 active:scale-90"
          title="Download this manually (faster) and put it in the models/<your binding> folder under your home directory/Documents/lollms folder then refresh">
            
           
          {{ title }}
          
        </a>
      </div>
      <div class="flex flex-shrink-0 items-center">
        <div class="flex flex-shrink-0 items-center" :class="linkNotValid? 'text-red-600':''">
          <i data-feather="file" class="w-5 m-1"></i>
          
        <b>File size:&nbsp;</b>
        
          {{ fileSize }}
        </div>

      </div>
      <div class="flex flex-shrink-0 items-center">
        <i data-feather="key" class="w-5 m-1"></i>
        <b>License:&nbsp;</b>
        {{ license }}
      </div>
      <div class="flex flex-shrink-0 items-center">
        <i data-feather="user" class="w-5 m-1"></i>
        <b>Owner:&nbsp;</b>
        <a :href="owner_link" target="_blank"  rel="noopener noreferrer" @click.stop class="flex hover:text-secondary duration-75 active:scale-90"
          title="Owner's profile">
          
          {{ owner }}
        </a>
      </div>
      <div class="flex items-center">
        <i data-feather="info" class="w-5 m-1"></i>
        <b>Description:&nbsp;</b><br>
      </div>
      <p class="mx-1 opacity-80">{{ description }}</p>
    </div>
    <div class="flex flex-row flex-shrink-0 items-center"  >
      <button class="text-lg hover:text-secondary duration-75 active:scale-90 p-2"
            title="Copy model info to clipboard" @click.stop="toggleCopy()">
            <i data-feather="clipboard"></i>
      </button>
      <button v-if="model_type !== 'api'" class="px-4 py-2 rounded-md text-white font-bold transition-colors duration-300"
        :class="[isInstalled ? 'bg-red-500 hover:bg-red-600' : linkNotValid ? 'bg-gray-500 hover:bg-gray-600' : 'bg-green-500 hover:bg-green-600']"
        :disabled="installing || uninstalling" @click.stop="toggleInstall">
        <template v-if="installing">
          <div class="flex items-center space-x-2">
            <div class="h-2 w-20 bg-gray-300 rounded">
              <div :style="{ width: progress + '%' }" class="h-full bg-red-500 rounded"></div>
            </div>
            <span>Installing...{{ Math.floor(progress) }}%</span>
          </div>
        </template>
        <template v-else-if="uninstalling">
          <div class="flex items-center space-x-2">
            <div class="h-2 w-20 bg-gray-300 rounded">
              <div :style="{ width: progress + '%' }" class="h-full bg-green-500"></div>
            </div>
            <span>Uninstalling...</span>
          </div>
        </template>
        <template v-else>
          {{ isInstalled ? model.isCustomModel ? 'Delete' : 'Uninstall' : linkNotValid ? 'Link is not valid':'Install' }}
        </template>
      </button>

    </div>

  </div>

</template>

<script>
import filesize from '../plugins/filesize'
import axios from "axios";
import { nextTick } from 'vue'
import feather from 'feather-icons'
import defaultImgPlaceholder from "../assets/default_model.png"
const bUrl = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
  props: {
    title: String,
    icon: String,
    path: String,
    owner: String,
    owner_link: String,
    license: String,
    description: String,
    isInstalled: Boolean,
    onInstall: Function,
    onUninstall: Function,
    onSelected: Function,
    onCopy: Function,
    selected: Boolean,
    model: Object,
    model_type: String
  },
  data() {
    return {
      progress: 0,
      installing: false,
      uninstalling: false,
      failedToLoad: false,
      fileSize: '',
      linkNotValid:false,
    };
  },
  async mounted() {
    this.fileSize = await this.getFileSize(this.model.path)
    //console.log('model path', this.model.path)
    nextTick(() => {
      feather.replace()


    })
  },
  methods: {
    computedFileSize(size){
            return filesize(size)
        },
    async getFileSize(url) {
      //console.log(this.model_type);
      if(this.model_type!="api"){
        try {
          const res = await axios.head(url)
          //console.log("addddd",url, res.headers)
          if (res) {
            
            if (res.headers["content-length"]) {
              return this.computedFileSize(res.headers["content-length"])
            }
            if (this.model.filesize) {
              return this.computedFileSize(this.model.filesize)
            }
            return 'Could not be determined'

          }
          if (this.model.filesize) {

            return this.computedFileSize(this.model.filesize)
          }
          return 'Could not be determined'

          // Example response
          // {
          //   date: 'Tue, 03 Apr 2018 14:29:32 GMT',
          //   'content-type': 'application/javascript; charset=utf-8',
          //   'content-length': '9068',
          //   connection: 'close',
          //   'last-modified': 'Wed, 28 Feb 2018 04:16:30 GMT',
          //   etag: '"5a962d1e-236c"',
          //   expires: 'Sun, 24 Mar 2019 14:29:32 GMT',
          //   'cache-control': 'public, max-age=30672000',
          //   'access-control-allow-origin': '*',
          //   'cf-cache-status': 'HIT',
          //   'accept-ranges': 'bytes',
          //   'strict-transport-security': 'max-age=15780000; includeSubDomains',
          //   'expect-ct': 'max-age=604800, report-uri="https://report-uri.cloudflare.com/cdn-cgi/beacon/expect-ct"',
          //   server: 'cloudflare',
          //   'cf-ray': '405c3a5cba7a68ba-CDG'
          // }


          } catch (error) {
          console.log(error.message,'getFileSize')
          this.linkNotValid=true
          return 'Could not be determined'

          }
      }


    },
    getImgUrl() {

      if (this.icon === '/images/default_model.png') {
        return defaultImgPlaceholder
      }

      return this.icon
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
        this.installing = true;
        this.onInstall(this);

      }
    },
    toggleSelected() {
      this.onSelected(this)
    },
    toggleCopy() {
 
      this.onCopy(this)
    },
    handleSelection() {
      if (this.isInstalled && !this.selected) {
        this.onSelected(this);
      }
    },
    copyContentToClipboard() {
      console.log('asdasdas')
            this.$emit('copy', 'this.message.content')

        },
  },
  watch:{
    linkNotValid(){
      nextTick(() => {
      feather.replace()


    })
    }
  }
};
</script>
