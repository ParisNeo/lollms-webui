<template>
  <div v-if="$store.state.ready" class="navbar-container z-60 flex flex-col sm:flex-row items-center">
    <div class="w-full text-center">
      <div class="m-0 flex border-b w-full items-center justify-center flex-row font-medium nav-ul text-center">
        <RouterLink
          v-for="(link, index) in filteredNavLinks"
          :key="index"
          :to="{ name: link.route }"
          class="nav-link"
          :class="{ 'active_link': isRouteActive(link.route) }"
        >
          {{ link.text }}
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { RouterLink } from 'vue-router';
import { store } from '../main';

const navLinks = [
  { active: true, route: 'discussions', text: 'Discussions' },
  { active: true, route: 'playground', text: 'Playground' },
  { active: true, route: 'AppsZoo', text: 'Apps Zoo' },
  { 
      active: false, 
      route: 'AutoSD', 
      text: 'Auto111-SD', 
      condition: () => store.state.config.enable_sd_service || store.state.config.active_tti_service === 'autosd' 
  },
  { 
      active: false, 
      route: 'ComfyUI', 
      text: 'ComfyUI', 
      condition: () => store.state.config.enable_comfyui_service || store.state.config.active_tti_service === 'comfyui' 
  },
  { 
      active: false, 
      route: 'interactive', 
      text: 'Interactive', 
      condition: () => store.state.config.active_tts_service !== 'None' && store.state.config.active_stt_service !== 'None' 
  },
  { active: true, route: 'settings', text: 'Settings' },
  { active: true, route: 'help_view', text: 'Help' }
];

const filteredNavLinks = computed(() => {
  if (!store.state.ready) {
      return navLinks.filter(link => link.active);
  }
  return navLinks.filter(link => {
      if (link.condition) {
          return link.condition();
      }
      return link.active;
  });
});
</script>

<script>
export default {
    name: 'Navigation',
    computed: {
        filteredNavLinks() {
            return filteredNavLinks.value;
        }
    },

    methods: {
      isRouteActive(routeName) {
        try {
          return this.$route.name === routeName;
        } catch {
          console.log("routeName not found");
          return false;
        }
      }
    },
};
</script>

<style scoped>
.nav-link.active_link {
  font-weight: bold;
  color: #fff; /* White text for active link */
  background-color: #007bff; /* Blue background for active link */
  border-radius: 5px; /* Rounded corners for active link */
}
</style>
