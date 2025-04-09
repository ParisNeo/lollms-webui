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
      renderCount: 0, // Added for detailed logging
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
        console.log(`[${this.instanceId}] Watcher triggered (Render #${currentRender}). UI changed: ${newValue !== oldValue}. New UI length: ${newValue?.length ?? 0}`);

        // Check if the container ref exists before evaluating if it needs render based on child nodes
        const htmlContainer = this.$refs.htmlContentContainer;
        const needsRenderBasedOnContent = !htmlContainer || !htmlContainer.hasChildNodes();

        // Determine if a render is needed: either the value changed OR the container is unexpectedly empty.
        const needsRender = newValue !== oldValue || needsRenderBasedOnContent;
        console.log(`[${this.instanceId}] Needs render evaluation (Render #${currentRender}): Value Changed=${newValue !== oldValue}, Container Empty=${needsRenderBasedOnContent} => Needs Render=${needsRender}`);

        if (needsRender) {
          console.log(`[${this.instanceId}] --- Starting Update Cycle (Render #${currentRender}) ---`);
          // Pass render context to cleanup for better logging
          this.cleanupDynamicContent(`before render #${currentRender}`);

          this.$nextTick(() => {
            console.log(`[${this.instanceId}] $nextTick after cleanup (Render #${currentRender}): Starting renderContent.`);
            // Pass render context to renderContent
            this.renderContent(currentRender);
          });
        } else {
           console.log(`[${this.instanceId}] Watcher triggered but skipping render (Render #${currentRender}). UI appears unchanged and container has content.`);
        }
      }
    }
  },
  beforeUnmount() {
    console.log(`[${this.instanceId}] Component beforeUnmount hook.`);
    // Pass context to cleanup
    this.cleanupDynamicContent('beforeUnmount');
  },
  methods: {
    logAlbumViewerMounted(type) {
      // Log when the conditional viewers actually get mounted
      console.log(`%c[${this.instanceId}] ${type} AlbumViewer successfully MOUNTED.`, 'color: green; font-weight: bold;');
    },

    renderContent(renderContext) {
      console.log(`%c[${this.instanceId}] renderContent CALLED (Context: Render #${renderContext})`, 'color: blue; font-weight: bold;');
      const targetContainer = this.$refs.htmlContentContainer;
      if (!targetContainer) {
        // This is a critical error for rendering
        console.error(`[${this.instanceId}] CRITICAL ERROR: htmlContentContainer ref NOT FOUND during renderContent (Context: Render #${renderContext})! Cannot render HTML.`);
        return;
      }

      // Clear previous standard HTML content *before* processing new UI
      targetContainer.innerHTML = '';
      console.log(`[${this.instanceId}] Cleared targetContainer innerHTML (Context: Render #${renderContext})`);

      // Initialize local collections for media elements found in this render cycle
      let imagesForMedia = [];
      let videosForMedia = [];
      let audiosForMedia = [];
      let mediaPlaceholderNeeded = false; // Flag to check if *any* media viewer might be needed later

      const incomingUi = this.ui || ''; // Ensure we have a string

      // Handle empty UI string explicitly
      if (!incomingUi.trim()) {
          console.warn(`[${this.instanceId}] No UI content provided or UI is empty whitespace (Context: Render #${renderContext}). Skipping parsing and rendering.`);
          // Explicitly reset media state if UI is empty
          this.resetMediaState(`empty UI received (Render #${renderContext})`);
          return; // Stop processing if there's nothing to render
      }

      console.log(`[${this.instanceId}] Parsing UI content (length: ${incomingUi.length}) (Context: Render #${renderContext})`);
      try {
          const parser = new DOMParser();
          const doc = parser.parseFromString(incomingUi, 'text/html');

          // --- 1. Inject Scoped CSS ---
          // Note: Styles are injected into the document <head>, not the component's container
          const styles = doc.head.querySelectorAll('style');
          console.log(`[${this.instanceId}] Found ${styles.length} style tags in parsed <head>.`);
          styles.forEach((style, index) => {
            console.log(`[${this.instanceId}] Injecting head style #${index + 1} (Context: Render #${renderContext}).`);
            this.injectScopedCss(style.textContent, `head style #${index + 1} / Render #${renderContext}`);
          });
          const bodyStyles = doc.body.querySelectorAll('style');
          console.log(`[${this.instanceId}] Found ${bodyStyles.length} style tags in parsed <body>.`);
          bodyStyles.forEach((style, index) => {
            console.log(`[${this.instanceId}] Injecting body style #${index + 1} (Context: Render #${renderContext}).`);
            this.injectScopedCss(style.textContent, `body style #${index + 1} / Render #${renderContext}`);
          });

          // --- 2. Process HTML Body Nodes ---
          console.log(`[${this.instanceId}] Processing body childNodes (Context: Render #${renderContext})`);
          const processedNodes = []; // Collect nodes to be appended to targetContainer
          const nodesToProcess = Array.from(doc.body.childNodes);
          console.log(`[${this.instanceId}] Found ${nodesToProcess.length} nodes in parsed body.`);

          nodesToProcess.forEach((node, index) => {
            const nodeIdentifier = `Node #${index + 1} (Type: ${node.nodeType})`;
            if (node.nodeType === Node.ELEMENT_NODE) {
              const tagName = node.tagName.toUpperCase();
              const classList = node.classList;
              console.log(`[${this.instanceId}] Processing ${nodeIdentifier}: <${tagName}>, Classes: [${Array.from(classList).join(', ')}]`);

              // --- Special Handling: Media Elements (Image, Video, Audio) ---
              if (classList.contains('media')) {
                 const src = node.getAttribute('src'); // Common attribute for media
                 if (!src) {
                     // Warn if a media element lacks a source
                     console.warn(`[${this.instanceId}]   -> Found '<${tagName}.media>' but it has NO 'src' attribute. Skipping this media element.`);
                     return; // Skip this specific node, don't add to processedNodes or media collections
                 }
                 mediaPlaceholderNeeded = true; // Mark that we found at least one valid media element

                 if (tagName === 'IMG') {
                     console.log(`[${this.instanceId}]   -> Found 'img.media' with src: ${src}. Adding to image album list.`);
                     imagesForMedia.push(src);
                     // IMPORTANT: Do *not* add to processedNodes, handled by ImageAlbumViewer
                     return;
                 } else if (tagName === 'VIDEO') {
                     console.log(`[${this.instanceId}]   -> Found 'video.media' with src: ${src}. Adding to video album list.`);
                     videosForMedia.push(src);
                     // IMPORTANT: Do *not* add to processedNodes
                     return;
                 } else if (tagName === 'AUDIO') {
                     console.log(`[${this.instanceId}]   -> Found 'audio.media' with src: ${src}. Adding to audio album list.`);
                     audiosForMedia.push(src);
                     // IMPORTANT: Do *not* add to processedNodes
                     return;
                 } else {
                     // Log if a non-standard tag has .media class
                     console.warn(`[${this.instanceId}]   -> Found '<${tagName}.media>' but it's not an IMG, VIDEO, or AUDIO tag. Treating as a standard HTML node.`);
                     // Fall through to be added to processedNodes below
                 }
              }

              // --- Special Handling: Clickable Image POST ---
              if (tagName === 'IMG' && classList.contains('clickable-post')) {
                 console.log(`[${this.instanceId}]   -> Found 'img.clickable-post'. Ensuring data attributes are present (or defaults).`);
                 // Ensure necessary data attributes exist for the click handler
                 if (!node.dataset.endpoint) node.dataset.endpoint = '/post_to_personality'; // Default endpoint
                 if (!node.dataset.payloadKey) node.dataset.payloadKey = 'img_path'; // Default payload key
                 // Fall through to be added to processedNodes
              }

              // --- Special Handling: Open Folder Link ---
              if (tagName === 'A' && classList.contains('open-folder')) {
                 console.log(`[${this.instanceId}]   -> Found 'a.open-folder'. Setting href='#' to prevent navigation.`);
                 node.setAttribute('href', '#'); // Prevent default link navigation
                 // Fall through to be added to processedNodes
              }

              // --- Special Handling: Source Elements (Rendered as standard HTML) ---
              if (tagName === 'INTERNET_SOURCE' || tagName === 'LOCAL_SOURCE') {
                  console.log(`[${this.instanceId}]   -> Found '${tagName}'. Will be rendered directly as HTML.`);
                  // Extract attributes for logging clarity, but mainly just render the element as is.
                  const href = node.getAttribute('href');
                  const summary = node.getAttribute('summary');
                  const similarity = node.getAttribute('similarity');
                  console.log(`[${this.instanceId}]      Attributes - href: ${href}, summary: ${summary}, similarity: ${similarity}`);
                  // Fall through to be added to processedNodes
              }

               // If node hasn't been returned (like media elements), add it for standard HTML rendering
               processedNodes.push(node);
               console.log(`[${this.instanceId}]      -> Adding <${tagName}> to processedNodes list for direct rendering.`);

            } else if (node.nodeType === Node.TEXT_NODE && node.textContent.trim()) {
                // Process non-empty text nodes
                console.log(`[${this.instanceId}] Processing ${nodeIdentifier}: TextNode (non-empty). Adding to processedNodes list.`);
                processedNodes.push(node);
            } else {
                // Log skipped nodes (like empty text nodes, comments)
                console.log(`[${this.instanceId}] Skipping ${nodeIdentifier}`);
            }
          });

          // --- 3. Append Processed Standard HTML & Source Nodes ---
          console.log(`[${this.instanceId}] Appending ${processedNodes.length} processed nodes to targetContainer (Context: Render #${renderContext})`);
          if (processedNodes.length > 0) {
              processedNodes.forEach(node => {
                  // Use importNode to ensure nodes are correctly adopted by the document
                  targetContainer.appendChild(document.importNode(node, true));
              });
              console.log(`[${this.instanceId}] Finished appending nodes. Current targetContainer innerHTML length: ${targetContainer.innerHTML.length}`);
          } else {
              console.log(`[${this.instanceId}] No standard HTML nodes to append.`);
          }

          // --- 4. Update State for Media Viewers ---
          // This happens *after* standard HTML is rendered
          console.log(`[${this.instanceId}] Evaluating media state updates (Context: Render #${renderContext}). Found media elements needing viewers: ${mediaPlaceholderNeeded}`);

          // Update Image Album State
          if (imagesForMedia.length > 0) {
              console.log(`[${this.instanceId}] SETTING Image Album state: show=true, count=${imagesForMedia.length}`);
              this.albumImages = [...imagesForMedia]; // Update with new images
              if (!this.showAlbumViewer) this.showAlbumViewer = true; // Trigger v-if
          } else {
              if (this.showAlbumViewer) {
                  console.log(`[${this.instanceId}] RESETTING Image Album state: show=false`);
                  this.showAlbumViewer = false; // Hide viewer if no images
              }
              if (this.albumImages.length > 0) this.albumImages = []; // Clear array
          }

          // Update Video Album State
          if (videosForMedia.length > 0) {
              console.log(`[${this.instanceId}] SETTING Video Album state: show=true, count=${videosForMedia.length}`);
              this.albumVideos = [...videosForMedia];
              if (!this.showVideoViewer) this.showVideoViewer = true;
          } else {
              if (this.showVideoViewer) {
                  console.log(`[${this.instanceId}] RESETTING Video Album state: show=false`);
                  this.showVideoViewer = false;
              }
              if (this.albumVideos.length > 0) this.albumVideos = [];
          }

          // Update Audio Album State
          if (audiosForMedia.length > 0) {
              console.log(`[${this.instanceId}] SETTING Audio Album state: show=true, count=${audiosForMedia.length}`);
              this.albumAudios = [...audiosForMedia];
              if (!this.showAudioViewer) this.showAudioViewer = true;
          } else {
              if (this.showAudioViewer) {
                  console.log(`[${this.instanceId}] RESETTING Audio Album state: show=false`);
                  this.showAudioViewer = false;
              }
               if (this.albumAudios.length > 0) this.albumAudios = [];
          }

          // If no media elements were found at all in this UI update
          if (!mediaPlaceholderNeeded && (this.showAlbumViewer || this.showVideoViewer || this.showAudioViewer)) {
              console.log(`[${this.instanceId}] No media elements found in this UI update. Resetting all media states.`);
              this.resetMediaState(`no media found in UI (Render #${renderContext})`);
          }

          // --- 5. Handle Original Scripts (Still generally discouraged for security/complexity) ---
          // const scripts = doc.body.getElementsByTagName('script');
          // console.log(`[${this.instanceId}] Found ${scripts.length} script tags in parsed body (Execution is disabled).`);
          // ... logic to handle scripts if ever needed ...

      } catch (error) {
          console.error(`[${this.instanceId}] Error during DOM parsing or processing (Context: Render #${renderContext}):`, error);
          // Consider resetting state or showing an error message in the UI
          this.cleanupDynamicContent(`error during render #${renderContext}`); // Attempt cleanup on error
      }

      console.log(`%c[${this.instanceId}] --- Finished renderContent (Context: Render #${renderContext}) ---`, 'color: blue; font-weight: bold;');
    },

    injectScopedCss(css, context) {
       console.log(`[${this.instanceId}] Attempting to inject scoped CSS (Context: ${context})`);
       if (!css || !css.trim()) {
           console.warn(`[${this.instanceId}] CSS content is empty or whitespace-only, skipping injection (Context: ${context}).`);
           return;
       }
       try {
           const scopedCss = this.scopeCSS(css);
           const styleElement = document.createElement('style');
           styleElement.textContent = scopedCss;
           // Append to document head so it applies globally but selectors are scoped
           document.head.appendChild(styleElement);
           this.injectedStyleElements.push(styleElement); // Track for removal
           console.log(`[${this.instanceId}] Injected style element #${this.injectedStyleElements.length} into <head> (Context: ${context}).`);
       } catch (error) {
           console.error(`[${this.instanceId}] Error injecting scoped CSS (Context: ${context}):`, error);
       }
    },

    scopeCSS(css) {
       // Ensure the container ID is available for scoping selectors
       const id = this.containerId;
       if (!id) {
            console.error(`[${this.instanceId}] Cannot scope CSS: containerId is missing or empty! Returning original CSS.`);
            return css;
       }
       const idSelector = `#${id}`; // e.g., #dynamic-ui-instance123

       // Improved Regex to handle various selectors including direct children (>), adjacent siblings (+), general siblings (~)
       // and pseudo-classes/elements (:hover, ::before, etc.)
       // It avoids scoping @-rules (like @keyframes, @media), pseudo-selectors starting with ':', and root selectors like 'html', 'body'.
       // It tries to prepend the ID selector correctly.
       const scopedCss = css.replace(/(^|[\s,}\]])([^@:%\s>+~][^{>,+~]*?)(\s*\{)/g, (match, prefix, selector, suffix) => {
           const trimmedSelector = selector.trim();

           // Skip scoping for already scoped selectors, @ rules, percentages, pseudo-classes/elements, html/body
           if (trimmedSelector.startsWith(idSelector) ||
               trimmedSelector.startsWith('@') ||
               trimmedSelector.startsWith(':') || // Handles pseudo-classes/elements
               trimmedSelector.startsWith('%') ||
               /^\d+%$/.test(trimmedSelector) ||
               trimmedSelector === 'html' ||
               trimmedSelector === 'body') {
               // console.log(`[${this.instanceId}] scopeCSS: Skipping selector "${trimmedSelector}"`);
               return match; // Return the original match
           }

           // Prepend the ID selector carefully
           const scopedSelector = trimmedSelector.split(',')
               .map(part => {
                   part = part.trim();
                   // Prepend ID selector, handling potential combinators at the start
                   if (part.startsWith('>') || part.startsWith('+') || part.startsWith('~')) {
                       return `${idSelector}${part}`; // e.g., #container>div
                   } else {
                       return `${idSelector} ${part}`; // e.g., #container div
                   }
               })
               .join(', ');
          // console.log(`[${this.instanceId}] scopeCSS: Scoping "${trimmedSelector}" to "${scopedSelector}"`);
           return `${prefix}${scopedSelector}${suffix}`;
       });
       // console.log(`[${this.instanceId}] scopeCSS: Final scoped CSS:\n${scopedCss}`);
       return scopedCss;
    },

    handleContainerClick(event) {
      const target = event.target;
      // Log the exact element clicked
      console.log(`[${this.instanceId}] Container clicked. Target: <${target.tagName.toLowerCase()}>`, target);

      // Use closest() to find the relevant interactive element, even if the click was on a child
      const clickablePost = target.closest('img.clickable-post');
      if (clickablePost) {
        console.log(`[${this.instanceId}] Click detected on or within 'img.clickable-post'.`);
        const endpoint = clickablePost.dataset.endpoint;
        const payloadKey = clickablePost.dataset.payloadKey; // Already defaulted during render
        const src = clickablePost.getAttribute('src');

        if (!endpoint) {
            console.error(`[${this.instanceId}] Clickable POST image is missing 'data-endpoint'! Cannot send POST.`);
            return;
        }
        if (!src) {
            console.error(`[${this.instanceId}] Clickable POST image is missing 'src'! Cannot determine payload.`);
            return;
        }

        event.preventDefault(); // Prevent any default image behavior if applicable
        const payload = { [payloadKey]: src };
        console.log(`[${this.instanceId}] Triggering POST request. Endpoint: ${endpoint}, Payload:`, payload);

        axios.post(endpoint, payload)
          .then(response => console.log(`[${this.instanceId}] POST to ${endpoint} successful:`, response.data))
          .catch(error => console.error(`[${this.instanceId}] Error posting to ${endpoint}:`, error.response ? error.response.data : error.message));
        return; // Handled
      }

      const openFolderLink = target.closest('a.open-folder');
      if (openFolderLink) {
        console.log(`[${this.instanceId}] Click detected on or within 'a.open-folder'.`);
        event.preventDefault(); // Prevent default link behavior (already set href="#")
        const discussionId = openFolderLink.dataset.discussionId;

        if (!discussionId) {
            console.error(`[${this.instanceId}] Open folder link is missing 'data-discussion-id'! Cannot open folder.`);
            return;
        }
        if (!this.clientId) {
          console.error(`[${this.instanceId}] CRITICAL: Client ID not found in Vuex store! Cannot send open_discussion_folder request.`);
          alert("Error: Client information is missing. Cannot perform this action.");
          return;
        }

        const payload = { client_id: this.clientId, discussion_id: discussionId };
        console.log(`[${this.instanceId}] Posting to '/open_discussion_folder'. Payload:`, payload);

        axios.post('/open_discussion_folder', payload)
          .then(response => console.log(`[${this.instanceId}] Open folder request successful:`, response.data))
          .catch(error => console.error(`[${this.instanceId}] Error requesting open folder:`, error.response ? error.response.data : error.message));
        return; // Handled
      }

      // Handle clicks on <internet_source> to open its href
      const internetSource = target.closest('internet_source[href]'); // Target only those with href
      if (internetSource) {
          event.preventDefault(); // Prevent any potential default behavior
          const href = internetSource.getAttribute('href');
          console.log(`[${this.instanceId}] Internet Source clicked. Opening href in new tab: ${href}`);
          window.open(href, '_blank', 'noopener,noreferrer'); // Security best practice
          return; // Handled
      }

      // Handle clicks on <local_source> (currently just logs info)
      const localSource = target.closest('local_source');
      if (localSource) {
           event.preventDefault(); // Prevent any potential default behavior
           const summary = localSource.getAttribute('summary') || 'No summary available.';
           const similarity = localSource.getAttribute('similarity') || 'N/A';
           console.log(`[${this.instanceId}] Local Source clicked. Summary: "${summary}", Similarity: ${similarity}%`);
           // Optional: Implement further UI interaction like showing details in a modal
           // alert(`Local Source:\nSimilarity: ${similarity}%\nSummary: ${summary}`);
           return; // Handled
       }

       // If the click wasn't on any known interactive element within the dynamic content
       console.log(`[${this.instanceId}] Click occurred but was not on a recognized interactive element (clickable-post, open-folder, internet_source[href], local_source). No action taken.`);
    },

    cleanupDynamicContent(cleanupContext) {
      // Provides context on *why* cleanup is happening (e.g., before new render, on unmount)
      console.log(`%c[${this.instanceId}] cleanupDynamicContent CALLED (Context: ${cleanupContext})`, 'color: orange;');

      // 1. Reset reactive data for all media viewers to ensure they are removed/reset
      this.resetMediaState(`cleanup (${cleanupContext})`);

      // 2. Remove injected stylesheets from the document <head>
      console.log(`[${this.instanceId}] Removing ${this.injectedStyleElements.length} injected style elements (Context: ${cleanupContext}).`);
      this.injectedStyleElements.forEach((styleElement, index) => {
        // Check if the element still exists and has a parent before trying to remove
        if (styleElement?.parentNode) {
          styleElement.parentNode.removeChild(styleElement);
          // console.log(`[${this.instanceId}]   Removed style element #${index + 1}.`);
        } else {
             // Warn if removal fails, might indicate issues elsewhere or double-cleanup
             console.warn(`[${this.instanceId}] Could not remove style element #${index + 1}. It might have already been removed or was never properly appended.`);
        }
      });
      this.injectedStyleElements = []; // Clear the tracking array

      // 3. Clear dynamically injected HTML content from its container
      const htmlContainer = this.$refs.htmlContentContainer;
      if (htmlContainer) {
        console.log(`[${this.instanceId}] Clearing innerHTML of htmlContentContainer (Context: ${cleanupContext}).`);
        htmlContainer.innerHTML = '';
      } else {
          // This might happen during unmount if refs are already gone, or if render failed initially
          console.warn(`[${this.instanceId}] htmlContentContainer ref not found during cleanup (Context: ${cleanupContext}). Cannot clear innerHTML.`);
      }
      console.log(`%c[${this.instanceId}] --- Finished cleanupDynamicContent (Context: ${cleanupContext}) ---`, 'color: orange;');
    },

    resetMediaState(context) {
        // Centralized method to reset all media-related state, with logging
        console.log(`[${this.instanceId}] Resetting media state (Context: ${context})`);
        let stateChanged = false;

        if (this.showAlbumViewer) {
            this.showAlbumViewer = false;
            console.log(`[${this.instanceId}]   - Set showAlbumViewer = false`);
            stateChanged = true;
        }
        if (this.albumImages.length > 0) {
            this.albumImages = [];
            console.log(`[${this.instanceId}]   - Cleared albumImages array`);
            stateChanged = true;
        }

        if (this.showVideoViewer) {
            this.showVideoViewer = false;
            console.log(`[${this.instanceId}]   - Set showVideoViewer = false`);
            stateChanged = true;
        }
        if (this.albumVideos.length > 0) {
            this.albumVideos = [];
            console.log(`[${this.instanceId}]   - Cleared albumVideos array`);
            stateChanged = true;
        }

        if (this.showAudioViewer) {
            this.showAudioViewer = false;
            console.log(`[${this.instanceId}]   - Set showAudioViewer = false`);
            stateChanged = true;
        }
        if (this.albumAudios.length > 0) {
            this.albumAudios = [];
            console.log(`[${this.instanceId}]   - Cleared albumAudios array`);
            stateChanged = true;
        }

        if (!stateChanged) {
             console.log(`[${this.instanceId}]   - Media state was already in its default (reset) state.`);
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
  line-height: 1.4; /* Improve readability */
}

:deep(internet_source) {
  border-left: 3px solid #007bff; /* Blue accent for internet */
}
/* Style internet sources with href to look clickable */
:deep(internet_source[href]) {
    cursor: pointer; /* Indicate clickability */
    color: #0056b3; /* Link-like color */
}
:deep(internet_source[href]:hover) {
    background-color: #eef; /* Slight hover effect */
    text-decoration: underline;
}

:deep(local_source) {
  border-left: 3px solid #28a745; /* Green accent for local */
}
/* Style local sources to indicate they might be interactable */
:deep(local_source) {
    cursor: default; /* Or 'pointer' if you add interaction */
}
:deep(local_source:hover) {
    background-color: #efe; /* Slight hover effect for consistency */
}


/* Style for icons within sources if the backend sends an <img> tag inside */
:deep(internet_source img),
:deep(local_source img) {
  width: 16px;
  height: 16px;
  margin-right: 6px;
  vertical-align: middle; /* Align icon nicely with text */
}

/* Display the summary attribute's content */
/* Using ::before allows text content and potential icon coexist */
:deep(internet_source::before),
:deep(local_source::before) {
    content: attr(summary); /* Display summary text */
    /* Add styles if needed, e.g., font-weight */
    /* display: inline-block; Optional: for better control with icons */
    /* vertical-align: middle; */
}

/* Add similarity info after local source content */
:deep(local_source)::after {
  content: ' (Similarity: ' attr(similarity) '%)';
  font-size: 0.85em;
  color: #555;
  margin-left: 8px;
  /* display: inline-block; */
  /* vertical-align: middle; */
}


/* Ensure the main container has some visual space */
div[id^="dynamic-ui-"] {
  min-height: 10px; /* Small minimum height */
  padding: 5px; /* Some internal padding */
  border: 1px dashed transparent; /* Invisible border for layout debugging if needed */
}

/* Style for the debug output */
pre {
  white-space: pre-wrap; /* Allow wrapping */
  word-break: break-all; /* Break long strings */
}
</style>