<template>
    <div>
      <input v-model="inputValue" :placeholder="placeholderText" />
      <button @click="pasteFromClipboard"><i data-feather="clipboard"></i></button>
    </div>
  </template>
  
  <script>
  import feather from 'feather-icons'
  export default {
    data() {
      return {
        inputValue: "",
        placeholderText: "Enter text here",
      };
    },
    mounted() {
        console.log('mnted all chat', this.allDiscussionPersonalities)
        nextTick(() => {
            feather.replace()
        })
    },
    methods: {
      pasteFromClipboard() {
        navigator.clipboard.readText().then((text) => {
          this.inputValue = text;
        });
      },
    },
  };
  </script>
  