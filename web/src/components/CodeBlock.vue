<template>
    <div :id="`code-block-container-${message_id}`" class="code-block-container bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel p-2 rounded-lg shadow-sm mb-4">
  
      <!-- == Function Call Display == -->
      <div v-if="isFunctionLanguage">
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
        <div class="p-2 rounded-b-md bg-white dark:bg-gray-800">
          <div class="flex items-center space-x-2 text-sm mb-1 cursor-pointer hover:opacity-80" @click="toggleFunctionDetails" role="button" :aria-expanded="isFunctionDetailsVisible">
            <span class="font-semibold text-gray-700 dark:text-gray-300">Function:</span>
            <span v-if="isValidFunctionCall" class="font-mono bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-gray-900 dark:text-gray-100 break-all">{{ functionName }}</span>
            <span v-else class="flex items-center text-amber-600 dark:text-amber-400">
              <i data-feather="alert-circle" class="w-4 h-4 mr-1 feather-small"></i> Invalid / Incomplete
            </span>
          </div>
          <div v-show="isFunctionDetailsVisible" class="mt-2 pt-2 border-t border-gray-200 dark:border-gray-700 max-h-60 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-600">
            <div v-if="isValidFunctionCall">
              <h4 class="text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 mb-2 sticky top-0 bg-white dark:bg-gray-800 py-1">Parameters:</h4>
              <div v-if="hasParameters" class="space-y-2">
                <div v-for="(value, key) in functionParametersObject" :key="key" class="parameter-item">
                  <div class="text-xs font-semibold text-gray-600 dark:text-gray-400 mb-0.5">{{ key }}:</div>
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
      <div v-else>
        <!-- Top Bar -->
        <div class="flex justify-between items-center px-2 py-1 mb-1 rounded-t-lg bg-gray-200 dark:bg-gray-700">
          <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ effectiveLanguage || 'plaintext' }}</span>
          <div class="flex flex-row space-x-1 items-center">
            <button v-if="!isEditing" @click="toggleEditMode" title="Edit Code" class="code-block-button" aria-label="Edit Code"><i data-feather="edit-2" class="w-4 h-4"></i></button>
            <template v-if="isEditing">
              <button @click="toggleEditMode" title="Finish Editing" class="code-block-button" aria-label="Finish Editing"><i data-feather="check" class="w-4 h-4"></i></button>
              <button @click="undo" :disabled="!canUndo" title="Undo (Ctrl+Z)" class="code-block-button" aria-label="Undo Edit"><i data-feather="rotate-ccw" class="w-4 h-4"></i></button>
              <button @click="redo" :disabled="!canRedo" title="Redo (Ctrl+Y)" class="code-block-button" aria-label="Redo Edit"><i data-feather="rotate-cw" class="w-4 h-4"></i></button>
               <div class="h-4 w-px bg-gray-400 dark:bg-gray-600 mx-1"></div>
               <button @click="toggleSearch" :title="isSearchVisible ? 'Hide Search' : 'Show Search'" class="code-block-button" aria-label="Toggle Search">
                  <i :data-feather="isSearchVisible ? 'x' : 'search'" class="w-4 h-4"></i>
               </button>
            </template>
            <button @click="copyCode" :title="copyTitle" class="code-block-button" aria-label="Copy Code"><i :data-feather="copyIcon" class="w-4 h-4"></i></button>
             <div v-if="!isEditing" class="h-4 w-px bg-gray-400 dark:bg-gray-600 mx-1"></div>
            <template v-if="!isEditing">
              <button v-if="canExecute" @click="executeCode" :title="executeTitle" class="code-block-button execute-button" :disabled="isExecuting" aria-label="Execute Code"><i :data-feather="executeIcon" :class="{'animate-spin': isExecuting}" class="w-4 h-4"></i></button>
              <button v-if="canExecuteInNewTab" @click="executeCode_in_new_tab" :title="executeNewTabTitle" class="code-block-button execute-button" :disabled="isExecuting" aria-label="Execute Code in New Tab"><i :data-feather="executeNewTabIcon" :class="{'animate-spin': isExecuting}" class="w-4 h-4"></i></button>
              <button @click="openFolder" title="Open Project Folder" class="code-block-button" aria-label="Open Project Folder"><i data-feather="folder" class="w-4 h-4"></i></button>
              <button v-if="canOpenFolderInVsCode" @click="openFolderVsCode" title="Open Project Folder in VS Code" class="code-block-button" aria-label="Open Project Folder in VS Code"><img src="@/assets/vscode_black.svg" class="w-4 h-4 dark:hidden" alt="VS Code"><img src="@/assets/vscode.svg" class="w-4 h-4 hidden dark:inline" alt="VS Code"></button>
              <button v-if="canOpenInVsCode" @click="openVsCode" title="Open Code in VS Code" class="code-block-button" aria-label="Open Code in VS Code"><img src="@/assets/vscode.svg" class="w-4 h-4" alt="VS Code"></button>
            </template>
          </div>
        </div>
  
        <!-- Search/Replace Panel -->
        <div v-if="isEditing && isSearchVisible" class="search-replace-panel flex items-center space-x-2 p-2 bg-gray-100 dark:bg-gray-700 text-sm mb-1 rounded">
          <input ref="searchInputRef" type="text" v-model.lazy="searchQuery" placeholder="Find" class="search-input flex-grow" aria-label="Search query" @keydown.enter.prevent="findNextAndHighlight" @keydown.shift.enter.prevent="findPreviousAndHighlight" />
          <span v-if="searchQuery" class="search-status" aria-live="polite"> {{ searchResults.length > 0 ? `${currentMatchIndexDisplay + 1} / ${searchResults.length}` : 'Not found' }} </span>
          <span v-else class="search-status text-gray-400 dark:text-gray-500" aria-live="polite">   </span>
          <button @click="findPreviousAndHighlight" :disabled="!hasMatches" title="Previous Match (Shift+Enter)" class="code-block-button search-button" aria-label="Previous Match"><i data-feather="chevron-left" class="w-4 h-4"></i></button>
          <button @click="findNextAndHighlight" :disabled="!hasMatches" title="Next Match (Enter)" class="code-block-button search-button" aria-label="Next Match"><i data-feather="chevron-right" class="w-4 h-4"></i></button>
          <input type="text" v-model="replaceQuery" placeholder="Replace with" class="replace-input flex-grow" aria-label="Replace query" @keydown.enter.prevent="replaceCurrentAndFindNext" />
          <button @click="replaceCurrent" :disabled="!hasActiveMatch" title="Replace Current" class="code-block-button search-button" aria-label="Replace Current">Replace</button>
          <button @click="replaceAll" :disabled="!hasMatches" title="Replace All" class="code-block-button search-button" aria-label="Replace All">All</button>
        </div>
  
        <!-- Code Area Wrapper -->
        <div ref="codeAreaWrapper" class="code-area-wrapper max-h-96 overflow-y-auto rounded-b-md bg-white dark:bg-gray-800 scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
          <div class="code-content-flex flex font-mono text-sm leading-snug">
            <!-- Line Numbers -->
            <div class="line-numbers flex-shrink-0 p-2 text-right text-gray-500 select-none bg-gray-100 dark:bg-gray-700 whitespace-pre overflow-y-hidden border-r border-gray-300 dark:border-gray-600" v-html="lineNumbersHtml" aria-hidden="true"></div>
            <!-- Code Content -->
            <div
              ref="codeContentEditable"
              class="code-content hljs flex-grow p-2 whitespace-pre-wrap break-words overflow-x-auto overflow-y-hidden scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-400 dark:scrollbar-thumb-gray-500 focus:outline-none"
              :contenteditable="isEditing" spellcheck="false" role="textbox" aria-multiline="true"
              :aria-label="`Code block (${effectiveLanguage || 'plaintext'})`"
              @input="debouncedHandleInput"
              @paste="handlePaste"
              @keydown.enter.prevent="handleEnterKey"
              @keydown.tab.prevent="handleTabKey"
              @blur="handleBlur"
              @click="clearSearchSelectionOnClick"
              @keydown="handleUndoRedoKeys"
            ></div>
          </div>
        </div>
      </div>
  
      <!-- == Execution Output (Common) == -->
      <div v-if="executionOutput" class="mt-2" aria-live="polite">
        <span class="text-lg font-semibold text-gray-700 dark:text-gray-300">Execution Output:</span>
        <div class="execution-output-content hljs mt-1 p-2 rounded-md break-words text-sm leading-relaxed bg-white dark:bg-gray-800 max-h-48 overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary" v-html="sanitizedExecutionOutputHtml"></div>
      </div>
  
    </div>
  </template>
  
  <script>
  import { nextTick } from 'vue';
  import hljs from 'highlight.js';
  import feather from 'feather-icons';
  import DOMPurify from 'dompurify';
  import { debounce } from 'lodash-es';
  
  import 'highlight.js/styles/github.css';
  import 'highlight.js/styles/tokyo-night-dark.css';
  
  const EXECUTABLE_LANGUAGES = new Set(['function', 'python', 'sh', 'shell', 'bash', 'cmd', 'powershell', 'latex', 'mermaid', 'graphviz', 'dot', 'javascript', 'html', 'html5', 'svg', 'lilypond']);
  const NEW_TAB_EXECUTABLE_LANGUAGES = new Set(['airplay', 'mermaid', 'graphviz', 'dot', 'javascript', 'html', 'html5', 'svg', 'css']);
  const VSCODE_SUPPORTED_LANGUAGES = new Set(['python', 'latex', 'html', 'javascript', 'typescript', 'css', 'scss', 'less', 'json', 'yaml', 'markdown', 'java', 'csharp', 'php', 'ruby', 'go', 'rust', 'shell', 'bash', 'powershell']);
  const STREAMING_UPDATE_DEBOUNCE_MS = 200; // Debounce prop updates
  const INPUT_DEBOUNCE_MS = 250;
  const SEARCH_DEBOUNCE_MS = 200;
  const UNDO_STACK_LIMIT = 50;
  
  function getHighlightedHtml(code, language) {
    const codeToHighlight = typeof code === 'string' ? code : '';
    try {
      const effectiveLang = hljs.getLanguage(language) ? language : 'plaintext';
      const result = hljs.highlight(codeToHighlight, { language: effectiveLang, ignoreIllegals: true });
      let finalHtml = result.value;
      if (codeToHighlight.endsWith('\n') && !finalHtml.endsWith('<br>')) {
         const tempDiv = document.createElement('div');
         tempDiv.innerHTML = finalHtml;
         const lastChild = tempDiv.lastChild;
          let endsWithBreakEquivalent = (lastChild?.nodeName === 'BR') || (lastChild?.nodeType === Node.TEXT_NODE && lastChild.textContent?.endsWith('\n'));
          if (!endsWithBreakEquivalent) finalHtml += '<br>';
      }
      return finalHtml;
    } catch (e) {
      console.warn("Highlighting error:", e, "Lang:", language);
      return codeToHighlight.replace(/</g, "<").replace(/>/g, ">").replace(/\n/g, '<br>');
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
        offset = Math.min(offset, nodeLength);
        return { node, offset };
      }
      currentTotalIndex += nodeLength;
    }
    if (charIndex === currentTotalIndex) {
      let lastTextNode = null;
      const walkerReverse = document.createTreeWalker(parentElement, NodeFilter.SHOW_TEXT, null, false);
      while(walkerReverse.nextNode()) { lastTextNode = walkerReverse.currentNode; }
      if (lastTextNode) return { node: lastTextNode, offset: lastTextNode.textContent?.length || 0 };
    }
    console.warn(`getTextNodeAndOffset: Could not find node/offset for index ${charIndex}.`);
    return null;
  }
  
  export default {
    name: 'CodeBlock',
    props: {
      host: { type: String, required: false, default: "" },
      language: { type: String, required: true },
      code: { type: String, required: true },
      client_id: { type: String, required: true },
      discussion_id: { type: [String, Number], required: true },
      message_id: { type: [String, Number], required: true },
    },
    emits: ['update-code'],
    data() {
      return {
        isExecuting: false,
        isCopied: false,
        executionOutput: '',
        copyTimeout: null,
        isComponentMounted: false,
        isFunctionDetailsVisible: false,
        internalCode: '',
        isEditing: false,
        isSearchVisible: false,
        searchQuery: '',
        replaceQuery: '',
        searchResults: [],
        currentMatchIndex: -1,
        undoStack: [],
        redoStack: [],
        isApplyingUndoRedo: false,
        isApplyingHighlight: false,
        debouncedHandleInput: null,
        debouncedFindMatches: null,
        debouncedUpdateFromProp: null,
      };
    },
    computed: {
      canUndo() { return this.undoStack.length > 1; }, // Need more than initial state
      canRedo() { return this.redoStack.length > 0; },
      safeCodeProp() { return typeof this.code === 'string' ? this.code : ''; },
      safeLanguageProp() { return typeof this.language === 'string' ? this.language : ''; },
      normalizedLanguage() { return this.safeLanguageProp.trim().toLowerCase(); },
      isFunctionLanguage() { return this.normalizedLanguage === 'function'; },
      canExecute() { return EXECUTABLE_LANGUAGES.has(this.normalizedLanguage); },
      canExecuteInNewTab() { return NEW_TAB_EXECUTABLE_LANGUAGES.has(this.normalizedLanguage); },
      canOpenFolderInVsCode() { return VSCODE_SUPPORTED_LANGUAGES.has(this.normalizedLanguage); },
      canOpenInVsCode() { return VSCODE_SUPPORTED_LANGUAGES.has(this.normalizedLanguage); },
      effectiveLanguage() {
        const lang = this.normalizedLanguage;
        if (this.isFunctionLanguage) return 'json';
        if (['vue', 'vue.js'].includes(lang)) return 'html';
        if (lang === 'html5') return 'html';
        if (['shell', 'sh', 'bash', 'cmd', 'powershell'].includes(lang)) return 'bash';
        if (lang === 'dot') return 'graphviz';
        return hljs.getLanguage(lang) ? lang : 'plaintext';
      },
      parsedFunctionCall() {
        if (!this.isFunctionLanguage || !this.safeCodeProp) return null;
        try {
          const parsed = JSON.parse(this.safeCodeProp);
          if (typeof parsed === 'object' && parsed !== null && typeof parsed.function_name === 'string' && parsed.function_name.trim() !== '' && typeof parsed.function_parameters === 'object' && parsed.function_parameters !== undefined) {
            return parsed;
          }
          return null;
        } catch (e) { return null; }
      },
      isValidFunctionCall() { return this.parsedFunctionCall !== null; },
      functionName() { return this.parsedFunctionCall?.function_name ?? 'N/A'; },
      functionParametersObject() { return this.parsedFunctionCall?.function_parameters ?? {}; },
      hasParameters() { return Object.keys(this.functionParametersObject).length > 0; },
      lineNumbersHtml() {
        if (this.isFunctionLanguage) return '';
        const codeSource = this.internalCode || ''; // Use internalCode, default to empty string
        const lines = codeSource.split('\n');
        const lineCount = Math.max(1, lines.length); // Ensure at least 1 line number
        const lineNumberWidth = Math.max(1, String(lineCount).length);
        let numbers = '';
        for (let i = 1; i <= lineCount; i++) {
          numbers += `${String(i).padStart(lineNumberWidth, ' ')}<br>`;
        }
         // Only remove trailing <br> if code doesn't end with newline AND there's more than one line
        if (!codeSource.endsWith('\n') && lineCount > 1 && numbers.endsWith('<br>')) {
          numbers = numbers.slice(0, -4);
        } else if (codeSource === '' && numbers === '1<br>') {
           numbers = '1'; // Handle empty code case specifically
        }
        return numbers || '1'; // Ensure at least '1' is returned
      },
      sanitizedExecutionOutputHtml() {
        const config = { USE_PROFILES: { html: true }, ADD_TAGS: ['iframe', 'svg', 'path', 'g', 'circle', 'rect', 'line', 'polyline', 'polygon', 'text', 'tspan', 'style', 'defs', 'marker', 'use', 'a'], ADD_ATTS: ['style', 'transform', 'cx', 'cy', 'r', 'x', 'y', 'width', 'height', 'fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'points', 'd', 'marker-start', 'marker-end', 'viewBox', 'preserveAspectRatio', 'class', 'id', 'href', 'target', 'text-anchor', 'dominant-baseline', 'font-size', 'font-family', 'dy', 'aria-label'], ALLOW_DATA_ATTR: true, ALLOW_UNKNOWN_PROTOCOLS: false, FORBID_TAGS: ['script'], FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur'] };
        return DOMPurify.sanitize(this.executionOutput, config);
      },
      copyIcon() { return this.isCopied ? 'check' : 'copy'; },
      copyTitle() { return this.isCopied ? 'Copied!' : 'Copy code'; },
      executeIcon() { return this.isExecuting ? 'loader' : 'play-circle'; },
      executeTitle() { return this.isExecuting ? 'Executing...' : (this.isFunctionLanguage ? 'Execute Function Call' : 'Execute Code'); },
      executeNewTabIcon() { return this.isExecuting ? 'loader' : 'airplay'; },
      executeNewTabTitle() { return this.isExecuting ? 'Executing...' : 'Execute Code in New Tab'; },
      hasMatches() { return this.searchResults.length > 0; },
      hasActiveMatch() { return this.currentMatchIndex >= 0 && this.currentMatchIndex < this.searchResults.length; },
      currentMatchIndexDisplay() { return this.hasActiveMatch ? this.currentMatchIndex : -1; },
    },
    watch: {
      code(newCode) {
        const newSafeCode = typeof newCode === 'string' ? newCode : '';
        // Ignore updates if editing, component not mounted, or code hasn't changed externally
        if (this.isEditing || !this.isComponentMounted || newSafeCode === this.internalCode) {
          return;
        }
         // Debounce the actual update and highlighting
         this.debouncedUpdateFromProp(newSafeCode);
      },
      searchQuery() {
        this.currentMatchIndex = -1;
        this.debouncedFindMatches();
      },
      isEditing(newValue) {
          if (!newValue) { // Exiting edit mode
               this.isSearchVisible = false; // Hide search when exiting edit mode
               this.applyHighlighting(this.internalCode, false); // Re-highlight
          } else { // Entering edit mode
              this.$nextTick(() => { this.$refs.codeContentEditable?.focus(); });
          }
          this.triggerIconUpdate();
      }
    },
    methods: {
      updateFromPropLogic(newSafeCode) {
          // This function is called by the debounced watcher
          // Ensure we're not in edit mode again just before applying
          if (this.isEditing) return;
  
          this.isApplyingHighlight = true; // Prevent input handler during highlight
          this.internalCode = newSafeCode;
          this.applyHighlighting(newSafeCode); // Update display
          this.undoStack = [newSafeCode]; // Reset history
          this.redoStack = [];
          this.clearSearchState(true); // Reset search
          this.triggerIconUpdate(); // Update undo/redo buttons etc.
          this.$nextTick(() => { this.isApplyingHighlight = false; });
      },
      getActualCode() {
        return this.isFunctionLanguage ? this.safeCodeProp : this.internalCode;
      },
      snapshotState(currentState) {
        if (this.isFunctionLanguage || this.isApplyingUndoRedo || this.isApplyingHighlight) return;
        const previousState = this.undoStack.length > 0 ? this.undoStack[this.undoStack.length - 1] : null;
        if (previousState !== currentState) {
          this.undoStack.push(currentState);
          if (this.undoStack.length > UNDO_STACK_LIMIT) this.undoStack.shift();
          if (this.redoStack.length > 0) this.redoStack = [];
          this.triggerIconUpdate();
        }
      },
      undo() {
        if (!this.canUndo || !this.isEditing || !this.$refs.codeContentEditable) return;
        this.isApplyingUndoRedo = true;
        const currentState = this.internalCode;
        const prevState = this.undoStack.pop();
        if (prevState !== undefined) {
          this.redoStack.push(currentState);
          this.internalCode = prevState;
          this.setEditorContent(prevState, true); // Update display, preserve cursor roughly
          this.$emit('update-code', this.internalCode);
          this.clearSearchState(false);
          this.triggerIconUpdate();
          this.$nextTick(() => { this.restoreCursorToEnd(); }); // Move cursor reliably after DOM update
        }
        this.$nextTick(() => { this.isApplyingUndoRedo = false; });
      },
      redo() {
        if (!this.canRedo || !this.isEditing || !this.$refs.codeContentEditable) return;
        this.isApplyingUndoRedo = true;
        const nextState = this.redoStack.pop();
        if (nextState !== undefined) {
          const currentState = this.internalCode;
          this.undoStack.push(currentState);
          if (this.undoStack.length > UNDO_STACK_LIMIT) this.undoStack.shift();
          this.internalCode = nextState;
          this.setEditorContent(nextState, true); // Update display, preserve cursor roughly
          this.$emit('update-code', this.internalCode);
          this.clearSearchState(false);
          this.triggerIconUpdate();
           this.$nextTick(() => { this.restoreCursorToEnd(); }); // Move cursor reliably after DOM update
        }
        this.$nextTick(() => { this.isApplyingUndoRedo = false; });
      },
      handleUndoRedoKeys(event) {
        if (!this.isEditing) return;
        const isMac = navigator.platform.toUpperCase().indexOf('MAC') >= 0;
        const isUndo = (isMac && event.metaKey && !event.shiftKey && event.key === 'z') || (!isMac && event.ctrlKey && !event.shiftKey && event.key === 'z');
        const isRedo = (isMac && event.metaKey && event.shiftKey && event.key === 'z') || (!isMac && event.ctrlKey && (event.key === 'y' || (event.shiftKey && event.key === 'z'))); // Ctrl+Y or Ctrl+Shift+Z
  
        if (isUndo) { event.preventDefault(); this.undo(); }
        else if (isRedo) { event.preventDefault(); this.redo(); }
      },
      setEditorContent(newCode, useInnerText = false) {
        const editor = this.$refs.codeContentEditable;
        if (!editor) return;
  
        if (useInnerText && this.isEditing) {
           // When editing, setting innerText is usually safer and preserves undo buffer better
           // than innerHTML, but we lose highlighting. This is a trade-off.
           // For Undo/Redo, let's set innerText and maybe re-highlight selectively later if needed.
           editor.innerText = newCode ?? '';
        } else {
           // For initial load, prop updates, or exiting edit mode, use highlighting.
           this.isApplyingHighlight = true;
           const highlightedHtml = getHighlightedHtml(newCode, this.effectiveLanguage);
           editor.innerHTML = highlightedHtml;
           this.$nextTick(() => { this.isApplyingHighlight = false; });
        }
      },
      applyHighlighting(codeToHighlight, preserveSelection = false) {
          if (this.isFunctionLanguage || !this.$refs.codeContentEditable || this.isEditing) return; // Only highlight when not editing
  
          const editor = this.$refs.codeContentEditable;
          let savedSelState = null;
  
          if (preserveSelection && document.activeElement === editor) {
              // Save selection logic (simplified - might be less precise after highlight)
              const sel = window.getSelection();
              if (sel?.rangeCount > 0 && editor.contains(sel.anchorNode)) {
                  try {
                       const range = sel.getRangeAt(0);
                       const preSelectionRange = document.createRange();
                       preSelectionRange.selectNodeContents(editor);
                       preSelectionRange.setEnd(range.startContainer, range.startOffset);
                       const start = preSelectionRange.toString().length;
                       const end = start + range.toString().length;
                       savedSelState = { start, end };
                  } catch (e) { console.warn("Could not save selection state:", e); }
              }
          }
  
          this.setEditorContent(codeToHighlight, false); // Apply highlighted HTML
  
          if (savedSelState) {
             this.$nextTick(() => {
                 try {
                     const startPos = getTextNodeAndOffset(editor, savedSelState.start);
                     const endPos = getTextNodeAndOffset(editor, savedSelState.end);
                     if (startPos && endPos) {
                         const newRange = document.createRange();
                          const safeStartOffset = Math.min(startPos.offset, startPos.node.textContent?.length ?? 0);
                          const safeEndOffset = Math.min(endPos.offset, endPos.node.textContent?.length ?? 0);
                          newRange.setStart(startPos.node, safeStartOffset);
                          newRange.setEnd(endPos.node, safeEndOffset);
                         const sel = window.getSelection();
                         sel?.removeAllRanges(); sel?.addRange(newRange);
                     }
                 } catch (e) { console.error("Error restoring selection:", e, "State:", savedSelState); }
             });
          }
      },
      restoreCursorToEnd() {
          const editor = this.$refs.codeContentEditable;
          if (!editor) return;
          this.$nextTick(() => {
              const range = document.createRange();
              const sel = window.getSelection();
              range.selectNodeContents(editor);
              range.collapse(false); // Collapse to end
              sel?.removeAllRanges();
              sel?.addRange(range);
              editor.focus();
          });
      },
      insertTextAtCursor(textToInsert) {
          if (!this.isEditing || !this.$refs.codeContentEditable) return;
  
          const editor = this.$refs.codeContentEditable;
          let sel = window.getSelection();
          if (!sel || sel.rangeCount === 0 || !editor.contains(sel.anchorNode)) {
              this.restoreCursorToEnd(); // Ensure cursor is somewhere valid
              sel = window.getSelection();
              if (!sel || sel.rangeCount === 0) return;
          }
  
          this.snapshotState(this.internalCode); // Snapshot before change
  
          const range = sel.getRangeAt(0);
          range.deleteContents();
          const textNode = document.createTextNode(textToInsert);
          range.insertNode(textNode);
          range.setStartAfter(textNode);
          range.collapse(true);
          sel.removeAllRanges();
          sel.addRange(range);
  
          this.$nextTick(() => { // Update internal state after DOM change
              const newCode = editor.innerText ?? '';
              if (newCode !== this.internalCode) {
                  this.internalCode = newCode;
                  this.$emit('update-code', newCode);
                  this.clearSearchState(false); // Clear matches, keep query
                  if(this.isSearchVisible && this.searchQuery) this.debouncedFindMatches();
              }
          });
      },
      handleInputLogic(event) {
        if (!this.isEditing || this.isApplyingUndoRedo || this.isApplyingHighlight || !this.$refs.codeContentEditable) return;
        const currentText = event.target.innerText ?? '';
        if (currentText !== this.internalCode) {
          this.snapshotState(this.internalCode); // Snapshot *before* this change
          this.internalCode = currentText;
          this.$emit('update-code', currentText);
          this.clearSearchState(false);
          if (this.isSearchVisible && this.searchQuery) this.debouncedFindMatches();
        }
      },
      handlePaste(event) {
        if (!this.isEditing) return;
        event.preventDefault();
        const text = event.clipboardData?.getData('text/plain') || '';
        if (text) this.insertTextAtCursor(text);
      },
      handleEnterKey(event) { if (this.isEditing) this.insertTextAtCursor('\n'); },
      handleTabKey(event) { if (this.isEditing) this.insertTextAtCursor('\t'); },
      handleBlur(event) {
          if (!this.isEditing || !this.$refs.codeContentEditable) return;
          this.debouncedHandleInput.flush(); // Ensure last input is processed
          // Don't re-highlight on blur while editing, user might click buttons
      },
      clearSearchSelectionOnClick(event) {
        if (this.isEditing && this.isSearchVisible && this.hasActiveMatch && event.target === this.$refs.codeContentEditable) {
          // If click is inside editor while search is active, deselect the search highlight
          this.$nextTick(() => { // Allow browser default click behavior first
              const sel = window.getSelection();
              if (sel && sel.type !== "Range") { // If selection is collapsed (caret)
                  this.currentMatchIndex = -1; // Deselect search logically
              }
          });
        }
      },
      toggleEditMode() {
          this.isEditing = !this.isEditing;
          // Highlighting/focus handled by watcher and setEditorContent
      },
      triggerIconUpdate() {
        this.$nextTick(() => { try { feather.replace(); } catch (e) { /* ignore */ } });
      },
      async copyCode() {
        if (this.isCopied) return;
        const codeToCopy = this.getActualCode();
        try {
          await navigator.clipboard.writeText(codeToCopy);
          this.isCopied = true;
          this.triggerIconUpdate();
          if (this.copyTimeout) clearTimeout(this.copyTimeout);
          this.copyTimeout = setTimeout(() => {
            this.isCopied = false; this.triggerIconUpdate(); this.copyTimeout = null;
            // Optional toast notification can be added here
          }, 1500);
        } catch (err) { console.error('Failed to copy code:', err); alert('Error: Could not copy code.'); }
      },
      executeCodeInternal(endpointUrl, shouldOpenInNewTab = false) {
        if (this.isExecuting) return;
        this.isExecuting = true;
        this.executionOutput = '';
        this.triggerIconUpdate();
        const currentCode = this.getActualCode();
        const requestPayload = { client_id: this.client_id, code: currentCode, discussion_id: Number(this.discussion_id || 0), message_id: Number(this.message_id || 0), language: this.normalizedLanguage };
  
        fetch(`${this.host}/${endpointUrl}`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json, text/plain, */*' }, body: JSON.stringify(requestPayload) })
          .then(async response => {
            const contentType = response.headers.get("content-type");
            let responseData;
            if (contentType?.includes("application/json")) responseData = await response.json();
            else responseData = { output: await response.text() };
            if (!response.ok) {
               let errorDetails = `HTTP error! Status: ${response.status}`;
               if (responseData?.error) errorDetails += `, Message: ${responseData.error}`;
               else if (typeof responseData?.output === 'string') errorDetails += `, Body: ${responseData.output.substring(0, 100)}...`;
               else if (responseData?.detail) errorDetails += `, Detail: ${responseData.detail}`;
               const error = new Error(errorDetails); error.response = responseData; throw error;
            }
            return responseData;
          })
          .then(data => {
            this.executionOutput = data.output ?? (data.message ?? (typeof data === 'object' ? JSON.stringify(data, null, 2) : String(data)));
            if (shouldOpenInNewTab && data.url) {
               try { window.open(data.url, '_blank', 'noopener,noreferrer'); }
               catch(e) { console.error("Failed to open URL:", e); this.executionOutput += `\n(Failed to open URL: ${data.url})`; }
            }
          })
          .catch(error => { console.error('Code execution failed:', error); this.executionOutput = `Execution Error: ${error.message}`; })
          .finally(() => {
            this.isExecuting = false; this.triggerIconUpdate();
            this.$nextTick(() => { this.$el.querySelector('.execution-output-content')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); });
          });
      },
      executeCode() { this.executeCodeInternal('execute_code', false); },
      executeCode_in_new_tab() { this.executeCodeInternal('execute_code_in_new_tab', true); },
      postRequest(endpointUrl, requestPayload = {}) {
        const payloadToSend = { ...requestPayload, client_id: this.client_id, discussion_id: Number(this.discussion_id || 0) };
        if (endpointUrl === 'open_code_in_vs_code') {
           payloadToSend.code = this.getActualCode();
           payloadToSend.message_id = Number(this.message_id || 0);
        }
        fetch(`${this.host}/${endpointUrl}`, { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(payloadToSend) })
          .then(async response => {
            if (!response.ok) {
               let errorDetail = `HTTP ${response.status}`; try { const eb = await response.json(); errorDetail += `: ${eb.detail || JSON.stringify(eb)}`; } catch (e) { errorDetail += ` (${response.statusText})`; } throw new Error(errorDetail);
            }
            const contentType = response.headers.get("content-type");
            return (contentType?.includes("application/json")) ? response.json() : {};
          })
          .then(data => { console.log(`${endpointUrl} success:`, data); /* Optional success notification */ })
          .catch(error => { console.error(`Fetch error during ${endpointUrl}:`, error); alert(`Operation failed: ${error.message}`); });
      },
      openFolderVsCode() { this.postRequest('open_discussion_folder_in_vs_code'); },
      openVsCode() { this.postRequest('open_code_in_vs_code'); },
      openFolder() { this.postRequest('open_discussion_folder'); },
      toggleFunctionDetails() { this.isFunctionDetailsVisible = !this.isFunctionDetailsVisible; this.triggerIconUpdate(); },
      clearSearchState(clearQueryAndReplace = false) {
        if (clearQueryAndReplace) { this.searchQuery = ''; this.replaceQuery = ''; }
        if (this.searchResults.length > 0 || this.currentMatchIndex !== -1) {
          this.searchResults = [];
          this.currentMatchIndex = -1;
          const sel = window.getSelection();
          if (this.$refs.codeContentEditable?.contains(sel?.anchorNode)) sel?.removeAllRanges();
        }
      },
      toggleSearch() {
        this.isSearchVisible = !this.isSearchVisible;
        if (!this.isSearchVisible) this.clearSearchState(true);
        else this.$nextTick(() => { this.$refs.searchInputRef?.focus(); if (this.searchQuery) this.debouncedFindMatches(); });
        this.triggerIconUpdate();
      },
      findMatchesLogic() {
        if (!this.isEditing || !this.$refs.codeContentEditable) return;
        const editor = this.$refs.codeContentEditable;
        const text = editor.innerText ?? '';
        const query = this.searchQuery;
  
        if (!query) { this.clearSearchState(false); return; }
  
        const results = []; let startIndex = 0; let index;
        while ((index = text.indexOf(query, startIndex)) > -1) {
          results.push({ start: index, end: index + query.length });
          if (query.length === 0) break; startIndex = index + 1;
        }
        this.searchResults = results;
  
        if (results.length > 0) {
            const needsNewSelection = this.currentMatchIndex === -1 || this.currentMatchIndex >= results.length;
            this.currentMatchIndex = needsNewSelection ? 0 : this.currentMatchIndex;
            this.highlightMatch(this.currentMatchIndex, false); // Select current/first match, no scroll initially
        } else {
            this.currentMatchIndex = -1;
            const sel = window.getSelection();
            if (editor.contains(sel?.anchorNode)) sel?.removeAllRanges(); // Clear selection if no matches
        }
      },
      scrollToMatch(index) {
          if (!this.isEditing || !this.$refs.codeContentEditable || index < 0 || index >= this.searchResults.length) return;
          const editor = this.$refs.codeContentEditable;
          const match = this.searchResults[index];
          const startPos = getTextNodeAndOffset(editor, match.start);
          if (startPos?.node) {
              try {
                   const range = document.createRange();
                   const safeOffset = Math.min(startPos.offset, startPos.node.textContent?.length ?? 0);
                   range.setStart(startPos.node, safeOffset); range.collapse(true);
                   const tempSpan = document.createElement('span'); tempSpan.textContent='\ufeff';
                   range.insertNode(tempSpan);
                   tempSpan.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'nearest' });
                   tempSpan.parentNode?.removeChild(tempSpan);
              } catch(e) { console.error("Scroll error:", e); startPos.node.parentElement?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); }
          }
      },
      highlightMatch(index, scroll = true) {
        if (!this.isEditing || !this.$refs.codeContentEditable || index < 0 || index >= this.searchResults.length) {
           const sel = window.getSelection();
           if (this.$refs.codeContentEditable?.contains(sel?.anchorNode)) sel?.removeAllRanges();
           return;
        }
        const editor = this.$refs.codeContentEditable;
        const match = this.searchResults[index];
        const startPos = getTextNodeAndOffset(editor, match.start);
        const endPos = getTextNodeAndOffset(editor, match.end);
  
        if (startPos && endPos) {
          try {
            const range = document.createRange();
             const safeStartOffset = Math.min(startPos.offset, startPos.node.textContent?.length ?? 0);
             const safeEndOffset = Math.min(endPos.offset, endPos.node.textContent?.length ?? 0);
             range.setStart(startPos.node, safeStartOffset); range.setEnd(endPos.node, safeEndOffset);
            const sel = window.getSelection();
            sel?.removeAllRanges(); sel?.addRange(range);
            if (scroll) this.scrollToMatch(index);
          } catch (e) { console.error("Highlight range error:", e); }
        } else {
            console.warn("Nodes not found for highlighting match:", match);
            const sel = window.getSelection();
            if (editor.contains(sel?.anchorNode)) sel?.removeAllRanges();
        }
      },
      findNextAndHighlight() {
        if (!this.hasMatches) return;
        let nextIndex = (this.currentMatchIndex + 1) % this.searchResults.length;
        this.currentMatchIndex = nextIndex;
        this.highlightMatch(this.currentMatchIndex, true);
        this.$nextTick(() => this.$refs.searchInputRef?.focus());
      },
      findPreviousAndHighlight() {
        if (!this.hasMatches) return;
        let prevIndex = (this.currentMatchIndex - 1 + this.searchResults.length) % this.searchResults.length;
        this.currentMatchIndex = prevIndex;
        this.highlightMatch(this.currentMatchIndex, true);
        this.$nextTick(() => this.$refs.searchInputRef?.focus());
      },
      replaceCurrent() {
          if (!this.isEditing || !this.$refs.codeContentEditable || !this.hasActiveMatch) return;
          this.snapshotState(this.internalCode); // Snapshot before replace
  
          const editor = this.$refs.codeContentEditable;
          const matchToReplace = this.searchResults[this.currentMatchIndex];
          const originalStart = matchToReplace.start;
          const replacementLength = this.replaceQuery.length;
          const originalLength = this.searchQuery.length; // Use searchQuery length
  
          // Select the match firmly before replacing
          this.highlightMatch(this.currentMatchIndex, false);
  
          this.$nextTick(() => {
               const sel = window.getSelection();
               if (sel && !sel.isCollapsed && editor.contains(sel.anchorNode)) {
                  // Use document.execCommand for potential better integration with browser undo/redo?
                  // document.execCommand('insertText', false, this.replaceQuery);
                  // Or stick with manual manipulation:
                  const range = sel.getRangeAt(0);
                  range.deleteContents();
                  const textNode = document.createTextNode(this.replaceQuery);
                  range.insertNode(textNode);
                  range.setStartAfter(textNode); range.collapse(true);
                  sel.removeAllRanges(); sel.addRange(range);
  
                  // Update internal state from DOM AFTER modification
                  const newCode = editor.innerText ?? '';
                  this.internalCode = newCode;
                  this.$emit('update-code', newCode);
  
                  // Re-find matches immediately based on the *new* code
                  this.findMatchesLogic(); // This will update searchResults and reset currentMatchIndex if needed
  
                  // Try to select the *next* logical match after the replacement point
                  if (this.hasMatches) {
                      // Calculate where the next match *should* start
                      const expectedNextStart = originalStart + replacementLength;
                       let nextLogicalIndex = this.searchResults.findIndex(m => m.start >= originalStart); // Find first match starting at or after the replaced position
                       if (nextLogicalIndex === -1) nextLogicalIndex = 0; // Wrap around if none found after
  
                      this.currentMatchIndex = nextLogicalIndex;
                      this.highlightMatch(this.currentMatchIndex, true); // Highlight and scroll
                  } else {
                      this.currentMatchIndex = -1; // No matches left
                  }
               } else {
                   console.warn("Replace failed: No active selection.");
                   this.findMatchesLogic(); // Refresh search state
               }
               this.$nextTick(() => this.$refs.searchInputRef?.focus());
          });
      },
      replaceCurrentAndFindNext() { if (this.hasActiveMatch) this.replaceCurrent(); },
      replaceAll() {
        if (!this.isEditing || !this.$refs.codeContentEditable || !this.hasMatches || !this.searchQuery) return;
        this.snapshotState(this.internalCode);
  
        const editor = this.$refs.codeContentEditable;
        const originalCode = editor.innerText ?? '';
        const query = this.searchQuery;
        const replacement = this.replaceQuery;
        let newCode = originalCode;
  
        try {
           // Use native replaceAll if available (more efficient and handles edge cases)
           if (typeof newCode.replaceAll === 'function') {
             newCode = newCode.replaceAll(query, replacement);
           } else { // Fallback using RegExp
             const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
             newCode = newCode.replace(new RegExp(escapedQuery, 'g'), replacement);
           }
        } catch (e) { console.error("Replace All error:", e); alert("Error during Replace All."); return; }
  
        if (newCode !== originalCode) {
          this.internalCode = newCode;
          // Update editor content without highlighting temporarily for stability
          this.setEditorContent(newCode, true);
          this.$emit('update-code', newCode);
          this.clearSearchState(false); // Clear results, keep query
          // Re-run search immediately after DOM update
          this.$nextTick(() => {
              this.findMatchesLogic();
              this.$refs.searchInputRef?.focus();
          });
        } else {
           this.$nextTick(() => this.$refs.searchInputRef?.focus());
        }
      },
    },
    created() {
      this.debouncedHandleInput = debounce(this.handleInputLogic, INPUT_DEBOUNCE_MS);
      this.debouncedFindMatches = debounce(this.findMatchesLogic, SEARCH_DEBOUNCE_MS);
      this.debouncedUpdateFromProp = debounce(this.updateFromPropLogic, STREAMING_UPDATE_DEBOUNCE_MS);
      this.internalCode = this.safeCodeProp;
      if (!this.isFunctionLanguage) this.undoStack = [this.internalCode];
    },
    mounted() {
      this.isComponentMounted = true;
      if (!this.isFunctionLanguage && this.$refs.codeContentEditable) {
          // Set initial content without highlighting if potentially editing later
          this.setEditorContent(this.internalCode, this.isEditing);
           // Apply highlighting only if not starting in edit mode (though default is false)
           if (!this.isEditing) {
               this.applyHighlighting(this.internalCode);
           }
      }
      this.triggerIconUpdate();
    },
    beforeUnmount() {
      if (this.copyTimeout) clearTimeout(this.copyTimeout);
      this.debouncedHandleInput?.cancel();
      this.debouncedFindMatches?.cancel();
      this.debouncedUpdateFromProp?.cancel();
    },
  };
  </script>
  
  <style scoped>
  .code-block-button { @apply p-1 rounded text-gray-600 dark:text-gray-300 hover:bg-primary dark:hover:bg-primary hover:text-white transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-primary disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent disabled:hover:text-gray-600 dark:disabled:hover:text-gray-300; }
  .feather-small { @apply w-3 h-3 inline-block align-middle; }
  .hljs { background: none !important; padding: 0 !important; margin: 0 !important; }
  .code-block-container { position: relative; }
  .code-content-flex { align-items: stretch; }
  .line-numbers { @apply flex-shrink-0 p-2 text-right text-gray-500 select-none bg-gray-100 dark:bg-gray-700 whitespace-pre overflow-y-hidden border-r border-gray-300 dark:border-gray-600; min-height: 100%; user-select: none; }
  .code-content { @apply flex-grow p-2 whitespace-pre-wrap break-words overflow-x-auto overflow-y-hidden scrollbar-thin scrollbar-track-transparent scrollbar-thumb-gray-400 dark:scrollbar-thumb-gray-500 focus:outline-none; min-height: 1.5em; caret-color: currentColor; color: theme('colors.gray.800'); background-color: theme('colors.white'); }
  .dark .code-content { color: theme('colors.gray.200'); background-color: theme('colors.gray.800'); }
  .code-content::-webkit-scrollbar { height: 8px; }
  .code-content::-webkit-scrollbar-thumb { border-radius: 4px; }
  .animate-spin { animation: spin 1s linear infinite; } @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
  .execute-button { @apply inline-flex items-center justify-center; }
  .dark .dark\:hidden { display: none; } .dark .dark\:inline { display: inline; } .hidden { display: none; }
  .code-block-button i[data-feather], .code-block-button img { vertical-align: middle; }
  .parameter-item { margin-bottom: 0.5rem; } .parameter-item > div:last-child { margin-left: 0.5rem; }
  .execution-output-content a { @apply text-blue-600 dark:text-blue-400 hover:underline; }
  .execution-output-content h1 { @apply text-xl font-bold my-2; } .execution-output-content h2 { @apply text-lg font-semibold my-1.5; } .execution-output-content h3 { @apply text-base font-semibold my-1; } .execution-output-content h4, .execution-output-content h5, .execution-output-content h6 { @apply font-semibold my-0.5; }
  .execution-output-content p { @apply my-1; } .execution-output-content ul { @apply list-disc list-inside ml-4 my-1; } .execution-output-content ol { @apply list-decimal list-inside ml-4 my-1; } .execution-output-content li { @apply my-0.5; }
  .execution-output-content code:not(pre > code) { @apply font-mono bg-gray-100 dark:bg-gray-700 px-1 py-0.5 rounded text-sm; } .execution-output-content pre { @apply font-mono bg-gray-100 dark:bg-gray-700 p-2 rounded my-1 overflow-x-auto text-sm; } .execution-output-content pre > code { @apply p-0 bg-transparent text-sm; }
  .execution-output-content blockquote { @apply border-l-4 border-gray-300 dark:border-gray-600 pl-2 italic my-1 text-gray-600 dark:text-gray-400; }
  .execution-output-content table { @apply w-full border-collapse border border-gray-300 dark:border-gray-600 my-2 text-sm; } .execution-output-content th, .execution-output-content td { @apply border border-gray-300 dark:border-gray-600 p-1.5 text-left; } .execution-output-content th { @apply bg-gray-100 dark:bg-gray-700 font-semibold; }
  .execution-output-content img { @apply max-w-full h-auto my-1 rounded border border-gray-200 dark:border-gray-700; } .execution-output-content svg { @apply max-w-full h-auto my-1; } .execution-output-content hr { @apply border-t border-gray-300 dark:border-gray-600 my-2; }
  .execution-output-content.hljs { color: theme('colors.gray.800'); background-color: theme('colors.white'); } .dark .execution-output-content.hljs { color: theme('colors.gray.200'); background-color: theme('colors.gray.800'); }
  .search-replace-panel { @apply border-b border-gray-300 dark:border-gray-600; }
  .search-replace-panel input[type="text"] { @apply px-2 py-1 border border-gray-300 dark:border-gray-500 rounded bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 text-xs focus:outline-none focus:ring-1 focus:ring-primary focus:border-primary; min-width: 80px; }
  .search-replace-panel .search-status { @apply text-xs text-gray-600 dark:text-gray-400 whitespace-nowrap px-1; min-width: 50px; text-align: center; }
  .search-replace-panel .search-button { @apply px-1 py-0.5 text-xs; } .search-replace-panel .search-button i[data-feather] { @apply w-3.5 h-3.5; }
  .search-replace-panel .code-block-button { @apply p-1 text-gray-600 dark:text-gray-300 hover:bg-primary dark:hover:bg-primary hover:text-white; } .search-replace-panel .code-block-button:disabled { @apply opacity-50 cursor-not-allowed hover:bg-transparent hover:text-gray-600 dark:hover:text-gray-300; }
  .code-content::selection { background-color: theme('colors.blue.200'); color: theme('colors.black'); } .dark .code-content::selection { background-color: theme('colors.blue.800'); color: theme('colors.white'); }
  .dark .code-content.hljs,.dark .execution-output-content.hljs{color:#a9b1d6}.dark .hljs-meta{color:#ff9e64}.dark .hljs-comment{color:#565f89;font-style:italic}.dark .hljs-tag{color:#f7768e}.dark .hljs-tag .hljs-name,.dark .hljs-tag .hljs-attr{color:#f7768e}.dark .hljs-keyword,.dark .hljs-selector-tag,.dark .hljs-literal,.dark .hljs-name{color:#bb9af7}.dark .hljs-deletion,.dark .hljs-number,.dark .hljs-attribute,.dark .hljs-variable,.dark .hljs-template-variable,.dark .hljs-symbol{color:#ff9e64}.dark .hljs-section,.dark .hljs-title,.dark .hljs-type{color:#7aa2f7}.dark .hljs-string,.dark .hljs-subst,.dark .hljs-regexp,.dark .hljs-link,.dark .hljs-addition,.dark .hljs-selector-id,.dark .hljs-selector-class{color:#9ece6a}.dark .hljs-built_in,.dark .hljs-bullet,.dark .hljs-code,.dark .hljs-formula{color:#7dcfff}.dark .hljs-emphasis{font-style:italic}.dark .hljs-strong{font-weight:bold}
  html:not(.dark) .code-content.hljs,html:not(.dark) .execution-output-content.hljs{color:#24292e}html:not(.dark) .hljs-meta{color:#6a737d}html:not(.dark) .hljs-comment{color:#6a737d;font-style:italic}html:not(.dark) .hljs-tag{color:#22863a}html:not(.dark) .hljs-tag .hljs-name,html:not(.dark) .hljs-tag .hljs-attr{color:#22863a}html:not(.dark) .hljs-keyword,html:not(.dark) .hljs-selector-tag,html:not(.dark) .hljs-literal,html:not(.dark) .hljs-name{color:#d73a49}html:not(.dark) .hljs-deletion,html:not(.dark) .hljs-number,html:not(.dark) .hljs-attribute,html:not(.dark) .hljs-variable,html:not(.dark) .hljs-template-variable,html:not(.dark) .hljs-symbol{color:#005cc5}html:not(.dark) .hljs-section,html:not(.dark) .hljs-title,html:not(.dark) .hljs-type{color:#6f42c1}html:not(.dark) .hljs-string,html:not(.dark) .hljs-subst,html:not(.dark) .hljs-regexp,html:not(.dark) .hljs-link,html:not(.dark) .hljs-addition,html:not(.dark) .hljs-selector-id,html:not(.dark) .hljs-selector-class{color:#032f62}html:not(.dark) .hljs-built_in,html:not(.dark) .hljs-bullet,html:not(.dark) .hljs-code,html:not(.dark) .hljs-formula{color:#e36209}html:not(.dark) .hljs-emphasis{font-style:italic}html:not(.dark) .hljs-strong{font-weight:bold}
  </style>