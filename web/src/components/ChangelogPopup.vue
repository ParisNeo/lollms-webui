<template>
  <div v-if="showChangelogPopup" 
       class="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 transition-opacity duration-300"
       :class="{ 'opacity-0': !showChangelogPopup, 'opacity-100': showChangelogPopup }">
    <div class="bg-white rounded-xl w-[95%] max-w-6xl max-h-[90vh] flex flex-col shadow-2xl transform transition-all duration-300"
         :class="{ 'scale-95': !showChangelogPopup, 'scale-100': showChangelogPopup }">
      <div class="changelog-header">
        <h2 class="header-title">What's New in LoLLMs</h2>
        <button class="close-btn" @click="closePopup">×</button>
      </div>
      <div class="changelog-content" v-html="parsedChangelogContent"></div>
      <div class="changelog-footer">
        <button class="action-btn" @click="handleUnderstand">
          I understood
        </button>
      </div>
    </div>
  </div>
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
      currentVersion: '0.0.0'
    }
  },
  computed: {
    parsedChangelogContent() {
      return DOMPurify.sanitize(marked(this.changelogContent));
    }
  },
  async mounted() {
    await this.checkChangelogUpdate();
  },
  methods: {
    async checkChangelogUpdate() {
      try {
        const changelogResponse = await axios.get("/get_changelog");
        this.changelogContent = changelogResponse.data;
        
        let res = await axios.get('/get_lollms_webui_version', {});
        if (res) {
          res = res.data
          if(res.version_type != "") {
            this.$store.state.version = `${res.version_main}.${res.version_secondary} ${res.version_type} (${res.version_codename})`
          } else {
            this.$store.state.version = `${res.version_main}.${res.version_secondary} (${res.version_codename})`
          }
        }
        this.currentVersion = this.$store.state.version
        
        const lastViewedResponse = await axios.get("/get_last_viewed_changelog_version");
        const lastViewedVersion = lastViewedResponse.data;
        
        this.$nextTick(() => {
          if (this.$store.state.config) {
            if (this.currentVersion !== lastViewedVersion && this.$store.state.config.app_show_changelogs) {
              this.showChangelogPopup = true;
            }
          } else {
            const unwatch = this.$watch('$store.state.config', (newConfig) => {
              if (newConfig) {
                if (this.currentVersion !== lastViewedVersion && newConfig.app_show_changelogs) {
                  this.showChangelogPopup = true;
                }
                unwatch();
              }
            });
          }
        });
      } catch (error) {
        console.error("Error checking changelog:", error);
      }
    },
    async handleUnderstand() {
      try {
        await axios.post("/set_last_viewed_changelog_version", {
          client_id: this.$store.state.client_id,
          version: this.currentVersion
        });
        this.closePopup();
      } catch (error) {
        console.error("Error setting changelog version:", error);
      }
    },
    closePopup() {
      this.showChangelogPopup = false;
    }
  }
}
</script>

<style scoped>
/* Header Styles */
.changelog-header {
  @apply p-6 flex justify-between items-center;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-top-left-radius: 0.75rem;
  border-top-right-radius: 0.75rem;
}

.header-title {
  @apply text-3xl font-bold text-white;
  letter-spacing: 0.05em;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.close-btn {
  @apply text-white text-3xl font-light w-10 h-10 flex items-center justify-center;
  transition: all 0.2s ease-in-out;
}

.close-btn:hover {
  @apply text-gray-200 bg-white/10;
  border-radius: 50%;
  transform: rotate(90deg);
}

/* Content Styles */
.changelog-content {
  @apply p-6 overflow-y-auto flex-1;
  font-family: 'Inter', sans-serif;
  color: #1f2937;
}

.changelog-content :deep(h1) {
  @apply text-3xl font-bold mt-8 mb-4;
  color: #1e40af;
}

.changelog-content :deep(h2) {
  @apply text-2xl font-semibold mt-6 mb-3;
  color: #1e40af;
}

.changelog-content :deep(h3) {
  @apply text-xl font-medium mt-4 mb-2;
  color: #1e40af;
}

.changelog-content :deep(p) {
  @apply mb-4 leading-relaxed;
}

.changelog-content :deep(ul),
.changelog-content :deep(ol) {
  @apply pl-8 mb-4;
  list-style-position: outside;
}

.changelog-content :deep(ul) {
  @apply list-disc;
}

.changelog-content :deep(ol) {
  @apply list-decimal;
}

.changelog-content :deep(code) {
  @apply px-1 py-0.5 text-sm bg-gray-100 rounded;
  font-family: 'Fira Code', monospace;
  color: #9d174d;
}

.changelog-content :deep(pre) {
  @apply p-4 mb-4 bg-gray-50 rounded-lg;
  box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
  font-family: 'Fira Code', monospace;
  color: #374151;
}

.changelog-content :deep(blockquote) {
  @apply pl-4 py-2 my-4 border-l-4 border-blue-200 bg-blue-50;
  color: #4b5563;
  font-style: italic;
}

/* Footer Styles */
.changelog-footer {
  @apply p-6 border-t border-gray-200 flex justify-end;
}

.action-btn {
  @apply px-6 py-2 text-white rounded-lg;
  background: linear-gradient(45deg, #10b981 0%, #14b8a6 100%);
  transition: all 0.3s ease;
}

.action-btn:hover {
  @apply scale-105;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

.action-btn:active {
  @apply scale-95;
}
</style>