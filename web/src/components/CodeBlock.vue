<template>
  <div :id="`code-block-container-${message_id}`" class="code-block-container bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel p-2 rounded-lg shadow-sm mb-4">

    <!-- == Function Call Display (language="function") == -->
    <div v-if="isFunctionLanguage">
      <!-- Top Bar -->
      <div class="flex justify-between items-center px-2 py-1 mb-1 rounded-t-lg bg-gray-200 dark:bg-gray-700">
        <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">
          <i data-feather="zap" class="w-3 h-3 inline-block mr-1 feather-small"></i> Function Call
        </span>
        <div class="flex flex-row space-x-1">
           <button @click="executeCode" :title="executeTitle" class="code-block-button execute-button" :disabled="isExecuting || !isValidFunctionCall" aria-label="Execute Function Call">
             <i :data-feather="executeIcon" :class="{'animate-spin': isExecuting}" class="w-4 h-4"></i>
           </button>
           <button @click="toggleFunctionDetails" :title="isFunctionDetailsVisible ? 'Hide Details' : 'Show Details'" class="code-block-button" aria-label="Toggle Function Details">
              <i :data-feather="isFunctionDetailsVisible ? 'chevron-up' : 'chevron-down'" class="w-4 h-4"></i>
           </button>
        </div>
      </div>
      <!-- Body -->
      <div class="p-2 rounded-b-md bg-white dark:bg-gray-800">
        <div class="flex items-center space-x-2 text-sm mb-1 cursor-pointer hover:opacity-80" @click="toggleFunctionDetails" role="button" :aria-expanded="isFunctionDetailsVisible">
          <span class="font-semibold text-gray-700 dark:text-gray-300">Function:</span>
          <span v-if="isValidFunctionCall" class="font-mono bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-gray-900 dark:text-gray-100 break-all">{{ functionName }}</span>
          <span v-else class="flex items-center text-amber-600 dark:text-amber-400">
             <i data-feather="alert-circle" class="w-4 h-4 mr-1 feather-small"></i> Invalid / Incomplete
          </span>
        </div>
        <!-- Details -->
        <div v-show="isFunctionDetailsVisible" class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700 max-h-60 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600">
           <div v-if="isValidFunctionCall">
               <h4 class="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 mb-2 sticky top-0 bg-white dark:bg-gray-800 py-1">Parameters:</h4>
               <div v-if="hasParameters" class="space-y-2">
                   <div v-for="(value, key) in functionParametersObject" :key="key" class="parameter-item">
                       <div class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-0.5">{{ key }}:</div>
                       <!-- Display Logic for Parameters -->
                       <div v-if="typeof value === 'object' && value !== null" class="text-xs font-mono bg-gray-100 dark:bg-gray-700 p-1 rounded text-gray-900 dark:text-gray-100 whitespace-pre-wrap break-words">
                           {{ JSON.stringify(value, null, 2) }}
                       </div>
                       <div v-else-if="typeof value === 'boolean'" class="text-sm font-mono text-blue-600 dark:text-blue-400"> {{ String(value) }} </div>
                       <div v-else-if="typeof value === 'number'" class="text-sm font-mono text-green-700 dark:text-green-400"> {{ value }} </div>
                       <div v-else-if="value === null" class="text-sm font-mono text-purple-600 dark:text-purple-400">null</div>
                       <div v-else class="text-sm font-mono bg-gray-100 dark:bg-gray-700 p-1 rounded text-gray-900 dark:text-gray-100 whitespace-pre-wrap break-words">"{{ String(value) }}"</div>
                   </div>
               </div>
               <span v-else class="text-xs text-gray-500 italic">No parameters provided.</span>
           </div>
           <div v-else>
             <h4 class="text-xs font-semibold uppercase text-red-600 dark:text-red-400 mb-1">Invalid JSON Input:</h4>
             <pre class="text-xs font-mono bg-red-50 dark:bg-red-900/20 p-2 rounded max-h-48 overflow-y-auto text-red-800 dark:text-red-300 whitespace-pre-wrap break-all">{{ safeCodeProp || '(empty)' }}</pre>
           </div>
        </div>
      </div>
    </div>

    <!-- == Standard Code Block Display == -->
    <div v-else v-memo="[safeCodeProp, safeLanguageProp, isSearchVisible, canUndo, canRedo]">
      <!-- Top Bar -->
       <div class="flex justify-between items-center px-2 py-1 mb-1 rounded-t-lg bg-gray-200 dark:bg-gray-700">
           <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ effectiveLanguage || 'plaintext' }}</span>
           <div class="flex flex-row space-x-1 items-center">
               <!-- Undo/Redo Buttons -->
               <button @click="undo" :disabled="!canUndo" title="Undo (Ctrl+Z)" class="code-block-button" aria-label="Undo Edit"><i data-feather="rotate-ccw" class="w-4 h-4"></i></button>
               <button @click="redo" :disabled="!canRedo" title="Redo (Ctrl+Y)" class="code-block-button" aria-label="Redo Edit"><i data-feather="rotate-cw" class="w-4 h-4"></i></button>
                <!-- Separator -->
               <div class="h-4 w-px bg-gray-400 dark:bg-gray-600 mx-1"></div>
               <!-- Other Buttons -->
               <button @click="toggleSearch" :title="isSearchVisible ? 'Hide Search' : 'Show Search'" class="code-block-button" aria-label="Toggle Search">
                  <i :data-feather="isSearchVisible ? 'x' : 'search'" class="w-4 h-4"></i>
               </button>
               <button @click="copyCode" :title="copyTitle" class="code-block-button" aria-label="Copy Code"><i :data-feather="copyIcon" class="w-4 h-4"></i></button>
               <button v-if="canExecute" @click="executeCode" :title="executeTitle" class="code-block-button execute-button" :disabled="isExecuting" aria-label="Execute Code"><i :data-feather="executeIcon" :class="{'animate-spin': isExecuting}" class="w-4 h-4"></i></button>
               <button v-if="canExecuteInNewTab" @click="executeCode_in_new_tab" :title="executeNewTabTitle" class="code-block-button execute-button" :disabled="isExecuting" aria-label="Execute Code in New Tab"><i :data-feather="executeNewTabIcon" :class="{'animate-spin': isExecuting}" class="w-4 h-4"></i></button>
               <button @click="openFolder" title="Open Project Folder" class="code-block-button" aria-label="Open Project Folder"><i data-feather="folder" class="w-4 h-4"></i></button>
               <button v-if="canOpenFolderInVsCode" @click="openFolderVsCode" title="Open Project Folder in VS Code" class="code-block-button" aria-label="Open Project Folder in VS Code"><img src="@/assets/vscode_black.svg" class="w-4 h-4 dark:hidden" alt="VS Code"><img src="@/assets/vscode.svg" class="w-4 h-4 hidden dark:inline" alt="VS Code"></button>
               <button v-if="canOpenInVsCode" @click="openVsCode" title="Open Code in VS Code" class="code-block-button" aria-label="Open Code in VS Code"><img src="@/assets/vscode.svg" class="w-4 h-4" alt="VS Code"></button>
           </div>
       </div>

      <!-- Search/Replace Panel -->
      <div v-if="isSearchVisible" class="search-replace-panel flex items-center space-x-2 p-2 bg-gray-100 dark:bg-gray-700 text-sm mb-1 rounded">
        <input
          ref="searchInputRef"
          type="text"
          v-model.lazy="searchQuery"
          placeholder="Find"
          class="search-input flex-grow"
          aria-label="Search query"
          @keydown.enter.prevent="findNextAndHighlight"
          @keydown.shift.enter.prevent="findPreviousAndHighlight"
        />
        <span v-if="searchQuery" class="search-status" aria-live="polite">
           {{ searchResults.length > 0 ? `${currentMatchIndexDisplay + 1} / ${searchResults.length}` : 'Not found' }}
        </span>
         <span v-else class="search-status text-gray-400 dark:text-gray-500" aria-live="polite"> <!-- Placeholder when query is empty -->
           
        </span>
        <button @click="findPreviousAndHighlight" :disabled="!hasMatches" title="Previous Match (Shift+Enter)" class="code-block-button search-button" aria-label="Previous Match"><i data-feather="chevron-left" class="w-4 h-4"></i></button>
        <button @click="findNextAndHighlight" :disabled="!hasMatches" title="Next Match (Enter)" class="code-block-button search-button" aria-label="Next Match"><i data-feather="chevron-right" class="w-4 h-4"></i></button>
        <input
          type="text"
          v-model="replaceQuery"
          placeholder="Replace with"
          class="replace-input flex-grow"
          aria-label="Replace query"
          @keydown.enter.prevent="replaceCurrentAndFindNext"
        />
        <button @click="replaceCurrent" :disabled="!hasActiveMatch" title="Replace Current" class="code-block-button search-button" aria-label="Replace Current">Replace</button>
        <button @click="replaceAll" :disabled="!hasMatches" title="Replace All" class="code-block-button search-button" aria-label="Replace All">All</button>
      </div>

      <!-- Code Area Wrapper -->
      <div ref="codeAreaWrapper" class="code-area-wrapper max-h-96 overflow-y-auto rounded-b-md bg-white dark:bg-gray-800 scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
         <!-- Apply line-height here for synchronization -->
        <div class="code-content-flex flex font-mono text-sm leading-snug">
          <!-- Line Numbers -->
          <div class="line-numbers flex-shrink-0 p-2 text-right text-gray-500 select-none bg-gray-100 dark:bg-gray-700 whitespace-pre overflow-y-hidden border-r border-gray-300 dark:border-gray-600" v-html="lineNumbersHtml" aria-hidden="true"></div>
          <!-- Code Content - Editable -->
          <div
            ref="codeContentEditable"
            class="code-content hljs flex-grow p-2 whitespace-pre-wrap break-words overflow-x-auto overflow-y-hidden scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-400 dark:scrollbar-thumb-gray-500 focus:outline-none"
            contenteditable="true" spellcheck="false" role="textbox" aria-multiline="true"
            :aria-label="`Code block (${effectiveLanguage || 'plaintext'})`"
            @input="debouncedHandleInput"
            @paste="handlePaste"
            @keydown.enter.prevent="handleEnterKey"
            @keydown.tab.prevent="handleTabKey"
            @blur="handleBlur"
            @click="clearSelectionIfOutsideSearch"
            @keydown="handleUndoRedoKeys"
          ></div> <!-- Content managed programmatically -->
        </div>
      </div>
    </div>

    <!-- == Execution Output (Common) - Renders Sanitized HTML == -->
    <div v-if="executionOutput" class="mt-2" aria-live="polite">
      <span class="text-lg font-semibold text-gray-700 dark:text-gray-300">Execution Output:</span>
      <div
        class="execution-output-content hljs mt-1 p-2 rounded-md break-words text-sm leading-relaxed bg-white dark:bg-gray-800 max-h-48 overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary"
        v-html="sanitizedExecutionOutputHtml">
      </div>
    </div>

  </div>
</template>

<script>
import { nextTick } from 'vue';
import hljs from 'highlight.js';
import feather from 'feather-icons';
import DOMPurify from 'dompurify';
import { debounce } from 'lodash-es';

// Import themes
import 'highlight.js/styles/github.css'; // Light theme for hljs
import 'highlight.js/styles/tokyo-night-dark.css'; // Dark theme for hljs

// --- Constants ---
const EXECUTABLE_LANGUAGES = new Set(['function', 'python', 'sh', 'shell', 'bash', 'cmd', 'powershell', 'latex', 'mermaid', 'graphviz', 'dot', 'javascript', 'html', 'html5', 'svg', 'lilypond']);
const NEW_TAB_EXECUTABLE_LANGUAGES = new Set(['airplay', 'mermaid', 'graphviz', 'dot', 'javascript', 'html', 'html5', 'svg', 'css']);
const VSCODE_SUPPORTED_LANGUAGES = new Set([
    'python', 'latex', 'html', 'javascript', 'typescript', 'css', 'scss', 'less',
    'json', 'yaml', 'markdown', 'java', 'csharp', 'php', 'ruby', 'go', 'rust',
    'shell', 'bash', 'powershell'
]);
const SEARCH_DEBOUNCE_MS = 200;
const UNDO_STACK_LIMIT = 50;
const INPUT_DEBOUNCE_MS = 250;

// --- Helpers ---
function escapeHtml(unsafe) {
    // Basic escaping, sufficient for use with highlight.js which handles further complexities
    return typeof unsafe === 'string' ? unsafe
         .replace(/&/g, "&") // Must be first
         .replace(/</g, "<")
         .replace(/>/g, ">")
         .replace(/"/g, "\"")
         .replace(/'/g, "'") : '';
}

function getHighlightedHtml(code, language) {
    const codeToHighlight = typeof code === 'string' ? code : '';
    try {
        const effectiveLang = hljs.getLanguage(language) ? language : 'plaintext';
        // No need to manually escape before hljs.highlightAuto or hljs.highlight
        // It expects raw text. Let hljs handle escaping internally.
        // Use highlight instead of highlightAuto if language is known for better accuracy
        const result = hljs.highlight(codeToHighlight, { language: effectiveLang, ignoreIllegals: true });

        // Ensure trailing newline visually renders if present in original code
        let finalHtml = result.value;
        if (codeToHighlight.endsWith('\n') && !finalHtml.endsWith('<br>')) {
             // Check if the last element isn't already implying a break
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = finalHtml;
            const lastChild = tempDiv.lastChild;
             let endsWithBreakEquivalent = false;
             if (lastChild?.nodeName === 'BR') {
                endsWithBreakEquivalent = true;
             } else if (lastChild?.nodeType === Node.TEXT_NODE && lastChild.textContent?.endsWith('\n')) {
                endsWithBreakEquivalent = true; // Although hljs usually converts \n to <br>
            }
             if (!endsWithBreakEquivalent) {
                 finalHtml += '<br>';
             }
        }
        // Replace remaining newlines (e.g., within comments) with <br> for consistent rendering in pre-wrap
        // Note: hljs typically handles this, but this ensures it if its output is inconsistent
         //return finalHtml.replace(/(?<!<br>)\n/g, '<br>');
         return finalHtml; // Let hljs handle newline conversion primarily

    } catch (e) {
        console.error("Highlighting error:", e, "Lang:", language, "Code snippet:", codeToHighlight.substring(0, 100));
        // Fallback: escape and replace newlines
        return escapeHtml(codeToHighlight).replace(/\n/g, '<br>');
    }
}

function getTextNodeAndOffset(parentElement, charIndex) {
    let node = null;
    let offset = -1;
    let currentTotalIndex = 0;
    const walker = document.createTreeWalker(parentElement, NodeFilter.SHOW_TEXT, null, false);

    while (node = walker.nextNode()) {
        const nodeLength = node.textContent?.length || 0;
        if (currentTotalIndex <= charIndex && charIndex <= currentTotalIndex + nodeLength) {
            offset = charIndex - currentTotalIndex;
            // Ensure offset is not beyond the node's actual length (can happen at boundaries)
            offset = Math.min(offset, nodeLength);
            return { node, offset };
        }
        currentTotalIndex += nodeLength;
    }

    // Handle case where the index is exactly at the end of the text content
     if (charIndex === currentTotalIndex) {
       // Try to find the last text node
       let lastTextNode = null;
       const walkerReverse = document.createTreeWalker(parentElement, NodeFilter.SHOW_TEXT, null, false);
       while(walkerReverse.nextNode()) { lastTextNode = walkerReverse.currentNode; }

       if (lastTextNode) {
          return { node: lastTextNode, offset: lastTextNode.textContent?.length || 0 };
       }
    }

    // Fallback or if index is out of bounds
    console.warn(`getTextNodeAndOffset: Could not find node/offset for index ${charIndex}. Parent text length: ${parentElement?.innerText?.length}. Returning null.`);
    return null;
}


export default {
  name: 'CodeBlock',
  props: {
    host: { type: String, required: false, default: "http://localhost:9600" },
    language: { type: String, required: true },
    code: { type: String, required: true },
    client_id: { type: String, required: true },
    discussion_id: { type: [String, Number], required: true },
    message_id: { type: [String, Number], required: true },
  },
  emits: ['update-code'],

  data() {
    return {
      // --- State ---
      isExecuting: false,
      isCopied: false,
      executionOutput: '',
      copyTimeout: null,
      isComponentMounted: false,
      isFunctionDetailsVisible: false,
      internalCode: '', // Internal state for editable code

      // --- Search/Replace State ---
      isSearchVisible: false,
      searchQuery: '',
      replaceQuery: '',
      searchResults: [], // Array of { start: number, end: number }
      currentMatchIndex: -1, // Index in searchResults array

      // --- Undo/Redo State ---
      undoStack: [], // Stores previous code states (strings)
      redoStack: [], // Stores undone code states (strings)
      isApplyingUndoRedo: false, // Flag to prevent snapshot during undo/redo

      // --- Debounced function references ---
      debouncedHandleInput: null, // Initialized in created()
      debouncedFindMatches: null, // Initialized in created()
    };
  },

  computed: {
    // --- Computed: Undo/Redo ---
    canUndo() { return this.undoStack.length > 0; },
    canRedo() { return this.redoStack.length > 0; },

    // --- Safe Computed Props ---
    safeCodeProp() { return typeof this.code === 'string' ? this.code : ''; },
    safeLanguageProp() { return typeof this.language === 'string' ? this.language : ''; },

    // --- Language Info ---
    normalizedLanguage() { return this.safeLanguageProp.trim().toLowerCase(); },
    isFunctionLanguage() { return this.normalizedLanguage === 'function'; },
    canExecute() { return EXECUTABLE_LANGUAGES.has(this.normalizedLanguage); },
    canExecuteInNewTab() { return NEW_TAB_EXECUTABLE_LANGUAGES.has(this.normalizedLanguage); },
    canOpenFolderInVsCode() { return VSCODE_SUPPORTED_LANGUAGES.has(this.normalizedLanguage); }, // Assumes context allows this
    canOpenInVsCode() { return VSCODE_SUPPORTED_LANGUAGES.has(this.normalizedLanguage); },

    // --- Computed Properties ---
    effectiveLanguage() {
        const lang = this.normalizedLanguage;
        if (this.isFunctionLanguage) return 'json'; // Treat function body as JSON
        if (['vue', 'vue.js'].includes(lang)) return 'html';
        if (lang === 'html5') return 'html';
        if (['shell', 'sh', 'bash', 'cmd', 'powershell'].includes(lang)) return 'bash';
        if (lang === 'dot') return 'graphviz';
        return hljs.getLanguage(lang) ? lang : 'plaintext';
    },

    // Function Block Computeds
    parsedFunctionCall() {
        if (!this.isFunctionLanguage || !this.safeCodeProp) return null;
        try {
            const parsed = JSON.parse(this.safeCodeProp);
            // Basic validation: must be an object with function_name (string) and function_parameters (object)
            if (typeof parsed === 'object' && parsed !== null &&
                typeof parsed.function_name === 'string' && parsed.function_name.trim() !== '' &&
                typeof parsed.function_parameters === 'object' && // Allow null/empty object
                parsed.function_parameters !== undefined) { // Check for existence
                return parsed;
            }
            return null;
        } catch (e) {
            // console.warn("Failed to parse function call JSON:", e);
            return null; // Invalid JSON
        }
    },
    isValidFunctionCall() { return this.parsedFunctionCall !== null; },
    functionName() { return this.parsedFunctionCall?.function_name ?? 'N/A'; },
    functionParametersObject() { return this.parsedFunctionCall?.function_parameters ?? {}; },
    hasParameters() { return Object.keys(this.functionParametersObject).length > 0; },

    // Line Numbers (Standard Blocks)
    lineNumbersHtml() {
        if (this.isFunctionLanguage) return '';
        // Use internalCode for editable blocks as it reflects the current state
        const codeSource = this.internalCode;
        try {
            const lines = codeSource.split('\n');
            // Handle empty string case (should be 1 line number)
            const lineCount = (lines.length === 1 && lines[0] === '') ? 1 : lines.length;
            const lineNumberWidth = Math.max(1, String(lineCount).length); // Ensure at least 1 digit width
            let numbers = '';
            for (let i = 1; i <= lineCount; i++) {
                // Pad start for alignment and add line break for HTML rendering
                numbers += `${String(i).padStart(lineNumberWidth, ' ')}<br>`;
            }
            // Remove trailing <br> only if the code doesn't end with a newline
            // and we actually added one too many.
            if (!codeSource.endsWith('\n') && numbers.endsWith('<br>')) {
                 // Check if the code wasn't empty, otherwise keep the single <br> for line 1
                 if (codeSource !== '' || lineCount > 1) {
                    numbers = numbers.slice(0, -4);
                 }
            }
            // Edge case: If code is "" (empty), we should have "1<br>" -> "1" after slice. Fix:
            if (codeSource === '' && numbers === '') return '1';

            return numbers;
        } catch (e) {
            console.error("Error calculating line numbers:", e);
            return 'Err'; // Indicate error in line numbers
        }
    },

    // --- Sanitized HTML Output ---
    sanitizedExecutionOutputHtml() {
        return DOMPurify.sanitize(this.executionOutput, {
             USE_PROFILES: { html: true },
             // Allow specific tags needed for common outputs like Mermaid, Graphviz, basic HTML
             ADD_TAGS: ['iframe', 'svg', 'path', 'g', 'circle', 'rect', 'line', 'polyline', 'polygon', 'text', 'tspan', 'style', 'defs', 'marker', 'use'],
             // Allow attributes needed by these tags + basic styling/links
             ADD_ATTS: ['style', 'transform', 'cx', 'cy', 'r', 'x', 'y', 'width', 'height', 'fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'points', 'd', 'marker-start', 'marker-end', 'viewBox', 'preserveAspectRatio', 'class', 'id', 'href', 'target', 'text-anchor', 'dominant-baseline', 'font-size', 'font-family', 'dy', 'aria-label'],
             ALLOW_DATA_ATTR: true, // Allow data-* attributes
             ALLOW_UNKNOWN_PROTOCOLS: false, // Prevent protocols like javascript:
             FORBID_TAGS: ['script'], // Disallow script tags
             FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur'] // Disallow dangerous event handlers
        });
    },

    // UI Computeds for button states/icons
    copyIcon() { return this.isCopied ? 'check' : 'copy'; },
    copyTitle() { return this.isCopied ? 'Copied!' : 'Copy code'; },
    executeIcon() { return this.isExecuting ? 'loader' : 'play-circle'; },
    executeTitle() { return this.isExecuting ? 'Executing...' : (this.isFunctionLanguage ? 'Execute Function Call' : 'Execute Code'); },
    executeNewTabIcon() { return this.isExecuting ? 'loader' : 'airplay'; },
    executeNewTabTitle() { return this.isExecuting ? 'Executing...' : 'Execute Code in New Tab'; },

    // Search/Replace UI Computeds
    hasMatches() { return this.searchResults.length > 0; },
    hasActiveMatch() { return this.currentMatchIndex >= 0 && this.currentMatchIndex < this.searchResults.length; },
    // Display index is 1-based, but ensure it's at least 1 even if index is 0
    currentMatchIndexDisplay() { return this.hasActiveMatch ? this.currentMatchIndex : -1; }, // Use -1 for no selection
  },

  watch: {
    // Watch the external `code` prop for changes
    code(newCode) {
        const newSafeCode = typeof newCode === 'string' ? newCode : '';
        // Only update if the component is mounted and the prop differs from internal state
        // Prevents overwriting user edits if the prop update was triggered by this component's emit
        if (!this.isComponentMounted || newSafeCode === this.internalCode) {
             return;
        }

        console.log("External 'code' prop changed. Updating internal state.");
        if (!this.isFunctionLanguage && this.$refs.codeContentEditable) {
            // Reset internal state and history when prop changes externally
            this.internalCode = newSafeCode;
            this.applyHighlighting(newSafeCode); // Update display
            this.undoStack = [newSafeCode]; // Reset history, start with new code
            this.redoStack = [];
            this.clearSearchState(true); // Reset search
        } else if (this.isFunctionLanguage) {
            // Function blocks are not editable, just reflect the prop change
            // No internalCode or undo stack needed for function blocks
             this.triggerIconUpdate(); // Update icons if needed (e.g., chevron)
        }
    },
    // Watch the internal `searchQuery` model for live search
    searchQuery() {
      // When query changes, reset index to -1 (no selection) and run debounced search
      this.currentMatchIndex = -1;
      this.debouncedFindMatches(); // Call the debounced method
    },
  },

  methods: {
    // --- Get Current Code ---
    getActualCode() {
        if (this.isFunctionLanguage) {
            return this.safeCodeProp; // Function blocks read directly from prop
        }
        // For standard blocks, use the internal state reflecting edits
        return this.internalCode;
        // Or, less reliably for complex content: return this.$refs.codeContentEditable?.innerText ?? this.internalCode;
    },

    // --- Snapshot State for Undo/Redo ---
    snapshotState(currentState) {
        if (this.isFunctionLanguage || this.isApplyingUndoRedo) return; // Don't snapshot during undo/redo
        const previousState = this.undoStack.length > 0 ? this.undoStack[this.undoStack.length - 1] : null;
        // Only push if the state has actually changed
        if (previousState !== currentState) {
             this.undoStack.push(currentState);
             // Limit stack size
             if (this.undoStack.length > UNDO_STACK_LIMIT) {
                 this.undoStack.shift(); // Remove oldest entry
             }
             // Clear redo stack whenever a new action is taken
             if (this.redoStack.length > 0) {
                 this.redoStack = [];
             }
            //  console.log("Snapshot:", currentState.substring(0, 20), "Undo Size:", this.undoStack.length);
             this.triggerIconUpdate(); // Update undo/redo button states
        }
    },

    // --- Undo/Redo Actions ---
    undo() {
        if (!this.canUndo || this.isFunctionLanguage || !this.$refs.codeContentEditable) return;
        this.isApplyingUndoRedo = true; // Prevent snapshotting this change
        const currentState = this.internalCode; // Get current state *before* popping
        const prevState = this.undoStack.pop();

        if (prevState !== undefined) {
            this.redoStack.push(currentState); // Push current state to redo stack
            this.internalCode = prevState;
            this.applyHighlighting(this.internalCode); // Update display
            this.$emit('update-code', this.internalCode); // Emit change
            this.clearSearchState(); // Clear search highlights on undo
            this.triggerIconUpdate(); // Update button states
            // console.log("Undo Applied. New code:", this.internalCode.substring(0, 20));
            this.$nextTick(() => {
                this.$refs.codeContentEditable?.focus(); // Restore focus
                 this.placeCursorAtEnd(this.$refs.codeContentEditable); // Move cursor to end after undo
            });
        }
        this.isApplyingUndoRedo = false;
    },
    redo() {
        if (!this.canRedo || this.isFunctionLanguage || !this.$refs.codeContentEditable) return;
         this.isApplyingUndoRedo = true; // Prevent snapshotting this change
        const nextState = this.redoStack.pop();

        if (nextState !== undefined) {
            const currentState = this.internalCode; // Get current state *before* applying redo
            this.undoStack.push(currentState); // Push current state back to undo stack
             if (this.undoStack.length > UNDO_STACK_LIMIT) this.undoStack.shift(); // Maintain limit

            this.internalCode = nextState;
            this.applyHighlighting(this.internalCode); // Update display
            this.$emit('update-code', this.internalCode); // Emit change
            this.clearSearchState(); // Clear search highlights on redo
            this.triggerIconUpdate(); // Update button states
             // console.log("Redo Applied. New code:", this.internalCode.substring(0, 20));
            this.$nextTick(() => {
                 this.$refs.codeContentEditable?.focus(); // Restore focus
                 this.placeCursorAtEnd(this.$refs.codeContentEditable); // Move cursor to end after redo
            });
        }
         this.isApplyingUndoRedo = false;
    },
    handleUndoRedoKeys(event) {
        if (this.isFunctionLanguage) return;
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        const isUndo = (isMac && event.metaKey && !event.shiftKey && event.key === 'z') || (!isMac && event.ctrlKey && !event.shiftKey && event.key === 'z');
        const isRedo = (isMac && event.metaKey && event.shiftKey && event.key === 'z') || (!isMac && event.ctrlKey && event.key === 'y'); // Ctrl+Y or Ctrl+Shift+Z on some systems

        if (isUndo) {
            event.preventDefault();
            this.undo();
        } else if (isRedo) {
            event.preventDefault();
            this.redo();
        }
    },

    // --- Manual Highlighting & State Update ---
    applyHighlighting(codeToHighlight, preserveSelection = false) {
        if (this.isFunctionLanguage || !this.$refs.codeContentEditable) return;

        const editor = this.$refs.codeContentEditable;
        let savedSelState = null;

        // --- Save Selection ---
        if (preserveSelection && document.activeElement === editor) {
            const sel = window.getSelection();
            if (sel && sel.rangeCount > 0 && editor.contains(sel.anchorNode)) {
                try {
                    const range = sel.getRangeAt(0);
                    let charCount = 0;
                    let startOffset = -1, endOffset = -1;

                    // Calculate start character index
                    const preSelectionRange = document.createRange();
                    preSelectionRange.selectNodeContents(editor);
                    preSelectionRange.setEnd(range.startContainer, range.startOffset);
                    startOffset = preSelectionRange.toString().length;

                    // Calculate end character index
                    endOffset = startOffset + range.toString().length;

                    if (startOffset !== -1 && endOffset !== -1) {
                        savedSelState = { start: startOffset, end: endOffset };
                    } else {
                         console.warn("Could not accurately determine selection char indices.");
                    }

                } catch (e) {
                    console.warn("Could not save selection state:", e);
                }
            }
        }

        // --- Apply Highlighting ---
        // Ensure code is a string
        const currentCode = typeof codeToHighlight === 'string' ? codeToHighlight : '';
        // Get highlighted HTML (let hljs handle escaping)
        const highlightedHtml = getHighlightedHtml(currentCode, this.effectiveLanguage);
        // Update the contenteditable div's HTML
        editor.innerHTML = highlightedHtml;

        // --- Restore Selection ---
        if (savedSelState) {
           this.$nextTick(() => {
               try {
                   const startPos = getTextNodeAndOffset(editor, savedSelState.start);
                   const endPos = getTextNodeAndOffset(editor, savedSelState.end);

                   if (startPos && endPos) {
                       const newRange = document.createRange();
                       // Ensure offsets are within the bounds of the identified nodes
                       const safeStartOffset = Math.min(startPos.offset, startPos.node.textContent?.length ?? 0);
                       const safeEndOffset = Math.min(endPos.offset, endPos.node.textContent?.length ?? 0);

                       newRange.setStart(startPos.node, safeStartOffset);
                       newRange.setEnd(endPos.node, safeEndOffset);

                       const sel = window.getSelection();
                       sel?.removeAllRanges();
                       sel?.addRange(newRange);
                   } else {
                        console.warn("Could not find nodes to restore selection:", savedSelState);
                       // Fallback: place cursor at the start index if possible
                        const fallbackStartPos = getTextNodeAndOffset(editor, savedSelState.start);
                        if (fallbackStartPos) {
                            const fallbackRange = document.createRange();
                             const safeFallbackOffset = Math.min(fallbackStartPos.offset, fallbackStartPos.node.textContent?.length ?? 0);
                             fallbackRange.setStart(fallbackStartPos.node, safeFallbackOffset);
                             fallbackRange.collapse(true); // Collapse to start
                             const sel = window.getSelection();
                             sel?.removeAllRanges(); sel?.addRange(fallbackRange);
                        }
                   }
               } catch (e) {
                   console.error("Error restoring selection:", e, "State:", savedSelState);
               }
           });
        }
        // } else if (!preserveSelection && document.activeElement === editor) {
        //     // Optional: If not preserving selection but editor has focus, move cursor to end?
        //     // this.placeCursorAtEnd(editor);
        // }
    },

    placeCursorAtEnd(element) {
        if (!element) return;
        const range = document.createRange();
        const sel = window.getSelection();
        // Select all content within the element
        range.selectNodeContents(element);
        // Collapse the range to the end point (false means collapse to end)
        range.collapse(false);
        // Remove any existing selections and add the new collapsed range
        sel?.removeAllRanges();
        sel?.addRange(range);
        // Ensure the element is focused
        element.focus();
    },

    scrollToBottom(elementRef) {
         const element = elementRef; // e.g., this.$refs.codeAreaWrapper
        if (!element) return;
        this.$nextTick(() => {
             element.scrollTo({ top: element.scrollHeight, behavior: 'smooth' });
        });
    },

    // --- Input Manipulation Helpers (Standard Blocks) ---
    insertTextAtCursor(textToInsert) {
        if (this.isFunctionLanguage || !this.$refs.codeContentEditable) return;

        const editor = this.$refs.codeContentEditable;
        let sel = window.getSelection();

        // Ensure editor has focus and a selection exists
        if (!sel || sel.rangeCount === 0 || !editor.contains(sel.anchorNode)) {
            editor.focus(); // Focus the editor first
            this.placeCursorAtEnd(editor); // Place cursor at end if no valid selection
            sel = window.getSelection(); // Get selection again
            if (!sel || sel.rangeCount === 0) return; // Still no selection, abort
        }

        // Take snapshot *before* modification
        this.snapshotState(this.internalCode);

        const range = sel.getRangeAt(0);
        range.deleteContents(); // Delete selected text (if any)

        const textNode = document.createTextNode(textToInsert);
        range.insertNode(textNode);

        // Move the cursor to the end of the inserted text
        range.setStartAfter(textNode);
        range.collapse(true); // Collapse the range to the end point

        // Update the selection
        sel.removeAllRanges();
        sel.addRange(range);

        // Update internal state *after* DOM manipulation
         this.$nextTick(() => {
            const newCode = editor.innerText ?? '';
             if (newCode !== this.internalCode) {
                this.internalCode = newCode;
                this.$emit('update-code', newCode);
                this.clearSearchState(); // Clear search results as content changed
                // No need to re-highlight immediately on typing; handled by blur or other triggers
             }
         });
    },

    // --- Input Handlers (Standard Blocks) ---
    // This is the target for the debounced input handler
    handleInputLogic(event) {
        if (this.isFunctionLanguage || !this.$refs.codeContentEditable || this.isApplyingUndoRedo) return;

        const currentText = event.target.innerText ?? '';
        if (currentText !== this.internalCode) {
             // Snapshot the state *before* this current change
            this.snapshotState(this.internalCode);
            // Update internal state
            this.internalCode = currentText;
            // Emit the change
            this.$emit('update-code', currentText);
            // Clear search results as content changed, but keep query
            this.clearSearchState(false);
             // Re-run search debounced if search is visible
             if(this.isSearchVisible && this.searchQuery) {
                 this.debouncedFindMatches();
             }
            // No immediate re-highlighting during typing for performance.
            // rely on blur or explicit actions for full re-highlight.
        }
    },

    handlePaste(event) {
        if (this.isFunctionLanguage || !this.$refs.codeContentEditable) return;
        event.preventDefault();
        // Take snapshot before paste
        this.snapshotState(this.internalCode);
        const text = event.clipboardData?.getData('text/plain') || '';
        if (text) {
             // Document.execCommand is deprecated but sometimes more reliable for paste
             // However, using insertTextAtCursor gives more control
             // document.execCommand('insertText', false, text);
             this.insertTextAtCursor(text);

             // After inserting, we need to update internal state and re-highlight potentially
             this.$nextTick(() => {
                const editor = this.$refs.codeContentEditable;
                 if (editor) {
                    const newCode = editor.innerText;
                    this.internalCode = newCode; // Update internal state from DOM
                    this.$emit('update-code', newCode);
                    this.clearSearchState();
                    // Optional: Re-highlight after paste might be desired
                    // this.applyHighlighting(newCode, true); // Preserve selection after paste point
                 }
             });
        }
    },
    handleEnterKey(event) {
        if (!this.isFunctionLanguage) {
            this.insertTextAtCursor('\n');
        }
    },
    handleTabKey(event) {
        if (!this.isFunctionLanguage) {
            this.insertTextAtCursor('\t'); // Insert a literal tab character
        }
    },
    handleBlur(event) {
        if (this.isFunctionLanguage || !this.$refs.codeContentEditable) return;

        // Flush any debounced input first
        this.debouncedHandleInput.flush();

        // Check if focus moved to an element *outside* the code block container
        const relatedTarget = event.relatedTarget;
        const container = event.currentTarget.closest('.code-block-container');
        if (!container || (relatedTarget && container.contains(relatedTarget))) {
             return; // Focus is still within the component (e.g., moved to a button or search input)
        }

        // Focus moved out, re-highlight the entire block for consistency
        console.log("Blur detected, focus moved outside. Re-highlighting.");
        this.applyHighlighting(this.internalCode, false); // Don't preserve selection
    },

    clearSelectionIfOutsideSearch(event) {
        if (this.isFunctionLanguage || !this.$refs.codeContentEditable) return;
        // If search is not visible, or we clicked inside the editable area
        // but not on a search highlight (difficult to detect reliably),
        // or if there's no active match, do nothing special here.
        // Let's simplify: If the user clicks within the editor while search is active,
        // we *might* want to clear the search selection.
        if (this.isSearchVisible && this.hasActiveMatch && event.target === this.$refs.codeContentEditable) {
            const sel = window.getSelection();
             // Check if the click didn't start within the current search highlight range
             // This check is complex and potentially unreliable across browsers.
             // A simpler approach: clear search selection on any click inside the editor?
             // Let's try clearing it. If it feels wrong, remove this.
            if (sel && sel.rangeCount > 0) {
                sel.removeAllRanges(); // Clear visual selection
                this.currentMatchIndex = -1; // Deselect search match logically
            }
        }
    },

    // --- Icon Update Helper ---
    triggerIconUpdate() {
        // Use nextTick to ensure the DOM has updated before Feather tries to replace icons
        this.$nextTick(() => {
             try {
                 feather.replace();
             } catch (e) {
                 console.warn("Feather icon replacement failed:", e);
             }
        });
    },

    // --- Action Methods (Copy, Execute, Open) ---
    async copyCode() {
        if (this.isCopied) return;
        const codeToCopy = this.getActualCode();
        try {
            await navigator.clipboard.writeText(codeToCopy);
            this.isCopied = true;
            this.triggerIconUpdate(); // Update icon to 'check'

            // Clear previous timeout if exists
            if (this.copyTimeout) clearTimeout(this.copyTimeout);

            // Set timeout to revert icon and state
            this.copyTimeout = setTimeout(() => {
                 this.isCopied = false;
                 this.triggerIconUpdate(); // Revert icon to 'copy'
                 this.copyTimeout = null;
                 // Optional: Show toast notification via store or event bus
                 // Check if store and toast system exist before calling
                 if (this.$store && this.$store.state && this.$store.state.toast && typeof this.$store.state.toast.showToast === 'function') {
                     this.$store.state.toast.showToast("Code copied successfully!", 4, true); // Example usage
                 } else {
                     // console.warn("Toast notification system not available at this.$store.state.toast.showToast");
                 }
            }, 1500); // Revert after 1.5 seconds

        } catch (err) {
             console.error('Failed to copy code to clipboard:', err);
             // Provide user feedback about the failure
             alert('Error: Could not copy code. See console for details.');
        }
    },

    executeCodeInternal(endpointUrl, shouldOpenInNewTab = false) {
        if (this.isExecuting) return;
        this.isExecuting = true;
        this.executionOutput = ''; // Clear previous output
        this.triggerIconUpdate(); // Show loader icon

        const currentCode = this.getActualCode();
        const requestPayload = {
            client_id: this.client_id,
            code: currentCode,
            discussion_id: this.discussion_id ? Number(this.discussion_id) : 0,
            message_id: this.message_id ? Number(this.message_id) : 0,
            language: this.normalizedLanguage
        };

        fetch(`${this.host}/${endpointUrl}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json, text/plain, */*' // Accept various response types
            },
            body: JSON.stringify(requestPayload)
        })
        .then(async response => {
            const contentType = response.headers.get("content-type");
            let responseData;

            if (contentType && contentType.includes("application/json")) {
                responseData = await response.json();
            } else {
                // Handle plain text or other non-JSON responses
                const textData = await response.text();
                // Wrap text data in a consistent structure if needed, or use directly
                responseData = { output: textData }; // Assume text response is the output
            }

            if (!response.ok) {
                // Construct detailed error message
                let errorDetails = `HTTP error! Status: ${response.status}`;
                if (responseData?.error) { // Prefer specific error field from JSON
                    errorDetails += `, Message: ${responseData.error}`;
                } else if (responseData?.output && typeof responseData.output === 'string') { // Include beginning of text output/error
                     errorDetails += `, Body: ${responseData.output.substring(0, 200)}${responseData.output.length > 200 ? '...' : ''}`;
                } else if (responseData?.detail) { // Handle FastAPI validation errors etc.
                     errorDetails += `, Detail: ${responseData.detail}`;
                }
                 const error = new Error(errorDetails);
                error.response = responseData; // Attach full response data if available
                throw error;
            }
            return responseData; // Return the parsed/handled data
        })
        .then(data => {
            // Determine what to display as output
            // Prioritize 'output', then 'message', then stringify the whole object if needed
            this.executionOutput = data.output ?? (data.message ?? (typeof data === 'object' ? JSON.stringify(data, null, 2) : String(data)));

            // Handle opening in new tab if requested and URL is provided
            if (shouldOpenInNewTab && data.url) {
                try {
                     window.open(data.url, '_blank', 'noopener,noreferrer');
                 } catch(e) {
                     console.error("Failed to open URL in new tab:", e);
                     this.executionOutput += `\n(Failed to open URL: ${data.url})`;
                 }
            }
        })
        .catch(error => {
            console.error('Code execution request failed:', error);
            // Display error message in the output area
            this.executionOutput = `Execution Error: ${error.message}`;
        })
        .finally(() => {
            this.isExecuting = false;
            this.triggerIconUpdate(); // Revert icon
            // Scroll output into view
            this.$nextTick(() => {
                const outputElement = this.$el.querySelector('.execution-output-content'); // Use this.$el
                outputElement?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
            });
        });
    },

    executeCode() {
        this.executeCodeInternal('execute_code', false); // Standard execution
    },
    executeCode_in_new_tab() {
        this.executeCodeInternal('execute_code_in_new_tab', true); // New tab execution
    },

    // Generic POST request helper for folder/VSCode actions
    postRequest(endpointUrl, requestPayload = {}) {
        const payloadToSend = { ...requestPayload }; // Copy payload

        // Add current code state if the endpoint requires it (and it's not a function block)
        if (endpointUrl === 'open_code_in_vs_code') {
             payloadToSend.code = this.getActualCode(); // Send potentially edited code
        }
        // Note: 'open_discussion_folder_in_vs_code' and 'open_discussion_folder' don't need the code content.

        fetch(`${this.host}/${endpointUrl}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json' // Expect JSON response for success/failure
            },
            body: JSON.stringify(payloadToSend)
        })
        .then(async response => {
            if (!response.ok) {
                // Try to get error details from JSON response body
                let errorDetail = `HTTP Status ${response.status}`;
                try {
                    const errorBody = await response.json();
                    errorDetail += `: ${errorBody.detail || JSON.stringify(errorBody)}`;
                } catch (e) {
                    // If response is not JSON or parsing fails, just use status text
                    errorDetail += ` (${response.statusText})`;
                }
                throw new Error(errorDetail);
            }
            // Check content type before parsing JSON
            const contentType = response.headers.get("content-type");
            if (contentType && contentType.includes("application/json")) {
                return response.json(); // Parse JSON response
            }
            return {}; // Return empty object for non-JSON success responses
        })
        .then(data => {
            console.log(`POST request to ${endpointUrl} successful:`, data);
            // Optional: Show success notification if needed
        })
        .catch(error => {
            console.error(`Fetch error during POST to ${endpointUrl}:`, error);
            // Show user-friendly error message
            alert(`Operation failed: ${error.message}`);
        });
    },

    openFolderVsCode() {
        this.postRequest('open_discussion_folder_in_vs_code', {
            client_id: this.client_id,
            discussion_id: this.discussion_id
        });
    },
    openVsCode() {
         // Payload includes code implicitly added by postRequest for this endpoint
        this.postRequest('open_code_in_vs_code', {
            client_id: this.client_id,
            discussion_id: this.discussion_id,
            message_id: this.message_id,
            // code: this.getActualCode() // Added within postRequest
        });
    },
    openFolder() {
        this.postRequest('open_discussion_folder', {
            client_id: this.client_id,
            discussion_id: this.discussion_id
        });
    },

    // --- Function Block Method ---
    toggleFunctionDetails() {
        this.isFunctionDetailsVisible = !this.isFunctionDetailsVisible;
        this.triggerIconUpdate(); // Update chevron icon
    },

    // --- Search/Replace Methods ---
    clearSearchState(clearQueryAndReplace = false) {
      if (clearQueryAndReplace) {
        this.searchQuery = ''; // Will trigger watcher and debouncedFindMatches
        this.replaceQuery = '';
      }
      // Always clear results and selection regardless of query clear
      if (this.searchResults.length > 0 || this.currentMatchIndex !== -1) {
          this.searchResults = [];
          this.currentMatchIndex = -1;
          // Clear visual selection in the editor if it exists
          const sel = window.getSelection();
          if (sel && sel.rangeCount > 0 && this.$refs.codeContentEditable?.contains(sel.anchorNode)) {
              // Check if selection is actually within our editable div
              const range = sel.getRangeAt(0);
              if (this.$refs.codeContentEditable.contains(range.commonAncestorContainer)) {
                 sel.removeAllRanges();
              }
          }
      }
    },

    toggleSearch() {
      this.isSearchVisible = !this.isSearchVisible;
      if (!this.isSearchVisible) {
        // Clear everything when hiding search
        this.clearSearchState(true);
      } else {
        // When showing search, focus the input and run initial search if needed
        this.$nextTick(() => {
          this.$refs.searchInputRef?.focus();
          // If there's already a query, run the search immediately (debounced)
          if (this.searchQuery) {
            this.debouncedFindMatches();
          }
        });
      }
      this.triggerIconUpdate(); // Update search/x icon
    },

    // This is the debounced function target
    findMatchesLogic() {
        if (this.isFunctionLanguage || !this.$refs.codeContentEditable) return;

        const editor = this.$refs.codeContentEditable;
        const text = editor.innerText; // Get current text content
        const query = this.searchQuery;

        // Clear results if query is empty
        if (!query) {
            this.clearSearchState(false); // Clear results but keep query potentially
            return;
        }

        const results = [];
        let startIndex = 0;
        let index;

        // Simple case-sensitive search
        // TODO: Add option for case-insensitive if needed
        while ((index = text.indexOf(query, startIndex)) > -1) {
            results.push({ start: index, end: index + query.length });
            // Prevent infinite loop for empty query (shouldn't happen with check above)
            if (query.length === 0) break;
            // Move start index past the current match
            startIndex = index + 1; // Use 1 to find overlapping matches correctly if needed, or query.length to find distinct
        }

        this.searchResults = results;

        if (results.length > 0) {
            // New search yielded results, select the first one without scrolling/focus stealing
            if (this.currentMatchIndex === -1) {
                 this.currentMatchIndex = 0;
                 this.highlightMatch(0, false); // Highlight, no scroll
                 // Ensure focus stays on search input after DOM updates
                //  this.$nextTick(() => this.$refs.searchInputRef?.focus()); // Re-focus might be needed
            } else {
                // Query might have changed, re-validate current index
                 if (this.currentMatchIndex >= results.length) {
                     this.currentMatchIndex = 0; // Wrap around or reset
                     this.highlightMatch(0, false); // Highlight new first match
                    //  this.$nextTick(() => this.$refs.searchInputRef?.focus());
                 } else {
                    // Index is still valid, maybe re-highlight in case position shifted?
                     this.highlightMatch(this.currentMatchIndex, false); // Re-highlight current
                    //  this.$nextTick(() => this.$refs.searchInputRef?.focus());
                 }
            }
        } else {
            // No matches found
            this.currentMatchIndex = -1;
            // Clear any existing selection in the editor
             const sel = window.getSelection();
             if (sel && sel.rangeCount > 0 && editor.contains(sel.anchorNode)) {
                  const range = sel.getRangeAt(0);
                 if (editor.contains(range.commonAncestorContainer)) {
                    sel.removeAllRanges();
                 }
             }
        }
        // Do NOT steal focus here, user is likely still typing in searchInputRef
    },

    scrollToMatch(index) {
        if (this.isFunctionLanguage || !this.$refs.codeContentEditable || index < 0 || index >= this.searchResults.length) return;

        const editor = this.$refs.codeContentEditable;
        const match = this.searchResults[index];
        const startPos = getTextNodeAndOffset(editor, match.start);

        if (startPos?.node) {
            try {
                // Create a temporary range or element to scroll to
                const range = document.createRange();
                const safeOffset = Math.min(startPos.offset, startPos.node.textContent?.length ?? 0);
                range.setStart(startPos.node, safeOffset);
                range.collapse(true); // Collapse to the start point

                // Create a temporary, invisible span to scroll to
                const tempSpan = document.createElement('span');
                 // Basic styles to make it exist but not affect layout significantly
                 tempSpan.style.display = 'inline';
                 tempSpan.style.width = '0';
                 tempSpan.style.height = '0';
                 tempSpan.style.overflow = 'hidden';
                 tempSpan.textContent = '\ufeff'; // Zero-width no-break space

                range.insertNode(tempSpan); // Insert the span at the cursor position

                // Scroll the span into view
                 tempSpan.scrollIntoView({
                     behavior: 'smooth',
                     block: 'nearest', // Scroll vertically minimally
                     inline: 'nearest' // Scroll horizontally minimally
                 });

                // Clean up the temporary span
                 tempSpan.parentNode?.removeChild(tempSpan);

             } catch(e) {
                 console.error("Error scrolling to match using temp span:", e);
                 // Fallback: Scroll the parent element of the text node into view
                 startPos.node.parentElement?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
             }
        } else {
             console.warn("Could not find start node for scrolling to match:", match);
        }
    },

    highlightMatch(index, scroll = true) {
        if (this.isFunctionLanguage || !this.$refs.codeContentEditable || index < 0 || index >= this.searchResults.length) {
            // If index is invalid, clear any existing selection
             const sel = window.getSelection();
             if (sel && sel.rangeCount > 0 && this.$refs.codeContentEditable.contains(sel.anchorNode)) {
                 const range = sel.getRangeAt(0);
                  if (this.$refs.codeContentEditable.contains(range.commonAncestorContainer)) {
                     sel.removeAllRanges();
                  }
             }
            return;
        }

        const editor = this.$refs.codeContentEditable;
        const match = this.searchResults[index];
        const startPos = getTextNodeAndOffset(editor, match.start);
        const endPos = getTextNodeAndOffset(editor, match.end);

        if (startPos && endPos) {
            try {
                const range = document.createRange();
                // Ensure offsets are valid for the nodes
                 const safeStartOffset = Math.min(startPos.offset, startPos.node.textContent?.length ?? 0);
                 const safeEndOffset = Math.min(endPos.offset, endPos.node.textContent?.length ?? 0);

                range.setStart(startPos.node, safeStartOffset);
                range.setEnd(endPos.node, safeEndOffset);

                const sel = window.getSelection();
                sel?.removeAllRanges();
                sel?.addRange(range);

                // Scroll the highlighted match into view if requested
                if (scroll) {
                    this.scrollToMatch(index);
                }
            } catch (e) {
                console.error("Error creating or selecting range for highlight:", e, "Match:", match, "Start:", startPos, "End:", endPos);
            }
        } else {
            console.warn("Could not find text nodes for highlighting match:", match);
             // Clear selection if nodes couldn't be found
             const sel = window.getSelection();
             if (sel && sel.rangeCount > 0 && editor.contains(sel.anchorNode)) sel.removeAllRanges();
        }
    },

    findNextAndHighlight() {
      if (!this.hasMatches) return;
      let nextIndex = this.currentMatchIndex + 1;
      // Wrap around if past the end
      if (nextIndex >= this.searchResults.length) {
          nextIndex = 0;
      }
      this.currentMatchIndex = nextIndex;
      this.highlightMatch(this.currentMatchIndex, true); // Highlight and scroll
      // Return focus to search input after DOM updates settle
      this.$nextTick(() => this.$refs.searchInputRef?.focus());
    },

    findPreviousAndHighlight() {
      if (!this.hasMatches) return;
      let prevIndex = this.currentMatchIndex - 1;
      // Wrap around if before the beginning
      if (prevIndex < 0) {
          prevIndex = this.searchResults.length - 1;
      }
      this.currentMatchIndex = prevIndex;
      this.highlightMatch(this.currentMatchIndex, true); // Highlight and scroll
      // Return focus to search input
      this.$nextTick(() => this.$refs.searchInputRef?.focus());
    },

    replaceCurrent() {
      if (this.isFunctionLanguage || !this.$refs.codeContentEditable || !this.hasActiveMatch) return;

      // Snapshot before replacing
      this.snapshotState(this.internalCode);

      const editor = this.$refs.codeContentEditable;
      const matchToReplace = this.searchResults[this.currentMatchIndex];
      const originalStartIndex = matchToReplace.start;

      // Ensure the match is selected before replacing
      this.highlightMatch(this.currentMatchIndex, false); // Select without scrolling

      this.$nextTick(() => { // Wait for selection to apply
          const sel = window.getSelection();
          if (sel && !sel.isCollapsed && editor.contains(sel.anchorNode)) {
                // Use insertTextAtCursor logic adapted for replacement
                const range = sel.getRangeAt(0);
                range.deleteContents();
                const textNode = document.createTextNode(this.replaceQuery);
                range.insertNode(textNode);
                range.setStartAfter(textNode);
                range.collapse(true);
                sel.removeAllRanges(); sel.addRange(range);

                // Update internal state and emit change *after* DOM manipulation
                const newCode = editor.innerText;
                this.internalCode = newCode;
                this.$emit('update-code', newCode);

                // Recalculate matches based on new code
                // Don't debounce here, we need results immediately
                this.findMatchesLogic();

                // Try to find the logical next match after the replacement point
                if (this.hasMatches) {
                    // Find the first match starting at or after the original start position
                    let nextLogicalIndex = this.searchResults.findIndex(m => m.start >= originalStartIndex);
                    // If none found after, wrap to the first match
                    if (nextLogicalIndex === -1) {
                        nextLogicalIndex = 0;
                    }
                    this.currentMatchIndex = nextLogicalIndex;
                    this.highlightMatch(this.currentMatchIndex, true); // Highlight and scroll to next potential match
                } else {
                     this.currentMatchIndex = -1; // No matches left
                }
          } else {
               console.warn("Replace current failed: No active selection found or selection outside editor.");
               // Attempt to re-run findMatchesLogic to reset state if selection was lost
               this.findMatchesLogic();
          }
           // Return focus to search input
           this.$nextTick(() => this.$refs.searchInputRef?.focus());
      });
    },

    replaceCurrentAndFindNext() {
        // Replace current first, the logic inside replaceCurrent handles finding the next one
        if (this.hasActiveMatch) {
           this.replaceCurrent();
        }
         // Focus should be handled by replaceCurrent
    },

    replaceAll() {
      if (this.isFunctionLanguage || !this.$refs.codeContentEditable || !this.hasMatches || !this.searchQuery) return;

      // Snapshot before massive change
      this.snapshotState(this.internalCode);

      const editor = this.$refs.codeContentEditable;
      const originalCode = editor.innerText; // Use innerText as source
      const query = this.searchQuery;
      const replacement = this.replaceQuery;
      let newCode = originalCode;
      let replacementsMade = 0;
      let offset = 0; // Track offset changes due to replacements

      // Iterate backwards through matches to avoid index issues
      const currentResults = [...this.searchResults]; // Copy results array
      for (let i = currentResults.length - 1; i >= 0; i--) {
          const match = currentResults[i];
           // Double check the text at the match position in the potentially modified string
           // This is complex if replacements have different lengths.
           // A simpler, generally safe approach for innerText: direct replacement.
           // However, for robustness, let's re-implement using split/join or regex replaceAll
      }

      // Simpler & more robust: Use replaceAll with proper escaping for regex if needed
      try {
            // Escape special regex characters in the search query for safe replacement
            // const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
            // Use string replaceAll if supported and sufficient (case-sensitive)
             if (typeof newCode.replaceAll === 'function') {
                const oldLength = newCode.length;
                 newCode = newCode.replaceAll(query, replacement);
                 replacementsMade = (oldLength - newCode.length + (replacement.length * (oldLength - newCode.length) / query.length)) / query.length; // Estimate count
                 if (oldLength !== newCode.length) replacementsMade = currentResults.length; // Assume all were replaced if length changed significantly
             } else {
                 // Fallback for older environments (less efficient)
                 const regex = new RegExp(query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'g'); // Global replace
                 const originalLength = newCode.length;
                 newCode = newCode.replace(regex, replacement);
                  if (originalLength !== newCode.length) replacementsMade = currentResults.length; // Estimate count
             }

      } catch (e) {
          console.error("Error during replaceAll:", e);
          alert("An error occurred during Replace All. Operation halted.");
          return; // Stop execution
      }


      if (replacementsMade > 0 || originalCode !== newCode) { // Check if actual change occurred
        this.internalCode = newCode;
        this.applyHighlighting(newCode, false); // Update display, don't preserve selection
        this.$emit('update-code', newCode); // Emit the final code
        this.clearSearchState(false); // Clear old results, keep query/replace fields
        // Re-run search immediately to show 0 matches or update if query still matches something new
        this.$nextTick(() => {
             this.findMatchesLogic();
             this.$refs.searchInputRef?.focus(); // Keep focus in search
        });
      } else {
           console.log("Replace All: No instances found or no change made.");
           this.$nextTick(() => this.$refs.searchInputRef?.focus());
      }
    },
  },

  created() {
    // Initialize debounced functions here, binding 'this' correctly
    this.debouncedHandleInput = debounce(this.handleInputLogic, INPUT_DEBOUNCE_MS);
    this.debouncedFindMatches = debounce(this.findMatchesLogic, SEARCH_DEBOUNCE_MS);

    // Initialize internalCode from prop on creation
    // For editable blocks, this establishes the baseline
    this.internalCode = this.safeCodeProp;
    // Add initial state to undo stack if editable
    if (!this.isFunctionLanguage) {
        this.undoStack = [this.internalCode];
    }
  },

  mounted() {
    this.isComponentMounted = true; // Mark as mounted after initial render

    if (!this.isFunctionLanguage && this.$refs.codeContentEditable) {
        // Apply initial highlighting based on the internalCode (which was set from prop in created)
        this.applyHighlighting(this.internalCode);
    }

    // Initial replacement of Feather icons in the template
    this.triggerIconUpdate();
  },

  beforeUnmount() {
    // Clean up timers
    if (this.copyTimeout) clearTimeout(this.copyTimeout);

    // Cancel any pending debounced calls to prevent errors after unmount
    this.debouncedHandleInput?.cancel();
    this.debouncedFindMatches?.cancel();
  },
};
</script>

<style>
/* Base button styles */
.code-block-button { @apply p-1 rounded text-gray-600 dark:text-gray-300 hover:bg-primary dark:hover:bg-primary hover:text-white transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent disabled:hover:text-gray-600 dark:disabled:hover:text-gray-300; }
.feather-small { @apply w-3 h-3 inline-block align-middle; } /* For small icons like in function call header */

/* Ensure hljs doesn't add its own background/padding */
.hljs { background: none !important; padding: 0 !important; margin: 0 !important; }

.code-block-container { position: relative; }
.code-area-wrapper { /* Max height and overflow handled by Tailwind */ }

/* Flex container for line numbers and code */
.code-content-flex {
    align-items: stretch; /* Ensure children stretch vertically */
    /* Apply consistent line-height for alignment */
     /* leading-snug is typically 1.375 */
}

/* Line Numbers Column */
.line-numbers {
    @apply flex-shrink-0 p-2 text-right text-gray-500 select-none bg-gray-100 dark:bg-gray-700 whitespace-pre overflow-y-hidden border-r border-gray-300 dark:border-gray-600;
    min-height: 100%; /* Try to match height */
    user-select: none; /* Prevent selecting line numbers */
    /* Font must match code content */
    /* Line height inherited from flex container */
}

/* Code Content Area (Editable) */
.code-content {
    @apply flex-grow p-2 whitespace-pre-wrap break-words overflow-x-auto overflow-y-hidden scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-400 dark:scrollbar-thumb-gray-500 focus:outline-none;
    min-height: 1.5em; /* Ensure it's not collapsed when empty */
    caret-color: currentColor; /* Use text color for cursor */
    /* Base text/bg colors */
    color: theme('colors.gray.800');
    background-color: theme('colors.white');
    /* Font must match line numbers */
    /* Line height inherited from flex container */
}
.dark .code-content {
    color: theme('colors.gray.200');
    background-color: theme('colors.gray.800');
}

/* Allow horizontal scrollbar for code content if needed */
.code-content::-webkit-scrollbar { height: 8px; }
.code-content::-webkit-scrollbar-thumb { border-radius: 4px; }

/* Spinner animation */
.animate-spin { animation: spin 1s linear infinite; }
@keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

/* Execute button alignment */
.execute-button { @apply inline-flex items-center justify-center; }

/* Dark mode helpers for VS Code icons */
.dark .dark\:hidden { display: none; }
.dark .dark\:inline { display: inline; }
.hidden { display: none; } /* Standard hidden class */

/* Ensure icons align vertically */
.code-block-button i[data-feather], .code-block-button img { vertical-align: middle; }

/* Function parameter styling */
.parameter-item { margin-bottom: 0.5rem; }
.parameter-item > div:last-child { margin-left: 0.5rem; } /* Indent value */

/* Execution Output basic styling */
.execution-output-content { /* Inherit font */ }
.execution-output-content a { @apply text-blue-600 dark:text-blue-400 hover:underline; }
.execution-output-content h1 { @apply text-xl font-bold my-2; }
.execution-output-content h2 { @apply text-lg font-semibold my-1.5; }
.execution-output-content h3 { @apply text-base font-semibold my-1; }
.execution-output-content h4, .execution-output-content h5, .execution-output-content h6 { @apply font-semibold my-0.5; }
.execution-output-content p { @apply my-1; }
.execution-output-content ul { @apply list-disc list-inside ml-4 my-1; }
.execution-output-content ol { @apply list-decimal list-inside ml-4 my-1; }
.execution-output-content li { @apply my-0.5; }
.execution-output-content code:not(pre > code) { /* Inline code */ @apply font-mono bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-sm; }
.execution-output-content pre { /* Code blocks within output */ @apply font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded my-1 overflow-x-auto text-sm; }
.execution-output-content pre > code { @apply p-0 bg-transparent text-sm; } /* Reset style for code inside pre */
.execution-output-content blockquote { @apply border-l-4 border-gray-300 dark:border-gray-600 pl-2 italic my-1 text-gray-600 dark:text-gray-400; }
.execution-output-content table { @apply w-full border-collapse border border-gray-300 dark:border-gray-600 my-2 text-sm; }
.execution-output-content th, .execution-output-content td { @apply border border-gray-300 dark:border-gray-600 p-1.5 text-left; }
.execution-output-content th { @apply bg-gray-100 dark:bg-gray-700 font-semibold; }
.execution-output-content img { @apply max-w-full h-auto my-1 rounded border border-gray-200 dark:border-gray-700; }
.execution-output-content svg { @apply max-w-full h-auto my-1; } /* Ensure SVGs scale */
.execution-output-content hr { @apply border-t border-gray-300 dark:border-gray-600 my-2; }

/* Ensure hljs theme applies to output as well */
.execution-output-content.hljs { color: theme('colors.gray.800'); background-color: theme('colors.white'); }
.dark .execution-output-content.hljs { color: theme('colors.gray.200'); background-color: theme('colors.gray.800'); }


/* Search/Replace Panel styling */
.search-replace-panel { @apply border-b border-gray-300 dark:border-gray-600; }
.search-replace-panel input[type="text"] { @apply px-2 py-1 border border-gray-300 dark:border-gray-500 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-xs focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary; min-width: 80px; }
.search-replace-panel .search-status { @apply text-xs text-gray-600 dark:text-gray-400 whitespace-nowrap px-1; min-width: 50px; text-align: center; } /* Give status width */
.search-replace-panel .search-button { @apply px-1 py-0.5 text-xs; }
.search-replace-panel .search-button i[data-feather] { @apply w-3.5 h-3.5; } /* Smaller icons for search buttons */
.search-replace-panel .code-block-button { @apply p-1 text-gray-600 dark:text-gray-300 hover:bg-primary dark:hover:bg-primary hover:text-white; }
.search-replace-panel .code-block-button:disabled { @apply opacity-50 cursor-not-allowed hover:bg-transparent hover:text-gray-600 dark:hover:text-gray-300; }

/* Selection styling within the code editor */
.code-content::selection { background-color: theme('colors.blue.200'); color: theme('colors.black'); }
.dark .code-content::selection { background-color: theme('colors.blue.800'); color: theme('colors.white'); }

/* --- Highlight.js Theme Overrides --- */

/* Tokyo Night Dark Theme (for .dark mode) */
.dark .code-content.hljs, .dark .execution-output-content.hljs { color:#a9b1d6; }
.dark .hljs-meta { color:#ff9e64; }
.dark .hljs-comment { color:#565f89; font-style:italic; }
.dark .hljs-tag { color:#f7768e; }
.dark .hljs-tag .hljs-name, .dark .hljs-tag .hljs-attr { color:#f7768e; } /* Adjusted */
.dark .hljs-keyword, .dark .hljs-selector-tag, .dark .hljs-literal, .dark .hljs-name { color:#bb9af7; }
.dark .hljs-deletion, .dark .hljs-number, .dark .hljs-attribute, .dark .hljs-variable, .dark .hljs-template-variable, .dark .hljs-symbol { color:#ff9e64; } /* Adjusted */
.dark .hljs-section, .dark .hljs-title, .dark .hljs-type { color:#7aa2f7; }
.dark .hljs-string, .dark .hljs-subst, .dark .hljs-regexp, .dark .hljs-link, .dark .hljs-addition, .dark .hljs-selector-id, .dark .hljs-selector-class { color:#9ece6a; }
.dark .hljs-built_in, .dark .hljs-bullet, .dark .hljs-code, .dark .hljs-formula { color:#7dcfff; }
.dark .hljs-emphasis { font-style:italic; }
.dark .hljs-strong { font-weight:bold; }

/* GitHub Light Theme (for light mode) */
html:not(.dark) .code-content.hljs, html:not(.dark) .execution-output-content.hljs { color:#24292e; }
html:not(.dark) .hljs-meta { color:#6a737d; }
html:not(.dark) .hljs-comment { color:#6a737d; font-style:italic; }
html:not(.dark) .hljs-tag { color:#22863a; }
html:not(.dark) .hljs-tag .hljs-name, html:not(.dark) .hljs-tag .hljs-attr { color:#22863a; } /* Adjusted */
html:not(.dark) .hljs-keyword, html:not(.dark) .hljs-selector-tag, html:not(.dark) .hljs-literal, html:not(.dark) .hljs-name { color:#d73a49; }
html:not(.dark) .hljs-deletion, html:not(.dark) .hljs-number, html:not(.dark) .hljs-attribute, html:not(.dark) .hljs-variable, html:not(.dark) .hljs-template-variable, html:not(.dark) .hljs-symbol { color:#005cc5; } /* Adjusted */
html:not(.dark) .hljs-section, html:not(.dark) .hljs-title, html:not(.dark) .hljs-type { color:#6f42c1; }
html:not(.dark) .hljs-string, html:not(.dark) .hljs-subst, html:not(.dark) .hljs-regexp, html:not(.dark) .hljs-link, html:not(.dark) .hljs-addition, html:not(.dark) .hljs-selector-id, html:not(.dark) .hljs-selector-class { color:#032f62; }
html:not(.dark) .hljs-built_in, html:not(.dark) .hljs-bullet, html:not(.dark) .hljs-code, html:not(.dark) .hljs-formula { color:#e36209; }
html:not(.dark) .hljs-emphasis { font-style:italic; }
html:not(.dark) .hljs-strong { font-weight:bold; }

</style>