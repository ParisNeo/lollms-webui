<template>
  <div :id="containerId" ref="container" @click="handleContainerClick"></div>
</template>

<script>
import { mapState } from 'vuex';
import axios from 'axios';
import ImageAlbumViewer from './ImageAlbumViewer.vue'; // Adjust path if needed

export default {
  name: 'DynamicUIRenderer',
  props: {
    ui: {
      type: String,
      required: true
    },
    instanceId: {
      type: String,
      required: true
    }
    // Removed discussion_id prop, as it will be in the HTML data attribute
  },
  data() {
    return {
      containerId: `dynamic-ui-${this.instanceId}`,
      albumImages: [], // Store images for the album viewer
      albumViewerInstance: null, // To keep track of the mounted album component
      injectedStyleElements: [], // To keep track of injected styles for cleanup
    };
  },
  computed: {
    ...mapState(['clientId']), // Map client_id from Vuex store
  },
  watch: {
    ui: {
      immediate: true,
      handler(newValue, oldValue) {
        // Only re-render if the UI actually changed
        if (newValue !== oldValue || this.$refs.container?.innerHTML === '') {
          console.log(`UI prop changed for instance ${this.instanceId}`);
          this.$nextTick(() => {
            this.cleanupDynamicContent(); // Clean up previous dynamic elements before rendering new
            this.renderContent();
          });
        }
      }
    }
  },
  beforeUnmount() {
    this.cleanupDynamicContent(); // Ensure cleanup when component is destroyed
    // Remove the main click listener
    this.$refs.container?.removeEventListener('click', this.handleContainerClick);
  },
  methods: {
    renderContent() {
      console.log(`Rendering content for instance ${this.instanceId}...`);
      const container = this.$refs.container;
      if (!container) {
        console.error(`Container ref not found for instance ${this.instanceId}`);
        return;
      }

      // Clear previous content safely
      container.innerHTML = '';
      this.albumImages = []; // Reset album images

      const parser = new DOMParser();
      const doc = parser.parseFromString(this.ui, 'text/html');

      // --- 1. Inject Scoped CSS ---
      const styles = doc.head.getElementsByTagName('style'); // Check head first
      Array.from(styles).forEach(style => this.injectScopedCss(style.textContent));
      const bodyStyles = doc.body.getElementsByTagName('style'); // Also check body
      Array.from(bodyStyles).forEach(style => this.injectScopedCss(style.textContent));

      // --- 2. Process HTML Body ---
      const processedNodes = [];
      let albumPlaceholderNeeded = false;

      // Convert NodeList to Array for easier manipulation
      const nodesToProcess = Array.from(doc.body.childNodes);

      nodesToProcess.forEach(node => {
        if (node.nodeType === Node.ELEMENT_NODE) {
          // --- Special Handling: Image Album ---
          if (node.tagName === 'IMG' && node.classList.contains('album')) {
            const src = node.getAttribute('src');
            if (src) {
              this.albumImages.push(src);
              albumPlaceholderNeeded = true;
            }
            // Don't add the original img.album node directly
            return; // Skip appending this node
          }

          // --- Special Handling: Clickable Image POST ---
          // Use a specific class like 'clickable-post' and data attributes for flexibility
          // Example HTML: <img src="path/img.jpg" class="clickable-post" data-endpoint="/post_to_personality" data-payload-key="img_path">
          if (node.tagName === 'IMG' && node.classList.contains('clickable-post')) {
            // Add necessary data attributes if they were in onclick="post_to_personality"
            // This part is tricky if relying solely on onclick. Best practice is to use data attributes.
            // Assuming HTML is updated to use data attributes as shown above.
             if (!node.dataset.endpoint) node.dataset.endpoint = '/post_to_personality'; // Default endpoint if not set
             if (!node.dataset.payloadKey) node.dataset.payloadKey = 'img_path'; // Default payload key
             // The click handling will be done via event delegation (handleContainerClick)
          }

          // --- Special Handling: Open Folder Link ---
          // Example HTML: <a href="#" class="open-folder" data-discussion-id="123">Open Folder</a>
          if (node.tagName === 'A' && node.classList.contains('open-folder')) {
             // Ensure it has the data-discussion-id attribute.
             // Click handling via event delegation.
             node.setAttribute('href', '#'); // Prevent navigation
          }
        }

        // Add the node (original or potentially modified) to our list
        processedNodes.push(node);
      });

      // --- 3. Add Album Placeholder if needed ---
      if (albumPlaceholderNeeded && this.albumImages.length > 0) {
        const albumPlaceholder = document.createElement('div');
        // Give it a unique ID for mounting the Vue component
        albumPlaceholder.id = `album-placeholder-${this.instanceId}`;
        container.appendChild(albumPlaceholder); // Add placeholder first
      }

      // --- 4. Append Processed Standard HTML Nodes ---
      processedNodes.forEach(node => {
        // Need to import the node into the current document context before appending
        container.appendChild(document.adoptNode(node));
      });


      // --- 5. Mount Album Viewer Component ---
      if (albumPlaceholderNeeded && this.albumImages.length > 0) {
        this.mountAlbumViewer();
      }

      // --- 6. Handle Original Scripts (Use with caution!) ---
      // Executing arbitrary scripts can be a security risk and might interfere
      // with Vue's reactivity or the event delegation. It's often better to
      // handle interactions via the defined patterns (classes/data attributes).
      // If absolutely necessary:
      // const scripts = doc.body.getElementsByTagName('script');
      // Array.from(scripts).forEach(script => {
      //   try {
      //     const newScript = document.createElement('script');
      //     newScript.textContent = script.textContent; // Might need scoping adjustments
      //     container.appendChild(newScript); // Scripts added this way often don't execute reliably or might execute in global scope
      //     // For reliable execution, you might need Function constructor or eval, which is risky:
      //     // try { new Function(script.textContent).call(window); } catch (e) { console.error("Error executing script:", e); }
      //   } catch (e) {
      //       console.error("Error processing script tag:", e)
      //   }
      // });
      console.log(`Finished rendering for instance ${this.instanceId}.`);
    },

    injectScopedCss(css) {
      const scopedCss = this.scopeCSS(css);
      const styleElement = document.createElement('style');
      styleElement.textContent = scopedCss;
      document.head.appendChild(styleElement);
      this.injectedStyleElements.push(styleElement); // Keep track for cleanup
    },

    scopeCSS(css) {
      // Basic scoping: prepend container ID to selectors not already scoped deeper
      // This regex is basic and might need refinement for complex CSS.
      // It tries to target selectors at the start of a rule block.
       return css.replace(/([^\r\n,{}]+)(,(?=[^}]*{)|\s*{)/g, (match, selector, suffix) => {
         // Avoid scoping pseudo-elements like ::before directly on the ID, scope the base selector instead
         // Avoid scoping keyframes, font-face etc.
         selector = selector.trim();
         if (selector.startsWith('@') || selector.startsWith(':') || selector.includes('#') || selector.includes('[')) {
           // Don't scope if it starts with @ (keyframes, media), is pseudo-element/class only, or already has an ID/attribute selector
           return match;
         }
         // Prepend the ID, handling multiple selectors separated by commas
         const scopedSelector = selector.split(',')
             .map(part => `#${this.containerId} ${part.trim()}`)
             .join(', ');
         return `${scopedSelector}${suffix}`;
       });
    },

    mountAlbumViewer() {
      // Ensure placeholder exists
      const placeholder = document.getElementById(`album-placeholder-${this.instanceId}`);
      if (!placeholder) {
        console.error("Album placeholder not found!");
        return;
      }

      // Create and mount the ImageAlbumViewer component
      const AlbumViewerComponent = Vue.extend(ImageAlbumViewer);
      this.albumViewerInstance = new AlbumViewerComponent({
        propsData: {
          images: this.albumImages
        }
      });
      this.albumViewerInstance.$mount(placeholder); // Mount it onto the placeholder element
      console.log(`Mounted ImageAlbumViewer for instance ${this.instanceId}`);
    },

    handleContainerClick(event) {
      const target = event.target;

      // --- Handle Clickable Image Post ---
      const clickablePost = target.closest('img.clickable-post');
      if (clickablePost && clickablePost.dataset.endpoint) {
        event.preventDefault();
        const endpoint = clickablePost.dataset.endpoint;
        const payloadKey = clickablePost.dataset.payloadKey || 'img_path'; // Default key
        const src = clickablePost.getAttribute('src');
        const payload = { [payloadKey]: src };

        console.log(`Posting to ${endpoint} with payload:`, payload);
        axios.post(endpoint, payload)
          .then(response => {
            console.log('Post successful:', response.data);
            // Optionally handle success (e.g., show message, update UI)
          })
          .catch(error => {
            console.error(`Error posting to ${endpoint}:`, error);
            // Optionally handle error
          });
        return; // Stop further processing if handled
      }

      // --- Handle Open Folder Link ---
      const openFolderLink = target.closest('a.open-folder');
      if (openFolderLink && openFolderLink.dataset.discussionId) {
        event.preventDefault();
        const discussionId = openFolderLink.dataset.discussionId;
        if (!this.clientId) {
          console.error("Client ID not found in Vuex store.");
          alert("Error: Client information is missing.");
          return;
        }

        console.log(`Posting to /open_discussion_folder with client_id: ${this.clientId}, discussion_id: ${discussionId}`);
        axios.post('/open_discussion_folder', { client_id: this.clientId, discussion_id: discussionId })
          .then(response => {
            console.log('Open folder request successful:', response.data);
            // Handle success (maybe response indicates folder opened)
          })
          .catch(error => {
            console.error('Error opening folder:', error);
            // Handle error (e.g., show error message)
          });
        return; // Stop further processing
      }

      // Add more delegated event handlers here if needed...
    },

    cleanupDynamicContent() {
      console.log(`Cleaning up dynamic content for instance ${this.instanceId}`);
      // Unmount and destroy the album viewer Vue instance if it exists
      if (this.albumViewerInstance) {
        try {
          this.albumViewerInstance.$destroy();
          // Remove the placeholder or container element if needed, check if $el exists first
           if (this.albumViewerInstance.$el && this.albumViewerInstance.$el.parentNode) {
               this.albumViewerInstance.$el.parentNode.removeChild(this.albumViewerInstance.$el);
           }
        } catch (e) {
            console.error("Error destroying album viewer instance:", e);
        }
        this.albumViewerInstance = null;
      }

      // Remove injected stylesheets
      this.injectedStyleElements.forEach(styleElement => {
        if (styleElement.parentNode) {
          styleElement.parentNode.removeChild(styleElement);
        }
      });
      this.injectedStyleElements = [];

      // Clear container content (already done at the start of renderContent, but good practice)
      const container = this.$refs.container;
      if (container) {
         // container.innerHTML = ''; // Be careful if renderContent is called immediately after
      }
    }
  }
};
</script>

<style scoped>
/* Add any styles specific to the container itself, if needed */
/* For example: */
/* div[id^="dynamic-ui-"] {
  border: 1px dashed lightgray;
  padding: 5px;
  margin-bottom: 10px;
} */
</style>