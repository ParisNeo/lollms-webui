<!-- DropdownMenu.vue -->
<template>
  <div class="relative inline-block text-left">
    <div>
      <ToolbarButton @click.stop="toggleMenu" :title="title" icon="code" />
    </div>

    <teleport to="body">
      <div v-if="isOpen" ref="dropdown" class="z-50 w-56 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 dark:ring-white dark:ring-opacity-20 focus:outline-none dropdown-shadow text-gray-700 dark:text-white">
        <div class="py-1" role="menu" aria-orientation="vertical" aria-labelledby="options-menu">
          <slot></slot>
        </div>
      </div>
    </teleport>
  </div>
</template>

<script>
import { createPopper } from '@popperjs/core';
import ToolbarButton from './ToolbarButton.vue'

export default {
  components: {
    ToolbarButton
  },
  props: ['title'],
  data() {
    return {
      isOpen: false,
      popperInstance: null
    }
  },
  mounted() {
    document.addEventListener('click', this.closeMenu)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.closeMenu)
    if (this.popperInstance) {
      this.popperInstance.destroy()
    }
  },
  methods: {
    toggleMenu(event) {
      if (event && typeof event.stopPropagation === 'function') {
        event.stopPropagation()
      }
      this.isOpen = !this.isOpen
      if (this.isOpen) {
        this.$nextTick(() => {
          this.createPopper()
        })
      }
    },
    closeMenu(event) {
      if (!this.$el.contains(event.target) && !this.$refs.dropdown?.contains(event.target)) {
        this.isOpen = false
      }
    },
    createPopper() {
      const button = this.$el.querySelector('button')
      const dropdown = this.$refs.dropdown

      if (button && dropdown) {
        this.popperInstance = createPopper(button, dropdown, {
          placement: 'bottom-end',
          modifiers: [
            {
              name: 'flip',
              options: {
                fallbackPlacements: ['top-end', 'bottom-start', 'top-start'],
              },
            },
            {
              name: 'preventOverflow',
              options: {
                boundary: document.body,
              },
            },
          ],
        })
      }
    }
  }
}
</script>

<style scoped>
.dropdown-shadow {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

:root.dark .dropdown-shadow {
  box-shadow: 0 4px 6px -1px rgba(255, 255, 255, 0.1), 0 2px 4px -1px rgba(255, 255, 255, 0.06);
}
</style>
