<!-- DropdownMenu.vue -->
<template>
  <div class="relative inline-block text-left">
    <div>
      <ToolbarButton @click.stop="toggleMenu" :title="title" icon="code" />
    </div>

    <div v-if="isOpen" class="z-50 origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5 focus:outline-none">
      <div class="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script>
import ToolbarButton from './ToolbarButton.vue'

export default {
  components: {
    ToolbarButton
  },
  props: ['title'],
  data() {
    return {
      isOpen: false
    }
  },
  methods: {
    toggleMenu() {
      this.isOpen = !this.isOpen
    }
  },
  mounted() {
    document.addEventListener('click', this.closeMenu)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeMenu)
  },
  methods: {
    toggleMenu(event) {
      if (event && typeof event.stopPropagation === 'function') {
        event.stopPropagation()
      }
      this.isOpen = !this.isOpen
    },
    closeMenu(event) {
      if (!this.$el.contains(event.target)) {
        this.isOpen = false
      }
    }
  }
}
</script>
