<template>
  <div
    class="items-start p-4 rounded-lg mb-2 shadow-lg border-2 cursor-pointer select-none transition-all duration-150 ease-in-out group"
    :class="{
      'border-primary bg-primary-light dark:bg-primary-dark': selected, // Selected state
      'hover:bg-gray-100 dark:hover:bg-gray-700': !selected && !isProcessing, // Hover state when not selected and not processing
      'border-transparent bg-white dark:bg-gray-800': !selected,      // Default state when not selected (handles installed/not installed)
      'opacity-70 cursor-wait': isProcessing                        // Visual cue when processing
    }"
    :title="binding.description || binding.name"
    @click.stop="!isProcessing ? emitSelect() : null"
  >
    <div>
      <!-- Header Section -->
      <div class="flex flex-row items-center gap-3 mb-2">
        <img
          ref="imgElement"
          :src="getImgUrl()"
          @error="defaultImg($event)"
          class="w-10 h-10 rounded-full object-fill flex-shrink-0 border border-gray-200 dark:border-gray-600"
          :class="{
              'ring-2 ring-offset-2 ring-green-500 dark:ring-offset-gray-800': binding.installed && !isProcessing,
              'ring-2 ring-offset-2 ring-yellow-500 dark:ring-offset-gray-800 animate-pulse': isProcessing
              }"
        >
        <h3 class="font-bold text-lg truncate text-gray-800 dark:text-white flex-grow">
          {{ binding.name }}
          <span v-if="binding.installed && !isProcessing" class="ml-2 text-xs font-medium text-green-600 dark:text-green-400">(Installed)</span>
          <span v-if="isProcessing" class="ml-2 text-xs font-medium text-yellow-600 dark:text-yellow-400">(Processing...)</span>
        </h3>

        <!-- Top Right Actions -->
        <div class="flex-none flex items-center gap-1">
           <button
             v-if="selected && binding.installed && !isProcessing"
             type="button"
             title="Reload binding"
             @click.stop="emitReloadBinding"
             class="text-gray-500 hover:text-secondary dark:text-gray-400 dark:hover:text-secondary-light duration-150 active:scale-90 font-medium rounded-lg text-sm p-1.5 text-center inline-flex items-center focus:outline-none focus:ring-2 focus:ring-gray-300 dark:focus:ring-gray-600"
           >
             <i data-feather="refresh-cw" class="w-5 h-5"></i>
             <span class="sr-only">Reload Binding</span>
           </button>
        </div>
      </div>

      <!-- Conditional UI Renderer -->
      <DynamicUIRenderer v-if="binding.ui" class="w-full h-full mb-3 border-t pt-3 border-gray-200 dark:border-gray-700" :code="binding.ui"></DynamicUIRenderer>

      <!-- Details Section -->
      <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1 mb-3">
        <!-- Author -->
        <div class="flex items-center">
          <i data-feather="user" class="w-4 h-4 mr-2 flex-shrink-0"></i>
          <b class="mr-1 font-medium text-gray-700 dark:text-gray-300">Author:</b>
          <span class="truncate">{{ binding.author }}</span>
        </div>
        <!-- Folder -->
        <div class="flex items-center">
          <i data-feather="folder" class="w-4 h-4 mr-2 flex-shrink-0"></i>
          <b class="mr-1 font-medium text-gray-700 dark:text-gray-300">Folder:</b>
          <span class="truncate font-mono text-xs bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded">{{ binding.folder }}</span>
          <div class="flex-grow"></div>
          <button
            class="ml-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 duration-150 active:scale-90 p-1 rounded disabled:opacity-50"
            title="Copy folder path to clipboard"
            @click.stop="copyToClipBoard(binding.folder)"
            :disabled="isProcessing"
          >
            <i data-feather="clipboard" class="w-4 h-4"></i>
            <span class="sr-only">Copy folder path</span>
          </button>
        </div>
        <!-- Version -->
        <div class="flex items-center">
          <i data-feather="git-merge" class="w-4 h-4 mr-2 flex-shrink-0"></i>
          <b class="mr-1 font-medium text-gray-700 dark:text-gray-300">Version:</b>
          <span>{{ binding.version }}</span>
        </div>
        <!-- Link -->
        <div class="flex items-center">
          <i data-feather="github" class="w-4 h-4 mr-2 flex-shrink-0"></i>
          <b class="mr-1 font-medium text-gray-700 dark:text-gray-300">Link:</b>
          <a
            :href="binding.link"
            target="_blank"
            rel="noopener noreferrer"
            class="text-blue-600 dark:text-blue-400 hover:underline truncate"
            :class="{'pointer-events-none opacity-70': isProcessing}"
            @click.stop
          >
            {{ binding.link }}
          </a>
        </div>
        <!-- Description -->
        <div class="flex items-start pt-1">
          <i data-feather="info" class="w-4 h-4 mr-2 mt-0.5 flex-shrink-0"></i>
          <div>
            <b class="font-medium text-gray-700 dark:text-gray-300">Description:</b>
            <p class="opacity-90 line-clamp-3" :title="binding.description" v-html="binding.description"></p>
          </div>
        </div>
      </div>

      <!-- Action Buttons Section -->
      <div class="flex items-center justify-end gap-2 border-t border-gray-200 dark:border-gray-700 pt-3 min-h-[44px]"> <!-- Added min-height to prevent layout jump -->
        <!-- Processing Indicator -->
         <div v-if="isProcessing" class="flex items-center justify-center text-gray-500 dark:text-gray-400 w-full">
             <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-current mr-2"></div>
             Processing...
         </div>

        <!-- Actual Buttons (show only when not processing) -->
        <template v-if="!isProcessing">
            <!-- Install Button -->
            <button
              v-if="!binding.installed"
              title="Click to install"
              type="button"
              @click.stop="emitInstall"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-center text-white bg-blue-600 rounded-lg shadow-sm hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 focus:outline-none dark:bg-blue-500 dark:hover:bg-blue-600 dark:focus:ring-blue-800 transition-colors duration-200 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i data-feather="download-cloud" class="w-4 h-4"></i>
            </button>

            <!-- Reinstall Button -->
            <button
              v-if="binding.installed"
              title="Click to Reinstall binding"
              type="button"
              @click.stop="emitReinstall"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-center text-white bg-green-600 rounded-lg shadow-sm hover:bg-green-700 focus:ring-4 focus:ring-green-300 focus:outline-none dark:bg-green-500 dark:hover:bg-green-600 dark:focus:ring-green-800 transition-colors duration-200 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i data-feather="refresh-ccw" class="w-4 h-4"></i>
            </button>

            <!-- Uninstall Button -->
            <button
              v-if="binding.installed"
              title="Click to Uninstall binding"
              type="button"
              @click.stop="emitUninstall"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-center text-white bg-red-600 rounded-lg shadow-sm hover:bg-red-700 focus:ring-4 focus:ring-red-300 focus:outline-none dark:bg-red-500 dark:hover:bg-red-600 dark:focus:ring-red-800 transition-colors duration-200 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
            >
               <i data-feather="trash-2" class="w-4 h-4"></i>
            </button>

            <!-- Settings Button -->
            <button
              v-if="selected && binding.installed"
              title="Click to open Settings"
              type="button"
              @click.stop="emitSettings"
              class="inline-flex items-center gap-2 px-4 py-2 text-sm font-semibold text-center text-white bg-gray-600 rounded-lg shadow-sm hover:bg-gray-700 focus:ring-4 focus:ring-gray-300 focus:outline-none dark:bg-gray-500 dark:hover:bg-gray-600 dark:focus:ring-gray-800 transition-colors duration-200 ease-in-out disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <i data-feather="settings" class="w-4 h-4"></i>
            </button>
        </template>
      </div>
    </div>
  </div>
</template>

<script>
import { nextTick } from 'vue';
import feather from 'feather-icons';
// Make sure this path is correct relative to your component file
import botImgPlaceholder from "../assets/logo.svg";
// Assuming DynamicUIRenderer is correctly imported and registered globally or locally
import DynamicUIRenderer from "@/components/DynamicUIRenderer.vue";

// Ensure VITE_LOLLMS_API_BASEURL is available in your environment (.env file)
const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL || ''; // Provide a fallback

export default {
  name: 'BindingEntry',
  components: { DynamicUIRenderer },
  props: {
    binding: {
      type: Object,
      required: true,
    },
    selected: { // Boolean indicating if this entry *is* currently selected (controlled by parent)
      type: Boolean,
      default: false,
    },
    isProcessing: { // Boolean indicating if an async operation is happening for this binding (controlled by parent)
      type: Boolean,
      default: false
    }
  },
  // Declare the events this component can emit to its parent
  emits: [
    'select', // Event emitted when the entry is clicked for selection
    'install', // Event emitted when the install button is clicked
    'uninstall', // Event emitted when the uninstall button is clicked
    'reinstall', // Event emitted when the reinstall button is clicked
    'settings', // Event emitted when the settings button is clicked
    'reload-binding' // Event emitted when the reload button is clicked
  ],
  mounted() {
    this.updateIcons();
  },
  updated() {
    // Ensures icons are rendered correctly after any prop changes or re-renders
    this.updateIcons();
  },
  methods: {
    updateIcons() {
       // Use nextTick to wait for the DOM to update before replacing icons
       nextTick(() => {
         try {
             feather.replace({
                 width: '1em', // Consistent sizing
                 height: '1em'
             });
         } catch (e) {
             console.error("Feather icons replacement failed:", e);
         }
       });
    },
    copyToClipBoard(text) {
      if (!text) {
          console.warn("Attempted to copy empty text.");
          return;
      }
      if (navigator.clipboard) {
          navigator.clipboard.writeText(text).then(() => {
              console.log("Copied to clipboard:", text);
              // Consider adding user feedback (e.g., a toast notification)
              // Example: this.$toast.success('Copied!');
          }).catch(err => {
              console.error("Failed to copy text using navigator.clipboard: ", err);
              this.fallbackCopyToClipboard(text); // Attempt fallback
          });
      } else {
          console.warn("Clipboard API not available, attempting fallback.");
          this.fallbackCopyToClipboard(text);
      }
    },
    fallbackCopyToClipboard(text) {
        // Fallback using execCommand (deprecated but might work in some environments)
        const textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "absolute"; // Avoid screen flicker
        textArea.style.left = "-9999px";
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                console.log("Fallback copy successful:", text);
                // Add user feedback
            } else {
                console.error('Fallback copy command failed.');
                // Add error feedback
            }
        } catch (err) {
            console.error('Error during fallback copy command:', err);
            // Add error feedback
        }
        document.body.removeChild(textArea);
    },
    getImgUrl() {
      // Basic check for the icon path
      if (!this.binding || typeof this.binding.icon !== 'string' || this.binding.icon.trim() === '') {
          return botImgPlaceholder; // Return placeholder if icon path is invalid
      }
      // Prepend base URL only if icon path is relative (doesn't start with http, https, or /)
      if (/^(https?:)?\/\//.test(this.binding.icon) || this.binding.icon.startsWith('/')) {
        return this.binding.icon; // Assume absolute path or full URL
      }
      // Ensure base URL ends with a slash if it's not empty
      const baseUrl = bUrl && !bUrl.endsWith('/') ? `${bUrl}/` : bUrl;
      return baseUrl + this.binding.icon;
    },
    defaultImg(event) {
      // Prevent potential infinite loop if the placeholder itself fails
      if (event.target.src !== botImgPlaceholder) {
        event.target.src = botImgPlaceholder;
      }
    },
    // --- Methods to EMIT events to the parent ---
    emitSelect() {
      if (this.isProcessing) return; // Double check processing state
      this.$emit('select', this.binding); // Emit 'select' event with the binding object
    },
    emitInstall() {
      if (this.isProcessing) return;
      this.$emit('install', this.binding); // Emit 'install' event
    },
    emitUninstall() {
       if (this.isProcessing) return;
      this.$emit('uninstall', this.binding); // Emit 'uninstall' event
    },
    emitReinstall() {
       if (this.isProcessing) return;
      this.$emit('reinstall', this.binding); // Emit 'reinstall' event
    },
    emitReloadBinding() {
       if (this.isProcessing) return;
      this.$emit('reload-binding', this.binding); // Emit 'reload-binding' event
    },
    emitSettings() {
       if (this.isProcessing) return;
      this.$emit('settings', this.binding); // Emit 'settings' event
    }
  },
  watch: {
    // Watch relevant props and call updateIcons if they change
    selected() { this.updateIcons(); },
    isProcessing() { this.updateIcons(); },
    'binding.installed'() { this.updateIcons(); },
    'binding.ui'() { this.updateIcons(); }, // If dynamic UI can add icons
  }
};
</script>

<style scoped>
/* Scoped styles specific to BindingEntry */
[data-feather] {
  vertical-align: middle;
  width: 1em; /* Ensure consistent icon size */
  height: 1em;
  stroke-width: 2; /* Default stroke width */
}

/* Tailwind's animate-spin utility class */
@keyframes spin {
  to { transform: rotate(360deg); }
}
.animate-spin {
  animation: spin 1s linear infinite;
}

/* Tailwind's animate-pulse utility class */
@keyframes pulse {
  50% { opacity: .5; }
}
.animate-pulse {
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

/* Improve line-clamp support (optional, Tailwind might handle this) */
.line-clamp-3 {
  overflow: hidden;
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
}
</style>