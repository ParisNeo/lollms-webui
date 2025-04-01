<template>
  <transition name="fade">
    <div v-if="showPopup" class="fixed inset-0 flex items-center justify-center z-50 bg-black bg-opacity-50">
      <div class="relative panels-color p-6 rounded-lg shadow-xl max-w-3xl w-full mx-4">
        <button @click="hide" class="absolute top-2 right-2 svg-button z-10" title="Close">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        <iframe :src="webpageUrl" class="w-full h-[70vh] rounded-md border border-blue-300 dark:border-blue-600 bg-white dark:bg-blue-900"></iframe>
        <div class="flex items-center mt-4">
          <input type="checkbox" id="startup" class="rounded border-blue-300 dark:border-blue-600 text-blue-600 focus:ring-blue-500 dark:bg-blue-700 dark:focus:ring-offset-blue-800" v-model="this.$store.state.config.show_news_panel" @change="save_configuration">
          <label for="startup" class="ml-2 label !mb-0 cursor-pointer">Show at startup</label> <!-- Use label class from theme -->
        </div>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.popup-container {
  background-color: #fff;
  color: #333;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 24px;
  width: 100%;
  height: 100%;
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.close-button {
  position: absolute;
  top: 16px;
  right: 16px;
  background-color: #3490dc;
  color: white;
  font-weight: bold;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.close-button:hover {
  background-color: #2779bd;
}

.iframe-content {
  width: 100%;
  height: 80%;
  border: none;
  margin-bottom: 16px;
}

.checkbox-container {
  display: flex;
  align-items: center;
  justify-content: center;
}

.styled-checkbox {
  width: 24px;
  height: 24px;
  accent-color: #3490dc;
  cursor: pointer;
}

.checkbox-label {
  margin-left: 8px;
  font-size: 16px;
  cursor: pointer;
  user-select: none;
}
</style>




<script>
import axios from "axios";

export default {
  data() {
    return {
      showPopup: false,
      webpageUrl: 'https://lollms.com/',
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
      axios.post('/apply_settings', {"client_id":this.$store.state.client_id, "config":this.$store.state.config}).then((res) => {
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
