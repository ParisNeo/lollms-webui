<template>
  <div :id="containerId" ref="container" @click="handleContainerClick">
    <!-- Container for dynamically injected HTML -->
    <div ref="htmlContentContainer"></div>
    <!-- Conditionally render the Vue ImageAlbumViewer component -->
    <!-- Added extra log to see when Vue *tries* to render this based on the v-if condition -->
    <ImageAlbumViewer
      v-if="showAlbumViewer"
      :images="albumImages"
      :key="`album-${instanceId}-${albumImages.length}`"
      @hook:mounted="logAlbumViewerMounted"
    />
    <!-- Debugging output -->

    <pre style="background: #eee; padding: 10px; margin-top: 10px; font-size: 12px; border: 1px solid #ccc;">
      DEBUG [{{ instanceId }}]:
      showAlbumViewer: {{ showAlbumViewer }}
      albumImages Count: {{ albumImages.length }}
      albumImages: {{ JSON.stringify(albumImages) }}
    </pre>

  </div>
</template>

<script>
import { mapState } from 'vuex';
import axios from 'axios';
import ImageAlbumViewer from './ImageAlbumViewer.vue'; // Adjust path if needed

export default {
  name: 'DynamicUIRenderer',
  components: {
    ImageAlbumViewer,
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
      albumImages: [],
      showAlbumViewer: false,
      injectedStyleElements: [],
      // Added a simple counter to help distinguish render calls
      renderCount: 0,
    };
  },
  computed: {
    ...mapState(['clientId']),
    containerId() {
      // Added log
      console.log(`[${this.instanceId}] Computed containerId: dynamic-ui-${this.instanceId}`);
      return `dynamic-ui-${this.instanceId}`;
    },
  },
  watch: {
    ui: {
      immediate: true,
      handler(newValue, oldValue) {
        this.renderCount++;
        const currentRender = this.renderCount;
        console.log(`[${this.instanceId}] Watcher triggered (Render #${currentRender}). UI changed: ${newValue !== oldValue}. New length: ${newValue?.length}, Old length: ${oldValue?.length}`);

        const htmlContainer = this.$refs.htmlContentContainer;
        const needsRender = newValue !== oldValue || !htmlContainer || htmlContainer.innerHTML === '';
        console.log(`[${this.instanceId}] Needs render evaluation (Render #${currentRender}): ${needsRender}`);

        if (needsRender) {
          console.log(`[${this.instanceId}] --- Starting Update Cycle (Render #${currentRender}) ---`);
          // Cleanup must happen *before* rendering new content
          this.cleanupDynamicContent(currentRender); // Pass render count for context

          // Use $nextTick to ensure DOM is updated after cleanup before rendering
          this.$nextTick(() => {
            console.log(`[${this.instanceId}] $nextTick after cleanup (Render #${currentRender}): Starting renderContent.`);
            this.renderContent(currentRender); // Pass render count for context
          });
        } else {
           console.log(`[${this.instanceId}] Watcher triggered but skipping render (Render #${currentRender}). UI likely unchanged or container still populated.`);
        }
      }
    }
  },
  beforeUnmount() {
    console.log(`[${this.instanceId}] Component beforeUnmount hook.`);
    this.cleanupDynamicContent('beforeUnmount'); // Ensure cleanup when component is destroyed
  },
  methods: {
    logAlbumViewerMounted() {
      console.log(`[${this.instanceId}] ImageAlbumViewer successfully MOUNTED.`);
    },

    renderContent(renderContext) {
      console.log(`[${this.instanceId}] renderContent CALLED (Context: ${renderContext})`);
      const targetContainer = this.$refs.htmlContentContainer;
      if (!targetContainer) {
        console.error(`[${this.instanceId}] ERROR: htmlContentContainer ref NOT FOUND during renderContent (Context: ${renderContext})!`);
        return;
      }

      // Ensure container is clean (belt-and-suspenders with cleanup)
      targetContainer.innerHTML = '';
      console.log(`[${this.instanceId}] Cleared targetContainer innerHTML (Context: ${renderContext})`);

      let imagesForAlbum = []; // Local variable for processing
      let localShowAlbumViewer = false; // Use a local flag during processing
      const incomingUi = this.ui || ''; // Use local variable for safety

      if (!incomingUi.trim()) {
          console.warn(`[${this.instanceId}] No UI content provided (Context: ${renderContext}). Skipping parsing.`);
          // Ensure state is reset if UI becomes empty
          this.albumImages = [];
          this.showAlbumViewer = false;
          console.log(`[${this.instanceId}] Reset album state due to empty UI (Context: ${renderContext}). showAlbumViewer=${this.showAlbumViewer}`);
          return;
      }

      console.log(`[${this.instanceId}] Parsing UI content (length: ${incomingUi.length}) (Context: ${renderContext})`);
      const parser = new DOMParser();
      const doc = parser.parseFromString(incomingUi, 'text/html');

      // --- 1. Inject Scoped CSS ---
      const styles = doc.head.getElementsByTagName('style');
      console.log(`[${this.instanceId}] Found ${styles.length} style tags in <head>.`);
      Array.from(styles).forEach((style, index) => {
        console.log(`[${this.instanceId}] Injecting head style #${index + 1}.`);
        this.injectScopedCss(style.textContent, renderContext);
      });
      const bodyStyles = doc.body.getElementsByTagName('style');
       console.log(`[${this.instanceId}] Found ${bodyStyles.length} style tags in <body>.`);
      Array.from(bodyStyles).forEach((style, index) => {
        console.log(`[${this.instanceId}] Injecting body style #${index + 1}.`);
        this.injectScopedCss(style.textContent, renderContext);
       });

      // --- 2. Process HTML Body ---
      console.log(`[${this.instanceId}] Processing body childNodes (Context: ${renderContext})`);
      const processedNodes = [];
      let albumPlaceholderNeeded = false;
      const nodesToProcess = Array.from(doc.body.childNodes);
      console.log(`[${this.instanceId}] Found ${nodesToProcess.length} nodes in parsed body.`);

      nodesToProcess.forEach((node, index) => {
        if (node.nodeType === Node.ELEMENT_NODE) {
           console.log(`[${this.instanceId}] Processing Node #${index + 1}: <${node.tagName}>, Classes: ${node.classList}`);
          // --- Special Handling: Image Album ---
          if (node.tagName === 'IMG' && node.classList.contains('album')) {
            const src = node.getAttribute('src');
            if (src) {
              console.log(`[${this.instanceId}]   -> Found 'img.album' with src: ${src}`);
              imagesForAlbum.push(src); // Add to local list
              albumPlaceholderNeeded = true;
            } else {
              console.warn(`[${this.instanceId}]   -> Found 'img.album' but it has NO src attribute.`);
            }
            return; // Skip appending this specific node
          }

          // --- Special Handling: Clickable Image POST ---
          if (node.tagName === 'IMG' && node.classList.contains('clickable-post')) {
             console.log(`[${this.instanceId}]   -> Found 'img.clickable-post'. Ensuring data attributes.`);
             if (!node.dataset.endpoint) node.dataset.endpoint = '/post_to_personality';
             if (!node.dataset.payloadKey) node.dataset.payloadKey = 'img_path';
          }

          // --- Special Handling: Open Folder Link ---
          if (node.tagName === 'A' && node.classList.contains('open-folder')) {
            console.log(`[${this.instanceId}]   -> Found 'a.open-folder'. Setting href='#'`);
             node.setAttribute('href', '#'); // Prevent navigation
          }
           processedNodes.push(node); // Add node for standard appending
        } else if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
            console.log(`[${this.instanceId}] Processing Node #${index + 1}: TextNode (non-empty)`);
             processedNodes.push(node); // Add node for standard appending
        } else {
             console.log(`[${this.instanceId}] Skipping Node #${index + 1} (Type: ${node.nodeType})`);
        }
      });

      // --- 3. Append Processed Standard HTML Nodes ---
      console.log(`[${this.instanceId}] Appending ${processedNodes.length} processed nodes to targetContainer (Context: ${renderContext})`);
      processedNodes.forEach(node => {
        // Use importNode to ensure the node can be appended to the current document
        targetContainer.appendChild(document.importNode(node, true));
      });
      console.log(`[${this.instanceId}] Finished appending nodes. Current targetContainer innerHTML length: ${targetContainer.innerHTML.length}`);


      // --- 4. Update State for Album Viewer ---
      console.log(`[${this.instanceId}] Evaluating album state (Context: ${renderContext}). albumPlaceholderNeeded=${albumPlaceholderNeeded}, images found=${imagesForAlbum.length}`);
      if (albumPlaceholderNeeded && imagesForAlbum.length > 0) {
          // Set the local flag first
          localShowAlbumViewer = true;
          console.log(`[${this.instanceId}] SETTING album state: images=`, JSON.stringify(imagesForAlbum));
          // Update reactive data properties
          this.albumImages = [...imagesForAlbum]; // Use spread to ensure reactivity change detection
          this.showAlbumViewer = true;
          console.log(`[${this.instanceId}] State AFTER update: showAlbumViewer=${this.showAlbumViewer}, albumImages count=${this.albumImages.length}`);
      } else {
          console.log(`[${this.instanceId}] RESETTING album state.`);
          localShowAlbumViewer = false;
          // Update reactive data properties
          this.albumImages = [];
          this.showAlbumViewer = false;
          console.log(`[${this.instanceId}] State AFTER reset: showAlbumViewer=${this.showAlbumViewer}`);
      }

      // --- 5. Handle Original Scripts (Still use with caution!) ---
      // const scripts = doc.body.getElementsByTagName('script');
      // Array.from(scripts).forEach(script => { /* ... */ });

      console.log(`[${this.instanceId}] --- Finished renderContent (Context: ${renderContext}) ---`);
    },

    injectScopedCss(css, renderContext) {
       console.log(`[${this.instanceId}] Injecting scoped CSS (Context: ${renderContext})`);
       if (!css || !css.trim()) {
           console.warn(`[${this.instanceId}] CSS content is empty, skipping injection.`);
           return;
       }
      const scopedCss = this.scopeCSS(css); // Call helper method
      const styleElement = document.createElement('style');
      styleElement.textContent = scopedCss;
      // Append to head for better standard compliance
      document.head.appendChild(styleElement);
      this.injectedStyleElements.push(styleElement); // Store ref in data property
      console.log(`[${this.instanceId}] Injected style element. Total injected: ${this.injectedStyleElements.length}`);
    },

    scopeCSS(css) {
       // Use computed containerId
       const id = this.containerId; // Get it once
        if (!id) {
            console.error(`[${this.instanceId}] Cannot scope CSS: containerId is missing!`);
            return css; // Return original CSS
        }
        const idSelector = `#${id}`;
        // Improved regex to handle more cases, including direct descendant (>), adjacent sibling (+), general sibling (~), pseudo-classes/elements
       return css.replace(/([^\r\n,{}\s][^{}]*)(?=\s*\{)/g, (match, selector) => {
         selector = selector.trim();
         // Avoid scoping @ rules, keyframes, font-faces, etc.
         if (selector.startsWith('@') || selector.startsWith('%') || /^\d+%$/.test(selector)) {
           return selector;
         }
         // Avoid scoping selectors that already seem specific (like IDs, maybe attribute selectors if needed)
         // Simple check for now: don't re-scope if it already contains the ID prefix
         if (selector.includes(idSelector)) {
             return selector;
         }

         // Scope each part of a comma-separated list
         const scopedSelector = selector.split(',')
             .map(part => {
                 part = part.trim();
                 // Handle cases like `html body .class` -> `#id .class` (avoiding `#id html body .class`)
                 // This is tricky, a simple prefix is often safer for dynamically injected content
                 // Option 1: Simple Prefix (Safest)
                 return `${idSelector} ${part}`;
                 // Option 2: More complex replacements (can break easily)
                 // e.g., if part starts with 'body' or 'html', replace it? -> Complex
             })
             .join(', ');
         return scopedSelector;
       });
    },

    handleContainerClick(event) {
      const target = event.target;
       console.log(`[${this.instanceId}] Container clicked. Target: <${target.tagName}>, Classes: ${target.classList}`);

      // --- Handle Clickable Image Post ---
      // Use closest to handle clicks on elements inside the intended target (e.g., if image is wrapped)
      const clickablePost = target.closest('img.clickable-post');
      if (clickablePost && clickablePost.dataset.endpoint) {
        event.preventDefault(); // Prevent default image drag behavior etc.
        const endpoint = clickablePost.dataset.endpoint;
        const payloadKey = clickablePost.dataset.payloadKey || 'img_path';
        const src = clickablePost.getAttribute('src');
        const payload = { [payloadKey]: src };

        console.log(`[${this.instanceId}] Clickable POST triggered. Endpoint: ${endpoint}, Payload:`, payload);
        axios.post(endpoint, payload)
          .then(response => console.log(`[${this.instanceId}] Post to ${endpoint} successful:`, response.data))
          .catch(error => console.error(`[${this.instanceId}] Error posting to ${endpoint}:`, error));
        return; // Handled
      }

      // --- Handle Open Folder Link ---
      const openFolderLink = target.closest('a.open-folder');
      if (openFolderLink) { // Check dataset.discussionId inside
         event.preventDefault(); // Prevent default link behavior (# navigation)
        const discussionId = openFolderLink.dataset.discussionId;
        if (!discussionId) {
            console.warn(`[${this.instanceId}] 'a.open-folder' clicked, but missing 'data-discussion-id' attribute.`);
            return;
        }
        console.log(`[${this.instanceId}] Open folder link clicked. Discussion ID: ${discussionId}`);
        // Access clientId from computed properties (mapped from Vuex)
        if (!this.clientId) {
          console.error(`[${this.instanceId}] ERROR: Client ID not found in Vuex store for open_discussion_folder!`);
          alert("Error: Client information is missing.");
          return;
        }

        console.log(`[${this.instanceId}] Posting to /open_discussion_folder with client_id: ${this.clientId}, discussion_id: ${discussionId}`);
        axios.post('/open_discussion_folder', { client_id: this.clientId, discussion_id: discussionId })
          .then(response => console.log(`[${this.instanceId}] Open folder request successful:`, response.data))
          .catch(error => console.error(`[${this.instanceId}] Error opening folder:`, error));
        return; // Handled
      }

       console.log(`[${this.instanceId}] Click was not handled by specific handlers.`);
    },

    cleanupDynamicContent(cleanupContext) {
      console.log(`[${this.instanceId}] cleanupDynamicContent CALLED (Context: ${cleanupContext})`);

      // Reset reactive data - this hides the ImageAlbumViewer via v-if
      // Important: Only reset if they are currently set, to avoid unnecessary reactive churn
      let stateChanged = false;
      if (this.showAlbumViewer) {
          this.showAlbumViewer = false;
          stateChanged = true;
      }
      if (this.albumImages.length > 0) {
          this.albumImages = [];
           stateChanged = true;
      }
       if (stateChanged) {
           console.log(`[${this.instanceId}] Album state reset during cleanup. showAlbumViewer=${this.showAlbumViewer}`);
       } else {
            console.log(`[${this.instanceId}] Album state was already reset.`);
       }


      // Remove injected stylesheets
      console.log(`[${this.instanceId}] Removing ${this.injectedStyleElements.length} injected style elements.`);
      this.injectedStyleElements.forEach((styleElement, index) => {
        if (styleElement && styleElement.parentNode) {
          console.log(`[${this.instanceId}] Removing style element #${index + 1}`);
          styleElement.parentNode.removeChild(styleElement);
        } else {
            console.warn(`[${this.instanceId}] Could not remove style element #${index + 1} (already removed or no parent).`);
        }
      });
      this.injectedStyleElements = []; // Clear the tracking array

      // Clear dynamically injected HTML content
      const htmlContainer = this.$refs.htmlContentContainer;
      if (htmlContainer) {
        console.log(`[${this.instanceId}] Clearing innerHTML of htmlContentContainer.`);
        htmlContainer.innerHTML = '';
      } else {
          console.warn(`[${this.instanceId}] htmlContentContainer ref not found during cleanup (Context: ${cleanupContext}). Might be called before mount or after unmount.`);
      }
      console.log(`[${this.instanceId}] --- Finished cleanupDynamicContent (Context: ${cleanupContext}) ---`);
    }
  }
};
</script>

<style scoped>
/* Add any styles specific to the main container itself, if needed */
/* Example: Add a min-height to prevent collapse when empty */
:deep(#dynamic-ui-root) { /* Using :deep to target potential root if needed, adjust selector */
  min-height: 20px; /* Or whatever makes sense */
}
</style>