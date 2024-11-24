<template>
  <div class="flex flex-col items-center justify-center w-full h-full min-h-screen p-8">
    <div class="text-center max-w-4xl">
      <div class="flex items-center justify-center gap-8 mb-12">
        <div class="relative w-24 h-24">
          <img 
            :src="logoSrc" 
            alt="LoLLMS Logo" 
            class="w-24 h-24 rounded-full absolute animate-rolling-ball"
          >
        </div>
        <div class="flex flex-col items-start">
          <h1 class="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-purple-600 dark:from-indigo-400 dark:to-purple-400">
            {{$store.state.theme_vars.lollms_title}}
          </h1>
          <p class="text-2xl italic mt-2">
            Lord of Large Language And Multimodal Systems
          </p>
        </div>
      </div>
      
      <div class="space-y-8 animate-fade-in-up">
        <h2 class="text-4xl font-semibold">
          {{$store.state.theme_vars.lollms_welcome_short_message}}
        </h2>
        <p class="text-xl max-w-3xl mx-auto">
          {{$store.state.theme_vars.lollms_welcome_message}}
        </p>
      </div>

      <!-- New section for latest news -->
      <div v-if="latestNews" class="mt-12 p-6 rounded-lg shadow-md animate-fade-in-up overflow-y-scroll scrollbar-thin">
        <h3>Latest LoLLMS News</h3>
        <p v-html="latestNews"></p>
      </div>
      <div v-if="error" class="mt-6 text-red-500">{{ error }}</div>
    </div>

    <!-- Floating button for latest ParisNeo video -->
    <div v-if="videoUrl && !buttonClicked" class="floating-button-container">
      <a :href="videoUrl" target="_blank" class="floating-button" @click="handleClick">
        <span class="tooltip">Latest ParisNeo Video</span>
        <img src="/play_video.png" alt="New Video" class="w-full h-full object-cover">
      </a>
    </div>
  </div>
</template>

<script>
import storeLogo from '@/assets/logo.png'
import axios from 'axios'

export default {
  name: 'WelcomeComponent',
  data() {
    return {
      buttonClicked: false,
      videoUrl: "",
      latestNews: "",
      error: ""
    }
  },
  computed: {
    logoSrc() {
      if (!this.$store.state.config) return storeLogo
      return this.$store.state.config.app_custom_logo 
        ? `/user_infos/${this.$store.state.config.app_custom_logo}` 
        : storeLogo
    }
  },
  methods: {
    async fetchLatestNews() {
      try {
        const response = await axios.get('/get_news')
        this.latestNews = response.data
      } catch (err) {
        console.error('Failed to fetch latest news:', err)
        this.error = 'Unable to fetch the latest news. Please try again later.'
      }
    },
    async fetchVideoUrl() {
      try {
        const response = await axios.get('/get_last_video_url')
        this.videoUrl = response.data
      } catch (err) {
        console.error('Failed to fetch video URL:', err)
        this.error = 'Unable to fetch the latest video URL. Please try again later.'
      }
    },
    handleClick() {
      localStorage.setItem('videoButtonClicked', 'true')
      this.buttonClicked = true
    }
  },
  mounted() {
    this.fetchLatestNews()
    this.fetchVideoUrl()
    if (localStorage.getItem('videoButtonClicked') === 'true') {
      this.buttonClicked = true
    }
  }
}
</script>

<style scoped>
@keyframes rolling-ball {
  0% { transform: translateX(-50px) rotate(0deg); }
  25% { transform: translateX(0) rotate(90deg); }
  50% { transform: translateX(50px) rotate(180deg); }
  75% { transform: translateX(0) rotate(270deg); }
  100% { transform: translateX(-50px) rotate(360deg); }
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}

@keyframes fade-in-up {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-rolling-ball {
  animation: rolling-ball 4s infinite ease-in-out, bounce 1s infinite ease-in-out;
}

.animate-fade-in-up {
  animation: fade-in-up 1.5s ease-out;
}

.floating-button-container {
  position: fixed;
  bottom: 30px;
  right: 30px;
  z-index: 9999;
}

.floating-button {
  position: fixed;
  bottom: 30px;
  right: 30px;
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background-color: rgba(79, 70, 229, 0.9);
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 0 20px rgba(79, 70, 229, 0.6);
  animation: pulse 1.5s infinite, glow 2s infinite;
  overflow: hidden;
  z-index: 9999;
  transition: all 0.3s ease;
}

.floating-button:hover {
  transform: scale(1.1);
  background-color: rgba(79, 70, 229, 1);
}

.tooltip {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  font-size: 14px;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
  top: -40px;
  left: 50%;
  transform: translateX(-50%);
}

.floating-button:hover .tooltip {
  opacity: 1;
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

@keyframes glow {
  0% { box-shadow: 0 0 20px rgba(79, 70, 229, 0.6); }
  50% { box-shadow: 0 0 40px rgba(79, 70, 229, 0.8), 0 0 60px rgba(79, 70, 229, 0.4); }
  100% { box-shadow: 0 0 20px rgba(79, 70, 229, 0.6); }
}

.hidden {
  display: none;
}
</style>
