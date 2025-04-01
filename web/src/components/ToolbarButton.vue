<!-- ToolbarButton.vue -->
<template>
  <button
    class="svg-button"
    :title="title"
    @click="emit_click"
  >
    <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <g v-html="iconPath"></g>
    </svg>
  </button>
</template>

<script>
export default {
  name: 'ToolbarButton',
  emits: ['click'],
  props: {
    icon: {
      type: String,
      required: true
    },
    title: {
      type: String,
      required: true
    }
  },
  computed: {
    iconPath() {
      // Uses feather icons paths/structure where possible
      // Custom icons for specific languages/formats
      switch (this.icon) {
        // Basic Controls
        case 'x':
          return '<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="12"></line>';
        case 'check':
          return '<polyline points="20 6 9 17 4 12"></polyline>';
        case 'edit':
          return '<path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>';
        case 'copy':
          return '<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>';
        case 'trash':
          return '<polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>';
        case 'plus-square':
          return '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="12" y1="8" x2="12" y2="16"></line><line x1="8" y1="12" x2="16" y2="12"></line>';
        case 'send':
          return '<line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>';
        case 'globe':
          return '<circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path>';
        case 'fast-forward':
          return '<polygon points="13 19 22 12 13 5 13 19"></polygon><polygon points="2 19 11 12 2 5 2 19"></polygon>';
        case 'refresh-cw': // Used for "sendSimple"
          return '<polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>';
        case 'thumbs-up':
           return '<path d="M14 9V5a3 3 0 0 0-3-3l-4 9v11h11.28a2 2 0 0 0 2-1.7l1.38-9a2 2 0 0 0-2-2.3zM7 22H4a2 2 0 0 1-2-2v-7a2 2 0 0 1 2-2h3"></path>';
        case 'thumbs-down':
           return '<path d="M10 15v4a3 3 0 0 0 3 3l4-9V2H5.72a2 2 0 0 0-2 1.7l-1.38 9a2 2 0 0 0 2 2.3zm7-13h3a2 2 0 0 1 2 2v7a2 2 0 0 1-2 2h-3"></path>';
        case 'volume-2':
           return '<polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon><path d="M19.07 4.93a10 10 0 0 1 0 14.14M15.54 8.46a5 5 0 0 1 0 7.07"></path>';
        case 'mic':
           return '<path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path><path d="M19 10v2a7 7 0 0 1-14 0v-2"></path><line x1="12" y1="19" x2="12" y2="23"></line><line x1="8" y1="23" x2="16" y2="23"></line>';

        // Code / Language Icons
        case 'code':
          return '<polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline>';
        case 'python': // Using simplified representation for clarity in small size
           return '<path d="M15 9l-2 10m-6-10l2 10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><ellipse cx="12" cy="14" rx="8" ry="5" fill="none" stroke="currentColor" stroke-width="2"/><ellipse cx="12" cy="6" rx="4" ry="2.5" fill="currentColor"/>';
        case 'js': // Keeping Text for JS/TS/etc. as it's standard
          return '<text x="12" y="17" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="currentColor">JS</text>';
        case 'typescript':
          return '<text x="12" y="17" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="currentColor">TS</text>';
        case 'java': // Simple representation
           return '<path d="M8 8c4 0 4 4 8 4M8 16c4 0 4-4 8-4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="12" cy="12" r="9" fill="none" stroke="currentColor" stroke-width="2"/>';
        case 'cplusplus':
        case 'c++':
          return '<text x="12" y="17" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle" fill="currentColor">C++</text>';
        case 'csharp':
          return '<text x="12" y="17" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="currentColor">C#</text>';
        case 'go':
          return '<text x="12" y="17" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" fill="currentColor">Go</text>';
        case 'rust': // Simple 'R' in a cog/gear like shape
           return '<circle cx="12" cy="12" r="8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 8v8M8 12h8" fill="none" stroke="currentColor" stroke-width="2"/><path d="M12 2l1 4h-2zm6.4 4.4l3 1.8-2.5 3zm-.8 9.2l-3 1.8-1-4zm-9.2.8l-3-1.8 1-4zm-.8-9.2l3-1.8 2.5 3z" fill="currentColor"/>';
        case 'swift':
           return '<path d="M22 12a10 10 0 11-20 0 10 10 0 0120 0z" fill="none" stroke="currentColor" stroke-width="2"/><path d="M21 10c-2 0-5-1-7-4M3 14c2 0 5 1 7 4" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>';
        case 'kotlin': // Two triangles forming K-like shape
           return '<path d="M2 2 l10 10 L2 22 M 12 12 l10 -10 v 20 l -10 -10" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>';
        case 'r-project':
           return '<text x="12" y="17" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" fill="currentColor">R</text>';

        // Web Tech
        case 'html5':
           return '<polygon points="3 2 21 2 19.5 19 12 22 4.5 19 3 2"></polygon><polygon points="12 4 12 20 17.5 18.5 18.5 6 12 4"></polygon><polygon points="12 4 5.5 6 6 10.5 12 10.5 12 4"></polygon><polygon points="12 12.5 6.5 12.5 7 16.5 12 18 12 12.5"></polygon><polygon points="12 12.5 12 10.5 17 10.5 16.5 16.5 12 18 12 12.5"></polygon>'; // Simplified HTML5 logo structure
        case 'css3':
           return '<polygon points="3 2 21 2 19.5 19 12 22 4.5 19 3 2"></polygon><polygon points="12 4 12 20 17.5 18.5 18.5 6 12 4"></polygon><polygon points="12 7 8.5 7 8 10.5 12 10.5 12 7"></polygon><polygon points="12 12.5 8 12.5 7.5 15.5 12 17 12 12.5"></polygon>'; // Simplified CSS3 logo structure
        case 'vuejs': // Simple V shape
           return '<path d="M2 3l10 17L22 3H17l-5 10L7 3H2z" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>';
        case 'react': // Atom symbol
           return '<circle cx="12" cy="12" r="2" fill="none" stroke="currentColor" stroke-width="2"></circle><ellipse cx="12" cy="12" rx="10" ry="4" stroke="currentColor" stroke-width="2" fill="none"></ellipse><ellipse cx="12" cy="12" rx="4" ry="10" transform="rotate(60 12 12)" stroke="currentColor" stroke-width="2" fill="none"></ellipse><ellipse cx="12" cy="12" rx="4" ry="10" transform="rotate(-60 12 12)" stroke="currentColor" stroke-width="2" fill="none"></ellipse>';
        case 'angular': // Shield with A
           return '<polygon points="12 2 2 7 4 21 12 23 20 21 22 7 12 2"></polygon><polygon points="12 4 18 7 16 18 12 20 8 18 6 7 12 4"></polygon><polygon points="12 6 8 14 10 14 11 11.5 13 11.5 14 14 16 14 12 6"></polygon>';

        // Markup/Data
        case 'xml':
          return '<polyline points="16 18 22 12 16 6"></polyline><polyline points="8 6 2 12 8 18"></polyline><line x1="4.5" y1="12" x2="19.5" y2="12"></line>'; // Simplified tags
        case 'json': // Braces icon
           return '<path d="M8 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h1m8-18h1a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-1M12 8a2 2 0 0 1-2-2V3m4 5a2 2 0 0 0 2-2V3"></path>';
        case 'yaml': // Hyphen list items
           return '<line x1="5" y1="6" x2="19" y2="6"></line><line x1="5" y1="12" x2="19" y2="12"></line><line x1="5" y1="18" x2="19" y2="18"></line><line x1="9" y1="6" x2="9" y2="18"></line>';
        case 'markdown': // 'M' down arrow
           return '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line>';
        case 'latex': // Simple TeX representation
           return '<text x="12" y="17" font-family="serif" font-size="12" font-style="italic" text-anchor="middle" fill="currentColor">TeX</text>';

        // Scripting/Shell
        case 'terminal':
          return '<polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line>';
        case 'bash': // Terminal icon
          return '<polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line>';
        case 'powershell': // Terminal icon with >_ prompt stylized
           return '<polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line><polyline points="13 15 15 17 13 19" stroke-width="1.5"></polyline>';
        case 'perl': // Camel icon (often associated with Perl)
           return '<path d="M17 16c-2 2-4 2-5 0M7 16c2 2 4 2 5 0M12 14v4M9 10h6M10 20a6 6 0 0 1-6-6V9a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v5a6 6 0 0 1-6 6z"></path>';

        // Diagramming
        case 'mermaid': // Abstract flow chart
           return '<rect x="3" y="3" width="7" height="7" rx="1"></rect><rect x="14" y="3" width="7" height="7" rx="1"></rect><rect x="3" y="14" width="7" height="7" rx="1"></rect><rect x="14" y="14" width="7" height="7" rx="1"></rect><line x1="7" y1="10" x2="7" y2="14"></line><line x1="17" y1="10" x2="17" y2="14"></line><line x1="10" y1="7" x2="14" y2="7"></line><line x1="10" y1="17" x2="14" y2="17"></line>';
        case 'graphviz': // Simple directed graph
           return '<circle cx="6" cy="6" r="3"></circle><circle cx="18" cy="18" r="3"></circle><line x1="8" y1="8" x2="16" y2="16"></line><polyline points="12 16 16 16 16 12"></polyline>';
        case 'plantuml': // UML class box style
           return '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="3" y1="9" x2="21" y2="9"></line><line x1="3" y1="15" x2="21" y2="15"></line>';

        // Database
        case 'database':
          return '<ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>';
        case 'sql': // Database symbol
           return '<ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>';
        case 'mongodb': // Leaf icon
           return '<path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8c2.38 0 4.53.97 6.08 2.56L12 12l6.08 6.44C16.53 19.03 14.38 20 12 20z" fill="currentColor"></path>';

        // Other generic icons used in the parent context
        case 'chrome': // Representing Web
           return '<circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="4"></circle><line x1="21.17" y1="8" x2="12" y2="8"></line><line x1="3.95" y1="6.06" x2="8.54" y2="14"></line><line x1="10.88" y1="21.94" x2="15.46" y2="14"></line>';
        case 'file-text': // Representing Markup/Data
           return '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline>';
        case 'git-branch': // Representing Diagramming/Flow
          return '<line x1="6" y1="3" x2="6" y2="15"></line><circle cx="18" cy="6" r="3"></circle><circle cx="6" cy="18" r="3"></circle><path d="M18 9a9 9 0 0 1-9 9"></path>';

        default: // Fallback to a simple circle or question mark if icon not found
          console.warn(`ToolbarButton: Icon "${this.icon}" not found.`);
          return '<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>'; // Question mark in circle
      }
    }
  },
  methods: {
    emit_click(event){
      console.log("ToolbarButton clicked:", this.title);
      this.$emit('click', event); // Pass the event object
    }
  }
}
</script>

<style scoped>
/* Scoped styles if needed, but svg-button from the theme should handle most styling */
</style>