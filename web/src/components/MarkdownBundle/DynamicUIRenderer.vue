<template>
  <div :id="containerId" ref="container" @click="handleContainerClick">
    <!-- Container for dynamically injected HTML -->
    <div ref="htmlContentContainer"></div>
    <!-- Conditionally render the Vue ImageAlbumViewer component -->
    <ImageAlbumViewer
      v-if="showAlbumViewer"
      :images="albumImages"
      :key="`album-${instanceId}`"
    />
  </div>
</template>

<script>
import { mapState } from 'vuex';
import axios from 'axios';
import ImageAlbumViewer from './ImageAlbumViewer.vue'; // Adjust path if needed

export default {
  name: 'DynamicUIRenderer',
  components: {
    ImageAlbumViewer, // Register the child component
  },
  props: {
    ui: {
      type: String,
      required: true
    },
    instanceId: {
      type: String,
      required: true
    }
  },
  data() {
    return {
      // containerId is computed, moved to computed section
      albumImages: [], // Reactive state for album images
      showAlbumViewer: false, // Reactive state to control v-if
      injectedStyleElements: [], // Keep track of injected styles
    };
  },
  computed: {
    ...mapState(['clientId']), // Map client_id from Vuex store

    // Compute containerId based on instanceId prop
    containerId() {
      return `dynamic-ui-${this.instanceId}`;
    },
  },
  watch: {
    ui: {
      immediate: true, // Run on component mount
      handler(newValue, oldValue) {
        // Only re-render if the UI actually changed or if the container is empty
        // Use $refs here as they are available after the initial render (due to immediate: true)
        const htmlContainer = this.$refs.htmlContentContainer;
        if (newValue !== oldValue || !htmlContainer || htmlContainer.innerHTML === '') {
          console.log(`UI prop changed for instance ${this.instanceId}`);
          // Cleanup must happen *before* rendering new content
          this.cleanupDynamicContent();
          // Use $nextTick to ensure DOM is updated after cleanup before rendering
          this.$nextTick(() => {
            this.renderContent();
          });
        }
      }
    }
  },
  beforeUnmount() {
    this.cleanupDynamicContent(); // Ensure cleanup when component is destroyed
    // No need to remove listener manually, Vue handles it on the root element
  },
  methods: {
    renderContent() {
      console.log(`Rendering content for instance ${this.instanceId}...`);
      const targetContainer = this.$refs.htmlContentContainer; // Access ref via this.$refs
      if (!targetContainer) {
        // This check might be less likely to fail here compared to setup,
        // as refs are generally available in methods called after mount.
        console.error(`HTML content container ref not found for instance ${this.instanceId}`);
        return;
      }

      // Clear previous content (already done in cleanup, but good practice)
      targetContainer.innerHTML = '';
      let imagesForAlbum = []; // Local variable for processing
      this.showAlbumViewer = false; // Reset viewer flag

      const parser = new DOMParser();
      // Use this.ui to access the prop
      const doc = parser.parseFromString(this.ui || '', 'text/html');

      // --- 1. Inject Scoped CSS ---
      const styles = doc.head.getElementsByTagName('style');
      Array.from(styles).forEach(style => this.injectScopedCss(style.textContent));
      const bodyStyles = doc.body.getElementsByTagName('style');
      Array.from(bodyStyles).forEach(style => this.injectScopedCss(style.textContent));

      // --- 2. Process HTML Body ---
      const processedNodes = [];
      let albumPlaceholderNeeded = false;
      const nodesToProcess = Array.from(doc.body.childNodes);

      nodesToProcess.forEach(node => {
        if (node.nodeType === Node.ELEMENT_NODE) {
          // --- Special Handling: Image Album ---
          if (node.tagName === 'IMG' && node.classList.contains('album')) {
            const src = node.getAttribute('src');
            if (src) {
              imagesForAlbum.push(src); // Add to local list
              albumPlaceholderNeeded = true;
            }
            return; // Skip appending this node
          }

          // --- Special Handling: Clickable Image POST ---
          if (node.tagName === 'IMG' && node.classList.contains('clickable-post')) {
             if (!node.dataset.endpoint) node.dataset.endpoint = '/post_to_personality';
             if (!node.dataset.payloadKey) node.dataset.payloadKey = 'img_path';
          }

          // --- Special Handling: Open Folder Link ---
          if (node.tagName === 'A' && node.classList.contains('open-folder')) {
             node.setAttribute('href', '#'); // Prevent navigation
          }
        }
        processedNodes.push(node);
      });

      // --- 3. Append Processed Standard HTML Nodes ---
      processedNodes.forEach(node => {
        targetContainer.appendChild(document.importNode(node, true));
      });

      // --- 4. Update State for Album Viewer ---
      if (albumPlaceholderNeeded && imagesForAlbum.length > 0) {
          this.albumImages = imagesForAlbum; // Update reactive data property
          this.showAlbumViewer = true;      // Update reactive data property
          console.log(`Scheduled ImageAlbumViewer rendering for instance ${this.instanceId} with ${imagesForAlbum.length} images.`);
      } else {
          this.albumImages = [];
          this.showAlbumViewer = false;
      }

      // --- 5. Handle Original Scripts (Still use with caution!) ---
      // const scripts = doc.body.getElementsByTagName('script');
      // Array.from(scripts).forEach(script => { /* ... */ });

      console.log(`Finished rendering for instance ${this.instanceId}.`);
    },

    injectScopedCss(css) {
      const scopedCss = this.scopeCSS(css); // Call helper method
      const styleElement = document.createElement('style');
      styleElement.textContent = scopedCss;
      document.head.appendChild(styleElement);
      this.injectedStyleElements.push(styleElement); // Store ref in data property
    },

    scopeCSS(css) {
       // Use computed containerId
       return css.replace(/([^\r\n,{}]+)(,(?=[^}]*{)|\s*{)/g, (match, selector, suffix) => {
         selector = selector.trim();
         if (selector.startsWith('@') || selector.startsWith(':') || selector.includes('#') || selector.includes('[')) {
           return match;
         }
         const scopedSelector = selector.split(',')
             .map(part => `#${this.containerId} ${part.trim()}`) // Scope relative to the main container ID
             .join(', ');
         return `${scopedSelector}${suffix}`;
       });
    },

    handleContainerClick(event) {
      const target = event.target;

      // --- Handle Clickable Image Post ---
      const clickablePost = target.closest('img.clickable-post');
      if (clickablePost && clickablePost.dataset.endpoint) {
        event.preventDefault();
        const endpoint = clickablePost.dataset.endpoint;
        const payloadKey = clickablePost.dataset.payloadKey || 'img_path';
        const src = clickablePost.getAttribute('src');
        const payload = { [payloadKey]: src };

        console.log(`Posting to ${endpoint} with payload:`, payload);
        axios.post(endpoint, payload)
          .then(response => console.log('Post successful:', response.data))
          .catch(error => console.error(`Error posting to ${endpoint}:`, error));
        return;
      }

      // --- Handle Open Folder Link ---
      const openFolderLink = target.closest('a.open-folder');
      if (openFolderLink && openFolderLink.dataset.discussionId) {
        event.preventDefault();
        const discussionId = openFolderLink.dataset.discussionId;
        // Access clientId from computed properties (mapped from Vuex)
        if (!this.clientId) {
          console.error("Client ID not found in Vuex store.");
          alert("Error: Client information is missing.");
          return;
        }

        console.log(`Posting to /open_discussion_folder with client_id: ${this.clientId}, discussion_id: ${discussionId}`);
        axios.post('/open_discussion_folder', { client_id: this.clientId, discussion_id: discussionId })
          .then(response => console.log('Open folder request successful:', response.data))
          .catch(error => console.error('Error opening folder:', error));
        return;
      }
    },

    cleanupDynamicContent() {
      console.log(`Cleaning up dynamic content for instance ${this.instanceId}`);

      // Reset reactive data - this hides the ImageAlbumViewer via v-if
      this.showAlbumViewer = false;
      this.albumImages = [];

      // Remove injected stylesheets
      this.injectedStyleElements.forEach(styleElement => {
        if (styleElement && styleElement.parentNode) {
          styleElement.parentNode.removeChild(styleElement);
        }
      });
      this.injectedStyleElements = []; // Clear the tracking array

      // Clear dynamically injected HTML content
      const htmlContainer = this.$refs.htmlContentContainer;
      if (htmlContainer) {
        htmlContainer.innerHTML = '';
      }
      console.log(`Finished cleanup for instance ${this.instanceId}.`);
    }
  }
};
</script>

<style scoped>
/* Add any styles specific to the main container itself, if needed */
</style>