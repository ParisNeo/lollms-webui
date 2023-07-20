<template>
  <div
    class="relative items-start p-4 hover:bg-primary-light  hover:border-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer select-none"
    @click.stop="toggleSelected" :class="selected ? ' border-primary bg-primary' : 'border-transparent'" :title="title">
    <!-- CUSTOM MODEL VIEW -->
    <div class="flex flex-row" v-if="model.isCustomModel">
      <div class="flex gap-3 items-center grow">
        <img :src="getImgUrl()" @error="defaultImg($event)" class="w-10 h-10 rounded-lg object-fill">
        <h3 class="font-bold font-large text-lg truncate ">
          {{ title }}
        </h3>
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
          {{ title }}
        </h3>
        <div class="grow">
          <!-- EMPTY SPACE FILLER -->
        </div>
        <!-- ADVANCED OPTIONS -->
        <div class="flex-none gap-1">
          <!-- <button v-if="!model.isInstalled" type="button" title="Not installed"
            class="hover:text-red-600 duration-75 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center "
            @click.stop="">
            <i data-feather="slash" class="w-5"></i>
            <span class="sr-only">Not installed</span>
          </button>
          <button v-if="!model.isInstalled" type="button" title="Click to install model"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center "
            @click.stop="toggleInstall">
            <i data-feather="plus-square" class="w-5"></i>
            <span class="sr-only">Install</span>
          </button>
          <button v-if="model.isInstalled"
            class=" hover:text-red-600 duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center "
            title="Delete file from disk" type="button" @click.stop="toggleInstall">
            <i data-feather="trash" class="w-5"></i>
          </button>
          <button
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center "
            title="Copy model info to clipboard" @click.stop="toggleCopy()">
            <i data-feather="clipboard" class="w-5"></i>
          </button> -->
          <!-- <button v-if="selected" type="button" title="Settings"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center "
            @click.stop="toggleSettings">
            <i data-feather="sliders" class="w-5"></i>
            <span class="sr-only">Settings</span>
          </button> -->
          <!-- - NOT IMPLEMENTED -->
          <!-- 
          <button type="button" title="Help - Not implemented"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="">
            <i data-feather="help-circle" class="w-5"></i>
            <span class="sr-only">Help</span>
          </button> -->
        </div>

      </div>
      <div class="flex items-center flex-row-reverse gap-2 my-1">
        <!-- CONTROLS -->
        <button type="button" title="Copy model info to clipboard" @click.stop="toggleCopy()"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          Copy info

          <span class="sr-only">Copy info</span>
        </button>
        <div class="flex flex-row  items-center ">

          <div v-if="linkNotValid" class="text-base text-red-600 flex  items-center mt-1 ">
            <i data-feather="alert-triangle" class="flex-shrink-0 mx-1"></i>
            Link is not valid
          </div>
        </div>
        <button v-if="!model.isInstalled && !linkNotValid" title="Click to install" type="button"
          @click.stop="toggleInstall"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          Install

          <span class="sr-only">Click to install</span>
        </button>
        <button v-if="model.isInstalled" title="Delete file from disk" type="button" @click.stop="toggleInstall"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300  rounded-lg  dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900">
          Uninstall

          <span class="sr-only">Remove</span>
        </button>

      </div>
      <div class="" :title="!model.isInstalled ? 'Not installed' : title">
        <div class="">
          <!-- <div class="flex flex-row  items-center ">

            <div v-if="linkNotValid" class="text-base text-red-600 flex  items-center mt-1 ">
              <i data-feather="alert-triangle" class="flex-shrink-0 mx-1"></i>
              Link is not valid
            </div>
          </div> -->
          <div class="flex flex-row  items-center ">

            <i data-feather="download" class="w-5 m-1 flex-shrink-0"></i>
            <b>Manual download:&nbsp;</b>



            <a :href="path" @click.stop
              class="m-1 flex items-center  hover:text-secondary duration-75 active:scale-90 truncate"
              :title="linkNotValid ? 'Link is not valid' : 'Download this manually (faster) and put it in the models/<current binding> folder then refresh'">


              Click here to download

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
            {{ license }}
          </div>
          <div class="flex items-center">
            <i data-feather="user" class="w-5 m-1"></i>
            <b>Owner:&nbsp;</b>
            <a :href="owner_link" target="_blank" rel="noopener noreferrer" @click.stop
              class="flex hover:text-secondary duration-75 active:scale-90" title="Owner's profile">

              {{ owner }}
            </a>
          </div>

        </div>
        <div class="flex items-center">
          <i data-feather="info" class="w-5 m-1"></i>
          <b>Description:&nbsp;</b><br>
        </div>
        <!-- <p class="mx-1 opacity-80 line-clamp-3" :title="description">{{ description }}</p> -->
        <p class="mx-1 opacity-80 line-clamp-3" :title="description">{{ description.replace(/<\/?[^>]+>/ig, " ") }}</p>
        <!-- <p class="mx-1 opacity-80 line-clamp-3" :title="description"><span v-html="description"></span></p> -->


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

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
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
    //this.fileSize = await this.getFileSize(this.model.path)
    //console.log('model path', this.model.path)
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
    async getFileSize(url) {
      if (this.model_type != "api") {
        try {
          const res = await axios.head(url)
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
          console.log(error.message, 'getFileSize')
          //this.linkNotValid = true
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
        //this.installing = true;
        this.onInstall(this);
      }
    },
    toggleSelected() {
      this.onSelected(this)
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
