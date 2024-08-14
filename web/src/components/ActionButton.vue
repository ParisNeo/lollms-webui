<template>
    <a :href="href" @click="onClick" class="text-2xl hover:text-primary transition duration-150 ease-in-out" :title="title">
      <i :data-feather="icon"></i>
    </a>
  </template>
  
  <script>
  export default {
    props: {
      href: {
        type: String,
        default: '#'
      },
      icon: {
        type: String,
        required: true
      },
      title: {
        type: String,
        default: ''
      }
    },
    methods: {
      onClick(event) {
        if (this.href === '#') {
          event.preventDefault();
          this.$emit('click');
        }
      }
    }
  }
  </script>
  