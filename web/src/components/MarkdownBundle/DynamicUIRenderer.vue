<template>
  <div :id="containerId" ref="container" @click="handleContainerClick">
    <!-- Container for dynamically injected standard HTML and Source elements -->
    <div ref="htmlContentContainer"></div>

    <!-- Conditionally render the Vue ImageAlbumViewer component -->
    <ImageAlbumViewer
      v-if="showAlbumViewer"
      :images="albumImages"
      :key="`album-image-${instanceId}-${albumImages.length}`"
      @hook:mounted="logAlbumViewerMounted('Image')"
    />

    <!-- Conditionally render the Vue VideoAlbumViewer component -->
    <VideoAlbumViewer
      v-if="showVideoViewer"
      :videos="albumVideos"
      :key="`album-video-${instanceId}-${albumVideos.length}`"
      @hook:mounted="logAlbumViewerMounted('Video')"
    />

    <!-- Conditionally render the Vue AudioAlbumViewer component -->
    <AudioAlbumViewer
      v-if="showAudioViewer"
      :audios="albumAudios"
      :key="`album-audio-${instanceId}-${albumAudios.length}`"
      @hook:mounted="logAlbumViewerMounted('Audio')"
    />

    <!-- Debugging output -->
    <pre style="background: #eee; padding: 10px; margin-top: 10px; font-size: 12px; border: 1px solid #ccc;">
      DEBUG [{{ instanceId }}]:
      --- Media State ---
      showAlbumViewer: {{ showAlbumViewer }}
      albumImages Count: {{ albumImages.length }}
      showVideoViewer: {{ showVideoViewer }}
      albumVideos Count: {{ albumVideos.length }}
      showAudioViewer: {{ showAudioViewer }}
      albumAudios Count: {{ albumAudios.length }}
      --- Raw Data ---
      albumImages: {{ JSON.stringify(albumImages) }}
      albumVideos: {{ JSON.stringify(albumVideos) }}
      albumAudios: {{ JSON.stringify(albumAudios) }}
    </pre>

  </div>
</template>

<script>
import { mapState } from 'vuex';
import axios from 'axios';
import ImageAlbumViewer from './ImageAlbumViewer.vue'; // Adjust path
// --- PLACEHOLDER: Import actual Video/Audio viewers when created ---
import VideoAlbumViewer from './VideoAlbumViewer.vue'; // Adjust path
import AudioAlbumViewer from './AudioAlbumViewer.vue'; // Adjust path
// --- END PLACEHOLDER ---

export default {
  name: 'DynamicUIRenderer',
  components: {
    ImageAlbumViewer,
    // --- PLACEHOLDER: Register actual Video/Audio viewers ---
    VideoAlbumViewer, // Example registration
    AudioAlbumViewer, // Example registration
    // --- END PLACEHOLDER ---
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
      // Image Album State
      albumImages: [],
      showAlbumViewer: false,
      // Video Album State
      albumVideos: [],
      showVideoViewer: false,
      // Audio Album State
      albumAudios: [],
      showAudioViewer: false,
      // Style Management
      injectedStyleElements: [],
      renderCount: 0,
    };
  },
  computed: {
    ...mapState(['clientId']),
    containerId() {
      return `dynamic-ui-${this.instanceId}`;
    },
  },
  watch: {
    ui: {
      immediate: true,
      handler(newValue, oldValue) {
        this.renderCount++;
        const currentRender = this.renderCount;
        console.log(`[${this.instanceId}] Watcher triggered (Render #${currentRender}). UI changed: ${newValue !== oldValue}.`);

        const htmlContainer = this.$refs.htmlContentContainer;
        // Ensure render happens if value changes OR if the container is somehow empty (e.g., HMR)
        const needsRender = newValue !== oldValue || !htmlContainer || !htmlContainer.hasChildNodes();
        console.log(`[${this.instanceId}] Needs render evaluation (Render #${currentRender}): ${needsRender}`);

        if (needsRender) {
          console.log(`[${this.instanceId}] --- Starting Update Cycle (Render #${currentRender}) ---`);
          this.cleanupDynamicContent(currentRender);

          this.$nextTick(() => {
            console.log(`[${this.instanceId}] $nextTick after cleanup (Render #${currentRender}): Starting renderContent.`);
            this.renderContent(currentRender);
          });
        } else {
           console.log(`[${this.instanceId}] Watcher triggered but skipping render (Render #${currentRender}).`);
        }
      }
    }
  },
  beforeUnmount() {
    console.log(`[${this.instanceId}] Component beforeUnmount hook.`);
    this.cleanupDynamicContent('beforeUnmount');
  },
  methods: {
    logAlbumViewerMounted(type) {
      console.log(`[${this.instanceId}] ${type} AlbumViewer successfully MOUNTED.`);
    },

    renderContent(renderContext) {
      console.log(`[${this.instanceId}] renderContent CALLED (Context: ${renderContext})`);
      const targetContainer = this.$refs.htmlContentContainer;
      if (!targetContainer) {
        console.error(`[${this.instanceId}] ERROR: htmlContentContainer ref NOT FOUND during renderContent (Context: ${renderContext})!`);
        return;
      }

      targetContainer.innerHTML = ''; // Ensure clean slate
      console.log(`[${this.instanceId}] Cleared targetContainer innerHTML (Context: ${renderContext})`);

      let imagesForMedia = []; // Local collection for images
      let videosForMedia = []; // Local collection for videos
      let audiosForMedia = []; // Local collection for audios
      let mediaPlaceholderNeeded = false; // Flag if any media viewer might be needed

      const incomingUi = this.ui || '';

      if (!incomingUi.trim()) {
          console.warn(`[${this.instanceId}] No UI content provided (Context: ${renderContext}). Skipping parsing.`);
          this.resetMediaState(`empty UI (${renderContext})`); // Ensure state is reset
          return;
      }

      console.log(`[${this.instanceId}] Parsing UI content (length: ${incomingUi.length}) (Context: ${renderContext})`);
      const parser = new DOMParser();
      const doc = parser.parseFromString(incomingUi, 'text/html');

      // --- 1. Inject Scoped CSS ---
      const styles = doc.head.querySelectorAll('style');
      console.log(`[${this.instanceId}] Found ${styles.length} style tags in <head>.`);
      styles.forEach((style, index) => {
        console.log(`[${this.instanceId}] Injecting head style #${index + 1}.`);
        this.injectScopedCss(style.textContent, renderContext);
      });
      const bodyStyles = doc.body.querySelectorAll('style');
       console.log(`[${this.instanceId}] Found ${bodyStyles.length} style tags in <body>.`);
      bodyStyles.forEach((style, index) => {
        console.log(`[${this.instanceId}] Injecting body style #${index + 1}.`);
        this.injectScopedCss(style.textContent, renderContext);
       });

      // --- 2. Process HTML Body ---
      console.log(`[${this.instanceId}] Processing body childNodes (Context: ${renderContext})`);
      const processedNodes = []; // Nodes to be appended directly
      const nodesToProcess = Array.from(doc.body.childNodes);
      console.log(`[${this.instanceId}] Found ${nodesToProcess.length} nodes in parsed body.`);

      nodesToProcess.forEach((node, index) => {
        if (node.nodeType === Node.ELEMENT_NODE) {
           const tagName = node.tagName.toUpperCase();
           const classList = node.classList;
           console.log(`[${this.instanceId}] Processing Node #${index + 1}: <${tagName}>, Classes: ${classList}`);

          // --- Special Handling: Media Elements (Image, Video, Audio) ---
          if (classList.contains('media')) {
             const src = node.getAttribute('src'); // Common attribute
             if (!src) {
                 console.warn(`[${this.instanceId}]   -> Found '<${tagName}.media>' but it has NO src attribute. Skipping.`);
                 return; // Skip nodes without src
             }
             mediaPlaceholderNeeded = true; // Mark that some media viewer might be needed

             if (tagName === 'IMG') {
                 console.log(`[${this.instanceId}]   -> Found 'img.media' with src: ${src}`);
                 imagesForMedia.push(src);
                 return; // Don't append media elements directly, they go to viewers
             } else if (tagName === 'VIDEO') {
                 console.log(`[${this.instanceId}]   -> Found 'video.media' with src: ${src}`);
                 videosForMedia.push(src);
                 return; // Don't append media elements directly
             } else if (tagName === 'AUDIO') {
                 console.log(`[${this.instanceId}]   -> Found 'audio.media' with src: ${src}`);
                 audiosForMedia.push(src);
                 return; // Don't append media elements directly
             } else {
                 console.warn(`[${this.instanceId}]   -> Found '<${tagName}.media>' but it's not an IMG, VIDEO, or AUDIO tag. Treating as standard node.`);
                 // Fall through to be added to processedNodes if not returned
             }
          }

          // --- Special Handling: Clickable Image POST ---
          if (tagName === 'IMG' && classList.contains('clickable-post')) {
             console.log(`[${this.instanceId}]   -> Found 'img.clickable-post'. Ensuring data attributes.`);
             if (!node.dataset.endpoint) node.dataset.endpoint = '/post_to_personality';
             if (!node.dataset.payloadKey) node.dataset.payloadKey = 'img_path';
             // Fall through to be added to processedNodes
          }

          // --- Special Handling: Open Folder Link ---
          if (tagName === 'A' && classList.contains('open-folder')) {
            console.log(`[${this.instanceId}]   -> Found 'a.open-folder'. Setting href='#'`);
             node.setAttribute('href', '#'); // Prevent navigation
             // Fall through to be added to processedNodes
          }

          // --- Special Handling: Source Elements ---
          if (tagName === 'INTERNET_SOURCE' || tagName === 'LOCAL_SOURCE') {
              console.log(`[${this.instanceId}]   -> Found '${tagName}'. Will be rendered directly.`);
              // Extract attributes for potential future use, but mainly just render it.
              // Attributes: icon, href, summary, similarity
              // Fall through to be added to processedNodes
          }

           processedNodes.push(node); // Add node for standard appending

        } else if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
            console.log(`[${this.instanceId}] Processing Node #${index + 1}: TextNode (non-empty)`);
             processedNodes.push(node); // Add text node
        } else {
             console.log(`[${this.instanceId}] Skipping Node #${index + 1} (Type: ${node.nodeType})`);
        }
      });

      // --- 3. Append Processed Standard HTML & Source Nodes ---
      console.log(`[${this.instanceId}] Appending ${processedNodes.length} processed nodes to targetContainer (Context: ${renderContext})`);
      processedNodes.forEach(node => {
        targetContainer.appendChild(document.importNode(node, true));
      });
      console.log(`[${this.instanceId}] Finished appending nodes. Current targetContainer innerHTML length: ${targetContainer.innerHTML.length}`);


      // --- 4. Update State for Media Viewers ---
      console.log(`[${this.instanceId}] Evaluating media state (Context: ${renderContext}). mediaPlaceholderNeeded=${mediaPlaceholderNeeded}`);
      if (mediaPlaceholderNeeded) {
          // Images
          if (imagesForMedia.length > 0) {
              this.albumImages = [...imagesForMedia];
              this.showAlbumViewer = true;
              console.log(`[${this.instanceId}] SETTING Image Album state: show=${this.showAlbumViewer}, count=${this.albumImages.length}`);
          } else {
              this.albumImages = [];
              this.showAlbumViewer = false;
          }
          // Videos
          if (videosForMedia.length > 0) {
              this.albumVideos = [...videosForMedia];
              this.showVideoViewer = true;
              console.log(`[${this.instanceId}] SETTING Video Album state: show=${this.showVideoViewer}, count=${this.albumVideos.length}`);
          } else {
              this.albumVideos = [];
              this.showVideoViewer = false;
          }
          // Audios
          if (audiosForMedia.length > 0) {
              this.albumAudios = [...audiosForMedia];
              this.showAudioViewer = true;
              console.log(`[${this.instanceId}] SETTING Audio Album state: show=${this.showAudioViewer}, count=${this.albumAudios.length}`);
          } else {
              this.albumAudios = [];
              this.showAudioViewer = false;
          }
      } else {
          console.log(`[${this.instanceId}] No media elements found. Resetting all media states.`);
          this.resetMediaState(`no media found (${renderContext})`);
      }

      // --- 5. Handle Original Scripts (Still discouraged) ---
      // const scripts = doc.body.getElementsByTagName('script');
      // ...

      console.log(`[${this.instanceId}] --- Finished renderContent (Context: ${renderContext}) ---`);
    },

    injectScopedCss(css, renderContext) {
       console.log(`[${this.instanceId}] Injecting scoped CSS (Context: ${renderContext})`);
       if (!css || !css.trim()) {
           console.warn(`[${this.instanceId}] CSS content is empty, skipping injection.`);
           return;
       }
      const scopedCss = this.scopeCSS(css);
      const styleElement = document.createElement('style');
      styleElement.textContent = scopedCss;
      document.head.appendChild(styleElement);
      this.injectedStyleElements.push(styleElement);
      console.log(`[${this.instanceId}] Injected style element. Total injected: ${this.injectedStyleElements.length}`);
    },

    scopeCSS(css) {
       const id = this.containerId;
        if (!id) {
            console.error(`[${this.instanceId}] Cannot scope CSS: containerId is missing!`);
            return css;
        }
        const idSelector = `#${id}`;
        // Regex needs careful adjustment for custom elements like <internet_source>
        // This simpler prefixing approach is generally safer for dynamic content.
       return css.replace(/([^\r\n,{}\s][^{}]*)(?=\s*\{)/g, (match, selector) => {
         selector = selector.trim();
         if (selector.startsWith('@') || selector.startsWith('%') || /^\d+%$/.test(selector) || selector.includes(idSelector)) {
           return selector;
         }
         const scopedSelector = selector.split(',')
             .map(part => `${idSelector} ${part.trim()}`)
             .join(', ');
         return scopedSelector;
       });
    },

    handleContainerClick(event) {
      const target = event.target;
       console.log(`[${this.instanceId}] Container clicked. Target: <${target.tagName}>, Classes: ${target.classList}`);

      const clickablePost = target.closest('img.clickable-post');
      if (clickablePost && clickablePost.dataset.endpoint) {
        event.preventDefault();
        const endpoint = clickablePost.dataset.endpoint;
        const payloadKey = clickablePost.dataset.payloadKey || 'img_path';
        const src = clickablePost.getAttribute('src');
        const payload = { [payloadKey]: src };
        console.log(`[${this.instanceId}] Clickable POST triggered. Endpoint: ${endpoint}, Payload:`, payload);
        axios.post(endpoint, payload)
          .then(response => console.log(`[${this.instanceId}] Post to ${endpoint} successful:`, response.data))
          .catch(error => console.error(`[${this.instanceId}] Error posting to ${endpoint}:`, error));
        return;
      }

      const openFolderLink = target.closest('a.open-folder');
      if (openFolderLink && openFolderLink.dataset.discussionId) {
         event.preventDefault();
        const discussionId = openFolderLink.dataset.discussionId;
        console.log(`[${this.instanceId}] Open folder link clicked. Discussion ID: ${discussionId}`);
        if (!this.clientId) {
          console.error(`[${this.instanceId}] ERROR: Client ID not found in Vuex store for open_discussion_folder!`);
          alert("Error: Client information is missing.");
          return;
        }
        console.log(`[${this.instanceId}] Posting to /open_discussion_folder with client_id: ${this.clientId}, discussion_id: ${discussionId}`);
        axios.post('/open_discussion_folder', { client_id: this.clientId, discussion_id: discussionId })
          .then(response => console.log(`[${this.instanceId}] Open folder request successful:`, response.data))
          .catch(error => console.error(`[${this.instanceId}] Error opening folder:`, error));
        return;
      }

      // Handle clicks on <internet_source> to open href
      const internetSource = target.closest('internet_source');
      if (internetSource && internetSource.hasAttribute('href')) {
          event.preventDefault();
          const href = internetSource.getAttribute('href');
          console.log(`[${this.instanceId}] Internet Source clicked. Opening href: ${href}`);
          window.open(href, '_blank', 'noopener,noreferrer');
          return;
      }

      // Potentially handle clicks on <local_source> differently if needed (e.g., show details)
      const localSource = target.closest('local_source');
       if (localSource) {
           event.preventDefault(); // Prevent any default action
           const summary = localSource.getAttribute('summary') || 'No summary provided.';
           const similarity = localSource.getAttribute('similarity');
           console.log(`[${this.instanceId}] Local Source clicked. Summary: ${summary}, Similarity: ${similarity}%`);
           // Could potentially trigger a modal or other UI element here
           // alert(`Local Source:\nSimilarity: ${similarity}%\nSummary: ${summary}`);
           return;
       }


       console.log(`[${this.instanceId}] Click was not handled by specific handlers.`);
    },

    cleanupDynamicContent(cleanupContext) {
      console.log(`[${this.instanceId}] cleanupDynamicContent CALLED (Context: ${cleanupContext})`);

      // Reset reactive data for all media viewers
      this.resetMediaState(`cleanup (${cleanupContext})`);

      // Remove injected stylesheets
      console.log(`[${this.instanceId}] Removing ${this.injectedStyleElements.length} injected style elements.`);
      this.injectedStyleElements.forEach((styleElement, index) => {
        if (styleElement?.parentNode) {
          styleElement.parentNode.removeChild(styleElement);
        } else {
             console.warn(`[${this.instanceId}] Could not remove style element #${index + 1}.`);
        }
      });
      this.injectedStyleElements = [];

      // Clear dynamically injected HTML content
      const htmlContainer = this.$refs.htmlContentContainer;
      if (htmlContainer) {
        console.log(`[${this.instanceId}] Clearing innerHTML of htmlContentContainer.`);
        htmlContainer.innerHTML = '';
      } else {
          console.warn(`[${this.instanceId}] htmlContentContainer ref not found during cleanup (Context: ${cleanupContext}).`);
      }
      console.log(`[${this.instanceId}] --- Finished cleanupDynamicContent (Context: ${cleanupContext}) ---`);
    },

    resetMediaState(context) {
        console.log(`[${this.instanceId}] Resetting media state (Context: ${context})`);
        let changed = false;
        if (this.showAlbumViewer) { this.showAlbumViewer = false; changed = true; }
        if (this.albumImages.length > 0) { this.albumImages = []; changed = true; }
        if (this.showVideoViewer) { this.showVideoViewer = false; changed = true; }
        if (this.albumVideos.length > 0) { this.albumVideos = []; changed = true; }
        if (this.showAudioViewer) { this.showAudioViewer = false; changed = true; }
        if (this.albumAudios.length > 0) { this.albumAudios = []; changed = true; }
        if (!changed) {
             console.log(`[${this.instanceId}] Media state was already reset.`);
        }
    }
  }
};
</script>

<style scoped>
/* Add basic styling for the custom source elements */
/* Use :deep() because these elements are injected into htmlContentContainer, not direct children */
:deep(internet_source),
:deep(local_source) {
  display: block; /* Make them block-level */
  border: 1px solid #ccc;
  padding: 8px 12px;
  margin: 8px 0;
  border-radius: 4px;
  background-color: #f9f9f9;
  font-size: 0.9em;
}

:deep(internet_source) {
  border-left: 3px solid #007bff; /* Blue accent for internet */
}
:deep(internet_source[href]) {
    cursor: pointer; /* Indicate clickability */
}
:deep(internet_source[href]:hover) {
    background-color: #eef; /* Slight hover effect */
}

:deep(local_source) {
  border-left: 3px solid #28a745; /* Green accent for local */
}

/* Optional: Style for icons within sources if provided */
:deep(internet_source[icon]),
:deep(local_source[icon]) {
  /* Basic icon styling idea - adjust as needed */
  /* This assumes the icon attr contains a URL */
  /* You might prefer using ::before with content: attr(icon) and background-image */
  padding-left: 28px; /* Make space for icon */
  background-repeat: no-repeat;
  background-position: 8px center;
  background-size: 16px 16px; /* Adjust size */
  background-image: var(--icon-url); /* Set via JS or more complex CSS if needed */
  /* A simple implementation might just rely on the backend sending an <img> inside */
}

/* Example if you want to display attributes directly (less common) */
/*
:deep(local_source)::after {
  content: ' (Similarity: ' attr(similarity) '%)';
  font-size: 0.8em;
  color: #666;
  margin-left: 5px;
}
*/

:deep(internet_source::before),
:deep(local_source::before) {
    content: attr(summary); /* Display summary text */
    /* Additional styling for summary if needed */
}


/* Ensure container has some height */
:deep(#dynamic-ui-root) {
  min-height: 20px;
}
</style>