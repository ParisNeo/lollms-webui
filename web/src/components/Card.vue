<template>
  <div v-if="isActive" class="overlay" @click="toggleCard"></div>
  <div v-show="shrink===false"
    :class="[
      'bg-white  dark:bg-gray-700 border-blue-300 rounded-lg shadow-lg p-2',
      cardWidthClass,
      'm-2',
      { hovered: !disableHoverAnimation && isHovered, active: isActive }
    ]"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @click.self="toggleCard"
    :style="{ cursor:!this.disableFocus  ?  'pointer' : ''}"
  >
    <!-- Title -->
    <div v-if="title" @click="shrink=true" class="font-bold mb-2 cursor-pointer">{{ title }}</div>

    <div v-if="isHorizontal" class="flex flex-wrap">
      <!-- Card Content -->
      <slot></slot>
    </div>

    <div v-else class="mb-2">
      <!-- Card Content -->
      <slot></slot>
    </div>
  </div>
  <div v-show="shrink===true"  @click="shrink=false" class="bg-white  dark:bg-gray-700 border-blue-300 rounded-lg shadow-lg p-2 h-10 cursor-pointer">
    +    
  </div>
</template>

<script>
export default {
  props: {
    is_shrunk: {
      type:Boolean,
      default:false
    },
    title: {
      type: String,
      default: "",
    },
    isHorizontal: {
      type: Boolean,
      default: false,
    },
    cardWidth: {
      type: String,
      default: "w-3/4",
    },
    disableHoverAnimation: {
      type: Boolean,
      default: true,
    },
    disableFocus: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      shrink: this.is_shrunk,
      isHovered: false,
      isActive: false,
    };
  },
  computed: {
    cardClass() {
      return [
        "bg-gray-50",
        "border",
        "border-gray-300",
        "text-gray-900",
        "text-sm",
        "rounded-lg",
        "focus:ring-blue-500",
        "focus:border-blue-500",

        "w-full",
        "p-2.5",
        "dark:bg-gray-700",
        "dark:border-gray-600",
        "dark:placeholder-gray-400",
        "dark:text-white",
        "dark:focus:ring-blue-500",
        "dark:focus:border-blue-500",
        {
          "cursor-pointer": !this.isActive && !this.disableFocus,
          "w-auto": !this.isActive,
        },
      ];
    },
    cardWidthClass() {
      return this.isActive ? this.cardWidth : "";
    },
  },
  methods: {
    toggleCard() {
      if(!this.disableFocus){
        this.isActive = !this.isActive;
      }
    },
  },
};
</script>

<style>
/* Add the animation for the hover effect */
.hovered {
  transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  transform: scale(1.1); /* You can adjust the scale value as per your preference */
}

/* Add the styles for centering the card when it's active */
.active {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
}

.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.6); /* You can adjust the opacity as per your preference */
   /* Make sure the overlay is above other elements */
  pointer-events: all; /* Allow interactions with the overlay itself */
}
</style>
