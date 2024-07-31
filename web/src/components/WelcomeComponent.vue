<template>
    <div class="flex flex-col items-center justify-center w-full h-full bg-gradient-to-br from-blue-100 to-purple-100 dark:from-blue-900 dark:to-purple-900">
      <div class="text-center">
        <div class="flex items-center justify-center gap-4 mb-8">
          <div class="relative w-20 h-80">
            <img 
              :src="logoSrc" 
              alt="LoLLMS Logo" 
              class="w-20 h-20 rounded-full absolute animate-ball-bounce"
            >
          </div>
          <div class="flex flex-col items-start">
            <h1 class="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 dark:from-blue-400 dark:to-purple-400">
              LoLLMS
            </h1>
            <p class="text-xl text-gray-600 dark:text-gray-300 italic">
              One tool to rule them all
            </p>
          </div>
        </div>
        
        <div class="space-y-6 animate-fade-in-up">
          <h2 class="text-3xl font-semibold text-gray-800 dark:text-gray-200">
            Welcome to LoLLMS WebUI
          </h2>
          <p class="text-xl text-gray-600 dark:text-gray-300">
            Your gateway to powerful language models and intelligent conversations
          </p>
          <div class="flex justify-center space-x-4 mt-8">
            <button class="px-6 py-3 text-white bg-blue-600 rounded-full hover:bg-blue-700 transform hover:scale-105 transition-all duration-200 ease-in-out shadow-lg">
              Create New Discussion
            </button>
            <button class="px-6 py-3 text-blue-600 bg-white border-2 border-blue-600 rounded-full hover:bg-blue-50 transform hover:scale-105 transition-all duration-200 ease-in-out shadow-lg">
              Select Existing Discussion
            </button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import { ref, computed } from 'vue'
  import { useStore } from 'vuex'
  import storeLogo from '@/assets/logo.png'
  
  export default {
    name: 'WelcomeComponent',
    setup() {
      const store = useStore()
  
      const logoSrc = computed(() => {
        if (!store.state.config) return storeLogo
        return store.state.config.app_custom_logo 
          ? `/user_infos/${store.state.config.app_custom_logo}` 
          : storeLogo
      })
  
      return {
        logoSrc
      }
    }
  }
  </script>
  
  <style scoped>
  @keyframes ball-bounce {
    0%, 100% { 
      transform: translateY(0) rotate(0deg); 
      animation-timing-function: ease-out;
    }
    25% { transform: translateY(-120px) rotate(90deg); }
    50% { transform: translateY(-160px) rotate(180deg); }
    75% { transform: translateY(-40px) rotate(270deg); }
    85%, 95% {
      transform: translateY(0) rotate(360deg);
      animation-timing-function: ease-in;
    }
    90%, 97% {
      transform: translateY(-20px) rotate(360deg);
      animation-timing-function: ease-out;
    }
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
  
  .animate-ball-bounce {
    animation: ball-bounce 4s infinite;
  }
  
  .animate-fade-in-up {
    animation: fade-in-up 1s ease-out;
  }
  </style>