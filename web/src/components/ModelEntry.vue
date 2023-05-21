<template>
  <div class="flex items-center p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 cursor-pointer" @click.stop="toggleSelected"  :class="selected?' border-primary-light':'border-transparent'">
    <div class="flex-shrink-0">
      <i :class="`fas ${icon} text-xl`"></i>
    </div>
    <div class="flex-1">
      <h3 class="font-bold font-large text-lg">
        {{ title }}
      </h3>
      <div class="flex flex-shrink-0">
        <b>Manual download:&nbsp;</b>
        <a :href="path" @click.stop 
        class="flex hover:text-secondary duration-75 active:scale-90"
          title="Download this manually (faster) and put it in the models/<your backend> folder then refresh">
          <i data-feather="link" class="w-5 p-1"></i>
          {{ title }}
        </a>
      </div>
      <div class="flex flex-shrink-0">
        <b>License:&nbsp;</b>
          {{ license }}
      </div>
      <div class="flex flex-shrink-0">
        <b>Owner:&nbsp;</b>
        <a :href="owner_link"  target="_blank" @click.stop 
        class="flex hover:text-secondary duration-75 active:scale-90"
          title="Owner's profile">
          <i data-feather="link" class="w-5 p-1"></i>
          {{ owner }}
        </a>
      </div>      
      <b>Description:&nbsp;</b><br>
      <p class="opacity-80">{{ description }}</p>
    </div>
    <div class="flex-shrink-0">
      <button class="px-4 py-2 rounded-md text-white font-bold transition-colors duration-300"
        :class="[isInstalled ? 'bg-red-500 hover:bg-red-600' : 'bg-green-500 hover:bg-green-600']"
        :disabled="installing || uninstalling" @click.stop="toggleInstall">
        <template v-if="installing">
          <div class="flex items-center space-x-2">
            <div class="h-2 w-20 bg-gray-300 rounded">
              <div :style="{ width: progress + '%' }" class="h-full bg-red-500 rounded"></div>
            </div>
            <span>Installing...{{ Math.floor(progress) }}%</span>
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
import { nextTick } from 'vue'
import feather from 'feather-icons'
export default {
  props: {
    title: String,
    icon: String,
    path: String,
    owner: String,
    owner_link: String,
    license: String,
    description: String,
    isInstalled: Boolean,
    onInstall: Function,
    onUninstall: Function,
    onSelected: Function,
    selected: Boolean
  },
  data() {
    return {
      progress: 0,
      installing: false,
      uninstalling: false
    };
  },
  mounted() {
    nextTick(() => {
      feather.replace()


    })
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
    toggleSelected(){
      this.onSelected(this)
    },
    handleSelection() {
      if (this.isInstalled && !this.selected) {
        this.onSelected(this);
      }
    }
  }
};
</script>
