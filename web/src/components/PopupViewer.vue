<template>
  <transition name="fade">
    <div v-if="showPopup" class="fixed inset-0 flex items-center justify-center z-50 mt-15">
      <div class="bg-white dark:bg-gray-800 rounded shadow p-6 m-4 w-full h-full text-center overflow-auto relative">
        <button @click="hide" class="absolute top-0 right-0 m-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
          X
        </button>
        <iframe :src="webpageUrl" class="m-15 w-full h-full"></iframe>
        <div class="absolute bottom-0 mb-4 w-full text-center">
          <input type="checkbox" id="startup" v-model="this.$store.state.config.show_news_panel" @change="save_configuration">
          <label for="startup" class="m-5">Show at startup</label>
        </div>
      </div>
    </div>
  </transition>
</template>



<script>
import axios from "axios";

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
    save_configuration() {
      axios.post('/apply_settings', {"config":this.$store.state.config}).then((res) => {
          this.isLoading = false;
          if (res.data.status) {

              this.$store.state.toast.showToast("Configuration changed successfully.", 4, true)
              this.settingsChanged = false
          } else {

              this.$store.state.toast.showToast("Configuration change failed.", 4, false)

          }
      })
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
