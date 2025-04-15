<template>
    <div class="image-album-viewer">
      <div class="main-view" v-if="selectedImage">
        <img :src="selectedImage" alt="Selected album image" />
      </div>
      <!-- Optional: Add a placeholder if no images exist -->
      <div class="main-view placeholder" v-else>
        <span>No image selected</span>
      </div>
      <div class="thumbnails">
        <img
          v-for="(image, index) in images"
          :key="index"
          :src="image"
          :class="{ active: image === selectedImage }"
          @click="selectImage(image)"
          alt="Album thumbnail"
          class="thumbnail"
        />
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'ImageAlbumViewer',
    props: {
      images: {
        type: Array,
        required: true,
        validator: (value) => value.every(item => typeof item === 'string'), // Ensure it's an array of strings (URLs)
      },
      initialSelected: {
        type: String,
        default: null,
      }
    },
    data() {
      return {
        selectedImage: null,
      };
    },
    created() {
      this.initializeSelection();
    },
    methods: {
      selectImage(image) {
        this.selectedImage = image;
      },
      initializeSelection() {
        // Select the initial image or the first one if none provided or if initial is invalid
        if (this.initialSelected && this.images.includes(this.initialSelected)) {
            this.selectedImage = this.initialSelected;
        } else if (this.images && this.images.length > 0) {
            this.selectedImage = this.images[0];
        } else {
            this.selectedImage = null;
        }
      }
    },
    watch: {
        // Reset selection if images array changes
        images(newImages, oldImages) {
            // Basic check if array content changed significantly or length is different
            // A more robust check might compare actual elements if needed
            if (JSON.stringify(newImages) !== JSON.stringify(oldImages)) {
                this.initializeSelection(); // Re-run selection logic
            }
        },
        // Also watch initialSelected if it can change dynamically
        initialSelected(newInitial) {
            this.initializeSelection();
        }
    }
  };
  </script>
  
  <style scoped>
  /* Light Mode / Default Variables (using CSS variables for easier theming) */
  :root { /* Or scope to .image-album-viewer if preferred */
    --viewer-bg: #f9f9f9;
    --viewer-border: #ccc;
    --main-view-bg: #eee;
    --main-view-placeholder-text: #888;
    --thumb-hover-border: #aaa;
    --thumb-active-border: #007bff;
  }

  .image-album-viewer {
    border: 1px solid var(--viewer-border);
    padding: 10px;
    margin: 10px 0;
    border-radius: 4px;
    background-color: var(--viewer-bg);
    transition: background-color 0.3s ease, border-color 0.3s ease; /* Smooth theme transition */
  }
  
  .main-view {
    text-align: center;
    margin-bottom: 10px;
    min-height: 150px; /* Ensure space even if no image selected initially */
    background-color: var(--main-view-bg);
    display: flex;
    justify-content: center;
    align-items: center;
    border-radius: 3px; /* Slight rounding */
    transition: background-color 0.3s ease; /* Smooth theme transition */
  }

  .main-view.placeholder span {
    color: var(--main-view-placeholder-text);
    font-style: italic;
  }
  
  .main-view img {
    max-width: 100%;
    max-height: 400px; /* Limit max height */
    display: block;
    object-fit: contain; /* Better than cover for viewing whole image */
  }
  
  .thumbnails {
    display: flex;
    flex-wrap: wrap;
    gap: 5px; /* Add spacing between thumbnails */
    justify-content: center; /* Center thumbnails */
  }
  
  .thumbnail {
    width: 60px;
    height: 60px;
    object-fit: cover;
    cursor: pointer;
    border: 2px solid transparent;
    transition: border-color 0.2s ease;
    border-radius: 3px; /* Slight rounding */
  }
  
  .thumbnail:hover {
    border-color: var(--thumb-hover-border);
  }
  
  .thumbnail.active {
    border-color: var(--thumb-active-border); /* Highlight active thumbnail */
  }

  /* Dark Mode Styles */
  @media (prefers-color-scheme: dark) {
    /* Redefine variables for dark mode */
    :root { /* Or scope to .image-album-viewer if preferred */
        --viewer-bg: #2d2d2d;
        --viewer-border: #555;
        --main-view-bg: #3a3a3a;
        --main-view-placeholder-text: #aaa;
        --thumb-hover-border: #777;
        --thumb-active-border: #409eff; /* Brighter blue for dark background */
    }

    /* Specific overrides if needed, though variables should handle most */
    /* Example: If you didn't use variables, you'd do this:
    .image-album-viewer {
        background-color: #2d2d2d;
        border-color: #555;
    }
    .main-view {
        background-color: #3a3a3a;
    }
    .main-view.placeholder span {
         color: #aaa;
    }
    .thumbnail:hover {
        border-color: #777;
    }
    .thumbnail.active {
        border-color: #409eff;
    }
    */
  }
  </style>