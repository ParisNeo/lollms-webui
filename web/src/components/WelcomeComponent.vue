<template>
    <div class="flex flex-col items-center justify-center w-full h-full min-h-screen bg-gradient-to-br from-indigo-100 to-purple-100 dark:from-indigo-900 dark:to-purple-900 p-8">
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
              L🍓LLMS
            </h1>
            <p class="text-2xl text-gray-600 dark:text-gray-300 italic mt-2">
              Lord of Large Language And Multimodal Systems
            </p>
          </div>
        </div>
        
        <div class="space-y-8 animate-fade-in-up">
          <h2 class="text-4xl font-semibold text-gray-800 dark:text-gray-200">
            Welcome to L🍓LLMS WebUI
          </h2>
          <p class="text-xl text-gray-600 dark:text-gray-300 max-w-3xl mx-auto">
            Embark on a journey through the realm of advanced AI with L🍓LLMS, your ultimate companion for intelligent conversations and multimodal interactions. Unleash the power of large language models and explore new frontiers in artificial intelligence.
          </p>
          <div class="mt-12 space-y-6">
            <p class="text-lg text-gray-700 dark:text-gray-300">
              Discover the capabilities of L🍓LLMS:
            </p>
            <ul class="text-left list-disc list-inside text-gray-600 dark:text-gray-300 space-y-2">
              <li>Engage in natural language conversations</li>
              <li>Generate creative content and ideas</li>
              <li>Analyze complex data and provide insights</li>
              <li>Assist with coding and technical tasks</li>
              <li>Process and understand multimodal inputs</li>
            </ul>
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