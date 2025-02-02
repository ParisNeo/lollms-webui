<template>
  <div v-if="loading" title="Loading.." class="flex flex-row flex-grow justify-end">
    <!-- Spinner remains the same -->
  </div>
  <div v-else class="relative" ref="menuContainer">
    <button 
      @click="toggleMenu"
      class="flex items-center gap-2 px-4 py-2 text-white rounded-lg transition-all duration-300 shadow-md"
      :title="help"
      :class="{
        'bg-blue-600 hover:bg-blue-700': !isAnyCommandChecked, // Default state
        'bg-yellow-400 hover:bg-yellow-500': isAnyCommandChecked // Highlighted state
      }"
    >      <!-- Custom Icon -->
      <template v-if="icon">
        <svg
          v-if="iconParts.type === 'feather'"
          class="w-4 h-4"
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          :data-feather="iconParts.value"
        ></svg>
        <img 
          v-else-if="iconParts.type === 'img'" 
          :src="iconParts.value" 
          class="w-4 h-4"
        />
        <img 
          v-else-if="iconParts.type === 'b64'" 
          :src="'data:image/png;base64,' + iconParts.value" 
          class="w-4 h-4"
        />
      </template>
      
      <!-- Chevron Icon -->
      <svg 
        class="w-4 h-4 transform transition-transform"
        :class="{ 'rotate-180': showMenu }"
        fill="none" 
        stroke="currentColor" 
        viewBox="0 0 24 24"
      >
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
      </svg>
    </button>

    <transition
      enter-active-class="transition-opacity duration-200 ease-out"
      leave-active-class="transition-opacity duration-150 ease-in"
      enter-from-class="opacity-0"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="showMenu"
        ref="menu"
        class="absolute z-50 mt-2 w-64 origin-top-right rounded-lg bg-white dark:bg-gray-800 shadow-xl ring-1 ring-black ring-opacity-5 focus:outline-none"
        :class="menuPosition === 'above' ? 'bottom-full mb-2' : 'top-full'"
      >
      <div class="p-2 space-y-1 custom-scrollbar max-h-96 overflow-y-auto">
        <template v-for="(cmd, index) in commandsList" :key="index">
          <button
            :title="cmd.help"
            @click="selected(cmd)"
            class="flex w-full items-center rounded-md px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors duration-200"
          >
            <!-- Custom Checkbox for is_checked -->
            <span v-if="cmd.is_checked !== undefined" class="mr-2 relative">
              <input
                type="checkbox"
                :checked="cmd.is_checked"
                @click.stop="selected(cmd)"
                class="opacity-0 absolute h-4 w-4"
                :id="`checkbox-${index}`"
              />
              <label
                :for="`checkbox-${index}`"
                class="flex items-center justify-center h-4 w-4 border-2 border-blue-500 rounded-sm cursor-pointer transition-colors duration-200"
                :class="{ 'bg-blue-500 border-blue-500': cmd.is_checked }"
              >
                <svg
                  v-if="cmd.is_checked"
                  class="h-3 w-3 text-white"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </label>
            </span>

            <!-- Icon handling -->
            <span v-if="cmd.icon" class="mr-2">
              <template v-if="cmd.icon.startsWith('feather:')">
                <i :data-feather="cmd.icon.replace('feather:', '')"></i>
              </template>
              <template v-else-if="cmd.icon.startsWith('img:')">
                <img :src="cmd.icon.replace('img:', '')" class="w-4 h-4" />
              </template>
              <template v-else-if="cmd.icon.startsWith('b64:')">
                <img :src="`data:image/png;base64,${cmd.icon.replace('b64:', '')}`" class="w-4 h-4" />
              </template>
            </span>

            <!-- Command name -->
            <span v-html="cmd.name" class="truncate"></span>
          </button>

          <!-- Divider between commands -->
          <div v-if="index < commandsList.length - 1" class="border-t border-gray-200 dark:border-gray-700"></div>
        </template>
      </div>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  data() {
    return {
      loading: false,
      showMenu: false,
      menuPosition: 'below'
    }
  },
  props: {
    commandsList: Array,
    sendCommand: Function,
    help: {
      type: String,
      default: ''
    },
    icon: {
      type: String,
      default: ''
    },
    highlighted: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    isAnyCommandChecked() {
      return this.commandsList.some((cmd) => cmd.is_checked);
    },
    iconParts() {
      if (!this.icon) return { type: null, value: null };
      const [type, ...valueParts] = this.icon.split(':');
      return {
        type,
        value: valueParts.join(':')
      };
    }
  },
  methods: {
    selected(cmd){
      if(cmd.is_checked !== undefined)
        cmd.is_checked = ! cmd.is_checked
      this.sendCommand(cmd.value)
    },
    toggleMenu() {
      this.showMenu = !this.showMenu
      if (this.showMenu) {
        this.$nextTick(() => {
          this.calculatePosition()
        })
      }
    },
    calculatePosition() {
      const menuButton = this.$refs.menuContainer.getBoundingClientRect()
      const menuHeight = this.$refs.menu?.offsetHeight || 300
      const spaceBelow = window.innerHeight - menuButton.bottom
      const spaceAbove = menuButton.top

      this.menuPosition = spaceBelow > menuHeight || spaceBelow > spaceAbove ? 'below' : 'above'
    },
    handleClickOutside(event) {
      if (!this.$refs.menuContainer.contains(event.target)) {
        this.showMenu = false
      }
    }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside)
    window.addEventListener('resize', this.calculatePosition)
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside)
    window.removeEventListener('resize', this.calculatePosition)
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  @apply w-2;
}

.custom-scrollbar::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-700 rounded-full;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-gray-400 dark:bg-gray-600 rounded-full;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-500 dark:bg-gray-500;
}
</style>