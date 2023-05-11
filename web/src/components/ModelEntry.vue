<template>
    <div class="flex items-center p-4 hover:bg-primary-light  rounded-lg mb-2 shadow-lg">
      


      <div class="flex-shrink-0">
        <i :class="`fas ${icon} text-xl`"></i>
      </div>
      <div class="flex-1">
        <h3 class="font-bold text-lg">{{ title }}</h3>
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
    },
    methods: {
      toggleInstall() {
        this.onToggleInstall(this.isInstalled, this.path);
      },
    },
  };
  </script>
  