<template>
    <button
      class="chat-bar-button"
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
  }
  </script>
  