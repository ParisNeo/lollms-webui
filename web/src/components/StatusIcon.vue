<template>
    <div :class="{'text-green-500': status, 'text-red-500': !status}" :title="status ? titleTrue : titleFalse">
      <i v-if="icon" :data-feather="icon"></i>
      <b v-else class="text-2xl">{{ iconTrue }}</b>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      status: Boolean,
      icon: String,
      iconTrue: String,
      iconFalse: String,
      titleTrue: String,
      titleFalse: String,
    }
  }
  </script>
  