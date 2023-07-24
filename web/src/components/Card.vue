<template>
    <div :class="cardClass">
      <!-- Title -->
      <div v-if="title" class="font-bold mb-2">{{ title }}</div>
  
      <!-- Child cards -->
      <div :class="containerClass">
        <slot></slot>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    props: {
      title: {
        type: String,
        default: "",
      },
      isHorizontal: {
        type: Boolean,
        default: false,
      },
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
          "block",
          "w-full",
          "p-2.5",
          "dark:bg-gray-700",
          "dark:border-gray-600",
          "dark:placeholder-gray-400",
          "dark:text-white",
          "dark:focus:ring-blue-500",
          "dark:focus:border-blue-500",
        ];
      },
      containerClass() {
        return {
          flex: this.isHorizontal,
          "flex-col": !this.isHorizontal,
        };
      },
    },
  };
  </script>
  
  <style>
  /* Optional: You can add more custom styling here if needed */
  </style>
  