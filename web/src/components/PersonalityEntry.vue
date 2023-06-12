<template>
  <div
    class=" items-start p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer  active:scale-95 duration-75 select-none"
    @click.stop="toggleSelected" :class="selected ? ' border-primary-light' : 'border-transparent'">


    <div class="flex flex-row items-center  flex-shrink-0 gap-3">
      <img ref="imgElement" :src="getImgUrl()" @error="defaultImg($event)"
        class="w-10 h-10 rounded-full object-fill text-red-700">
      <h3 class="font-bold font-large text-lg line-clamp-3">
        {{ personality.name }}
      </h3>
      <div class="grow">
        <!-- EMPTY SPACE FILLER -->
      </div>
      <!-- ADVANCED OPTIONS - NOT IMPLEMENTED -->
      <div class="flex-none">

        <!--  -->
        <div class="flex items-center mb-4" @click.stop>
          <input id="default-checkbox" type="checkbox" v-model="isMounted" @change.stop="toggleMounted"
            class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600">
          <label for="default-checkbox" class="ml-2 text-sm font-medium">Mounted</label>
        </div>
      </div>


    </div>
    <div class="">
      <div class="">

        <div class="flex items-center">
          <i data-feather="user" class="w-5 m-1"></i>
          <b>Author:&nbsp;</b>

          {{ personality.author }}
        </div>
        <!-- <div class="">
  <b>Language:&nbsp;</b>
  {{ personality.language }}
</div>
<div class="">
  <b>Category:&nbsp;</b>
  {{ personality.category }}
</div> -->
      </div>
      <div class="flex items-center">
        <i data-feather="info" class="w-5 m-1"></i>
        <b>Description:&nbsp;</b><br>
      </div>
      <p class="mx-1 opacity-80 line-clamp-3" :title="personality.description">{{ personality.description }}</p>


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
 
  },
  data() {
    return {
      isMounted:false
    };
  },
  mounted() {

    this.isMounted=this.personality.isMounted

    nextTick(() => {
      feather.replace()


    })
  },
  computed: {

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

  }
};
</script>
