<template>
  <transition name="fade">
    <div v-if="showPopup" class="fixed inset-0 flex items-center justify-center z-50">
      <div class="bg-white dark:bg-gray-800 rounded shadow p-6 m-4 max-w-xs max-h-full text-center overflow-auto">
        <button @click="hide" class="mb-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          Hide
        </button>
        <iframe :src="webpageUrl" class="w-full"></iframe>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  data() {
    return {
      showPopup: false,
      webpageUrl: 'https://lollms.com/index.php/news/',
    };
  },
  methods: {
    show() {
      this.showPopup = true;
    },
    hide() {
      this.showPopup = false;
    },
  },
};
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity .5s;
}
.fade-enter, .fade-leave-to {
  opacity: 0;
}
.dark-theme {
  /* Add your dark theme CSS here */
}
.light-theme {
  /* Add your light theme CSS here */
}
</style>
