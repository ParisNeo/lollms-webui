<template>
  <div
    class="items-start p-4 rounded-lg mb-2 shadow-lg border-2 cursor-pointer select-none transition-all duration-150 ease-in-out group"
    :class="{
      // Selected: Use a noticeable border and slightly different bg from theme
      'border-blue-400 dark:border-sky-500 bg-blue-100 dark:bg-slate-700': selected,
      // Hover: Use theme hover colors
      'hover:bg-blue-50 dark:hover:bg-slate-700': !selected && !isProcessing,
      // Default: Use theme panel/card base colors (adjusting light bg slightly)
      'border-transparent bg-blue-50 dark:bg-slate-800 text-slate-800 dark:text-slate-200': !selected,
      // Processing: Keep opacity/cursor
      'opacity-70 cursor-wait': isProcessing
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
          class="w-10 h-10 rounded-full object-fill flex-shrink-0 border border-blue-200 dark:border-slate-700"
          :class="{
              // Use theme status colors and offset relative to parent bg
              'ring-2 ring-offset-2 ring-green-500 dark:ring-green-400 ring-offset-blue-50 dark:ring-offset-slate-800': binding.installed && !isProcessing && !selected,
              'ring-2 ring-offset-2 ring-green-500 dark:ring-green-400 ring-offset-blue-100 dark:ring-offset-slate-700': binding.installed && !isProcessing && selected, // Adjust offset if selected bg is different
              'ring-2 ring-offset-2 ring-yellow-500 dark:ring-yellow-400 ring-offset-blue-50 dark:ring-offset-slate-800 animate-pulse': isProcessing // Assuming processing bg is default
              }"
        >
        <h3 class="font-bold text-lg truncate text-slate-800 dark:text-slate-100 flex-grow"> <!-- Theme text -->
          {{ binding.name }}
          <!-- Status colors are fine -->
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
             class="svg-button text-slate-500 dark:text-slate-400 hover:text-blue-600 dark:hover:text-sky-400 hover:bg-transparent dark:hover:bg-transparent active:scale-90 focus:ring-blue-300 dark:focus:ring-slate-600"
             >
             <i data-feather="refresh-cw" class="w-5 h-5"></i>
             <span class="sr-only">Reload Binding</span>
           </button>
        </div>
      </div>

      <!-- Conditional UI Renderer -->
      <!-- Use theme border -->
      <DynamicUIRenderer v-if="binding.ui" class="w-full h-full mb-3 border-t pt-3 border-blue-200 dark:border-slate-700" :code="binding.ui"></DynamicUIRenderer>

      <!-- Details Section -->
      <!-- Use theme text color for details section -->
      <div class="text-sm text-slate-600 dark:text-slate-400 space-y-1 mb-3">
        <!-- Author -->
        <div class="flex items-center">
          <i data-feather="user" class="w-4 h-4 mr-2 flex-shrink-0"></i>
          <!-- Use theme label-like text color -->
          <b class="mr-1 font-medium text-slate-700 dark:text-slate-300">Author:</b>
          <span class="truncate">{{ binding.author }}</span>
        </div>
        <!-- Folder -->
        <div class="flex items-center">
          <i data-feather="folder" class="w-4 h-4 mr-2 flex-shrink-0"></i>
          <b class="mr-1 font-medium text-slate-700 dark:text-slate-300">Folder:</b>
          <!-- Use theme code/input background -->
          <span class="truncate font-mono text-xs bg-blue-100 dark:bg-slate-700 px-1 py-0.5 rounded">{{ binding.folder }}</span>
          <div class="flex-grow"></div>
          <button
            class="ml-2 text-slate-400 hover:text-slate-600 dark:text-slate-500 dark:hover:text-slate-300 duration-150 active:scale-90 p-1 rounded disabled:opacity-50"
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
          <b class="mr-1 font-medium text-slate-700 dark:text-slate-300">Version:</b>
          <span>{{ binding.version }}</span>
        </div>
        <!-- Link -->
        <div class="flex items-center">
          <i data-feather="github" class="w-4 h-4 mr-2 flex-shrink-0"></i>
          <b class="mr-1 font-medium text-slate-700 dark:text-slate-300">Link:</b>
          <a
            :href="binding.link"
            target="_blank"
            rel="noopener noreferrer"
            class="link truncate"
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
            <b class="font-medium text-slate-700 dark:text-slate-300">Description:</b>
            <!-- Inherits detail section text color -->
            <p class="opacity-90 line-clamp-3" :title="binding.description" v-html="binding.description"></p>
          </div>
        </div>
      </div>

      <!-- Action Buttons Section -->
      <!-- Use theme border -->
      <div class="flex items-center justify-end gap-2 border-t border-blue-200 dark:border-slate-700 pt-3 min-h-[44px]">
        <!-- Processing Indicator -->
         <div v-if="isProcessing" class="flex items-center justify-center text-slate-500 dark:text-slate-400 w-full"> <!-- Theme text -->
             <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-current mr-2"></div>
             Processing...
         </div>

        <!-- Actual Buttons (show only when not processing) -->
        <template v-if="!isProcessing">
            <!-- Install Button: Use btn-primary -->
            <button
              v-if="!binding.installed"
              title="Click to install"
              type="button"
              @click.stop="emitInstall"
              class="btn btn-primary btn-sm"
              :disabled="isProcessing"
            >
              <i data-feather="download-cloud" class="w-4 h-4 mr-1"></i> <!-- Added margin -->
              <span>Install</span> <!-- Added text for clarity on small buttons -->
            </button>

            <!-- Reinstall Button: Use btn-success -->
            <button
              v-if="binding.installed"
              title="Click to Reinstall binding"
              type="button"
              @click.stop="emitReinstall"
              class="btn btn-success btn-sm"
              :disabled="isProcessing"
            >
              <i data-feather="refresh-ccw" class="w-4 h-4 mr-1"></i> <!-- Added margin -->
              <span>Reinstall</span> <!-- Added text -->
            </button>

            <!-- Uninstall Button: Use custom red based on theme patterns -->
            <button
              v-if="binding.installed"
              title="Click to Uninstall binding"
              type="button"
              @click.stop="emitUninstall"
              class="btn btn-sm bg-red-600 text-white hover:bg-red-700 focus:ring-4 focus:ring-red-300 dark:bg-red-500 dark:hover:bg-red-600 dark:focus:ring-red-800 disabled:opacity-50" 
              :disabled="isProcessing"
            >
               <i data-feather="trash-2" class="w-4 h-4 mr-1"></i> <!-- Added margin -->
               <span>Uninstall</span> <!-- Added text -->
            </button>

            <!-- Settings Button: Use btn-secondary -->
            <button
              v-if="selected && binding.installed"
              title="Click to open Settings"
              type="button"
              @click.stop="emitSettings"
              class="btn btn-secondary btn-sm"
              :disabled="isProcessing"
            >
              <i data-feather="settings" class="w-4 h-4 mr-1"></i> <!-- Added margin -->
              <span>Settings</span> <!-- Added text -->
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
import DynamicUIRenderer from "@/components/MarkdownBundle/DynamicUIRenderer.vue";

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