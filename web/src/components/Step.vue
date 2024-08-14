<template>
  <div class="step-container">
    <div
      class="step-wrapper transition-all duration-300 ease-in-out"
      :class="{
        'bg-green-100 dark:bg-green-900': done && status,
        'bg-red-100 dark:bg-red-900': done && !status,
        'bg-gray-100 dark:bg-gray-800': !done
      }"
    >
      <div class="step-icon">
        <div v-if="step_type === 'start_end'">
          <div v-if="!done">
            <i
              data-feather="circle"
              class="feather-icon text-gray-600 dark:text-gray-300"
            ></i>
          </div>
          <div v-else-if="done && status">
            <i
              data-feather="check-circle"
              class="feather-icon text-green-600 dark:text-green-400"
            ></i>
          </div>
          <div v-else>
            <i
              data-feather="x-circle"
              class="feather-icon text-red-600 dark:text-red-400"
            ></i>
          </div>
        </div>
        <div v-if="!done">
          <div class="spinner"></div>
        </div>
      </div>
      <div class="step-content">
        <h3
          class="step-text"
          :class="{
            'text-green-600 dark:text-green-400': done && status,
            'text-red-600 dark:text-red-400': done && !status,
            'text-gray-800 dark:text-gray-200': !done
          }"
        >
          {{ text || 'No text provided' }}
        </h3>
        <p v-if="description" class="step-description">{{ description || 'No description provided' }}</p>
      </div>
    </div>
  </div>
</template>


<script>
export default {
  props: {
    done: {
      type: Boolean,
      default: false // Default to false if not provided
    },
    text: {
      type: String,
      default: '' // Default to empty string if not provided
    },
    status: {
      type: Boolean,
      default: false // Default to false if not provided
    },
    step_type: {
      type: String,
      default: 'start_end' // Default to 'start_end' if not provided
    },
    description: {
      type: String,
      default: '' // Default to empty string if not provided
    }
  },
  mounted() {

    this.amounted();
  },
  methods: {
    amounted() {
      console.log('Component mounted with the following properties:');
      console.log('done:', this.done);
      console.log('text:', this.text);
      console.log('status:', this.status);
      console.log('step_type:', this.step_type);
      console.log('description:', this.description);
    }
  },
  watch: {
    done(newValue) {
      if (typeof newValue !== 'boolean') {
        console.error('Invalid type for done. Expected Boolean.');
      }
    },
    status(newValue) {
      if (typeof newValue !== 'boolean') {
        console.error('Invalid type for status. Expected Boolean.');
      }
      if (this.done && !newValue) {
        console.error('Task completed with errors.');
      }
    }
  }
};
</script>

<style scoped>
.step-container {
  @apply mb-4;
}

.step-wrapper {
  @apply flex items-start p-4 rounded-lg shadow-md;
}

.step-icon {
  @apply flex-shrink-0 w-6 h-6 mr-4 flex items-center justify-center;
}

.feather-icon {
  @apply w-6 h-6 stroke-2 stroke-current;
}

.spinner {
  @apply w-6 h-6 border-2 border-gray-600 border-t-2 border-t-blue-600 rounded-full animate-spin;
}

.step-content {
  @apply flex-grow;
}

.step-text {
  @apply text-lg font-semibold mb-1;
}

.step-description {
  @apply text-sm text-gray-600 dark:text-gray-400;
}
</style>
