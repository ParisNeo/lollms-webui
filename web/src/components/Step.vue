<template>
  <div
    class="step-component"
    :class="[
      done ? (status ? 'step-component-success' : 'step-component-fail') : 'step-component-pending'
    ]"
  >
    <!-- Icon Wrapper with Transition -->
    <div class="step-icon-wrapper"> <!-- This is w-5 h-5 from theme -->
      <transition name="fade-icon" mode="out-in">
        <!-- Spinner (Pending) -->
        <div v-if="!done" key="spinner" class="step-spinner"></div> <!-- This is w-4 h-4 from theme -->

        <!-- Success Icon -->
        <svg
          v-else-if="status"
          key="success"
          class="step-icon-success w-4 h-4"
          fill="currentColor"
          viewBox="0 0 20 20"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"></path>
        </svg>

        <!-- Failure Icon -->
        <svg
          v-else
          key="fail"
          class="step-icon-fail w-4 h-4"
          fill="currentColor"
          viewBox="0 0 20 20"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd"></path>
        </svg>
      </transition>
    </div>

    <!-- Text Content -->
    <div class="step-text-content">
      <div class="step-text">
        {{ text || 'Processing...' }}
      </div>
      <div
        v-if="description"
        class="step-description"
      >
        {{ description }}
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Step',
  props: {
    done: Boolean,
    text: String,
    status: Boolean,
    description: String
  }
};
</script>

<style scoped>
/* Scoped styles are minimal now, relying on theme.css */

/* Re-define animation locally if not in global scope or if needed */
/* .fade-icon-enter-active,
.fade-icon-leave-active {
  transition: opacity 0.2s ease-in-out, transform 0.2s ease-in-out;
}
.fade-icon-enter-from,
.fade-icon-leave-to {
  opacity: 0;
  transform: scale(0.8);
} */

/* Spinner animation (if not globally defined via animate-spin) */
/* @keyframes spin { to { transform: rotate(360deg); } }
.animate-spin { animation: spin 0.8s linear infinite; } */

/* Pulse animation (if not globally defined) */
/* @keyframes pulse-border { ... } */
/* .animate-pulse-border { ... } */

</style>