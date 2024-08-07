<template>
  <div>
  <div v-if="isActive" class="overlay" @click="toggleCard"></div>
  <div v-show="shrink===false"
    :class="[
      'border-blue-300 rounded-lg shadow-lg p-2',
      cardWidthClass,
      'm-2',
      {'subcard': is_subcard},
      {'bg-white dark:bg-gray-900': !is_subcard},
      { hovered: !disableHoverAnimation && isHovered, active: isActive }
    ]"
    @mouseenter="isHovered = true"
    @mouseleave="isHovered = false"
    @click.self="toggleCard"
    :style="{ cursor:!this.disableFocus  ?  'pointer' : ''}"
  >
    <!-- Title -->
    <div v-if="title" @click="shrink=true" :class="{'text-center p-2 m-2 bg-gray-200':!is_subcard}" class="bg-gray-100 dark:bg-gray-500 rounded-lg pl-2 pr-2 mb-2  font-bold cursor-pointer">{{ title }}</div>

    <div v-if="isHorizontal" class="flex flex-wrap">
      <!-- Card Content -->
      <slot></slot>
    </div>

    <div v-else class="mb-2">
      <!-- Card Content -->
      <slot></slot>
    </div>
  </div>
  <div v-if="is_subcard" v-show="shrink===true"  @click="shrink=false" class="bg-white text-center text-xl bold dark:bg-gray-500 border-blue-300 rounded-lg shadow-lg p-2 h-10 cursor-pointer m-2">
    {{ title }}    
  </div>
  <div v-else v-show="shrink===true"  @click="shrink=false" class="bg-white text-center text-2xl dark:bg-gray-500 border-2 border-blue-300 rounded-lg shadow-lg p-0 h-7 cursor-pointer hover:h-8 hover:bg-blue-300">
    +    
  </div>
  </div>
</template>
<script>
export default {
  props: {
    is_subcard:{
      type:Boolean,
      default:false
    },
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
        "dark:bg-gray-500",
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
.overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

.hovered {
  transform: scale(1.05);
  transition: transform 0.2s ease-in-out;
}

.active {
  transform: scale(1.1);
  transition: transform 0.2s ease-in-out;
}
</style>

