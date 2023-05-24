<template>
  <div class=" items-start p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer"
    @click.stop="toggleSelected" :class="selected ? ' border-primary-light' : 'border-transparent'">


    <div class="flex flex-row items-center  flex-shrink-0 gap-3">
      <img :src="getImgUrl()" @error="defaultImg($event)" class="w-10 h-10 rounded-full object-fill text-red-700">
      <h3 class="font-bold font-large text-lg line-clamp-3">
      {{ personality.name }}
    </h3>


    </div>
    <div class="">
      <div class="">

<div class="">
  <b>Author:&nbsp;</b>
  {{ personality.author }}
</div>
<div class="">
  <b>Language:&nbsp;</b>
  {{ personality.language }}
</div>
<div class="">
  <b>Category:&nbsp;</b>
  {{ personality.category }}
</div>
</div>
      <b>Description:&nbsp;</b><br>

      <p class="opacity-80 line-clamp-3" :title="personality.description">{{ personality.description }}</p>


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
      return bUrl + this.personality.avatar
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
