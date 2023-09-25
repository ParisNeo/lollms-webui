<template>
  <div class=" items-start p-4 hover:bg-primary-light hover:border-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer select-none"
    @click.stop="toggleSelected" :class="selected ? ' border-primary bg-primary' : 'border-transparent'"
    :title="!binding.installed ? 'Not installed' : binding.name">

    <div>

      <div class="flex flex-row items-center   gap-3 ">
        <img ref="imgElement" :src="getImgUrl()" @error="defaultImg($event)"
          class="w-10 h-10 rounded-full object-fill text-blue-700">
        <h3 class="font-bold font-large text-lg truncate">
          {{ binding.name }}
        </h3>
        <div class="grow">
          <!-- EMPTY SPACE FILLER -->
        </div>
        <!-- ADVANCED OPTIONS -->
        <div class="flex-none gap-1">

          <!-- <button v-if="!binding.installed" type="button" title="Not installed"
            class="hover:text-red-600 duration-75 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center "
            @click.stop="">
            <i data-feather="slash" class="w-5"></i>
            <span class="sr-only">Not installed</span>
          </button> -->

          <!-- <button v-if="binding.installed" type="button" title="Reinstall binding"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center "
            @click.stop="toggleReinstall">
            <i data-feather="tool" class="w-5"></i>
            <span class="sr-only">Reinstall binding</span>
          </button>
          <button v-if="selected" type="button" title="Settings"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center "
            @click.stop="toggleSettings">
            <i data-feather="sliders" class="w-5"></i>
            <span class="sr-only">Settings</span>
          </button> -->
          <!-- - NOT IMPLEMENTED -->

          <button v-if="selected" type="button" title="Reload binding"
            @click="toggleReloadBinding"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="">
            <i data-feather="refresh-cw" class="w-5"></i>
            <span class="sr-only">Help</span>
          </button>
        </div>

      </div>
      <div class="flex items-center flex-row-reverse gap-2 my-1">
        <!-- CONTROLS -->
        <button v-if="!binding.installed" title="Click to install" type="button" @click.stop="toggleInstall"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          Install

          <span class="sr-only">Click to install</span>
        </button>
        <button v-if="binding.installed" title="Click to Reinstall binding" type="button"  @click.stop="toggleReinstall"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center focus:outline-none text-white bg-green-700 hover:bg-red-800 focus:ring-4 focus:ring-green-300  rounded-lg  dark:bg-green-600 dark:hover:bg-green-700 dark:focus:ring-red-900">
          Reinstall

          <span class="sr-only">Reinstall</span>
        </button>
        <button v-if="binding.installed" title="Click to Reinstall binding" type="button"  @click.stop="toggleUnInstall"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300  rounded-lg  dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900">
          Uninstall

          <span class="sr-only">UnInstall</span>
        </button>
        <button v-if="selected" title="Click to open Settings" type="button" @click.stop="toggleSettings"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          Settings

          <span class="sr-only">Settings</span>
        </button>
      </div>
      <DynamicUIRenderer v-if="binding.ui" class="w-full h-full" :code="binding.ui"></DynamicUIRenderer>
      <!-- <div class="  justify-end">
          <i data-feather="sliders" class="w-5 m-1"></i>
        </div>
      </div> -->
      <div class="">
        <div class="">

          <div class="flex items-center">
            <i data-feather="user" class="w-5 m-1"></i>
            <b>Author:&nbsp;</b>

            {{ binding.author }}
          </div>
          <div class="flex items-center">
            <i data-feather="folder" class="w-5 m-1"></i>
            <b>Folder:&nbsp;</b>

            {{ binding.folder }}
          </div>
          <div class="flex items-center">
            <i data-feather="git-merge" class="w-5 m-1"></i>
            <b>Version:&nbsp;</b>
            {{ binding.version }}
          </div>
          <div class="flex items-center">

            <i data-feather="github" class="w-5 m-1"></i>
            <b>Link:&nbsp;</b>
            <a :href="binding.link" target="_blank"
              class="flex items-center  hover:text-secondary duration-75 active:scale-90">
              {{ binding.link }}
            </a>
          </div>
        </div>
        <div class="flex items-center">
          <i data-feather="info" class="w-5 m-1"></i>
          <b>Description:&nbsp;</b><br>
        </div>
        <p class="mx-1 opacity-80 line-clamp-3" :title="binding.description">{{ binding.description }}</p>


      </div>
    </div>
  </div>
</template>

<script>
import { nextTick } from 'vue'
import feather from 'feather-icons'
import botImgPlaceholder from "../assets/logo.svg"
import userImgPlaceholder from "../assets/default_user.svg"
import DynamicUIRenderer from "@/components/DynamicUIRenderer.vue"

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
export default {
  components:{DynamicUIRenderer},
  props: {
    binding: {},
    onSelected: Function,
    onReinstall: Function,
    onInstall: Function,
    onUnInstall: Function,
    onSettings: Function,
    onReloadBinding: Function,
    selected: Boolean,

  },
  data() {
    return {
      isTemplate: false,

    };
  },
  mounted() {
    nextTick(() => {
      feather.replace()


    })
    // Disabled for now
    //this.getStatus()


  },
  methods: {
    getImgUrl() {
      return bUrl + this.binding.icon
    },
    defaultImg(event) {
      event.target.src = botImgPlaceholder
    },
    toggleSelected() {
        this.onSelected(this)
    },
    toggleInstall() {
        this.onInstall(this)
    },
    toggleUnInstall() {
        this.onUnInstall(this)
    },
    toggleReinstall() {
      this.onReinstall(this)
    },
    toggleReloadBinding(){
      this.onReloadBinding(this)
    },
    toggleSettings() {
      this.onSettings(this)
    },
    getStatus() {
      if (this.binding.folder === 'backend_template' || this.binding.folder === 'binding_template') {
        this.isTemplate = true


      }
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
