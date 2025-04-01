<template>
  <div class="app-card relative flex flex-col"
       :class="{
           'border-2 border-blue-500 dark:border-blue-400 shadow-lg': isActive,
           'border-blue-200 dark:border-blue-700': !isActive,
           'opacity-50 pointer-events-none': isProcessing
       }"
       :title="personality.tool_description || personality.description || personality.name"
       @click="handleSelect"> <!-- Main click selects if mounted -->

      <!-- Processing Overlay -->
      <div v-if="isProcessing" class="absolute inset-0 bg-blue-400 dark:bg-blue-700 bg-opacity-50 dark:bg-opacity-50 flex items-center justify-center rounded-lg z-20">
          <svg aria-hidden="true" class="w-8 h-8 text-blue-200 animate-spin dark:text-blue-600 fill-blue-600 dark:fill-blue-300" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg"> <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor"/> <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill"/> </svg>
      </div>

      <!-- Star Button -->
      <button
          @click.stop="toggleStar"
          class="absolute top-2 right-2 svg-button text-yellow-400 hover:text-yellow-500 dark:text-yellow-500 dark:hover:text-yellow-400 z-10"
          :title="isStarred ? 'Unstar' : 'Star'">
          <i v-if="isStarred" data-feather="star" class="w-5 h-5 fill-current"></i>
          <i v-else data-feather="star" class="w-5 h-5 stroke-current"></i>
      </button>

      <div class="flex-grow flex flex-col"> <!-- Added flex flex-col for proper height growth -->
          <!-- Header: Icon, Name, Author etc. -->
          <div class="flex items-start mb-3">
               <img :src="getPersonalityIconUrl(personality.avatar)" @error="handleImgError" alt="Personality Icon"
                    class="w-16 h-16 rounded-lg object-cover mr-4 flex-shrink-0 border border-blue-200 dark:border-blue-600 shadow-sm">
               <div class="flex-grow overflow-hidden min-w-0">
                   <h3 class="font-bold text-lg text-blue-800 dark:text-blue-100 truncate" :title="personality.name">{{ personality.name }}</h3>
                   <p v-if="personality.author" class="text-xs text-blue-500 dark:text-blue-400 truncate" :title="`By ${personality.author}`">
                       By {{ personality.author }}
                   </p>
                   <p v-if="personality.version" class="text-xs text-blue-500 dark:text-blue-400" :title="`Version: ${personality.version}`">
                       v{{ personality.version }}
                   </p>
                    <p v-if="personality.category" class="text-xs text-blue-500 dark:text-blue-400 truncate" :title="`Category: ${personality.category}`">
                       {{ personality.category }}
                   </p>
               </div>
                <!-- Help Icon -->
               <button v-if="personality.help" @click.stop="showHelp" class="ml-2 svg-button text-blue-500 hover:text-blue-600 dark:text-blue-400 dark:hover:text-blue-300 flex-shrink-0 -mr-1" title="Help">
                   <i data-feather="help-circle" class="h-5 w-5"></i>
               </button>
          </div>

           <!-- Dates -->
           <div class="text-xs text-blue-400 dark:text-blue-500 mb-3 space-y-1">
               <p v-if="personality.creation_date">Created: {{ formatDate(personality.creation_date) }}</p>
               <p v-if="personality.last_update_date">Updated: {{ formatDate(personality.last_update_date) }}</p>
           </div>

          <!-- Description -->
          <div class="mb-4 flex-grow"> <!-- Added flex-grow -->
              <p class="text-sm text-blue-700 dark:text-blue-300 h-20 overflow-y-auto scrollbar" v-html="renderedDescription"></p>
          </div>

           <!-- Language Selector (if applicable and not mounted) -->
           <div v-if="select_language && personality.languages && personality.languages.length > 0 && !isMounted" class="mb-3 mt-auto">
               <label :for="'lang-select-' + personalityId" class="label mb-1">Language:</label>
               <select :id="'lang-select-' + personalityId" v-model="selectedLanguage" @click.stop
                       class="input w-full text-sm"> <!-- Adjusted input class for select -->
                    <option value="">Default</option>
                    <option v-for="lang in personality.languages" :key="lang" :value="lang">{{ lang }}</option>
               </select>
           </div>

          <!-- Footer Actions -->
          <div class="mt-auto pt-3 border-t border-blue-200 dark:border-blue-700">
              <div class="flex justify-between items-center">
                  <!-- Mount/Unmount/Remount Buttons -->
                  <div class="flex space-x-1">
                      <button v-if="!isMounted" @click.stop="emitAction('mount')"
                              class="btn btn-sm btn-success" title="Mount personality">
                          <div class="flex items-center"><i data-feather="play" class="w-3 h-3 mr-1 stroke-current"></i>Mount</div>
                      </button>
                      <button v-else @click.stop="emitAction('unmount')"
                              class="btn btn-sm bg-red-600 hover:bg-red-700 text-white focus:ring-red-500 dark:bg-red-700 dark:hover:bg-red-600 dark:focus:ring-red-600" title="Unmount personality">
                           <div class="flex items-center"><i data-feather="stop-circle" class="w-3 h-3 mr-1 stroke-current"></i>Unmount</div>
                      </button>
                      <button v-if="isMounted" @click.stop="emitAction('remount')"
                              class="svg-button p-1" title="Remount personality">
                           <i data-feather="refresh-cw" class="w-4 h-4"></i>
                      </button>
                  </div>

                  <!-- Other Actions Menu -->
                  <InteractiveMenu :commands="commandsList" :force_position="2" title="More actions" class="p-1">
                       <template #trigger>
                           <button class="svg-button p-1">
                              <i data-feather="more-vertical" class="w-5 h-5"></i>
                          </button>
                      </template>
                  </InteractiveMenu>
              </div>
          </div>
      </div> <!-- End of flex-grow flex flex-col -->


      <!-- Help Popup -->
      <div v-if="showHelpPopup" @click.stop class="fixed inset-0 bg-black bg-opacity-70 flex justify-center items-center z-50 p-4">
          <div class="card w-full max-w-2xl max-h-[80vh] flex flex-col"> <!-- Using card class -->
              <div class="flex justify-between items-center mb-4 border-b pb-2 border-blue-200 dark:border-blue-600">
                  <h2 class="text-xl font-bold text-blue-800 dark:text-blue-100">Help: {{ personality.name }}</h2>
                  <button @click="closeHelp" class="svg-button hover:text-red-600 dark:hover:text-red-500 p-1">
                       <i data-feather="x" class="w-5 h-5"></i>
                  </button>
              </div>
              <div class="flex-grow overflow-y-auto scrollbar prose-blue max-w-none pr-2"> <!-- Added prose-blue and scrollbar -->
                   <div v-html="renderedHelp"></div>
              </div>
               <div class="mt-4 pt-4 border-t border-blue-200 dark:border-blue-600 text-right">
                   <button @click="closeHelp" class="btn btn-primary">Close</button>
               </div>
          </div>
      </div>
  </div>
</template>

<script>
import feather from 'feather-icons';
import { marked } from 'marked';
import DOMPurify from 'dompurify';
import botImgPlaceholder from "@/assets/logo.png"; // Adjust path if needed
import InteractiveMenu from "@/components/InteractiveMenu.vue"; // Adjust path if needed
import { nextTick } from 'vue';

export default {
  name: 'PersonalityEntry',
  components: {
      InteractiveMenu
  },
  props: {
      personality: { type: Object, required: true },
      select_language: { type: Boolean, default: false },
      isActive: { type: Boolean, default: false },
      full_path: { type: String, required: true },
      isMounted: { type: Boolean, default: false },
      isProcessing: { type: Boolean, default: false },
      isStarred: { type: Boolean, default: false },
      baseUrl: { type: String, default: '' },
  },
  emits: [
      'select', 'mount', 'unmount', 'remount', 'edit', 'copy-to-custom',
      'reinstall', 'settings', 'copy-personality-name', 'open-folder', 'error',
      'toggle-star'
  ],
  data() {
      return {
          // Initialize selectedLanguage based on the prop passed during creation
          selectedLanguage: this.personality.language || '',
          showHelpPopup: false,
          renderedHelp: '',
      };
  },
  computed: {
      personalityId() {
          return this.personality.id || this.full_path.replace(/[/:]/g, '-');
      },
      renderedDescription() {
          if (!this.personality.description) return 'No description available.';
          const containsHtml = /<[a-z][\s\S]*>/i.test(this.personality.description);
          if (containsHtml) {
              // Use DOMPurify to sanitize if it looks like HTML
              return DOMPurify.sanitize(this.personality.description);
          } else {
              // Treat as plain text (or Markdown if you prefer - uncomment marked below)
              // return marked.parse(this.personality.description); // If you want markdown rendering
              return this.escapeHtml(this.personality.description).replace(/\n/g, '<br>'); // Safely display plain text with line breaks
          }
      },
      commandsList() {
          let main_menu = [];

          if (this.isMounted) {
               // Pass the method reference directly
              main_menu.push({ name: "unmount", icon: "feather:stop-circle", is_file: false, value: this.emitUnmount });
          } else {
              main_menu.push({ name: "mount", icon: "feather:play", is_file: false, value: this.emitMount });
          }

          if (this.isMounted) {
              main_menu.push({ name: "remount", icon: "feather:refresh-cw", is_file: false, value: this.emitRemount });
          }

          main_menu.push({ name: "reinstall", icon: "feather:download-cloud", is_file: false, value: this.emitReinstall });

          // Check if personality belongs to custom_personalities category
          // Assuming full_path indicates the category like "personalities_zoo/animals/cat" or "custom_personalities/my_bot"
          const isCustom = this.full_path.startsWith('custom_personalities/') || this.personality.category === "custom_personalities"; // Added check for category prop too

          if (isCustom) {
              main_menu.push({ name: "edit", icon: "feather:edit-3", is_file: false, value: this.emitEdit });
          } else {
              main_menu.push({ name: "Copy to custom personalities", icon: "feather:copy", is_file: false, value: this.emitCopyToCustom });
          }

          if (this.isActive && this.personality.has_scripts) {
              main_menu.push({ name: "settings", icon: "feather:settings", is_file: false, value: this.emitSettings });
          }

          main_menu.push({ name: "Open Folder", icon: "feather:folder", is_file: false, value: this.emitOpenFolder });
          main_menu.push({ name: "Copy Name", icon: "feather:clipboard", is_file: false, value: this.emitCopyName });

          return main_menu;
      },
      // Computed property to group reactive sources for the watcher
      watchedFeatherProps() {
          // Make sure all relevant reactive properties that affect feather icons are included
          return [this.isActive, this.isMounted, this.isProcessing, this.isStarred, this.showHelpPopup, this.commandsList];
      }
  },
  watch: {
      // Watch the incoming prop and update local data if it changes
      'personality.language'(newVal) {
          const lang = newVal || '';
          if (this.selectedLanguage !== lang) {
              this.selectedLanguage = lang;
          }
      },
      // Watch the computed property grouping relevant states
      watchedFeatherProps: {
          handler() {
              this.updateFeatherIcons();
          },
          deep: true, // Necessary if watching objects/arrays within the computed prop
          flush: 'post' // Run after DOM updates
      }
  },
  methods: {
      // Helper to escape HTML entities for safer rendering of plain text
      escapeHtml(unsafe) {
        if (!unsafe) return '';
        return unsafe
             .replace(/&/g, "&")
             .replace(/</g, "<")
             .replace(/>/g, ">")
             .replace(/"/g, "\"")
             .replace(/'/g, "'");
      },
      updateFeatherIcons() {
          nextTick(() => {
             try {
                 feather.replace();
             } catch (e) {
                 console.error("Feather icons replacement failed:", e);
             }
          });
      },
      formatDate(dateString) {
          if (!dateString) return '';
          try {
              const options = { year: 'numeric', month: 'short', day: 'numeric' };
              return new Date(dateString).toLocaleDateString(undefined, options);
          } catch (e) {
              console.error("Error formatting date:", e);
              return dateString;
          }
      },
      getPersonalityIconUrl(avatarPath) {
          if (!avatarPath) return botImgPlaceholder;
          // Ensure the base URL doesn't end with a slash if the path starts with one
          const effectiveBaseUrl = this.baseUrl.endsWith('/') ? this.baseUrl.slice(0, -1) : this.baseUrl;
          // Ensure the path starts with a slash
          const effectivePath = avatarPath.startsWith('/') ? avatarPath : `/${avatarPath}`;
          return `${effectiveBaseUrl}${effectivePath}`;
      },
      handleImgError(event) {
          event.target.src = botImgPlaceholder;
          this.$emit('error', { type: 'image_load', message: 'Failed to load personality icon', event });
      },
      handleSelect() {
          // Allow selection regardless of mounted state, parent decides what to do
          // if (!this.isMounted) {
          //     console.log("Personality must be mounted to be selected.");
          //     // Optionally add toast notification here if integrated
          //     // return; // Prevent selection if not mounted - uncomment if needed
          // }
          this.$emit('select', { personality: { ...this.personality, language: this.selectedLanguage } });

      },
      // Emit helper that includes current language state
      emitAction(actionName) {
          // Ensure personality data is cloned and language is updated
          const payload = {
              personality: {
                  ...this.personality,
                  language: this.selectedLanguage || this.personality.language || '' // Use selected, fallback to original, then empty
              }
          };
          this.$emit(actionName, payload);
      },
      // Specific emit methods for clarity in computed properties/template
      toggleStar() { this.emitAction('toggle-star'); },
      emitMount() { this.emitAction('mount'); },
      emitUnmount() { this.emitAction('unmount'); },
      emitRemount() { this.emitAction('remount'); },
      emitReinstall() { this.emitAction('reinstall'); },
      emitEdit() { this.emitAction('edit'); },
      emitCopyToCustom() { this.emitAction('copy-to-custom'); },
      emitSettings() { this.emitAction('settings'); },
      emitOpenFolder() { this.emitAction('open-folder'); },
      emitCopyName() { this.emitAction('copy-personality-name'); },

      // Help Popup Logic
      showHelp() {
          if (this.personality.help) {
              marked.setOptions({
                  gfm: true, // Enable GitHub Flavored Markdown
                  breaks: true, // Convert single line breaks to <br>
                  mangle: false, // Deprecated/Removed in newer Marked - keep false or remove
                  headerIds: false // Don't add IDs to headers automatically
               });
              try {
                  const rawHtml = marked.parse(this.personality.help);
                  // Sanitize the HTML generated from Markdown
                  this.renderedHelp = DOMPurify.sanitize(rawHtml);
                  this.showHelpPopup = true;
                  this.updateFeatherIcons(); // Update icons after showing popup DOM updates
              } catch(e) {
                  console.error("Error parsing or sanitizing help markdown:", e);
                  this.renderedHelp = "<p>Error displaying help content.</p>";
                   this.showHelpPopup = true;
              }

          }
      },
      closeHelp() {
          this.showHelpPopup = false;
      },
  },
  mounted() {
      // Initial icon render on mount
      this.updateFeatherIcons();
       // Ensure initial selected language respects the prop
      this.selectedLanguage = this.personality.language || '';
  },
};
</script>

