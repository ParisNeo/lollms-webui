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
          <p class="text-2xl text-gray-600 dark:text-gray-300 italic mt-2">
            Lord of Large Language And Multimodal Systems
          </p>
        </div>
      </div>
      
      <div class="space-y-8 animate-fade-in-up">
        <h2 class="text-4xl font-semibold text-gray-800 dark:text-gray-200">
          {{$store.state.theme_vars.lollms_welcome_short_message}}
        </h2>
        <p class="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
          {{$store.state.theme_vars.lollms_welcome_message}}
        </p>
      </div>

      <!-- New section for latest news -->
      <div id="newsContainer" class="mt-12 p-6 bg-gray-100 dark:bg-gray-800 rounded-lg shadow-md animate-fade-in-up overflow-y-scroll" style="display: none;">
        <h3 class="text-2xl font-semibold text-gray-800 dark:text-gray-200 mb-4">Latest LoLLMS News</h3>
        <p id="newsContent" class="text-gray-600 dark:text-gray-300"></p>
      </div>
      <div id="errorContainer" class="mt-6 text-red-500 dark:text-red-400" style="display: none;"></div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import storeLogo from '@/assets/logo.png'
import axios from 'axios'

export default {
  name: 'WelcomeComponent',
  setup() {
    const store = useStore()
    const latestNews = ref('')
    const error = ref('')

    const logoSrc = computed(() => {
      if (!store.state.config) return storeLogo
      return store.state.config.app_custom_logo 
        ? `/user_infos/${store.state.config.app_custom_logo}` 
        : storeLogo
    })

    const fetchLatestNews = async () => {
      try {
        const response = await axios.get('/get_news')
        latestNews.value = response.data
        document.getElementById('newsContent').innerHTML = latestNews.value;
        document.getElementById('newsContainer').style.display = 'block';
      } catch (err) {
        console.error('Failed to fetch latest news:', err)
        error.value = 'Unable to fetch the latest news. Please try again later.'
        document.getElementById('errorContainer').textContent = err;
        document.getElementById('errorContainer').style.display = 'block';
      }
    }

    onMounted(() => {
      fetchLatestNews()
    })

    return {
      logoSrc,
      latestNews,
      error
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
</style>
