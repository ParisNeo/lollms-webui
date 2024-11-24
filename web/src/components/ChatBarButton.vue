<template>
    <button
      class="svg-button"
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
  