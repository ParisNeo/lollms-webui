<template>
  <div v-if="loading" title="Loading.." class="flex flex-row flex-grow justify-end">
    <svg class="animate-spin h-5 w-5 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
      <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  </div>
  <div v-else class="relative" ref="menuContainer">
    <button
      @click="toggleMenu"
      class="flex items-center gap-2 px-4 py-2 text-white rounded-lg transition-all duration-300 shadow-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-400 dark:focus:ring-offset-gray-900"
      :title="help"
      :class="{
        'bg-blue-600 hover:bg-blue-700': !isAnyCommandChecked,
        'bg-yellow-400 hover:bg-yellow-500 text-gray-800': isAnyCommandChecked
      }"
    >
      <template v-if="icon">
        <i v-if="iconParts.type === 'feather'" :data-feather="iconParts.value" class="w-4 h-4"></i>
        <img v-else-if="iconParts.type === 'img'" :src="iconParts.value" class="w-4 h-4" alt="Icon" />
        <img v-else-if="iconParts.type === 'b64'" :src="'data:image/png;base64,' + iconParts.value" class="w-4 h-4" alt="Icon" />
      </template>
      <span>{{ buttonLabel }}</span>
      <svg
        class="w-4 h-4 transform transition-transform duration-200"
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
        class="absolute z-50 mt-2 w-80 origin-top-right rounded-lg bg-white dark:bg-gray-800 shadow-xl ring-1 ring-black ring-opacity-5 focus:outline-none flex flex-col overflow-hidden"
        :class="menuPosition === 'above' ? 'bottom-full mb-2' : 'top-full'"
        style="max-height: calc(28rem + 3rem);"
      >
        <div v-if="commandsList.length > 10" class="p-2 sticky top-0 bg-white dark:bg-gray-800 z-10 border-b border-gray-200 dark:border-gray-700 flex-shrink-0">
           <input
             ref="searchInput"
             type="search"
             v-model="searchTerm"
             placeholder="Search commands..."
             class="w-full px-3 py-1.5 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:text-gray-200"
             @click.stop
           />
        </div>

        <div class="custom-scrollbar overflow-y-auto flex-grow">
          <ul class="divide-y divide-gray-100 dark:divide-gray-700 px-1 py-1">
            <li
              v-for="(cmd) in filteredCommandsList"
              :key="cmd.value || cmd.name"
              class="group flex items-center justify-between w-full text-sm rounded-md hover:bg-blue-50 dark:hover:bg-gray-700 transition-colors duration-150"
              :class="{'bg-blue-50 dark:bg-gray-700': cmd.value === recentlyClicked}"
            >
              <button
                :title="cmd.help"
                @click="handleSelect(cmd)"
                class="flex items-center flex-1 min-w-0 px-3 py-2 text-gray-700 dark:text-gray-200 group-hover:text-blue-700 dark:group-hover:text-blue-300"
              >
                <span v-if="cmd.is_checked !== undefined" class="mr-3 flex-shrink-0 relative h-4 w-4">
                  <input
                    type="checkbox"
                    :checked="cmd.is_checked"
                    class="opacity-0 absolute h-full w-full cursor-pointer"
                    :id="`checkbox-${cmd.value || cmd.name}`"
                    tabindex="-1"
                  />
                  <label
                    :for="`checkbox-${cmd.value || cmd.name}`"
                    class="flex items-center justify-center h-4 w-4 border-2 border-gray-400 dark:border-gray-500 rounded-sm cursor-pointer transition-all duration-200 group-hover:border-blue-500"
                    :class="{ 'bg-blue-500 border-blue-500 dark:border-blue-400 dark:bg-blue-400': cmd.is_checked }"
                  >
                    <svg
                      v-if="cmd.is_checked"
                      class="h-3 w-3 text-white"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"/>
                    </svg>
                  </label>
                </span>

                <span v-if="cmd.icon" class="mr-2 flex-shrink-0 w-4 h-4">
                  <i v-if="cmdIconType(cmd.icon) === 'feather'" :data-feather="cmdIconValue(cmd.icon)" class="w-full h-full"></i>
                  <img v-else-if="cmdIconType(cmd.icon) === 'img'" :src="cmdIconValue(cmd.icon)" class="w-full h-full object-contain" alt="" />
                  <img v-else-if="cmdIconType(cmd.icon) === 'b64'" :src="`data:image/png;base64,${cmdIconValue(cmd.icon)}`" class="w-full h-full object-contain" alt="" />
                </span>

                <span v-html="highlightMatch(cmd.name)" class="truncate flex-1 text-left"></span>
              </button>

              <button
                v-if="showSettings && typeof showSettings === 'function'"
                @click.stop="handleShowSettings(cmd)"
                class="text-gray-400 hover:text-green-600 dark:hover:text-green-400 transition duration-150 flex-shrink-0 p-2 mr-1 focus:outline-none opacity-0 group-hover:opacity-100"
                title="Settings"
                tabindex="-1"
              >
                <i data-feather="settings" class="h-4 w-4"></i>
              </button>
            </li>
          </ul>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import feather from 'feather-icons';

export default {
  name: 'CommandMenu',
  props: {
    commandsList: {
      type: Array,
      required: true,
      default: () => []
    },
    sendCommand: {
      type: Function,
      required: true
    },
    showSettings: {
      type: Function,
      default: undefined
    },
    help: {
      type: String,
      default: 'Select Command'
    },
    icon: {
      type: String,
      default: 'feather:tool'
    },
    buttonLabel: {
        type: String,
        default: ''
    }
  },
  data() {
    return {
      loading: false,
      showMenu: false,
      menuPosition: 'below',
      searchTerm: '',
      recentlyClicked: null,
      clickTimeout: null
    }
  },
  computed: {
    isAnyCommandChecked() {
      return this.commandsList.some((cmd) => cmd.is_checked);
    },
    iconParts() {
      return this.parseIconString(this.icon);
    },
    filteredCommandsList() {
      if (!this.searchTerm) {
        return this.commandsList;
      }
      const lowerSearchTerm = this.searchTerm.toLowerCase();
      const stripHtml = (html) => {
          const tmp = document.createElement("DIV");
          tmp.innerHTML = html;
          return tmp.textContent || tmp.innerText || "";
      };
      return this.commandsList.filter(cmd =>
        stripHtml(cmd.name).toLowerCase().includes(lowerSearchTerm)
      );
    }
  },
  methods: {
    parseIconString(iconString) {
      if (!iconString) return { type: null, value: null };
      const parts = iconString.split(':');
      const type = parts[0];
      const value = parts.slice(1).join(':');
      if (['feather', 'img', 'b64'].includes(type)) {
        return { type, value };
      }
      return { type: 'feather', value: iconString };
    },
    cmdIconType(iconString) {
        return this.parseIconString(iconString).type;
    },
    cmdIconValue(iconString) {
        return this.parseIconString(iconString).value;
    },
    handleSelect(cmd) {
      if (cmd.is_checked !== undefined) {
        // Avoid direct prop mutation if possible, emit event instead if commandsList is a prop
        // Assuming direct modification is intended based on original code
         cmd.is_checked = !cmd.is_checked;
      }
      this.sendCommand(cmd.value);
      this.recentlyClicked = cmd.value;
      this.closeMenu();

      if(this.clickTimeout) clearTimeout(this.clickTimeout);
      this.clickTimeout = setTimeout(() => {
        this.recentlyClicked = null;
      }, 300);
    },
    handleShowSettings(cmd) {
        if(this.showSettings && typeof this.showSettings === 'function') {
            this.showSettings(cmd);
            this.closeMenu();
        }
    },
    toggleMenu() {
      this.showMenu = !this.showMenu;
      if (this.showMenu) {
          this.searchTerm = '';
          this.$nextTick(() => {
              this.calculatePosition();
              this.replaceFeatherIcons();
              this.$refs.searchInput?.focus();
          });
      }
    },
    closeMenu() {
        this.showMenu = false;
        this.searchTerm = '';
    },
    calculatePosition() {
      if (!this.$refs.menuContainer || !this.showMenu) return; // Check showMenu here

       this.$nextTick(() => { // Ensure menu is rendered for measurement
           if (!this.$refs.menu) return;
            const menuButtonRect = this.$refs.menuContainer.getBoundingClientRect();
            const menuHeightEst = Math.min(this.$refs.menu.scrollHeight, 480); // Use scrollHeight up to max-height approx
            const spaceBelow = window.innerHeight - menuButtonRect.bottom;
            const spaceAbove = menuButtonRect.top;
            const safetyMargin = 10;

            this.menuPosition = (spaceBelow < menuHeightEst + safetyMargin) && (spaceAbove > spaceBelow) ? 'above' : 'below';
       });
    },
    handleClickOutside(event) {
      if (this.$refs.menuContainer && !this.$refs.menuContainer.contains(event.target)) {
        this.closeMenu();
      }
    },
    replaceFeatherIcons() {
        this.$nextTick(() => {
            feather.replace({
                width: '1em',
                height: '1em',
                'stroke-width': 2
            });
        });
    },
    highlightMatch(text) {
        if (!this.searchTerm) return text;
         // Strip potential existing HTML before searching
        const strippedText = (() => {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = text;
            return tempDiv.textContent || tempDiv.innerText || '';
        })();

        const lowerText = strippedText.toLowerCase();
        const lowerSearch = this.searchTerm.toLowerCase();
        const index = lowerText.indexOf(lowerSearch);

        if (index === -1) return text; // Return original HTML if no match in text content

        const before = strippedText.substring(0, index);
        const match = strippedText.substring(index, index + this.searchTerm.length);
        const after = strippedText.substring(index + this.searchTerm.length);

        // Escape HTML entities for parts before/after match, wrap match in strong
        const escapeHtml = (unsafe) => unsafe.replace(/&/g, "&").replace(/</g, "<").replace(/>/g, ">").replace(/"/g, "\"").replace(/'/g, "'");

        return `${escapeHtml(before)}<strong class="font-semibold bg-yellow-200 dark:bg-yellow-600 rounded-sm">${escapeHtml(match)}</strong>${escapeHtml(after)}`;
    }
  },
  watch: {
      filteredCommandsList() {
          if (this.showMenu) {
              this.$nextTick(() => {
                  this.calculatePosition(); // Recalculate potentially changed height
                  this.replaceFeatherIcons();
              });
          }
      },
      searchTerm() {
         if (this.showMenu) {
             this.replaceFeatherIcons();
             this.$nextTick(() => this.calculatePosition()); // Recalculate as list size changes
         }
      },
       showMenu(newVal) {
        // Ensure position is calculated *after* menu is rendered
        if (newVal) {
          this.$nextTick(() => this.calculatePosition());
        }
      }
  },
  mounted() {
    document.addEventListener('click', this.handleClickOutside, true);
    window.addEventListener('resize', this.calculatePosition);
    this.replaceFeatherIcons();
  },
  beforeUnmount() {
    document.removeEventListener('click', this.handleClickOutside, true);
    window.removeEventListener('resize', this.calculatePosition);
    if(this.clickTimeout) clearTimeout(this.clickTimeout);
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  @apply w-1.5;
}
.custom-scrollbar::-webkit-scrollbar-track {
  @apply bg-gray-100 dark:bg-gray-700; /* Removed rounded-full for edge */
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  @apply bg-gray-400 dark:bg-gray-500 rounded-full; /* Keep thumb rounded */
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  @apply bg-gray-500 dark:bg-gray-400;
}

/* Ensure consistent icon sizing */
li svg[data-feather], li img,
button > svg[data-feather], button > img {
    width: 1rem;
    height: 1rem;
    flex-shrink: 0;
}
</style>