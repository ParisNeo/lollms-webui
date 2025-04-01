<template>
  <div class="interactive-menu-container" ref="menuContainerRef">
      <!-- Trigger Button -->
      <button
          @click.prevent="toggleMenu"
          :title="title || 'Open Menu'"
          :class="['interactive-menu-trigger', menuIconClass]"
          ref="menuButtonRef"
          type="button"
      >
          <!-- Slot for custom trigger content -->
          <slot name="trigger">
              <!-- Default trigger content -->
              <img v-if="icon && !icon.includes('#') && !icon.includes('feather:')" :src="icon" class="interactive-menu-trigger-icon" alt="Menu Icon">
              <i v-else-if="icon && icon.includes('feather:')" :data-feather="icon.split(':')[1]" class="interactive-menu-trigger-icon"></i>
              <span v-else-if="icon && icon.includes('#')" class="interactive-menu-trigger-text">{{ icon.split('#')[1] }}</span>
              <i v-else data-feather="menu" class="interactive-menu-trigger-icon"></i>
          </slot>
      </button>

      <!-- Menu List Dropdown -->
      <transition name="interactive-menu-transition">
          <div
              v-if="isMenuOpen"
              class="interactive-menu-dropdown"
              :style="menuStyle"
              ref="menuRef"
              role="menu" aria-orientation="vertical" :aria-labelledby="`menu-button-${_uid}`"
          >
              <ul class="interactive-menu-list" role="none">
                  <li v-for="(command, index) in commands"
                      :key="index"
                      @click.prevent="executeCommand(command)"
                      class="interactive-menu-item group"
                      role="menuitem"
                      :tabindex="-1" :id="`menu-item-${_uid}-${index}`"
                  >
                      <!-- Checkmark/Placeholder - Reduced margin -->
                      <span class="interactive-menu-item-checkmark-placeholder">
                          <i v-if="selected_entry === command.name" data-feather="check" class="interactive-menu-item-checkmark-icon"></i>
                      </span>
                      <!-- Icon - Reduced margin -->
                      <span class="interactive-menu-item-icon-container">
                           <img v-if="command.icon && !command.icon.includes('#') && !command.icon.includes('feather:')" :src="command.icon" :alt="command.name" class="interactive-menu-item-icon">
                           <i v-else-if="command.icon && command.icon.includes('feather:')" :data-feather="command.icon.split(':')[1]" class="interactive-menu-item-icon"></i>
                           <span v-else-if="command.icon && command.icon.includes('#')" class="interactive-menu-item-icon-text">{{ command.icon.split('#')[1] }}</span>
                           <!-- Explicit empty span if no icon to maintain alignment -->
                           <span v-else class="interactive-menu-item-icon-placeholder"></span>
                      </span>
                       <!-- Name -->
                      <span class="interactive-menu-item-name">{{ command.name }}</span>
                  </li>
              </ul>
          </div>
      </transition>
  </div>
</template>

<script>
import { nextTick } from 'vue';
import feather from 'feather-icons';

export default {
  name: 'InteractiveMenu',
  props: {
      title: {
          type: String,
          required: false,
          default: "Menu"
      },
      icon: {
          type: String,
          required: false,
          default: "feather:more-vertical"
      },
      commands: {
          type: Array,
          required: true,
          default: () => []
      },
      // 0: auto, 1: force above, 2: force below, 3: force right-align, 4: force left-align
      force_position: {
          type: Number,
          required: false,
          default: 0
      },
      execute_cmd: {
          type: Function,
          required: false
      },
      menuIconClass: {
          type: String,
          required: false,
          default: ""
      },
      selected_entry: {
          type: String,
          required: false,
          default: null
      }
  },
  data() {
      return {
          isMenuOpen: false,
          menuStyle: {
              top: 'auto',
              bottom: 'auto',
              left: 'auto',
              right: 'auto',
              transformOrigin: 'top left' // Default transform origin
          }
      };
  },
  methods: {
      updateFeatherIcons() {
          nextTick(() => {
              feather.replace({
                  width: '1em',
                  height: '1em',
                  'stroke-width': 2
              });
          });
      },
      handleClickOutside(event) {
          // Close the menu if the click is outside the component root element
          if (this.$refs.menuContainerRef && !this.$refs.menuContainerRef.contains(event.target)) {
               this.closeMenu();
          }
      },
      toggleMenu() {
          if (this.isMenuOpen) {
              this.closeMenu();
          } else {
              this.openMenu();
          }
      },
      openMenu() {
          this.isMenuOpen = true;
          nextTick(() => {
              this.positionMenu(); // Position after menu is rendered
              this.updateFeatherIcons(); // Render icons
               // Add listener AFTER menu is open to avoid self-closing on the initial click
              document.addEventListener('click', this.handleClickOutside, true); // Use capture phase
          });
      },
      closeMenu() {
           this.isMenuOpen = false;
           document.removeEventListener('click', this.handleClickOutside, true);
      },
      executeCommand(command) {
          this.closeMenu(); // Close menu after selection

          if (typeof command.value === 'function') {
              command.value(); // Execute command's specific function
          } else if (this.execute_cmd) {
              this.execute_cmd(command); // Execute generic handler
          } else {
              console.warn('InteractiveMenu: No action defined for command:', command.name);
          }
      },
      positionMenu() {
          if (!this.isMenuOpen || !this.$refs.menuButtonRef || !this.$refs.menuRef) {
              return; // Don't position if closed or refs not available
          }

          const buttonRect = this.$refs.menuButtonRef.getBoundingClientRect();
          const menuEl = this.$refs.menuRef; // Get the menu element

           // --- Accurate Measurement ---
           const originalVisibility = menuEl.style.visibility;
           const originalDisplay = menuEl.style.display;
           const originalPosition = menuEl.style.position;
           const originalTop = menuEl.style.top;
           const originalLeft = menuEl.style.left;

           menuEl.style.visibility = 'hidden';
           menuEl.style.position = 'fixed'; // Use fixed to measure against viewport without scroll influence
           menuEl.style.top = '-9999px';   // Position way off-screen
           menuEl.style.left = '-9999px';
           menuEl.style.display = 'block'; // Ensure it has layout

           const menuRect = menuEl.getBoundingClientRect(); // Now measure

           // Restore original styles
           menuEl.style.visibility = originalVisibility;
           menuEl.style.position = originalPosition;
           menuEl.style.top = originalTop;
           menuEl.style.left = originalLeft;
           menuEl.style.display = originalDisplay;
           // --- End Measurement ---


          const viewportWidth = window.innerWidth;
          const viewportHeight = window.innerHeight;
          const margin = 8; // Small margin from viewport edges

          let newStyle = {
              top: 'auto',
              bottom: 'auto',
              left: 'auto',
              right: 'auto',
              transformOrigin: '' // Reset transform origin
          };

          // --- Vertical Positioning ---
          const spaceBelow = viewportHeight - buttonRect.bottom - margin;
          const spaceAbove = buttonRect.top - margin;
          const requiredHeight = menuRect.height;
          let positionVertically = 'below'; // Default

          if (this.force_position === 1) { // Force Above
               positionVertically = 'above';
          } else if (this.force_position === 2) { // Force Below
               positionVertically = 'below';
          } else { // Auto (force_position === 0 or undefined)
              // Check if 'below' fits. If not, check if 'above' fits.
              if (spaceBelow >= requiredHeight) {
                  positionVertically = 'below';
              } else if (spaceAbove >= requiredHeight) {
                  positionVertically = 'above';
              } else {
                  // Neither fits perfectly, choose the one with more space (will still be cropped)
                  positionVertically = (spaceAbove > spaceBelow) ? 'above' : 'below';
              }
          }

          // Apply vertical styles based on decision
          if (positionVertically === 'above') {
              newStyle.bottom = `calc(100% + 4px)`; // Position above button with 4px gap
              newStyle.top = 'auto';
              newStyle.transformOrigin = 'bottom '; // Append horizontal later
          } else { // Below
              newStyle.top = `calc(100% + 4px)`; // Position below button with 4px gap
              newStyle.bottom = 'auto';
              newStyle.transformOrigin = 'top '; // Append horizontal later
          }

           // --- Horizontal Positioning ---
          const spaceRightFromButton = viewportWidth - buttonRect.left - margin;
          const spaceLeftFromButton = buttonRect.right - margin;
          const requiredWidth = menuRect.width;
          let positionHorizontally = 'left-align'; // Default: align left edges

           if (this.force_position === 3) { // Force Right Align
               positionHorizontally = 'right-align';
           } else if (this.force_position === 4) { // Force Left Align
               positionHorizontally = 'left-align';
           } else { // Auto
               // Check if 'left-align' overflows the viewport right edge
               if ((buttonRect.left + requiredWidth) > (viewportWidth - margin)) {
                    // If it overflows right, check if 'right-align' *would* fit within the left edge
                    if ((buttonRect.right - requiredWidth) > margin) {
                         positionHorizontally = 'right-align';
                    }
                    // If neither fits horizontally without overflow, stick to left-align (will overflow right)
               }
               // Otherwise, default 'left-align' is fine
           }

          // Apply horizontal styles based on decision
          if (positionHorizontally === 'right-align') {
              newStyle.right = `0px`; // Align right edge of menu with right edge of button
              newStyle.left = 'auto';
              newStyle.transformOrigin += 'right';
          } else { // Left-align (default)
              newStyle.left = `0px`; // Align left edge of menu with left edge of button
              newStyle.right = 'auto';
              newStyle.transformOrigin += 'left';
          }

          // Apply the calculated styles
          this.menuStyle = newStyle;
      }
  },
  mounted() {
      // Listen to window resize to reposition the menu if it's open
      window.addEventListener('resize', this.positionMenu);
      this.updateFeatherIcons(); // Initial render for trigger icon
  },
  beforeUnmount() {
      // Cleanup the event listeners
      window.removeEventListener('resize', this.positionMenu);
      // Ensure click listener is removed if component is destroyed while menu is open
      document.removeEventListener('click', this.handleClickOutside, true);
  },
};
</script>

<style scoped>
/* --- Base Container --- */
.interactive-menu-container {
@apply relative inline-block text-left;
/* Theme Variables (Defaults based on Tailwind) */
--menu-trigger-bg: theme('colors.gray.100');
--menu-trigger-text: theme('colors.gray.600');
--menu-trigger-hover-bg: theme('colors.gray.200');
--menu-trigger-hover-text: theme('colors.gray.800');
--menu-trigger-focus-ring: theme('colors.indigo.500');

--menu-dropdown-bg: theme('colors.white');
--menu-dropdown-border: theme('colors.black / 5%');
--menu-dropdown-shadow: theme('boxShadow.xl');

--menu-item-text: theme('colors.gray.700');
--menu-item-hover-bg: theme('colors.indigo.100');
--menu-item-hover-text: theme('colors.gray.900');
--menu-item-icon-color: theme('colors.gray.500');
--menu-item-icon-hover-color: theme('colors.gray.700');
--menu-item-checkmark-color: theme('colors.indigo.600');
}

/* Dark Mode Theme Variables */
.dark .interactive-menu-container {
--menu-trigger-bg: theme('colors.gray.700');
--menu-trigger-text: theme('colors.gray.400');
--menu-trigger-hover-bg: theme('colors.gray.600');
--menu-trigger-hover-text: theme('colors.gray.200');

--menu-dropdown-bg: theme('colors.gray.800');
--menu-dropdown-border: theme('colors.white / 10%');

--menu-item-text: theme('colors.gray.200');
--menu-item-hover-bg: theme('colors.indigo.900');
--menu-item-hover-text: theme('colors.gray.100');
--menu-item-icon-color: theme('colors.gray.400');
--menu-item-icon-hover-color: theme('colors.gray.200');
--menu-item-checkmark-color: theme('colors.indigo.400');
}

/* --- Trigger Button --- */
.interactive-menu-trigger {
@apply inline-flex items-center justify-center p-1 rounded-md transition duration-150 ease-in-out;
background-color: var(--menu-trigger-bg);
color: var(--menu-trigger-text);
line-height: 0; /* Prevent extra space */
border: none; /* Ensure no default button border */
cursor: pointer;
}
.interactive-menu-trigger:hover {
background-color: var(--menu-trigger-hover-bg);
color: var(--menu-trigger-hover-text);
}
.interactive-menu-trigger:focus {
@apply outline-none ring-2 ring-offset-2;
ring-color: var(--menu-trigger-focus-ring);
}
.interactive-menu-trigger-icon {
@apply w-5 h-5; /* Adjust size as needed */
}
.interactive-menu-trigger-text {
  @apply font-semibold text-sm px-1; /* Style for text trigger */
}

/* --- Dropdown Panel --- */
.interactive-menu-dropdown {
/* Uses Tailwind classes: absolute mt-2 w-56 rounded-md shadow-xl ring-1 focus:outline-none z-50 */
@apply absolute mt-2 w-56 rounded-md shadow-xl ring-1 focus:outline-none z-50;
background-color: var(--menu-dropdown-bg);
ring-color: var(--menu-dropdown-border);
box-shadow: var(--menu-dropdown-shadow);
min-width: 14rem; /* w-56 */
max-height: 75vh; /* Add max height */
overflow-y: auto; /* Add vertical scroll if needed */
}

/* --- Menu List --- */
.interactive-menu-list {
@apply py-1 list-none p-0 m-0; /* py-1 for padding top/bottom */
}

/* --- Menu Item --- */
.interactive-menu-item {
@apply flex items-center px-3 py-2 text-sm cursor-pointer whitespace-nowrap; /* Added whitespace-nowrap */
color: var(--menu-item-text);
min-height: 2.25rem; /* Consistent height */
}
.interactive-menu-item:hover,
.interactive-menu-item:focus { /* Combined hover and focus for consistency */
background-color: var(--menu-item-hover-bg);
color: var(--menu-item-hover-text);
outline: none; /* Remove default focus outline, handled by ring potentially */
}
/* Apply icon color change on hover of the parent item */
.interactive-menu-item:hover .interactive-menu-item-icon-container,
.interactive-menu-item:focus .interactive-menu-item-icon-container {
 color: var(--menu-item-icon-hover-color);
}


/* --- Item Components (Checkmark, Icon, Name) --- */
.interactive-menu-item-checkmark-placeholder {
@apply w-4 flex items-center justify-center mr-2 flex-shrink-0; /* Reduced width and margin */
}
.interactive-menu-item-checkmark-icon {
 @apply h-4 w-4; /* Ensure icon size */
 color: var(--menu-item-checkmark-color);
}

.interactive-menu-item-icon-container {
@apply w-4 flex items-center justify-center mr-2 flex-shrink-0; /* Reduced width and margin */
color: var(--menu-item-icon-color);
transition: color 150ms ease-in-out; /* Smooth color transition */
}
.interactive-menu-item-icon {
@apply h-4 w-4; /* Consistent icon size */
}
.interactive-menu-item-icon-text {
 @apply text-xs font-bold; /* Style for text icon e.g., #T */
}
.interactive-menu-item-icon-placeholder {
  @apply inline-block w-4 h-4; /* Same size as icon for alignment */
}

.interactive-menu-item-name {
@apply flex-1 truncate; /* Allow name to take remaining space and truncate */
}


/* --- Transition --- */
.interactive-menu-transition-enter-active { @apply transition ease-out duration-100; }
.interactive-menu-transition-enter-from { @apply transform opacity-0 scale-95; }
.interactive-menu-transition-enter-to { @apply transform opacity-100 scale-100; }
.interactive-menu-transition-leave-active { @apply transition ease-in duration-75; }
.interactive-menu-transition-leave-from { @apply transform opacity-100 scale-100; }
.interactive-menu-transition-leave-to { @apply transform opacity-0 scale-95; }

/* Optional: Custom scrollbar for dropdown if needed */
.interactive-menu-dropdown::-webkit-scrollbar {
  width: 6px;
}
.interactive-menu-dropdown::-webkit-scrollbar-track {
  background: transparent;
}
.interactive-menu-dropdown::-webkit-scrollbar-thumb {
  background-color: rgba(156, 163, 175, 0.4); /* gray-400 with lower opacity */
  border-radius: 3px;
}
.dark .interactive-menu-dropdown::-webkit-scrollbar-thumb {
  background-color: rgba(75, 85, 99, 0.5); /* gray-600 with lower opacity */
}
.interactive-menu-dropdown {
  scrollbar-width: thin;
  scrollbar-color: rgba(156, 163, 175, 0.4) transparent;
}
.dark .interactive-menu-dropdown {
  scrollbar-color: rgba(75, 85, 99, 0.5) transparent;
}

</style>