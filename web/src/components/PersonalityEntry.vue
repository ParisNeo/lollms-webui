<template>
  <div
    class=" min-w-96 items-start p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer  active:scale-95 duration-75 select-none"
    @click.stop="toggleSelected" :class="selected_computed ? 'border-primary-light' : 'border-transparent'"
    :title="!personality.installed ? 'Not installed' : ''">

    <div :class="!personality.installed ? 'opacity-50' : ''">

      <div class="flex flex-row items-center  flex-shrink-0 gap-3">
        <img ref="imgElement" :src="getImgUrl()" @error="defaultImg($event)"
          class="w-10 h-10 rounded-full object-fill text-red-700">
        <!-- :class="personality.installed ? 'grayscale-0':'grayscale'" -->
        <h3 class="font-bold font-large text-lg line-clamp-3">
          {{ personality.name }}
        </h3>




      </div>
      <div class="flex items-center flex-row-reverse gap-2 my-1">
        <!-- CONTROLS -->
        <button v-if="selected_computed" type="button" title="Settings" @click.stop="toggleSettings"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          Settings

          <span class="sr-only">Settings</span>
        </button>

        <button v-if="!isMounted" title="Mount personality" type="button"
          @click.stop="toggleMounted"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center text-white bg-blue-700 rounded-lg hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
          Mount

          <span class="sr-only">Click to install</span>
        </button>
        <button v-if="isMounted" title="Unmount personality" type="button" @click.stop="toggleMounted"
          class="inline-flex items-center gap-2 px-3 py-2 text-xs font-medium text-center focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300  rounded-lg  dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900">
          Unmount

          <span class="sr-only">Remove</span>
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
const bUrl = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
  props: {
    personality: {},
    onSelected: Function,
    selected: Boolean,
    onMounted: Function,
    full_path: String,
    onSettings: Function


  },
  data() {
    return {
      isMounted: false,
      name: this.personality.name
    };
  },
  mounted() {

    this.isMounted = this.personality.isMounted

    nextTick(() => {
      feather.replace()


    })
  },
  computed: {
selected_computed(){
  return this.selected
}
  },
  methods: {
    getImgUrl() {
      return bUrl + this.personality.avatar
    },
    defaultImg(event) {
      event.target.src = botImgPlaceholder
    },
    toggleSelected() {
      this.onSelected(this)
    },
    toggleMounted() {
      this.onMounted(this)
    },
    toggleSettings() {
      this.onSettings(this)
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
