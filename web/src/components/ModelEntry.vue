<template>
  <div class="flex items-center p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg">
    <div class="flex-shrink-0">
      <i :class="`fas ${icon} text-xl`"></i>
    </div>
    <div class="flex-1">
      <h3 class="font-bold text-lg">
        <input
          type="radio"
          :checked="selected"
          :disabled="!isInstalled"
          @change="handleSelection"
        />
        {{ title }}
      </h3>
      <a :href="path">{{ title }}</a>
      <p class="opacity-80">{{ description }}</p>
    </div>
    <div class="flex-shrink-0">
      <button
        class="px-4 py-2 rounded-md text-white font-bold transition-colors duration-300"
        :class="[isInstalled ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600']"
        :disabled="installing || uninstalling"
        @click="toggleInstall"
      >
        <template v-if="installing">
          <div class="flex items-center space-x-2">
            <div class="h-2 w-20 bg-gray-300 rounded">
              <div :style="{ width: progress + '%' }" class="h-full bg-green-500"></div>
            </div>
            <span>Installing...</span>
          </div>
        </template>
        <template v-else-if="uninstalling">
          <div class="flex items-center space-x-2">
            <div class="h-2 w-20 bg-gray-300 rounded">
              <div :style="{ width: progress + '%' }" class="h-full bg-green-500"></div>
            </div>
            <span>Uninstalling...</span>
          </div>
        </template>
        <template v-else>
          {{ isInstalled ? 'Uninstall' : 'Install' }}
        </template>
      </button>
    </div>
  </div>
</template>

<script>
import socket from '@/services/websocket.js'
export default {
  props: {
    progress: {
      type: Number,
      default: 0
    },
    title: String,
    icon: String,
    path: String,
    description: String,
    isInstalled: Boolean,
    onInstall: Function,
    onUninstall: Function,
    onSelected: Function,
    selected: Boolean
  },
  data() {
    return {
      installing: false,
      uninstalling: false
    };
  },
  methods: {
    toggleInstall() {
      if (this.isInstalled) {
        this.uninstalling = true;
        // Simulate uninstallation delay (replace this with your WebSocket logic)
        this.onUninstall(this);
      } else {
        this.installing = true;
        this.onInstall(this);

      }
    },
    handleSelection() {
      if (this.isInstalled && !this.selected) {
        this.onSelected(this);
        this.$set(this, 'selected', true);
      }
    }
  }
};
</script>
