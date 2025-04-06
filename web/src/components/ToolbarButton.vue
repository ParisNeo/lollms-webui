<!-- ToolbarButton.vue -->
<template>
  <button
    :class="['svg-button focus:outline-none focus:ring-1 focus:ring-blue-400 dark:focus:ring-blue-500', buttonClass]"
    :title="title"
    @click="emit_click"
    type="button"
  >
    <svg :class="svgSizeClass" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
       <!-- Use v-html to inject the path data -->
      <g v-html="iconContent"></g>
    </svg>
    <!-- Slot for potential text alongside icon, e.g., H1 -->
    <slot></slot>
  </button>
</template>

<script>
import feather from 'feather-icons';

export default {
  name: 'ToolbarButton',
  emits: ['click'],
  props: {
    icon: { type: String, required: true },
    title: { type: String, required: true },
    // Optional class for the button element itself
    buttonClass: { type: [String, Object, Array], default: '' },
    // Optional class for the SVG element size
    svgSizeClass: { type: String, default: 'w-4 h-4' } // Default size (Adjusted to w-4 h-4 to match editor's default iconSize=16)
  },
  computed: {
    iconContent() {
      // --- Feather Icons (Keep using Feather for consistency where available) ---
      const featherIcon = feather.icons[this.icon]?.contents;
      if (featherIcon) return featherIcon;

      // --- Custom SVG Icons ---
      // Use viewBox="0 0 24 24" for consistency when creating/finding SVG paths
      switch (this.icon) {
        // Formatting
        case 'strikethrough': // S with line through
          return '<text x="12" y="16" font-family="sans-serif" font-size="14" font-weight="bold" text-anchor="middle" dominant-baseline="central" fill="currentColor">S</text><line x1="5" y1="12" x2="19" y2="12" stroke-width="2.5"></line>';
        case 'inlinecode': // Feather 'code' is good, but provide alternative if needed
          // return '<polyline points="7 8 3 12 7 16"></polyline><polyline points="17 8 21 12 17 16"></polyline>'; // Alternative: Angle brackets
          return feather.icons['code']?.contents || this.getFallbackIcon('code'); // Stick with Feather for now
        case 'blockquote': // Stylized quote mark or indent symbol
          // return '<path d="M6 17h3l2-4V7H5v6h3l-2 4zm8 0h3l2-4V7h-6v6h3l-2 4z"></path>'; // Standard double quote marks
          return '<polyline points="10 9 6 9 6 15 10 15"></polyline><polyline points="8 12 18 12"></polyline>'; // Indent symbol

        // LaTeX / Math Symbols
        case 'sigma': // Sigma symbol for main LaTeX menu
           return '<text x="12" y="15" font-family="serif" font-size="18" font-style="italic" text-anchor="middle" dominant-baseline="central" fill="currentColor">∑</text>';
        case 'latex': // Inline Math: $...$
           return '<text x="12" y="15" font-family="monospace" font-size="14" text-anchor="middle" dominant-baseline="central" fill="currentColor">$...$</text>';
        case 'latexBlock': // Display Math: $$...$$
           return '<text x="12" y="15" font-family="monospace" font-size="14" text-anchor="middle" dominant-baseline="central" fill="currentColor">$$...$$</text>';
        case 'equation': // Represents single-line math env: f(x) or Integral ∫
           return '<path d="M7 4v16M17 4v16M7 12h10"/>'; // Looks like Pi, alternative:
           // return '<path d="M9 4v16c-1 0-2 1-2 2s1 2 2 2h6c1 0 2-1 2-2s-1-2-2-2V4c1 0 2-1 2-2s-1-2-2-2H9C8 0 7 1 7 2s1 2 2 2zM9 12h6"/>'; // Stylized 'E' for equation?
           // return '<path d="M10 4v16c0 2 2 3 4 3s4-1 4-3V4"/>'; // Simple integral symbol - Let's use this one
        case 'align': // Represents multi-line aligned math: Stacked lines with alignment point
           return '<line x1="6" y1="8" x2="18" y2="8"></line><line x1="10" y1="12" x2="18" y2="12"></line><line x1="6" y1="16" x2="18" y2="16"></line><circle cx="9" cy="12" r="1" fill="currentColor"></circle><path d="M9 12v-1 M9 12v1"/>'; // Lines + Alignment marker (subtle)
           // Alt: Just stacked lines
           // return '<line x1="6" y1="8" x2="18" y2="8"/><line x1="6" y1="12" x2="18" y2="12"/><line x1="6" y1="16" x2="18" y2="16"/>';
        case 'gather': // Represents multi-line centered math: Centered stacked lines
           return '<line x1="9" y1="8" x2="15" y2="8"></line><line x1="7" y1="12" x2="17" y2="12"></line><line x1="9" y1="16" x2="15" y2="16"></line>';

        // Programming Languages & Frameworks (Keeping existing custom ones)
        case 'python':
           return '<path d="M18 9.5a4.5 4.5 0 0 1-4.5 4.5H10a4.5 4.5 0 0 1 0-9h3.5A4.5 4.5 0 0 1 18 9.5z M6 14.5a4.5 4.5 0 0 1 4.5-4.5H14a4.5 4.5 0 0 1 0 9H10.5A4.5 4.5 0 0 1 6 14.5z"></path><circle cx="7.5" cy="8" r="1.5" fill="currentColor"></circle><circle cx="16.5" cy="16" r="1.5" fill="currentColor"></circle>';
        case 'js':
           return '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><text x="12" y="14.5" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle" dominant-baseline="central" fill="currentColor">JS</text>';
        case 'typescript':
           return '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><text x="12" y="14.5" font-family="sans-serif" font-size="10" font-weight="bold" text-anchor="middle" dominant-baseline="central" fill="currentColor">TS</text>';
        case 'java':
           return '<path d="M18 8h1a4 4 0 0 1 0 8h-1"></path><path d="M2 8h14v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path><line x1="6" y1="1" x2="6" y2="4"></line><line x1="10" y1="1" x2="10" y2="4"></line><line x1="14" y1="1" x2="14" y2="4"></line>';
        case 'cplusplus': case 'c++':
           return '<text x="8.5" y="15" font-family="monospace" font-size="13" font-weight="bold" text-anchor="middle" dominant-baseline="central" fill="currentColor">C</text><path d="M14 11h4M16 9v4M18 15h4M20 13v4"></path>';
        case 'csharp': case 'c#':
           return '<text x="8" y="15" font-family="monospace" font-size="13" font-weight="bold" text-anchor="middle" dominant-baseline="central" fill="currentColor">C</text><path d="M14.5 10l-1.5 8M18.5 10l-1.5 8M13 13h6M13 17h6"></path>';
        case 'go':
           return '<text x="12" y="14.5" font-family="sans-serif" font-size="11" font-weight="bold" text-anchor="middle" dominant-baseline="central" fill="currentColor">Go</text>';
        case 'rust':
           return '<circle cx="12" cy="12" r="6.5"></circle><path d="M12 5.5 V2 M12 18.5 V22 M18.5 12 H22 M5.5 12 H2 M16.6 7.4 L19.5 4.5 M4.5 19.5 L7.4 16.6 M16.6 16.6 L19.5 19.5 M4.5 4.5 L7.4 7.4"></path><path d="M12 9 a3 3 0 0 0 0 6 a3 3 0 0 0 0-6 Z M12 9 L8 15 M12 9 L16 15 M8 15 h8" fill="none"></path>';
        case 'swift':
           return '<path d="M22 12c0 5.52-4.48 10-10 10S2 17.52 2 12 6.48 2 12 2s10 4.48 10 10z M14.5 7.8c-2.9 2.3-5.45 3.85-7.35 4.65 M9.5 16.2c2.9-2.3 5.45-3.85 7.35-4.65"></path>';
        case 'kotlin':
           return '<path d="M3 3h18v18H3z"></path><path d="M3 3l9 9L3 21 M12 12l9-9v18l-9-9"></path>';
        case 'r-project':
           return '<circle cx="12" cy="12" r="10"></circle><text x="12" y="14.5" font-family="sans-serif" font-size="12" font-weight="bold" text-anchor="middle" dominant-baseline="central" fill="currentColor">R</text>';
        case 'html5':
           return '<path d="M4 3l1.5 16.5L12 22l6.5-2.5L20 3H4zm12.5 3.5H7.5l.5 5.5h8l-.5 5.5-3.5 1.5-3.5-1.5-.25-3h-2.5l.5 6 5.75 2 5.75-2 1-11.5h-11z"></path>';
        case 'css3':
           return '<path d="M4 3l1.5 16.5L12 22l6.5-2.5L20 3H4zm12.5 3.5h-9l.25 3h8.5l-.5 5-3.25 1-3.25-1-.25-2.5h-2.5l.5 5 5.5 1.5 5.5-1.5 1-10h-11z"></path>';
        case 'vuejs':
           return '<path d="M2 3l10 17L22 3H17l-5 10L7 3H2z"></path><path d="M7 3l5 10 5-10H7z"></path>';
        case 'react':
           return '<circle cx="12" cy="12" r="2"></circle><ellipse cx="12" cy="12" rx="11" ry="4.2"></ellipse><ellipse cx="12" cy="12" rx="11" ry="4.2" transform="rotate(60 12 12)"></ellipse><ellipse cx="12" cy="12" rx="11" ry="4.2" transform="rotate(120 12 12)"></ellipse>';
        case 'angular':
           return '<path d="M12 2L2 7l2 14 8 2 8-2 2-14L12 2zm0 3l7.5 3.5-1.5 10h-12l-1.5-10L12 5z"></path><path d="M12 8l-4 8h2.5l1.5-3h3l1.5 3H16l-4-8z"></path>';

        // Data Formats & Markup
        case 'xml':
          return '<polyline points="7 8 3 12 7 16"></polyline><polyline points="17 8 21 12 17 16"></polyline>';
        case 'json':
           return '<path d="M8 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h1 M16 3h1a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-1"></path><path d="M10 9a2 2 0 1 0-4 0v6a2 2 0 1 0 4 0 M18 9a2 2 0 1 0-4 0v6a2 2 0 1 0 4 0"></path>';
        case 'yaml':
           return '<line x1="6" y1="8" x2="18" y2="8"></line><line x1="8" y1="12" x2="18" y2="12"></line><line x1="8" y1="16" x2="18" y2="16"></line>';
        case 'markdown':
           return '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><path d="M7 15V9l3 3 3-3v6 M17 11l-3-3-3 3"></path>';
        // Removed 'latex' text case here as it's handled by $...$ above

        // Shells & Tools
        case 'bash':
          return feather.icons['terminal']?.contents || this.getFallbackIcon('terminal');
        case 'powershell':
           return (feather.icons['terminal']?.contents || '') + '<path d="M15 15 l 3 2 l-3 2" stroke-width="1.5"></path>' || this.getFallbackIcon('terminal');
        case 'perl':
           return '<path d="M12 2a10 10 0 0 0-7.5 16.8 1 1 0 0 0 .5.2h14a1 1 0 0 0 .5-.2A10 10 0 0 0 12 2zm0 3a7 7 0 0 1 5.3 11.8 1 1 0 0 1-.3.2H7a1 1 0 0 1-.3-.2A7 7 0 0 1 12 5z"></path><path d="M12 11a2 2 0 1 0 0 4 2 2 0 0 0 0-4z"></path>';
        case 'mermaid':
           return '<rect x="4" y="4" width="6" height="6" rx="1"></rect><rect x="14" y="4" width="6" height="6" rx="1"></rect><rect x="4" y="14" width="6" height="6" rx="1"></rect><rect x="14" y="14" width="6" height="6" rx="1"></rect><line x1="7" y1="10" x2="7" y2="14"></line><line x1="17" y1="10" x2="17" y2="14"></line><line x1="10" y1="7" x2="14" y2="7"></line><line x1="10" y1="17" x2="14" y2="17"></line>';
        case 'graphviz':
           return '<circle cx="6" cy="6" r="3"></circle><circle cx="18" cy="18" r="3"></circle><circle cx="6" cy="18" r="3"></circle><line x1="8.1" y1="7.5" x2="15.9" y2="16.5"></line><line x1="6" y1="15" x2="6" y2="9"></line><line x1="8.1" y1="16.5" x2="15.9" y2="7.5"></line>';
        case 'plantuml':
           return '<rect x="3" y="8" width="8" height="8" rx="1"></rect><rect x="13" y="8" width="8" height="8" rx="1"></rect><line x1="7" y1="16" x2="7" y2="20"></line><line x1="17" y1="16" x2="17" y2="20"></line><line x1="7" y1="20" x2="17" y2="20"></line><line x1="12" y1="12" x2="16" y2="8"></line>';

        // Databases
        case 'sql':
           return feather.icons['database']?.contents || this.getFallbackIcon('database');
        case 'mongodb':
           return '<path d="M15.75 2.5A10.16 10.16 0 0012 2 10 10 0 002.03 11.1a.5.5 0 01.47.5v.8a.5.5 0 01-.5.5A10 10 0 0012 22a10.16 10.16 0 003.75-.5.5.5 0 01.5.5v.8a.5.5 0 01-.5.5 10 10 0 00-8.22-8.22.5.5 0 01.5-.5h.8a.5.5 0 01.5.47A10 10 0 0022 12a10.16 10.16 0 00-.5-3.75.5.5 0 01.5-.5h.8a.5.5 0 01.47.5A10 10 0 0012.9 21.97a.5.5 0 01-.5-.47v-.8a.5.5 0 01.5-.5A10 10 0 0015.75 2.5zm-1.5 6A4.25 4.25 0 1112 12.25 4.25 4.25 0 0114.25 8.5z"></path>';

        // --- Fallback ---
        default:
          // Return fallback if no Feather or Custom icon matched
          return this.getFallbackIcon(this.icon);
      }
    }
  },
  methods: {
    emit_click(event){
      this.$emit('click', event);
    },
    getFallbackIcon(iconName = 'unknown') {
      console.warn(`ToolbarButton: Icon "${iconName}" not found in Feather or custom definitions. Using fallback.`);
      // Feather 'help-circle' is a good fallback
      return feather.icons['help-circle']?.contents || '<circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line>'; // Fallback's fallback
    }
  },
  mounted() {
    // If using text elements, ensure they inherit color correctly
    // This might be handled by CSS, but can be double-checked if issues arise.
  }
}
</script>

<style scoped>
.svg-button {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem; /* Add some padding for better click area */
  border-radius: 0.25rem; /* Slightly round corners */
  transition: background-color 0.15s ease-in-out;
  gap: 0.25rem; /* Add gap between icon and slot content */
}
.svg-button:hover {
   background-color: rgba(128, 128, 128, 0.1); /* Subtle hover */
}
.dark .svg-button:hover {
  background-color: rgba(128, 128, 128, 0.2); /* Subtle hover dark */
}

/* Ensure SVG and text elements inherit color and have consistent stroke */
.svg-button svg {
  stroke: currentColor; /* Inherit color for stroke by default */
}
.svg-button svg text {
  fill: currentColor; /* Inherit color for fill */
  stroke: none; /* Text usually shouldn't have a stroke */
  paint-order: stroke fill; /* Ensure fill is drawn on top of potential stroke */
}
/* Override stroke for specific text elements if needed, e.g., for outlined text */
/* .svg-button svg text.outlined { stroke: currentColor; stroke-width: 0.5px; } */

/* Ensure elements with explicit fill="currentColor" work */
.svg-button svg [fill="currentColor"] {
    fill: currentColor;
}
/* Ensure elements with explicit stroke="currentColor" work */
.svg-button svg [stroke="currentColor"] {
    stroke: currentColor;
}
</style>