<template>
  <div class="sticky top-0 z-50 w-full bg-transparent">
    <nav class="container mx-auto px-4">
      <div class="flex items-center justify-between h-16">
        <!-- Navigation Links -->
        <div class="hidden md:block">
          <div class="flex items-center space-x-4">
            <RouterLink
              v-for="(link, index) in filteredNavLinks"
              :key="index"
              :to="{ name: link.route }"
              class="nav-button"
              :class="{
                'nav-button-active': 
                  isRouteActive(link.route)
              }"
              @click="setActiveIndex(index)"
              ref="menuItems"
            >
              <div class="flex items-center space-x-1">
                {{ link.text }}
                <span 
                  v-if="isRouteActive(link.route)" 
                  class="ml-1 text-xs"
                  aria-hidden="true"
                >
                  ✨
                </span>
              </div>
            </RouterLink>
          </div>
        </div>

        <!-- Mobile Menu Button -->
        <div class="md:hidden">
          <button 
            @click="isMobileMenuOpen = !isMobileMenuOpen"
            class="inline-flex items-center justify-center p-2 rounded-md text-gray-700 dark:text-gray-300
                   hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none"
          >
            <svg 
              class="h-6 w-6" 
              :class="{'hidden': isMobileMenuOpen, 'block': !isMobileMenuOpen}"
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
            <svg 
              class="h-6 w-6" 
              :class="{'block': isMobileMenuOpen, 'hidden': !isMobileMenuOpen}"
              fill="none" 
              viewBox="0 0 24 24" 
              stroke="currentColor"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Mobile Menu -->
      <div 
        :class="{'block': isMobileMenuOpen, 'hidden': !isMobileMenuOpen}"
        class="md:hidden"
      >
        <div class="px-2 pt-2 pb-3 space-y-1">
          <RouterLink
            v-for="(link, index) in filteredNavLinks"
            :key="index"
            :to="{ name: link.route }"
            class="block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 ease-in-out
                   text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
            :class="{
              'bg-blue-500 text-white hover:bg-blue-600 dark:bg-blue-600 dark:hover:bg-blue-700': 
                isRouteActive(link.route)
            }"
            @click="setActiveIndex(index); isMobileMenuOpen = false"
          >
            <div class="flex items-center justify-between">
              {{ link.text }}
              <span 
                v-if="isRouteActive(link.route)" 
                class="text-xs"
                aria-hidden="true"
              >
                ✨
              </span>
            </div>
          </RouterLink>
        </div>
      </div>
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
const isMobileMenuOpen = ref(false);

const navLinks = [
  { active: true, route: 'discussions', text: 'Discussions' },
  { active: true, route: 'playground', text: 'Playground' },
  { active: true, route: 'PersonalitiesZoo', text: 'Personalities Zoo' },
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
  name: 'Navigation'
};
</script>
