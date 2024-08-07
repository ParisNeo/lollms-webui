<template>
  <div v-if="$store.state.ready" class="navbar-container z-10000">
    <nav class="game-menu">
      <RouterLink
        v-for="(link, index) in filteredNavLinks"
        :key="index"
        :to="{ name: link.route }"
        class="menu-item"
        :class="{ 'active-link': isRouteActive(link.route) }"
        @click="setActiveIndex(index)"
        ref="menuItems"
      >
        {{ link.text }}
      </RouterLink>
    </nav>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, watch } from 'vue';
import { RouterLink, useRoute } from 'vue-router';
import { store } from '../main';

const route = useRoute();
const activeItemIndex = ref(0);
const menuItems = ref([]);

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

onMounted(() => {
  updateActiveItem();
});

watch(() => route.name, updateActiveItem);

function updateActiveItem() {
  const newIndex = filteredNavLinks.value.findIndex(link => link.route === route.name);
  if (newIndex !== -1) {
    activeItemIndex.value = newIndex;
  }
}

function isRouteActive(routeName) {
  return route.name === routeName;
}

function setActiveIndex(index) {
  activeItemIndex.value = index;
}
</script>

<script>
export default {
  name: 'Navigation',
  computed: {
    filteredNavLinks() {
      return filteredNavLinks.value;
    }
  },
};
</script>
