<template>
    <div v-if="show" class="fixed top-0 left-0 right-0 bottom-0 flex items-center justify-center bg-black bg-opacity-50">
      <div class="bg-bg-light dark:bg-bg-dark p-8 rounded-lg shadow-lg">
        <h3 class="text-lg font-medium">{{ message }}</h3>
        <div class="mt-4 flex justify-center">
          <button @click="hide" class="bg-primary hover:bg-primary-light active:scale-95 duration-150 text-white px-4 py-2 rounded-lg shadow-lg hover:bg-secondary-dark">
            OK
          </button>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        show: false,
        message: "",
      };
    },
    methods: {
      hide() {
        this.show = false;
        this.$emit("ok");
      },
      showMessage(message) {
        this.message = message;
        this.show = true;
      },
    },
  };
  </script>
  