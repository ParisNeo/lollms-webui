<template>
    <div
      class="app-card relative flex flex-col cursor-pointer transition-all duration-200 ease-in-out hover:shadow-lg"
      :class="{
          'border-2 border-blue-500 dark:border-blue-400 shadow-md scale-[1.02]': isActive,
          'border border-gray-200 dark:border-gray-700': !isActive,
          'opacity-60 hover:opacity-100': !isActive && service.name !== 'None' && service.name !== 'browser' /* Slightly fade non-active configurable services */
      }"
      @click="selectService"
    >
      <div class="flex-grow flex flex-col p-4">
        <div class="flex items-start mb-3">
          <img
            :src="getServiceIconUrl(service.icon)"
            @error="handleImgError"
            alt="Service Icon"
            class="w-12 h-12 rounded-lg object-cover mr-4 flex-shrink-0 border border-gray-200 dark:border-gray-600 shadow-sm"
          />
          <div class="flex-grow overflow-hidden min-w-0">
            <h3
              class="font-semibold text-md text-gray-800 dark:text-gray-100 truncate"
              :title="service.caption || service.name"
            >
              {{ service.caption || service.name }}
            </h3>
             <p v-if="service.description" class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2" :title="service.description">
                  {{ service.description }}
             </p>
          </div>
        </div>
  
        <div class="mt-auto pt-3 border-t border-gray-200 dark:border-gray-700">
          <div class="flex justify-end items-center">
            <button
              v-if="isConfigurable"
              @click.stop="configureService"
              class="btn btn-secondary btn-sm p-1.5 flex-shrink-0"
              title="Configure Service"
              :disabled="!isActive"  
              :class="{'cursor-not-allowed opacity-50': !isActive}" 
            >
              <i data-feather="settings" class="w-4 h-4"></i>
            </button>
             <span v-else class="text-xs text-gray-400 dark:text-gray-500 italic">No settings</span>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import feather from 'feather-icons';
  import { nextTick } from 'vue';
  import defaultServiceIconPlaceholder from "@/assets/logo.png";
  
  export default {
    name: 'ServiceEntry',
    props: {
      service: { type: Object, required: true },
      serviceType: { type: String, required: true },
      isActive: { type: Boolean, default: false },
      baseUrl: { type: String, default: '' },
    },
    emits: ['select', 'configure', 'error'],
    computed: {
       isConfigurable() {
          return this.service.name !== 'None' && this.service.name !== 'browser';
       }
    },
    methods: {
      selectService() {
          this.$emit('select', { serviceType: this.serviceType, serviceName: this.service.name });
      },
      configureService() {
         // Only emit if active, button is already disabled but this is belt-and-suspenders
         if (this.isActive) {
            this.$emit('configure', { serviceType: this.serviceType, serviceName: this.service.name });
         }
      },
      getServiceIconUrl(iconPath) {
        if (!iconPath) return defaultServiceIconPlaceholder;
        if (iconPath.startsWith('http') || iconPath.startsWith('/')) {
              return iconPath;
        }
        const effectiveBaseUrl = this.baseUrl.endsWith('/') ? this.baseUrl.slice(0, -1) : this.baseUrl;
        return `${effectiveBaseUrl}/${iconPath.startsWith('/') ? iconPath.substring(1) : iconPath}`;
      },
      handleImgError(event) {
        event.target.src = defaultServiceIconPlaceholder;
        this.$emit('error', { type: 'image_load', message: 'Failed to load service icon', event });
      },
       replaceFeatherIcons() {
           nextTick(() => { try { if (this.$el && this.$el.parentNode) feather.replace(); } catch (e) {} });
       }
    },
    mounted() {
       this.replaceFeatherIcons();
    },
    updated() {
       this.replaceFeatherIcons();
    }
  };
  </script>
  
  <style scoped>
  .app-card { @apply rounded-lg border bg-white dark:bg-gray-800 shadow-sm overflow-hidden; }
  .btn { @apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:opacity-50 transition-colors duration-150 whitespace-nowrap; }
  .btn-sm { @apply px-2.5 py-1.5 text-xs; }
  .btn-secondary { @apply text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-blue-500 border-gray-300 dark:border-gray-500 disabled:hover:bg-gray-100 dark:disabled:hover:bg-gray-700; }
  </style>