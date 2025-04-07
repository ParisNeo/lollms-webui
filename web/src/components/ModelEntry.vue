<template>
  <div
    class="relative items-start p-4 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg mb-2 shadow-lg border-2 select-none transition-colors duration-150"
    :class="computedClasses"
    :title="model.name"
    role="button"
    tabindex="0"
    :aria-pressed="isSelected"
    :aria-disabled="isDisabled"
    @click.prevent="handleClick"
    @keydown.enter="handleClick"
    @keydown.space.prevent="handleClick"
  >
    <!-- CUSTOM MODEL VIEW -->
    <div v-if="model.isCustomModel">
       <div class="flex flex-row">
         <div class="max-w-[300px] overflow-x-auto"> <!-- Ensure content doesn't overflow container -->
            <div class="flex gap-3 items-center grow">
                <img :src="getImgUrl()" @error="defaultImg($event)" class="w-10 h-10 rounded-lg object-cover flex-shrink-0">
                 <!-- Removed link around image as it's not always present -->
                <div class="flex-1 overflow-hidden">
                    <h3 class="font-bold font-large text-lg truncate">
                         {{ model.name }}
                     </h3>
                 </div>
             </div>
         </div>
       </div>
      <div class="flex items-center flex-row gap-2 my-1 mt-3">
        <div class="flex grow items-center text-sm text-gray-600 dark:text-gray-400">
          <i data-feather="hard-drive" class="w-4 h-4 mr-1"></i>
          Local Reference
        </div>
        <div>
          <button v-if="isInstalled" title="Remove Reference (Doesn't delete file)" type="button" @click.stop="handleUninstallClick" :disabled="isProcessing"
            class="button-danger-sm">
             <i data-feather="trash-2" class="w-4 h-4 mr-1"></i> Remove
          </button>
        </div>
      </div>
    </div>

    <!-- STANDARD MODEL VIEW -->
     <div v-if="!model.isCustomModel">
       <div class="flex flex-row items-center gap-3 mb-2">
         <img ref="imgElement" :src="getImgUrl()" @error="defaultImg($event)" class="w-10 h-10 rounded-lg object-cover flex-shrink-0"
           :class="{ 'grayscale': linkNotValid }">
         <h3 class="font-bold font-large text-lg truncate flex-grow">
           {{ model.name }}
         </h3>
         <InteractiveMenu :commands="commandsList" :force_position="2" title="Menu" @click.stop>
         </InteractiveMenu>
       </div>

       <div class="space-y-1 text-sm text-gray-700 dark:text-gray-300" :class="{'opacity-60': linkNotValid}">
         <!-- Details Section -->
         <div class="flex items-center" title="Hugging Face Model Card">
           <i data-feather="link" class="w-4 h-4 mr-2 flex-shrink-0"></i>
           <b class="mr-1 flex-shrink-0">Card:</b>
            <a :href="'https://huggingface.co/'+model.quantizer+'/'+model.name" target="_blank" @click.stop
              class="truncate hover:text-blue-600 dark:hover:text-blue-400 duration-150 underline"
              :class="{'text-red-500 pointer-events-none': linkNotValid}">
               {{ linkNotValid ? 'Link Invalid' : `${model.quantizer}/${model.name}` }}
            </a>
         </div>

          <div class="flex items-center" title="Approximate File Size">
             <i data-feather="file" class="w-4 h-4 mr-2 flex-shrink-0"></i>
             <b class="mr-1">Size:</b>
             <span>{{ fileSize || 'N/A' }}</span>
          </div>

          <div class="flex items-center" title="Model License">
             <i data-feather="key" class="w-4 h-4 mr-2 flex-shrink-0"></i>
             <b class="mr-1">License:</b>
            <span>{{ model.license || 'N/A' }}</span>
          </div>

          <div v-if="model.quantizer && model.quantizer !== 'None' && model.type !== 'transformers'" class="flex items-center" title="Quantizer Profile">
            <i data-feather="user" class="w-4 h-4 mr-2 flex-shrink-0"></i>
            <b class="mr-1">Quantizer:</b>
            <a :href="'https://huggingface.co/'+model.quantizer" target="_blank" rel="noopener noreferrer" @click.stop
              class="truncate hover:text-blue-600 dark:hover:text-blue-400 duration-150 underline">
              {{ model.quantizer }}
            </a>
          </div>

          <div v-if="model.model_creator" class="flex items-center" title="Original Model Creator Profile">
            <i data-feather="users" class="w-4 h-4 mr-2 flex-shrink-0"></i>
             <b class="mr-1">Creator:</b>
            <a :href="model.model_creator_link" target="_blank" rel="noopener noreferrer" @click.stop
              class="truncate hover:text-blue-600 dark:hover:text-blue-400 duration-150 underline">
               {{ model.model_creator }}
            </a>
          </div>

          <div v-if="model.last_commit_time" class="flex items-center" title="Last Update Date">
            <i data-feather="clock" class="w-4 h-4 mr-2 flex-shrink-0"></i>
             <b class="mr-1">Updated:</b>
            <span>{{ formatDate(model.last_commit_time) }}</span>
          </div>

          <div v-if="model.category" class="flex items-center" title="Model Category">
            <i data-feather="grid" class="w-4 h-4 mr-2 flex-shrink-0"></i>
             <b class="mr-1">Category:</b>
             <!-- Assuming category isn't usually a link -->
            <span>{{ model.category }}</span>
          </div>

         <div v-if="model.rank" class="flex items-center" title="Hugging Face Rank (May be outdated)">
             <i data-feather="bar-chart-2" class="w-4 h-4 mr-2 flex-shrink-0"></i>
             <b class="mr-1">Rank:</b>
            <a href="https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard" target="_blank" rel="noopener noreferrer" @click.stop
              class="hover:text-blue-600 dark:hover:text-blue-400 duration-150 underline">
               {{ model.rank }}
             </a>
         </div>
       </div>
     </div>

     <!-- Download/Uninstall Overlay/Progress -->
    <div v-if="isProcessing"
      class="absolute z-10 inset-0 -m-px p-4 shadow-md text-center rounded-lg bg-white/80 dark:bg-gray-800/80 flex justify-center items-center backdrop-blur-sm">
      <div class="relative flex flex-col items-center justify-center w-full h-full">
        <!-- Spinner -->
        <div role="status" class="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
           <svg aria-hidden="true" class="w-16 h-16 text-gray-300 animate-spin dark:text-gray-600 fill-blue-600"
            viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
             <!-- Spinner SVG paths -->
             <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
            <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
           </svg>
           <span class="sr-only">Processing...</span>
         </div>
        <!-- Progress Bar & Info -->
         <div class="absolute bottom-2 left-2 right-2 w-auto bg-white/70 dark:bg-gray-800/70 rounded-lg p-2 backdrop-blur-sm">
          <div class="flex justify-between mb-1 text-xs">
            <span class="font-medium text-blue-700 dark:text-blue-300">{{ progressName }}</span>
            <span v-if="progress > 0" class="font-medium text-blue-700 dark:text-blue-300">{{ Math.floor(progress) }}%</span>
          </div>
          <div v-if="progress > 0" class="w-full bg-gray-200 rounded-full h-1.5 dark:bg-gray-700 mb-1">
            <div class="bg-blue-600 h-1.5 rounded-full" :style="{ width: progress + '%' }"></div>
          </div>
          <div v-if="progress > 0 && total_size > 0" class="flex justify-between text-xs text-blue-600 dark:text-blue-400">
            <span>{{ downloaded_size_computed }}/{{ total_size_computed }}</span>
            <span>{{ speed_computed }}/s</span>
          </div>
           <button @click.stop="handleCancelClick" type="button" title="Cancel Operation"
            class="button-danger-sm w-full mt-2 text-xs">
             Cancel
           </button>
         </div>
      </div>
    </div>

  </div>
</template>

<script>
import { nextTick } from 'vue';
import feather from 'feather-icons';
import filesize from '../plugins/filesize';
import defaultImgPlaceholder from "../assets/default_model.png";
import InteractiveMenu from "@/components/InteractiveMenu.vue";

// Removed axios import as it's not used directly here

export default {
  name: 'ModelEntry',
  components: { InteractiveMenu },
  props: {
    model: { type: Object, required: true },
    isSelected: { type: Boolean, default: false },
    isInstalled: { type: Boolean, default: false },
    isProcessing: { type: Boolean, default: false }, // Received from parent
    // Removed function props like onInstall, onSelected, etc.
    // Add progress props if needed (or rely on isProcessing) - Let's use isProcessing for simplicity first
    progress: { type: Number, default: 0 },
    speed: { type: Number, default: 0 },
    total_size: { type: Number, default: 0 },
    downloaded_size: { type: Number, default: 0 },
    progressName: { type: String, default: 'Processing...'} // Name for the progress bar
  },
  emits: ['select', 'install', 'uninstall', 'cancel-install', 'copy', 'copy-link'], // Declare emitted events
  data() {
    return {
      // Removed local state like installing, uninstalling - use isProcessing prop
      failedToLoad: false, // Keep for image loading errors
      linkNotValid: this.model.error ? true:false, // Determine initial validity (optional) - check model.error field!
    };
  },
  mounted() {
    nextTick(() => {
      feather.replace();
    });
    // Check link validity if needed (could be done in parent too)
    // this.checkLinkValidity();
  },
  updated() {
    // Ensure Feather icons are re-rendered if content changes
    nextTick(() => {
      feather.replace();
    });
  },
  methods: {
    formatDate(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
             // Check if date is valid
             if (isNaN(date.getTime())) {
                 return 'Invalid Date';
             }
            return date.toLocaleDateString(undefined, { year: 'numeric', month: 'short', day: 'numeric' });
        } catch (e) {
            console.error("Error formatting date:", e);
            return 'Invalid Date';
        }
    },
    formatFileSize(sizeInBytes) {
       // Using the imported filesize library for consistency
       return filesize(sizeInBytes);
    },
    getImgUrl() {
      // Prefer model icon, fallback to default
      return this.model.icon || defaultImgPlaceholder;
    },
    defaultImg(event) {
      this.failedToLoad = true;
      event.target.src = defaultImgPlaceholder;
    },
    // --- Event Handlers ---
    handleClick() {
      // Prevent selection if busy, not installed, or already selected
      if (this.isProcessing || !this.isInstalled || this.isSelected) {
          console.log(`Click ignored: processing=${this.isProcessing}, installed=${this.isInstalled}, selected=${this.isSelected}`);
        return;
      }
      console.log("Emitting select event for:", this.model.name);
      this.$emit('select', this.model); // Emit 'select' with the model data object
    },
    handleInstallClick() {
        if (this.isProcessing) return;
        console.log("Emitting install event for:", this.model.name);
        // Pass necessary data for the parent to handle
        this.$emit('install', { model: this.model });
    },
    handleUninstallClick() {
        if (this.isProcessing || !this.isInstalled) return;
         console.log("Emitting uninstall event for:", this.model.name);
        // Pass necessary data
        this.$emit('uninstall', { model: this.model });
    },
    handleCancelClick() {
       // Parent handles the logic, just emit the event
        console.log("Emitting cancel-install event for:", this.model.name);
        // Parent needs details to cancel, potentially pass model or identifier
       this.$emit('cancel-install', { model: this.model });
    },
    handleCopyClick() {
        this.$emit('copy', { model: this.model });
    },
    handleCopyLinkClick() {
        this.$emit('copy-link', { model: this.model });
    },
    // --- Other Methods ---
    checkLinkValidity() {
      // Optional: If you need client-side link checking (less reliable than backend)
      // This might involve trying to fetch HEAD or using other heuristics
      // For now, assume the backend provides validity info or handle errors during install
      // Example: Set this.linkNotValid = true if model has an error property
       this.linkNotValid = !!this.model.error; // Check if model object has an error field
    },
  },
  computed: {
    computedClasses() {
      const classes = [];

      // Base classes for all entries (optional)
      // classes.push('transition-all duration-150 ease-in-out');

      // State: Processing (takes precedence)
      if (this.isProcessing) {
        classes.push('opacity-70 pointer-events-none');
      }
      // State: Selected and Installed
      else if (this.isSelected && this.isInstalled) {
         // Use prominent styles for the selected item
         classes.push('border-[3px] border-blue-500 dark:border-blue-400 ring-2 ring-blue-300 dark:ring-blue-600 ring-offset-1 dark:ring-offset-gray-800');
         classes.push('bg-blue-50 dark:bg-blue-900/50'); // Highlight background
         classes.push('cursor-default'); // Already selected, no need for pointer
      }
      // State: Installed but Not Selected
      else if (this.isInstalled && !this.isSelected) {
         classes.push('border-gray-200 dark:border-gray-700'); // Standard border
         classes.push('hover:border-blue-400 dark:hover:border-blue-600'); // Hover effect
         classes.push('hover:bg-blue-50/50 dark:hover:bg-blue-900/20'); // Hover background
         classes.push('cursor-pointer'); // Indicate it's clickable
      }
      // State: Not Installed
      else if (!this.isInstalled) {
          classes.push('border-dashed border-gray-300 dark:border-gray-600');
          classes.push('opacity-80'); // Slightly faded
          // Optionally make it non-clickable visually if needed, handled by click logic too
          // classes.push('pointer-events-none');
      }

      // State: Link Invalid (can be combined with other states)
      if (this.linkNotValid && !this.isProcessing) {
         // Use a subtle error indicator, doesn't override selection border necessarily
         classes.push('border-l-4 border-l-red-500'); // Red left border for error
         // Or override the main border:
         // classes = classes.filter(c => !c.startsWith('border-') || c.startsWith('border-l-')); // Remove other borders first
         // classes.push('border-red-400 dark:border-red-600');
      }

      return classes.join(' ');
    },
    isDisabled() {
        // Used for ARIA state and potentially disabling clicks further
        return this.isProcessing || !this.isInstalled;
    },
    commandsList() {
       // Dynamically build the menu based on state
      let menu = [];

      if (!this.isInstalled) {
        menu.push({ name: "Install", icon: "feather:download", value: this.handleInstallClick, disabled: this.isProcessing || this.linkNotValid });
      } else {
         // Options for installed models
         menu.push({ name: "Uninstall", icon: "feather:trash-2", value: this.handleUninstallClick, disabled: this.isProcessing });
         // Add reload only if it's the selected model (or always allow?)
         if (this.isSelected) {
            // Assuming reload means re-selecting it to trigger potential backend actions
            menu.push({ name: "Reload", icon: "feather:refresh-cw", value: this.handleClick, disabled: this.isProcessing });
         }
      }

      // Common actions
       menu.push({ name: "Copy Info", icon: "feather:copy", value: this.handleCopyClick });
       if (!this.model.isCustomModel) {
           menu.push({ name: "Copy Link", icon: "feather:clipboard", value: this.handleCopyLinkClick });
       }

      return menu;
    },
    fileSize() {
       // Prioritize variant size if available, format using library
      const variant = this.model?.variants?.[0]; // Assume first variant for display size
      const size = variant?.size ?? this.model?.size; // Fallback to model size if no variant/variant size
      return size ? this.formatFileSize(size) : 'N/A';
    },
    // Computed properties for progress bar clarity
    speed_computed() { return this.formatFileSize(this.speed) + '/s'; },
    total_size_computed() { return this.formatFileSize(this.total_size); },
    downloaded_size_computed() { return this.formatFileSize(this.downloaded_size); },
  },
  watch: {
    // Watch the isProcessing prop to potentially update UI or internal state if needed
    isProcessing(newValue, oldValue) {
        console.log(`Model ${this.model.name} processing state changed to: ${newValue}`);
        nextTick(() => { feather.replace(); }); // Ensure icons update if state changes visibility
    },
    // Watch the model object itself for changes like 'error' if the parent updates it
    'model.error': function(newError) {
        this.linkNotValid = !!newError;
    }
  }
};
</script>

<style scoped>
/* Add any specific styles for ModelEntry here if needed */
/* Example: Style for disabled state */
[aria-disabled="true"] {
  cursor: not-allowed;
  /* Optional: Slightly different visual indication */
  /* filter: grayscale(50%); */
}
/* Consistent button styles */
.button-base-sm {
     @apply inline-flex items-center justify-center px-2 py-1 border border-transparent text-xs font-medium rounded shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:opacity-50 transition-colors duration-150;
}
.button-primary-sm { @apply button-base-sm text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500; }
.button-success-sm { @apply button-base-sm text-white bg-green-600 hover:bg-green-700 focus:ring-green-500; }
.button-danger-sm { @apply button-base-sm text-white bg-red-600 hover:bg-red-700 focus:ring-red-500; }
.button-secondary-sm { @apply button-base-sm text-gray-700 dark:text-gray-200 bg-gray-200 dark:bg-gray-700 hover:bg-gray-300 dark:hover:bg-gray-600 focus:ring-gray-500; }

/* Ensure feather icons are vertically aligned */
[data-feather] {
    @apply inline-block align-middle w-4 h-4; /* Default size */
}
</style>