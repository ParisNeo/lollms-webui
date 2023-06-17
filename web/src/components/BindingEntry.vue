<template>
  <div class=" items-start p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer select-none"
    @click.stop="toggleSelected" :class="selected ? ' border-primary-light' : 'border-transparent'">

    <div :class="isTemplate ? 'opacity-50' : ''">
      <!-- 
<div class="inline-flex items-center"> -->


      <div class="flex flex-row items-center   gap-3 ">
        <img ref="imgElement" :src="getImgUrl()" @error="defaultImg($event)" class="w-10 h-10 rounded-full object-fill text-blue-700">
        <h3 class="font-bold font-large text-lg truncate">
          {{ binding.name }}
        </h3>
        <div class="grow">
          <!-- EMPTY SPACE FILLER -->
        </div>
        <!-- ADVANCED OPTIONS -->
        <div  class="flex-none gap-1">
          <button type="button" title="Reinstall binding"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="toggleReinstall">
            <i data-feather="tool" class="w-5"></i>
            <span class="sr-only">Reinstall binding</span>
          </button>
          <!-- - NOT IMPLEMENTED -->
          <!-- <button type="button" title="Settings - Not implemented"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="">
            <i data-feather="sliders" class="w-5"></i>
            <span class="sr-only">Settings</span>
          </button>
          <button type="button" title="Help - Not implemented"
            class="hover:text-secondary duration-75 active:scale-90 font-medium rounded-lg text-sm p-2 text-center inline-flex items-center " @click.stop="">
            <i data-feather="help-circle" class="w-5"></i>
            <span class="sr-only">Help</span>
          </button> -->
        </div>

      </div>
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
            <a :href="binding.link" target="_blank" class="flex items-center  hover:text-secondary duration-75 active:scale-90">
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
const bUrl = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
  props: {
    binding: {},
    onSelected: Function,
    onReinstall: Function,
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
    toggleReinstall() {
      this.onReinstall(this)
    },
    getStatus() {
      if (this.binding.folder === 'backend_template' || this.binding.folder === 'binding_template') {
        this.isTemplate = true


      }
    }

  },

};
</script>
