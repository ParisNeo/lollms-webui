<template>
    <div class="audio-album-viewer" v-if="audios && audios.length > 0">
      <!-- Optional Title -->
      <h4 class="audio-viewer-title">Audio Files</h4>
  
      <div class="audio-list">
        <div v-for="(audioSrc, index) in audios" :key="`audio-${index}-${audioSrc}`" class="audio-item">
          <audio
            controls
            :src="audioSrc"
            preload="metadata" 
            class="audio-player"
          >
            Your browser does not support the audio element.
            <!-- Provide fallback content -->
            <a :href="audioSrc" target="_blank" rel="noopener noreferrer">Download audio {{ index + 1 }}</a>
          </audio>
           <!-- Optional: Display filename or index if helpful -->
           <!-- <span class="audio-label">Track {{ index + 1 }}</span> -->
           <!-- <span class="audio-label">{{ getFilename(audioSrc) }}</span> -->
        </div>
      </div>
    </div>
     <div v-else class="audio-album-viewer-empty">
      <!-- Optional: Message if somehow rendered with no audios, though parent v-if should prevent this -->
       <!-- <p>No audio files to display.</p> -->
    </div>
  </template>
  
  <script>
  export default {
    name: 'AudioAlbumViewer',
    props: {
      /**
       * An array of strings, where each string is a URL to an audio file.
       */
      audios: {
        type: Array,
        required: true,
        default: () => [], // Good practice for array props
        validator: (prop) => Array.isArray(prop) && prop.every(item => typeof item === 'string'), // Ensure it's an array of strings
      }
    },
    mounted() {
      // Log when the component is successfully mounted and how many items it received
      console.log(`[AudioAlbumViewer] Mounted with ${this.audios.length} audio file(s):`, this.audios);
    },
    methods: {
      /**
       * Optional helper to extract filename from URL for display.
       * @param {string} url - The full URL of the audio file.
       * @returns {string} - The extracted filename or the original URL if parsing fails.
       */
      getFilename(url) {
        if (!url) return '';
        try {
          // Decode URI components first in case of encoded characters
          const decodedUrl = decodeURIComponent(url);
          // Basic extraction - might need refinement for complex URLs/paths
          return decodedUrl.substring(decodedUrl.lastIndexOf('/') + 1).split('?')[0].split('#')[0] || url;
        } catch (e) {
          console.warn(`[AudioAlbumViewer] Could not parse filename from URL: ${url}`, e);
          return url; // Fallback to full URL
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .audio-album-viewer {
    border: 1px solid #e0e0e0; /* Softer border */
    border-left: 3px solid #fd7e14; /* Orange accent for audio */
    background-color: #fdfdfd; /* Slightly off-white background */
    padding: 15px;
    margin-top: 15px; /* Spacing from other content */
    border-radius: 4px;
  }
  
  .audio-viewer-title {
    margin-top: 0;
    margin-bottom: 15px;
    font-size: 1.1em;
    font-weight: 600;
    color: #555;
  }
  
  .audio-list {
    display: flex;
    flex-direction: column;
    gap: 10px; /* Spacing between audio players */
  }
  
  .audio-item {
    /* Could add item-specific styling here if needed */
    display: flex; /* Align items if label is uncommented */
    align-items: center; /* Center items vertically */
    gap: 10px;
  }
  
  .audio-player {
    width: 100%; /* Make player take full width */
    height: 40px; /* Consistent height for standard controls */
    /* Add vendor prefixes if needed for specific styling, but 'controls' is standard */
  }
  
  /* Optional styling for the label if you uncomment it */
  /* .audio-label {
    font-size: 0.9em;
    color: #666;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 150px; /* Limit label width */
  /* } */
  
  .audio-album-viewer-empty {
     /* Styles if you want to show a placeholder when empty */
     /* (Currently not active due to parent v-if) */
  }
  
  /* Fallback link styling */
  .audio-player a {
      color: #007bff;
      text-decoration: none;
  }
  .audio-player a:hover {
      text-decoration: underline;
  }
  </style>