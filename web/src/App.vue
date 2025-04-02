<template>
  <div :class="['flex flex-col h-screen font-sans background-color text-slate-950 dark:bg-bg-dark dark:text-slate-50 w-full overflow-hidden', currentThemeClass]">
    <!-- TopBar Component - Remains fixed for animations -->
    <TopBar @update:occupying-space="updateSpaceOccupation" />

    <!--
      Placeholder Div: REMOVED. We will directly translate the main content instead.
    -->
    <!-- <div
      :class="[
        'transition-height duration-300 ease-in-out',
        shouldOccupySpace ? 'h-14' : 'h-0'
      ]"
    ></div> -->

    <!-- Main Content Area -->
    <!-- Apply dynamic transform and padding-top -->
    <div :class="[
           'flex overflow-hidden flex-grow w-full',
           'transition-transform duration-300 ease-in-out', // Add transition for transform
           shouldOccupySpace ? 'translate-y-14' : 'translate-y-0' // Translate down when TopBar is visible
         ]"
         >
      <!-- VIEW CONTAINER -->
      <!-- Add padding-top to compensate for the translation so scroll container starts correctly -->
       <div class="flex-1 overflow-y-auto" :class="[shouldOccupySpace ? 'pt-0' : 'pt-0']">
          <RouterView v-slot="{ Component }">
              <KeepAlive>
                <component :is="Component" />
              </KeepAlive>
          </RouterView>
       </div>
    </div>

    <!-- FOOTER (Optional) -->
    <!-- <Footer /> -->
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useStore } from 'vuex';
import { RouterView } from 'vue-router';
import TopBar from './components/TopBar.vue';
// import Footer from './components/Footer.vue';

const store = useStore();

// State to track if TopBar should be occupying visual space
const shouldOccupySpace = ref(false);

// Method to update state based on TopBar's effective visibility
const updateSpaceOccupation = (isOccupying) => {
  shouldOccupySpace.value = isOccupying;
};

// Compute the current theme class (optional, depends on global styling)
const currentThemeClass = computed(() => {
    return localStorage.getItem('preferred-theme') || 'default';
});

// Initialize state on mount
onMounted(() => {
   // Initialize based on the initial pinned state from the store
   shouldOccupySpace.value = store.state.isTopBarPinned ?? false;

   // Initialize languages if not done elsewhere
   if (!store.state.languages || store.state.languages.length <= 1) {
        store.dispatch('initializeLanguages');
   }
});

</script>

<style>
/* Ensure CSS transitions are defined if not using Tailwind defaults fully */
/* Tailwind handles transition-transform, duration, and ease */

/* Body/html overflow might need to be hidden if strange scrollbars appear */
/* html, body {
  overflow: hidden;
} */
</style>