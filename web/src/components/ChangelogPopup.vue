<template>
  <transition name="fade">
    <div v-if="showChangelogPopup"
         class="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[100] transition-opacity duration-300"
         :class="{ 'opacity-0 pointer-events-none': !showChangelogPopup, 'opacity-100': showChangelogPopup }">

      <div class="panels-color rounded-lg w-[95%] max-w-4xl max-h-[90vh] flex flex-col shadow-2xl overflow-hidden transform transition-all duration-300 ease-out border border-blue-300 dark:border-blue-600"
           :class="{ 'opacity-0 scale-95': !showChangelogPopup, 'opacity-100 scale-100': showChangelogPopup }">

        <!-- Header -->
        <div class="flex justify-between items-center p-4 px-6 border-b border-blue-300 dark:border-blue-600 flex-shrink-0 unicolor-panels-color"> 
          <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100">What's New</h2>
          <button class="svg-button" @click="closePopup" aria-label="Close Changelog">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
              <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <!-- Content -->
        <!-- Added scrollbar class from theme and slightly more padding -->
        <div class="p-6 md:p-8 flex-grow overflow-y-auto scrollbar text-blue-900 dark:text-blue-200">
             <!-- Apply prose classes if Tailwind Typography plugin is used for better markdown styling -->
             <!-- Or ensure h*, p, ul, ol, li, code, blockquote styles from the theme are sufficient -->
            <div class="prose prose-blue dark:prose-invert max-w-none" v-html="parsedChangelogContent">
            </div>
        </div>

        <!-- Footer -->
        <div class="flex justify-end p-4 px-6 border-t border-blue-300 dark:border-blue-600 flex-shrink-0 unicolor-panels-color"> <!-- Used unicolor for footer bg -->
          <button class="btn btn-primary" @click="handleUnderstand">
            Got it
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
import axios from 'axios';
import { marked } from 'marked';
import DOMPurify from 'dompurify';

export default {
  name: 'ChangelogPopup',
  data() {
    return {
      showChangelogPopup: false,
      changelogContent: '',
      currentVersion: '0.0.0' // Initialize with a default
    }
  },
  computed: {
    parsedChangelogContent() {
      // Basic configuration for marked - adjust if needed
      const markedOptions = {
        breaks: true, // Interpret carriage returns as <br>
        gfm: true,    // Use GitHub Flavored Markdown
      };
      const rawHtml = marked(this.changelogContent, markedOptions);
      return DOMPurify.sanitize(rawHtml);
    }
  },
  async mounted() {
    await this.checkChangelogUpdate();
  },
  methods: {
    async fetchVersion() {
      try {
        const res = await axios.get('/get_lollms_webui_version');
        if (res && res.data) {
          const { version_main, version_secondary, version_type, version_codename } = res.data;
          let versionString = `${version_main}.${version_secondary}`;
          if (version_type) {
            versionString += ` ${version_type}`;
          }
          if (version_codename) {
            versionString += ` (${version_codename})`;
          }
          this.$store.commit('setVersion', versionString); // Assuming a mutation exists
          this.currentVersion = versionString;
          return versionString;
        }
      } catch (error) {
        console.error("Error fetching LoLLMs version:", error);
      }
      // Fallback if fetch fails or store isn't ready yet
      return this.$store.state.version || '0.0.0';
    },
    async checkChangelogUpdate() {
      try {
        // Fetch changelog first
        const changelogResponse = await axios.get("/get_changelog");
        this.changelogContent = changelogResponse.data || '*No changelog content found.*'; // Provide fallback content

        // Fetch current version
        const currentVersion = await this.fetchVersion();

        // Fetch last viewed version
        const lastViewedResponse = await axios.get("/get_last_viewed_changelog_version");
        const lastViewedVersion = lastViewedResponse.data; // Assuming this returns a string directly

        // Ensure config is loaded before checking visibility
        const checkVisibility = (config) => {
          if (config && config.app_show_changelogs && currentVersion !== lastViewedVersion && currentVersion !== '0.0.0') {
             this.showChangelogPopup = true;
          }
        };

        if (this.$store.state.config) {
          checkVisibility(this.$store.state.config);
        } else {
          // Watch for config changes if not yet available
          const unwatch = this.$watch('$store.state.config', (newConfig) => {
            if (newConfig) {
              checkVisibility(newConfig);
              unwatch(); // Stop watching once config is loaded
            }
          }, { immediate: false }); // Don't run immediately, wait for change
        }

      } catch (error) {
        console.error("Error checking changelog:", error);
        // Optionally inform the user or log centrally
      }
    },
    async handleUnderstand() {
      try {
        await axios.post("/set_last_viewed_changelog_version", {
          client_id: this.$store.state.client_id, // Ensure client_id is available
          version: this.currentVersion
        });
        this.closePopup();
      } catch (error) {
        console.error("Error setting last viewed changelog version:", error);
        // Optionally inform the user? Maybe just close the popup anyway.
        this.closePopup(); // Close even if the API call fails
      }
    },
    closePopup() {
      this.showChangelogPopup = false;
    }
  }
}
</script>

<style scoped>
/* Overlay */
.fixed.inset-0 {
  /* Slightly lighter overlay */
  background-color: rgba(0, 0, 0, 0.4);
}

/* Modal Container */
.bg-white {
  max-width: 56rem; /* Adjusted max-width (equivalent to max-w-5xl, slightly smaller than 6xl) */
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04); /* Softer shadow (like shadow-lg) */
}

/* Header Styles */
.changelog-header {
  @apply p-4 flex justify-between items-center border-b border-gray-200 bg-gray-50; /* Lighter background, simple border */
  border-top-left-radius: 0.5rem; /* Match rounded-lg */
  border-top-right-radius: 0.5rem; /* Match rounded-lg */
}

.header-title {
  @apply text-xl font-semibold text-gray-800; /* Smaller, standard weight, dark gray text */
}

.close-btn {
  @apply p-1 text-gray-500 rounded-full transition-colors duration-150;
}

.close-btn:hover {
  @apply text-gray-700 bg-gray-200; /* Simple hover effect */
}

/* Content Styles */
.changelog-content {
  @apply p-6 overflow-y-auto flex-1 text-gray-700; /* Standard text color */
  font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; /* Use system font stack */
  line-height: 1.6; /* Improved readability */
}

/* Markdown Element Styling (using :deep or >>> for scoped styles) */
.changelog-content :deep(h1),
.changelog-content :deep(h2),
.changelog-content :deep(h3),
.changelog-content :deep(h4),
.changelog-content :deep(h5),
.changelog-content :deep(h6) {
  @apply font-semibold text-gray-800 mb-3 mt-5 first:mt-0;
}

.changelog-content :deep(h1) { @apply text-2xl border-b pb-2 mb-4; }
.changelog-content :deep(h2) { @apply text-xl border-b pb-1 mb-3; }
.changelog-content :deep(h3) { @apply text-lg; }
.changelog-content :deep(h4) { @apply text-base; }

.changelog-content :deep(p) {
  @apply mb-4;
}

.changelog-content :deep(ul),
.changelog-content :deep(ol) {
  @apply pl-6 mb-4;
}

.changelog-content :deep(li) {
  @apply mb-1;
}

.changelog-content :deep(ul) {
  @apply list-disc;
}

.changelog-content :deep(ol) {
  @apply list-decimal;
}

.changelog-content :deep(code) {
  @apply px-1 py-0.5 text-sm bg-gray-100 text-gray-800 rounded border border-gray-200; /* More subtle code style */
  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace; /* Standard mono font stack */
}

.changelog-content :deep(pre) {
  @apply p-4 mb-4 bg-gray-50 rounded border border-gray-200 overflow-x-auto text-sm; /* Subtle pre block */
  font-family: Consolas, Monaco, 'Andale Mono', 'Ubuntu Mono', monospace;
}
.changelog-content :deep(pre) code {
    @apply bg-transparent border-none p-0 text-sm; /* Reset code style inside pre */
}

.changelog-content :deep(blockquote) {
  @apply pl-4 py-2 my-4 border-l-4 border-gray-300 bg-gray-50 text-gray-600 italic; /* Muted blockquote */
}

.changelog-content :deep(a) {
 @apply text-blue-600 hover:text-blue-800 hover:underline; /* Standard link styling */
}

/* Footer Styles */
.changelog-footer {
  @apply p-4 border-t border-gray-200 flex justify-end bg-gray-50; /* Lighter background */
  border-bottom-left-radius: 0.5rem; /* Match rounded-lg */
  border-bottom-right-radius: 0.5rem; /* Match rounded-lg */
}

.action-btn {
  @apply px-5 py-2 text-sm font-medium text-white bg-blue-600 rounded-md transition-colors duration-150;
  /* Standard primary button style */
}

.action-btn:hover {
  @apply bg-blue-700; /* Darken on hover */
}

.action-btn:focus {
  @apply outline-none ring-2 ring-offset-2 ring-blue-500; /* Focus state */
}

.action-btn:active {
  @apply bg-blue-800; /* Slightly darker on active */
}

</style>