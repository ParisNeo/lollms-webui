<template>
  <button
    class="svg-button"
    v-bind="$attrs"
    @click="$emit('click', $event)"
  >
    <slot name="icon"></slot>
    <slot></slot>
  </button>
</template>

<script>
export default {
  name: 'ChatBarButton',
  // Define the events this component can emit
  emits: ['click'],
}
</script>