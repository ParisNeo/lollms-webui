<!-- DropdownMenu.vue -->
<template>
  <div class="relative inline-block text-left">
    <div>
      <!-- Bind the icon prop here -->
      <ToolbarButton @click.stop="toggleMenu" :title="title" :icon="icon" />
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
  // Add 'icon' to props
  props: {
      title: { type: String, required: true },
      icon: { type: String, required: true } // Make icon required
  },
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
      } else if (this.popperInstance) {
        // Destroy popper when closing to avoid potential memory leaks/issues
        this.popperInstance.destroy();
        this.popperInstance = null;
      }
    },
    closeMenu(event) {
      // Close only if clicking outside the button AND the dropdown itself
      const button = this.$el?.querySelector('button'); // Get reference to the button
      if (button && !button.contains(event.target) && !this.$refs.dropdown?.contains(event.target)) {
        if (this.isOpen) { // Only change state and destroy if currently open
            this.isOpen = false;
            if (this.popperInstance) {
                this.popperInstance.destroy();
                this.popperInstance = null;
            }
        }
      }
    },
    createPopper() {
       // Destroy existing instance before creating a new one
       if (this.popperInstance) {
           this.popperInstance.destroy();
           this.popperInstance = null;
       }
      const button = this.$el?.querySelector('button') // Use optional chaining
      const dropdown = this.$refs.dropdown

      if (button && dropdown) {
        this.popperInstance = createPopper(button, dropdown, {
          placement: 'bottom-start', // Changed default placement for toolbars
          modifiers: [
             { name: 'offset', options: { offset: [0, 8], }, }, // Add some space
            {
              name: 'flip',
              options: {
                fallbackPlacements: ['top-start', 'bottom-end', 'top-end'],
              },
            },
            {
              name: 'preventOverflow',
              options: {
                boundary: 'clippingParents', // Usually better than document.body
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
  box-shadow: 0 4px 6px -1px rgba(255, 255, 255, 0.05), 0 2px 4px -1px rgba(255, 255, 255, 0.03); /* Adjusted for dark mode */
}
</style>