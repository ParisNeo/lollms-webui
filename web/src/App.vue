<template>
  <div :class="['flex flex-col h-screen font-sans background-color text-slate-950 dark:bg-bg-dark dark:text-slate-50 w-full overflow-hidden', currentThemeClass]">
    <!-- TopBar Component -->
    <TopBar @update:occupying-space="updateSpaceOccupation" />

    <!-- Placeholder Div -->
    <div
      :class="[
        'transition-height duration-300 ease-in-out', // Smooth height transition
        shouldOccupySpace ? 'h-14' : 'h-0'         // Dynamic height (h-14 = 56px)
      ]"
      style="flex-shrink: 0;"
      ></div>

    <!-- Main Content Area - No transform needed here -->
    <div class="flex overflow-hidden flex-grow w-full">
      <!-- VIEW CONTAINER - Directly contains RouterView -->
      <RouterView v-slot="{ Component }">
        <KeepAlive>
          <component :is="Component" />
        </KeepAlive>
      </RouterView>
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

// State to control the placeholder's height
const shouldOccupySpace = ref(false);

// Method to update the state when TopBar emits the event
const updateSpaceOccupation = (isOccupying) => {
  shouldOccupySpace.value = isOccupying;
};

// Compute the current theme class (optional)
const currentThemeClass = computed(() => {
    // Using localStorage might cause a flicker on load if theme changes often.
    // Consider managing theme via store for better reactivity if needed.
    return localStorage.getItem('preferred-theme') || 'default';
});

// Initialize state on mount
onMounted(() => {
   // Initialize based on the initial pinned state from the store
   shouldOccupySpace.value = store.state.isTopBarPinned ?? false;

});

</script>

<style>
.transition-height {
  transition-property: height;
  /* Ensure transition duration/easing match TopBar if desired */
  /* transition-duration: 300ms; */
  /* transition-timing-function: ease-in-out; */
}

/* Add other global styles if needed */
</style>