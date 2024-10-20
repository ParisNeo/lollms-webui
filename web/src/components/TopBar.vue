<template>
  <div class="topbar-container" @mouseenter="show" @mouseleave="hide">
    <div class="topbar" :class="{ 'topbar-hidden': !isVisible }">
      <div class="topbar-content">
        <slot name="navigation"></slot>
        <button class="pin-button" @click="togglePin" :title="isPinned ? 'Unpin' : 'Pin'">
          <svg :fill="isPinned ? '#FF0000' : '#000000'" height="24px" width="24px" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" 
            viewBox="0 0 490.125 490.125" xml:space="preserve">
              <g>
                <path d="M300.625,5.025c-6.7-6.7-17.6-6.7-24.3,0l-72.6,72.6c-6.7,6.7-6.7,17.6,0,24.3l16.3,16.3l-40.3,40.3l-63.5-7
                  c-3-0.3-6-0.5-8.9-0.5c-21.7,0-42.2,8.5-57.5,23.8l-20.8,20.8c-6.7,6.7-6.7,17.6,0,24.3l108.5,108.5l-132.4,132.4
                  c-6.7,6.7-6.7,17.6,0,24.3c3.3,3.3,7.7,5,12.1,5s8.8-1.7,12.1-5l132.5-132.5l108.5,108.5c3.3,3.3,7.7,5,12.1,5s8.8-1.7,12.1-5
                  l20.8-20.8c17.6-17.6,26.1-41.8,23.3-66.4l-7-63.5l40.3-40.3l16.2,16.2c6.7,6.7,17.6,6.7,24.3,0l72.6-72.6c3.2-3.2,5-7.6,5-12.1
                  s-1.8-8.9-5-12.1L300.625,5.025z M400.425,250.025l-16.2-16.3c-6.4-6.4-17.8-6.4-24.3,0l-58.2,58.3c-3.7,3.7-5.5,8.8-4.9,14
                  l7.9,71.6c1.6,14.3-3.3,28.3-13.5,38.4l-8.7,8.7l-217.1-217.1l8.7-8.6c10.1-10.1,24.2-15,38.4-13.5l71.7,7.9
                  c5.2,0.6,10.3-1.2,14-4.9l58.2-58.2c6.7-6.7,6.7-17.6,0-24.3l-16.3-16.3l48.3-48.3l160.3,160.3L400.425,250.025z"/>
              </g>
          </svg>
        </button>
        <Navigation></Navigation>
      </div>
    </div>
    <div class="placeholder" v-if="!isVisible"></div>
  </div>
</template>

<script>
import Navigation from '@/components/Navigation.vue';

export default {
  name: 'TopBar',
  components: {
    Navigation
  },
  data() {
    return {
      isVisible: false,
      isPinned: false,
    }
  },
  methods: {
    show() {
      this.isVisible = true
    },
    hide() {
      if (!this.isPinned) {
        this.isVisible = false
      }
    },
    togglePin() {
      this.isPinned = !this.isPinned
      this.isVisible = this.isPinned
    },
  },
}
</script>

<style scoped>
.topbar-container {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
}

.topbar {
  background-color: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(5px);
  transition: transform 0.3s ease-in-out;
  display: flex;
  justify-content: center;
}

.topbar-hidden {
  transform: translateY(-100%);
}

.topbar-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;
  width: 100%;
}

.pin-button {
  background-color: transparent;
  border: none;
  cursor: pointer;
  padding: 5px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.pin-button svg {
  width: 24px;
  height: 24px;
  transition: transform 0.3s ease;
}

.pin-button:hover svg {
  transform: scale(1.2);
}

.placeholder {
  height: 10px;
}
</style>
