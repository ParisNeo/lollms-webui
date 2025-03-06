<template>
  <div v-if="showChangelogPopup" class="changelog-popup-overlay">
    <div class="changelog-popup">
      <div class="changelog-header">
        <h2>What's New in LoLLMs</h2>
        <button class="close-button" @click="closePopup">×</button>
      </div>
      <div class="changelog-content markdown-body" v-html="parsedChangelogContent"></div>
      <div class="changelog-footer">
        <button class="understood-button" @click="handleUnderstand">
          I understood
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import { marked } from 'marked';
import DOMPurify from 'dompurify'; // For security

import { nextTick } from 'vue'
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
      // Convert markdown to HTML and sanitize
      return DOMPurify.sanitize(marked(this.changelogContent));
    }
  },
  async mounted() {
    await this.checkChangelogUpdate();
  },
  methods: {
    async checkChangelogUpdate() {
      try {
        // Get current changelog
        const changelogResponse = await axios.get("/get_changelog");
        this.changelogContent = changelogResponse.data;
        
        // Extract version from changelog
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
        console.log("checkChangelogUpdate")
        console.log(this.$store.state.version)
        
        // Get last viewed version
        const lastViewedResponse = await axios.get("/get_last_viewed_changelog_version");
        const lastViewedVersion = lastViewedResponse.data;
        
        // Show popup if versions don't match
                  

        this.$nextTick(() => {
          if (this.$store.state.config) {
            if (this.currentVersion !== lastViewedVersion && this.$store.state.config.app_show_changelogs) {
              console.log("Showing changelog");
              this.showChangelogPopup = true;
            }
          } else {
            // If config is not loaded yet, you can set up a watcher or retry after a delay
            const unwatch = this.$watch('$store.state.config', (newConfig) => {
              if (newConfig) {
                if (this.currentVersion !== lastViewedVersion && newConfig.app_show_changelogs) {
                  console.log("Showing changelog");
                  this.showChangelogPopup = true;
                }
                unwatch(); // Stop watching once the config is loaded
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
.changelog-popup-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.changelog-popup {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
}

.changelog-header {
  padding: 1rem;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.changelog-content {
  padding: 1rem;
  overflow-y: auto;
  flex-grow: 1;
}

.changelog-footer {
  padding: 1rem;
  border-top: 1px solid #eee;
  text-align: right;
}

.understood-button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}

/* Markdown Styles */
.markdown-body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
  font-size: 16px;
  line-height: 1.5;
  word-wrap: break-word;
}

.markdown-body h1,
.markdown-body h2,
.markdown-body h3,
.markdown-body h4,
.markdown-body h5,
.markdown-body h6 {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body h1 { font-size: 2em; }
.markdown-body h2 { font-size: 1.5em; }
.markdown-body h3 { font-size: 1.25em; }

.markdown-body p {
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body ul,
.markdown-body ol {
  padding-left: 2em;
  margin-top: 0;
  margin-bottom: 16px;
}

.markdown-body code {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(27,31,35,0.05);
  border-radius: 3px;
}

.markdown-body pre {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 3px;
}

.markdown-body blockquote {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
  margin: 0;
}
</style>
