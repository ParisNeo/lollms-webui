<template>
  <div class=" items-start p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer"
    @click.stop="toggleSelected" :class="selected ? ' border-primary-light' : 'border-transparent'">


    <div class="flex flex-row items-center  flex-shrink-0 gap-3">
      <img :src="getImgUrl()" @error="defaultImg($event)" class="w-10 h-10 rounded-full object-fill text-red-700">
      <h3 class="font-bold font-large text-lg line-clamp-3">
        {{ binding.name }}
      </h3>


    </div>
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
      </div>
      <div class="flex items-center">
        <i data-feather="info" class="w-5 m-1"></i>
        <b>Description:&nbsp;</b><br>
      </div>
      <p class="mx-1 opacity-80 line-clamp-3" :title="binding.description">{{ binding.description }}</p>


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
    selected: Boolean
  },
  data() {
    return {

    };
  },
  mounted() {
    nextTick(() => {
      feather.replace()


    })
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

  }
};
</script>
