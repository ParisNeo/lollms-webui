<template>
  <div :class="marginClass">
    <!-- Overlay for focused state -->
    <div v-if="isActive" class="overlay" @click="blurCard"></div>

    <!-- Expanded Card View -->
    <div
      v-show="!isShrunkInternal"
      :id="contentId"
      :class="[
        'card-container relative border rounded-lg shadow-lg p-4 transition-all duration-300 ease-in-out', // Added transition-all, duration-300
        cardWidth, // Apply base width always
        // Glassmorphism Styles
        'bg-clip-padding backdrop-filter backdrop-blur-xl bg-opacity-60', // Core glass effect: requires bg image/color behind it
        'border border-gray-200/30', // Softer border
        { 'bg-gray-100 dark:bg-gray-800': isSubcard }, // Base color tint for subcard (semi-transparent due to bg-opacity)
        { 'bg-white dark:bg-gray-900': !isSubcard }, // Base color tint for main card (semi-transparent due to bg-opacity)
        // { 'hover:scale-105': !disableHoverAnimation && !isActive && !disableFocus }, // REMOVED Hover zoom effect
        { 'scale-110 z-[1001]': isActive }, // Active/focused effect (increased scale and z-index) - Kept focus zoom
        { 'cursor-pointer': !disableFocus } // Pointer cursor if focus is enabled
      ]"
      @click.self="focusCard"
    >
      <!-- Close Button (Top Right) - Visible only when active -->
      <button
        v-if="isActive"
        @click="blurCard"
        class="absolute top-2 right-2 text-gray-700 hover:text-black dark:text-gray-300 dark:hover:text-white text-2xl leading-none z-10 transition-colors"
        aria-label="Close"
      >
        ×
      </button>

      <!-- Title Area -->
      <div
        v-if="title"
        :class="[
          'flex justify-between items-center rounded-t-lg pl-3 pr-3 pt-2 pb-2 mb-3 font-bold', // Adjusted padding slightly
          // Removed specific background for title to blend with glass effect
          'text-gray-800 dark:text-gray-100', // Ensure title text is visible
          { 'cursor-pointer': canShrink }, // Cursor only if shrinkable
        ]"
        @click="toggleShrink"
        role="button"
        :aria-expanded="!isShrunkInternal"
        :aria-controls="contentId"
        :tabindex="canShrink ? 0 : -1"
        @keydown.enter.space="toggleShrink"
      >
        <span>{{ title }}</span>
        <!-- Shrink/Expand Chevron -->
        <span v-if="canShrink" class="ml-2 text-sm">
          {{ isShrunkInternal ? '▼' : '▲' }}
        </span>
      </div>

      <!-- Card Content Area -->
      <!-- Added text color for better visibility on potentially complex backgrounds -->
      <div :class="[
          'text-gray-700 dark:text-gray-200',
         { 'flex flex-wrap': isHorizontal, 'mb-2': !isHorizontal }
         ]">
        <slot></slot>
      </div>
    </div>

    <!-- Shrunk Card View -->
    <div
      v-if="canShrink"
      v-show="isShrunkInternal"
      @click="expandCard"
      :class="[
        'shrunk-card border rounded-lg shadow-lg p-2 text-center cursor-pointer transition-all duration-300 ease-in-out', // Added transition-all, duration-300
        cardWidth, // Apply base width always
        // Glassmorphism Styles for shrunk card
        'bg-clip-padding backdrop-filter backdrop-blur-md bg-opacity-70', // Slightly less blur/more opaque when shrunk? Adjust as needed.
        'border border-gray-200/30', // Softer border
        { 'bg-gray-100 dark:bg-gray-800': isSubcard }, // Base color tint for subcard (semi-transparent)
        { 'bg-white dark:bg-gray-900': !isSubcard }, // Base color tint for main card (semi-transparent)
        'hover:bg-opacity-80 dark:hover:bg-opacity-80', // Subtle hover: increase opacity slightly
        { 'text-lg font-semibold text-gray-800 dark:text-gray-200': isSubcard }, // Adjusted shrunk text color
        { 'text-xl font-bold text-gray-800 dark:text-gray-200': !isSubcard } // Adjusted shrunk text color
      ]"
      role="button"
      :aria-label="`Expand ${title || 'Card'}`"
      tabindex="0"
      @keydown.enter.space="expandCard"
    >
      {{ title || 'Show Card' }} <span class="text-sm">▼</span>
    </div>
  </div>
</template>

<script>
// Script section remains the same as before
import { computed, ref, watch, onMounted, onBeforeUnmount } from 'vue';

export default {
  name: 'EnhancedCard',
  props: {
    isSubcard: {
      type: Boolean,
      default: false,
    },
    initiallyShrunk: {
      type: Boolean,
      default: false,
    },
    canShrink: {
      type: Boolean,
      default: true,
    },
    title: {
      type: String,
      default: '',
    },
    isHorizontal: {
      type: Boolean,
      default: false,
    },
    cardWidth: {
      type: String,
      default: 'w-full',
    },
    marginClass: {
      type: String,
      default: 'm-2',
    },
    disableHoverAnimation: {
      type: Boolean,
      default: false, // This prop is now less relevant as hover zoom is removed
    },
    disableFocus: {
      type: Boolean,
      default: false,
    },
  },
  emits: ['shrunk', 'expanded', 'focused', 'blurred'],

  setup(props, { emit }) {
    const isShrunkInternal = ref(props.initiallyShrunk);
    const isActive = ref(false);
    const contentId = computed(() => `card-content-${Math.random().toString(36).substring(2, 9)}`);

    const shrinkCard = () => {
      if (props.canShrink && !isShrunkInternal.value) {
        isShrunkInternal.value = true;
        emit('shrunk');
        if (isActive.value) {
            blurCard();
        }
      }
    };

    const expandCard = () => {
      if (props.canShrink && isShrunkInternal.value) {
        isShrunkInternal.value = false;
        emit('expanded');
      }
    };

    const toggleShrink = () => {
        if (!props.canShrink) return;
        if (isShrunkInternal.value) {
            expandCard();
        } else {
            shrinkCard();
        }
    };

    const focusCard = () => {
      if (!props.disableFocus && !isActive.value) {
        isActive.value = true;
        emit('focused');
        document.body.style.overflow = 'hidden';
      }
    };

    const blurCard = () => {
      if (isActive.value) {
        isActive.value = false;
        emit('blurred');
        document.body.style.overflow = '';
      }
    };

    const handleEscKey = (event) => {
        if (event.key === 'Escape' && isActive.value) {
            blurCard();
        }
    };

    onMounted(() => {
        document.addEventListener('keydown', handleEscKey);
        // Ensure backdrop-filter is enabled in your Tailwind config if using JIT or PurgeCSS
        // Usually under theme.extend.backdropFilter = { ... }
        // and variants.extend.backdropFilter = ['responsive']
    });

    onBeforeUnmount(() => {
         document.removeEventListener('keydown', handleEscKey);
         if (isActive.value) {
             document.body.style.overflow = '';
         }
    });


    return {
      isShrunkInternal,
      isActive,
      contentId,
      shrinkCard,
      expandCard,
      toggleShrink,
      focusCard,
      blurCard,
    };
  },
};
</script>

<style>
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  /* Slightly lighter overlay to complement glass */
  background-color: rgba(0, 0, 0, 0.4);
  /* Higher backdrop blur for the overlay itself if desired */
  /* backdrop-filter: blur(4px); */
  z-index: 1000;
  cursor: pointer;
}

/* Ensure the active card is above the overlay */
.card-container.scale-110 {
  z-index: 1001;
}

/* Smooth transition for more properties including background/blur */
.card-container, .shrunk-card {
    transition-property: transform, background-color, border-color, color, box-shadow, background-opacity, backdrop-filter; /* Added more properties */
    transition-timing-function: ease-in-out;
    transition-duration: 300ms; /* Slightly longer duration */
}

/* Improve focus visibility for keyboard navigation */
.card-container:focus-within,
.shrunk-card:focus {
    /* Using Tailwind's ring utility for focus */
    @apply ring-2 ring-offset-2 ring-blue-500 ring-offset-transparent;
}
/* Hide default outline when using custom focus style */
.card-container, .shrunk-card, button {
    outline: none;
}

/* IMPORTANT: For glassmorphism to work, the element needs something *behind* it
   with color/texture to blur. Place this card over an image, gradient, or
   colorful background. */
body {
  /* Example: Add a gradient background to the body or a parent container */
  /* background: linear-gradient(to right, #ff7e5f, #feb47b); */
}

/* Ensure backdrop-filter utilities are available. If not, add to tailwind.config.js */
/*
module.exports = {
  theme: {
    extend: {
      backdropBlur: {
        xs: '2px',
        // ... other blur values if needed
      }
    }
  },
  variants: {
    extend: {
      backdropBlur: ['responsive'], // Enable variants if needed
      backgroundOpacity: ['hover', 'focus', 'dark'], // Ensure opacity variants are enabled
    },
  },
  plugins: [],
}
*/
</style>