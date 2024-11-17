<template>
    <div :title="title" :class="['text-2xl cursor-pointer', isOk ? 'text-green-500' : 'text-red-500']">
      <i v-if="typeof icon === 'string'" :data-feather="icon"></i>
      <b v-else class="text-2xl">{{ icon }}</b>
    </div>
  </template>
  
  <script>
  import feather from 'feather-icons'
  export default {
    props: {
      isOk: Boolean,
      icon: [String, Object],
      title: String
    },
    mounted() {
      if (typeof this.icon === 'string') {
        this.$nextTick(() => {
          feather.replace()
        })
      }
    }
  }
  </script>