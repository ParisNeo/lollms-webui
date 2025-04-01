<template>
  <div class="flex flex-col items-center justify-center w-full h-full min-h-screen p-8 bg-gradient-welcome">
    <div class="text-center max-w-4xl">
      <div class="flex items-center justify-center gap-8 mb-12">
        <div class="relative w-24 h-24">
          <img
            :src="logoSrc"
            alt="LoLLMS Logo"
            class="w-24 h-24 rounded-full absolute animate-rolling-ball shadow-lg border-2 border-blue-300 dark:border-blue-600"
          >
        </div>
        <div v-if="$store.state.config!=null&&$store.state.config.app_custom_name!=null&&$store.state.config.app_custom_name!=''" class="flex flex-col items-start">
          <h1 class="text-6xl font-bold text-gradient-title">
              {{$store.state.config.app_custom_name}}
            </h1>
        </div>
        <div v-else class="flex flex-col items-start">
            <h1 class="text-6xl font-bold text-gradient-title">
              {{$store.state.theme_vars.lollms_title}}
            </h1>
            <p class="text-2xl italic mt-2 text-subtitle">
              Lord of Large Language And Multimodal Systems
            </p>
        </div>
      </div>
      <div v-if="$store.state.config!=null&&$store.state.config.app_custom_name!=null&&$store.state.config.app_custom_name!=''"  class="space-y-8 animate-fade-in-up">
        <p class="text-lg md:text-xl text-blue-700 dark:text-blue-200" v-html="$store.state.config.app_custom_welcome_message">
        </p>

      </div>
      <div v-else class="space-y-8 animate-fade-in-up">
        <h2 class="text-4xl font-semibold text-blue-700 dark:text-blue-200">
          {{$store.state.theme_vars.lollms_welcome_short_message}}
        </h2>
        <p class="text-lg md:text-xl max-w-3xl mx-auto text-blue-800 dark:text-blue-300">
          {{$store.state.theme_vars.lollms_welcome_message}}
        </p>
        <!-- New section for latest news -->
        <div v-if="latestNews" class="mt-12 p-6 card animate-fade-in-up max-h-60 overflow-y-auto scrollbar">
          <h3 class="text-2xl font-medium text-blue-600 dark:text-blue-300 mb-3 border-b border-blue-300 dark:border-blue-600 pb-2">Latest LoLLMS News</h3>
          <p class="text-base text-blue-700 dark:text-blue-300" v-html="latestNews"></p>
        </div>
      </div>

      <div v-if="error" class="mt-6 text-red-500 dark:text-red-400">{{ error }}</div>
    </div>

    <!-- Floating button for latest ParisNeo video -->
    <div v-if="showVideoButton" class="floating-button-container">
      <a :href="videoUrl" target="_blank" class="floating-button" @click="handleClick">
        <span class="tooltip">New ParisNeo Video!</span>
        <img
          :src="getImageForVideoType"
          :alt="'New ' + videoType"
          class="w-full h-full object-cover"
        >
      </a>
    </div>
  </div>
</template>

<style scoped>
/* Keep existing animations and floating button styles as they are custom */
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
  z-index: 9999; /* Ensure it's above other content */
}

.floating-button {
  position: relative; /* Changed from fixed to relative to container */
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background-color: rgba(255, 69, 0, 0.9); /* Keeping custom color for distinction */
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 0 30px rgba(255, 69, 0, 0.8);
  animation: pulse 1.5s infinite, glow 2s infinite, wobble 3s infinite;
  overflow: hidden; /* Keep overflow hidden for image */
  transition: all 0.3s ease;
  cursor: pointer;
}

.floating-button:hover {
  transform: scale(1.2) rotate(5deg);
  background-color: rgba(255, 69, 0, 1);
}

.tooltip {
  position: absolute;
  background-color: rgba(0, 0, 0, 0.8); /* Keeping custom tooltip style */
  color: white;
  padding: 8px 12px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  white-space: nowrap;
  opacity: 0;
  transition: opacity 0.3s ease, transform 0.3s ease;
  pointer-events: none;
  top: -50px; /* Position above the button */
  left: 50%;
  transform: translateX(-50%) scale(0.9);
}

.floating-button:hover .tooltip {
  opacity: 1;
  transform: translateX(-50%) scale(1);
}

@keyframes pulse {
  0% { transform: scale(1); }
  50% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

@keyframes glow {
  0% { box-shadow: 0 0 30px rgba(255, 69, 0, 0.8); }
  50% { box-shadow: 0 0 60px rgba(255, 69, 0, 1), 0 0 90px rgba(255, 69, 0, 0.6); }
  100% { box-shadow: 0 0 30px rgba(255, 69, 0, 0.8); }
}

@keyframes wobble {
  0%, 100% { transform: rotate(-3deg); }
  50% { transform: rotate(3deg); }
}
</style>