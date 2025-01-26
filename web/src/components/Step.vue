<template>
  <div 
    class="flex items-center p-2 rounded transition-colors duration-200"
    :class="[
      done ? 'bg-opacity-5' : 'bg-opacity-3',
      status ? 'bg-green-50 dark:bg-green-900/20' : 'bg-gray-50 dark:bg-gray-800/20'
    ]"
  >
    <div class="flex items-start gap-2 w-full">
      <div class="w-4 h-4 flex-shrink-0">
        <template v-if="done">
          <svg 
            v-if="status" 
            class="w-4 h-4 text-green-500 dark:text-green-400" 
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41L9 16.17z" />
          </svg>
          <svg 
            v-else 
            class="w-4 h-4 text-red-500 dark:text-red-400" 
            viewBox="0 0 24 24"
            fill="currentColor"
          >
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" />
          </svg>
        </template>
        <div 
          v-else 
          class="w-4 h-4 border-2 border-t-primary rounded-full animate-spin"
        ></div>
      </div>

      <div class="min-w-0">
        <div class="text-sm text-gray-700 dark:text-gray-200 truncate">
          {{ text || 'No text provided' }}
        </div>
        <div 
          v-if="description" 
          class="text-xs text-gray-500 dark:text-gray-400 truncate"
        >
          {{ description }}
        </div>
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

<style scoped>
.border-t-primary {
  border-color: #e2e8f0;
  border-top-color: currentColor;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 0.8s linear infinite;
}
</style>
