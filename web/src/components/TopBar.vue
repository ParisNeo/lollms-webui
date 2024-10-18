<template>
  <div class="dock-container" @mousemove="handleMouseMove" @mouseleave="handleMouseLeave">
    <header class="navbar-container" :class="{ 'translate-y-0 opacity-100': showDock || isFullMode, '-translate-y-full opacity-0': !showDock && !isFullMode}">
      <div class="flex flex-row items-center justify-between w-full max-w-screen-xl mx-auto px-4">
        <!-- NAVIGATION BUTTONS -->
        <Navigation />
        <!-- PIN BUTTON -->
        <button @click="togglePin" class="pin-button" :class="{ 'pinned': isFullMode }">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
          </svg>
        </button>
      </div>
    </header>
  </div>
</template>





<script>
import { ref, computed } from 'vue'
import { useStore } from 'vuex'
import Navigation from '@/components/Navigation.vue'
import { store } from '../main';

export default {
  name: 'TopBar',
  components: {
    Navigation
  },
  computed:{
    isFullMode() {
      return store.state.view_mode === 'full'; // Accessing the mode directly
    },    
  },
  setup() {
    const store = useStore()
    const showDock = ref(false)
    const isFullMode = computed(() => store.state.view_mode === 'full')

    const handleMouseMove = (event) => {
      if (!isFullMode.value) {
        showDock.value = event.clientY <= 50
      }
    }

    const handleMouseLeave = () => {
      if (!isFullMode.value) {
        showDock.value = false
      }
    }

    const togglePin = () => {
      const newMode = store.state.view_mode=='compact' ? 'full' : 'compact';
      store.commit('setViewMode', newMode); // Assuming you have a mutation to set the view mode
      showDock.value = isFullMode.value
    }

    return {
      showDock,
      handleMouseMove,
      handleMouseLeave,
      togglePin
    }
  }
}
</script>

<style scoped>
  .dock-container {
    @apply fixed flex m-[50px] flex-row top-0 left-0 right-0 h-[50px] z-50;
  }

  .navbar-container {
    @apply fixed top-0 left-0 right-0 flex justify-center items-center
           py-2 rounded-b-2xl shadow-lg bg-white bg-opacity-80 backdrop-blur-sm
           transition-all duration-300 ease-in-out;
  }

  .dark .navbar-container {
    @apply bg-gray-800 bg-opacity-80;
  }


  .pin-button {
    @apply p-2 rounded-full transition-colors duration-200 z-10;
    background-color: rgba(255, 255, 255, 0.8);
  }

  .pin-button:hover {
    @apply bg-gray-200;
  }

  .dark .pin-button {
    background-color: rgba(31, 41, 55, 0.8);
  }

  .dark .pin-button:hover {
    @apply bg-gray-700;
  }

  .pin-button.pinned {
    @apply text-blue-500;
  }

  .dark .pin-button.pinned {
    @apply text-blue-400;
  }
</style>
