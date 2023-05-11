<template>
  <div
    class="flex items-center p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg"
    :class="{ 'bg-primary-light': selected }"
  >
    <div class="flex-shrink-0">
      <i :class="`fas ${icon} text-xl`"></i>
    </div>
    <div class="flex-1">
      <h3 class="font-bold text-lg">
        <input
          type="radio"
          :checked="selected"
          :disabled="!isInstalled" <!-- Disable radio button if not installed -->
          @change="handleSelection"
        />
        {{ title }}
      </h3>
      <p class="opacity-80">{{ description }}</p>
    </div>
    <div class="flex-shrink-0">
      <button
        class="px-4 py-2 rounded-md text-white font-bold transition-colors duration-300"
        :class="[isInstalled ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600']"
        @click="toggleInstall"
      >
        {{ isInstalled ? 'Uninstall' : 'Install' }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  props: {
    title: String,
    icon: String,
    path: String,
    description: String,
    isInstalled: Boolean,
    onToggleInstall: Function,
    selected: Boolean // Use a boolean selected prop
  },
  methods: {
    toggleInstall() {
      this.onToggleInstall(this.isInstalled, this.path);
    },
    handleSelection() {
      if (this.isInstalled && !this.selected) { // Only emit event if installed and not already selected
        this.$emit('update:selected', true);
      }
    }
  }
};
</script>
