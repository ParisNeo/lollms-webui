<template>
  <div class=" items-start p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer"
    @click.stop="toggleSelected" :class="selected ? ' border-primary-light' : 'border-transparent'">
    <h3 class="font-bold font-large text-lg">
        {{ personality.name }}
      </h3>
      
    <div class="flex flex-row items-center  flex-shrink-0 gap-3">
      <img :src="getImgUrl()" class="w-14 h-14 rounded-full object-fill text-red-700">
      
    
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
  </div>
    <div class="">

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

      if (this.personality.avatar) {
        return bUrl+this.personality.avatar

      }
      return botImgPlaceholder;
    },
    toggleSelected() {
      this.onSelected(this)
    },

  }
};
</script>
