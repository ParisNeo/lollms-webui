<template>
  <div class="status-icon" :title="getTitle">
    <template v-if="icon">
      <svg v-if="status === 'Done'" class="icon icon-success" viewBox="0 0 24 24">
        <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
      </svg>
      <svg v-else-if="status === 'Failed'" class="icon icon-fail" viewBox="0 0 24 24">
        <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" />
      </svg>
      <div v-else class="icon-spinner"></div>
    </template>
    <span v-else class="icon-text">
      {{ getIconText }}
    </span>
  </div>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  status: {
    type: String,
    required: true
  },
  icon: Boolean,
  iconDone: {
    type: String,
    default: '✓'
  },
  iconFailed: {
    type: String,
    default: '✗'
  },
  iconProcessing: {
    type: String,
    default: '⟳'
  },
  titleDone: {
    type: String,
    default: 'Success'
  },
  titleFailed: {
    type: String,
    default: 'Failure'
  },
  titleProcessing: {
    type: String,
    default: 'Processing'
  },
});

const getTitle = computed(() => {
  if (props.status === 'Done') return props.titleDone;
  if (props.status === 'Failed') return props.titleFailed;
  return props.titleProcessing;
});

const getIconText = computed(() => {
  if (props.status === 'Done') return props.iconDone;
  if (props.status === 'Failed') return props.iconFailed;
  return props.iconProcessing;
});
</script>

<style scoped>
/* You can remove this style block if you're using the CSS in a global stylesheet */
</style>
