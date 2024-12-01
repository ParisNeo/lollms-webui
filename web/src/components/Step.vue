<template>
  <div class="step-container" :class="{ 'step-done': done }">
    <div class="step-wrapper">
      <div class="step-icon">
        <template v-if="done">
          <svg v-if="status" class="icon-success" viewBox="0 0 24 24">
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
          </svg>
          <svg v-else class="icon-fail" viewBox="0 0 24 24">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" />
          </svg>
        </template>
        <div v-else class="icon-spinner"></div>
      </div>
      <div class="step-content">
        <h3 class="step-text">
          {{ text || 'No text provided' }}
        </h3>
        <p v-if="description" class="step-description">{{ description }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    done: Boolean,
    text: String,
    status: Boolean,
    description: String
  }
};
</script>
