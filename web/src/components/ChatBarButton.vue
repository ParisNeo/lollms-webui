<template>
    <button
      class="p-2 rounded-full transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
      :class="[
        buttonClass,
        'hover:bg-gray-200 dark:hover:bg-gray-700',
        'active:bg-gray-300 dark:active:bg-gray-600'
      ]"
      v-bind="$attrs"
      v-on="$listeners"
    >
      <slot name="icon"></slot>
      <slot></slot>
    </button>
  </template>
  
  <script>
  export default {
    name: 'ChatBarButton',
    props: {
      buttonClass: {
        type: String,
        default: 'text-gray-600 dark:text-gray-300'
      }
    }
  }
  </script>
  