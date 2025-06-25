<template>
  <div :id="`code-block-container-${message_id}`" class="code-block-container bg-bg-light-tone-panel dark:bg-bg-dark-tone-panel p-2 rounded-lg shadow-sm mb-2">

      <!-- == Function Call Display == -->
      <div v-if="isFunctionLanguage" ref="functionDisplayRef">
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

      <!-- == SVG Display (Code/Render Tabs) == -->
      <div v-else-if="isSvgLanguage">
          <div class="flex justify-between items-center px-2 py-1 mb-1 rounded-t-lg bg-gray-200 dark:bg-gray-700">
              <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">SVG</span>
              <div class="flex flex-row space-x-1 items-center">
                  <button v-if="!isEditing" @click="toggleEditMode" title="Edit SVG Code" class="code-block-button" aria-label="Edit SVG Code"><i data-feather="edit-2" class="w-4 h-4"></i></button>
                  <template v-if="isEditing && svgActiveTab === 'code'">
                      <button @click="toggleEditMode" title="Finish Editing" class="code-block-button" aria-label="Finish Editing"><i data-feather="check" class="w-4 h-4"></i></button>
                      <button @click="undo" :disabled="!canUndo" title="Undo (Ctrl+Z)" class="code-block-button" aria-label="Undo Edit"><i data-feather="rotate-ccw" class="w-4 h-4"></i></button>
                      <button @click="redo" :disabled="!canRedo" title="Redo (Ctrl+Y)" class="code-block-button" aria-label="Redo Edit"><i data-feather="rotate-cw" class="w-4 h-4"></i></button>
                      <div class="h-4 w-px bg-gray-400 dark:bg-gray-600 mx-1"></div>
                      <button @click="toggleSearch" :title="isSearchVisible ? 'Hide Search' : 'Show Search'" class="code-block-button" :class="{'active-search-button': isSearchVisible}" aria-label="Toggle Search">
                          <i :data-feather="isSearchVisible ? 'x' : 'search'" class="w-4 h-4"></i>
                      </button>
                  </template>
                  <button @click="copyCode" :title="copyTitle" class="code-block-button" aria-label="Copy SVG Code"><i :data-feather="copyIcon" class="w-4 h-4"></i></button>
                  <div v-if="!isEditing" class="h-4 w-px bg-gray-400 dark:bg-gray-600 mx-1"></div>
                  <template v-if="!isEditing">
                      <button v-if="canExecuteInNewTab" @click="executeCode_in_new_tab" :title="executeNewTabTitle" class="code-block-button execute-button" :disabled="isExecuting" aria-label="Execute Code in New Tab"><i :data-feather="executeNewTabIcon" :class="{'animate-spin': isExecuting}" class="w-4 h-4"></i></button>
                      <button @click="openFolder" title="Open Project Folder" class="code-block-button" aria-label="Open Project Folder"><i data-feather="folder" class="w-4 h-4"></i></button>
                      <button v-if="canOpenFolderInVsCode" @click="openFolderVsCode" title="Open Project Folder in VS Code" class="code-block-button" aria-label="Open Project Folder in VS Code"><img src="@/assets/vscode_black.svg" class="w-4 h-4 dark:hidden" alt="VS Code"><img src="@/assets/vscode.svg" class="w-4 h-4 hidden dark:inline" alt="VS Code"></button>
                      <button v-if="canOpenInVsCode" @click="openVsCode" title="Open SVG Code in VS Code" class="code-block-button" aria-label="Open SVG Code in VS Code"><img src="@/assets/vscode.svg" class="w-4 h-4" alt="VS Code"></button>
                  </template>
              </div>
          </div>

          <div v-if="isEditing && isSearchVisible && svgActiveTab === 'code'" class="search-replace-panel flex items-center space-x-2 p-2 bg-gray-100 dark:bg-gray-700 text-sm mb-1 rounded">
              <input ref="searchInputRef" type="text" v-model.lazy="searchQuery" placeholder="Find" class="search-input flex-grow" aria-label="Search query" @keydown.enter.prevent="findNextAndHighlight" @keydown.shift.enter.prevent="findPreviousAndHighlight" />
              <span class="search-status" aria-live="polite"> {{ searchStatusText }} </span>
              <button @click="findPreviousAndHighlight" :disabled="!hasMatches" title="Previous Match (Shift+Enter)" class="code-block-button search-button" aria-label="Previous Match"><i data-feather="chevron-left" class="w-4 h-4"></i></button>
              <button @click="findNextAndHighlight" :disabled="!hasMatches" title="Next Match (Enter)" class="code-block-button search-button" aria-label="Next Match"><i data-feather="chevron-right" class="w-4 h-4"></i></button>
              <input type="text" v-model.lazy="replaceQuery" placeholder="Replace with" class="replace-input flex-grow" aria-label="Replace query" @keydown.enter.prevent="replaceCurrentAndFindNext" />
              <button @click="replaceCurrent" :disabled="!hasActiveMatch" title="Replace Current" class="code-block-button search-button" aria-label="Replace Current">Replace</button>
              <button @click="replaceAllMatches" :disabled="!hasMatches" title="Replace All" class="code-block-button search-button" aria-label="Replace All">All</button>
          </div>

          <div class="flex border-b border-gray-300 dark:border-gray-600 mb-1">
              <button
                  @click="setSvgTab('render')"
                  :class="[ 'px-3 py-1 text-sm font-medium rounded-t-md focus:outline-none', svgActiveTab === 'render' ? 'border-b-2 border-primary text-primary dark:border-primary-dark dark:text-primary-dark bg-bg-light-tone dark:bg-bg-dark-tone' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700']"
                  aria-controls="svg-render-panel" :aria-selected="svgActiveTab === 'render'" role="tab"
              > Render </button>
              <button
                  @click="setSvgTab('code')"
                  :class="[ 'px-3 py-1 text-sm font-medium rounded-t-md focus:outline-none', svgActiveTab === 'code' ? 'border-b-2 border-primary text-primary dark:border-primary-dark dark:text-primary-dark bg-bg-light-tone dark:bg-bg-dark-tone' : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700']"
                  aria-controls="svg-code-panel" :aria-selected="svgActiveTab === 'code'" role="tab"
              > Code </button>
          </div>

          <div class="svg-content-container rounded-b-md border border-gray-300 dark:border-gray-600 overflow-hidden" :class="{'editing-border': isEditing && svgActiveTab === 'code'}">
              <div v-show="svgActiveTab === 'render'" id="svg-render-panel" role="tabpanel" aria-labelledby="tab-render" class="p-2 bg-white dark:bg-gray-800 max-h-96 overflow-auto">
                  <div v-html="sanitizedSvgContent"></div>
              </div>
              <div v-show="svgActiveTab === 'code'" id="svg-code-panel" role="tabpanel" aria-labelledby="tab-code">
                  <div ref="cmEditorRef" class="cm-editor-wrapper-svg"></div>
              </div>
          </div>
      </div>

      <!-- == Standard Code Block Display == -->
      <div v-else>
          <div class="flex justify-between items-center px-2 py-1 mb-1 rounded-t-lg bg-gray-200 dark:bg-gray-700">
              <span class="text-sm font-semibold text-gray-700 dark:text-gray-300">{{ effectiveLanguageDisplay || 'plaintext' }}</span>
              <div class="flex flex-row space-x-1 items-center">
                  <button v-if="!isEditing" @click="toggleEditMode" title="Edit Code" class="code-block-button" aria-label="Edit Code"><i data-feather="edit-2" class="w-4 h-4"></i></button>
                  <template v-if="isEditing">
                      <button @click="toggleEditMode" title="Finish Editing" class="code-block-button" aria-label="Finish Editing"><i data-feather="check" class="w-4 h-4"></i></button>
                      <button @click="undo" :disabled="!canUndo" title="Undo (Ctrl+Z)" class="code-block-button" aria-label="Undo Edit"><i data-feather="rotate-ccw" class="w-4 h-4"></i></button>
                      <button @click="redo" :disabled="!canRedo" title="Redo (Ctrl+Y)" class="code-block-button" aria-label="Redo Edit"><i data-feather="rotate-cw" class="w-4 h-4"></i></button>
                      <div class="h-4 w-px bg-gray-400 dark:bg-gray-600 mx-1"></div>
                      <button @click="toggleSearch" :title="isSearchVisible ? 'Hide Search' : 'Show Search'" class="code-block-button" :class="{'active-search-button': isSearchVisible}" aria-label="Toggle Search">
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

          <div v-if="isEditing && isSearchVisible" class="search-replace-panel flex items-center space-x-2 p-2 bg-gray-100 dark:bg-gray-700 text-sm mb-1 rounded">
              <input ref="searchInputRef" type="text" v-model.lazy="searchQuery" placeholder="Find" class="search-input flex-grow" aria-label="Search query" @keydown.enter.prevent="findNextAndHighlight" @keydown.shift.enter.prevent="findPreviousAndHighlight" />
              <span class="search-status" aria-live="polite"> {{ searchStatusText }} </span>
              <button @click="findPreviousAndHighlight" :disabled="!hasMatches" title="Previous Match (Shift+Enter)" class="code-block-button search-button" aria-label="Previous Match"><i data-feather="chevron-left" class="w-4 h-4"></i></button>
              <button @click="findNextAndHighlight" :disabled="!hasMatches" title="Next Match (Enter)" class="code-block-button search-button" aria-label="Next Match"><i data-feather="chevron-right" class="w-4 h-4"></i></button>
              <input type="text" v-model.lazy="replaceQuery" placeholder="Replace with" class="replace-input flex-grow" aria-label="Replace query" @keydown.enter.prevent="replaceCurrentAndFindNext" />
              <button @click="replaceCurrent" :disabled="!hasActiveMatch" title="Replace Current" class="code-block-button search-button" aria-label="Replace Current">Replace</button>
              <button @click="replaceAllMatches" :disabled="!hasMatches" title="Replace All" class="code-block-button search-button" aria-label="Replace All">All</button>
          </div>

          <div ref="cmEditorRef" class="cm-editor-wrapper rounded-b-md border border-gray-300 dark:border-gray-600 overflow-hidden" :class="{'editing-border': isEditing}"></div>
      </div>

      <!-- == Execution Output (Common) == -->
      <div v-if="executionOutput" class="mt-2" aria-live="polite">
          <span class="text-lg font-semibold text-gray-700 dark:text-gray-300">Execution Output:</span>
          <div class="execution-output-content hljs mt-1 p-2 rounded-md break-words text-sm leading-relaxed bg-white dark:bg-gray-800 max-h-48 overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary" v-html="sanitizedExecutionOutputHtml"></div>
      </div>

  </div>
</template>

<script>
import { nextTick, defineComponent } from 'vue';
import hljs from 'highlight.js';
import feather from 'feather-icons';
import DOMPurify from 'dompurify';
import { debounce } from 'lodash-es';

import { EditorView, keymap, lineNumbers, highlightSpecialChars, drawSelection, dropCursor, rectangularSelection, crosshairCursor, highlightActiveLine, highlightActiveLineGutter } from "@codemirror/view";
import { EditorState, Compartment } from "@codemirror/state";
import { defaultHighlightStyle, syntaxHighlighting, indentOnInput, bracketMatching, foldGutter, foldKeymap, StreamLanguage } from "@codemirror/language";
import { defaultKeymap, history, historyKeymap, indentWithTab, undo as cmUndo, redo as cmRedo, historyField } from "@codemirror/commands";
import { search, searchKeymap, findNext, findPrevious, replaceNext, replaceAll, SearchQuery, getSearchQuery, setSearchQuery } from "@codemirror/search";
import { autocompletion, completionKeymap, closeBrackets, closeBracketsKeymap } from "@codemirror/autocomplete";
import { lintKeymap } from "@codemirror/lint";
import { oneDark } from '@codemirror/theme-one-dark';

import { javascript } from "@codemirror/lang-javascript";
import { python } from "@codemirror/lang-python";
import { html } from "@codemirror/lang-html";
import { css } from "@codemirror/lang-css";
import { json } from "@codemirror/lang-json";
import { markdown } from "@codemirror/lang-markdown";
import { cpp } from "@codemirror/lang-cpp";
import { java } from "@codemirror/lang-java";
import { php } from "@codemirror/lang-php";
import { rust } from "@codemirror/lang-rust";
import { sql } from "@codemirror/lang-sql";
import { xml } from "@codemirror/lang-xml";
import { yaml } from "@codemirror/lang-yaml";
import { vue } from "@codemirror/lang-vue";

import { shell } from '@codemirror/legacy-modes/mode/shell';
import { go } from '@codemirror/legacy-modes/mode/go';
import { ruby } from '@codemirror/legacy-modes/mode/ruby';
import { lua } from '@codemirror/legacy-modes/mode/lua';

import 'highlight.js/styles/github.css';
import 'highlight.js/styles/tokyo-night-dark.css';

const EXECUTABLE_LANGUAGES = new Set(['function', 'python', 'sh', 'shell', 'bash', 'cmd', 'powershell', 'latex', 'mermaid', 'graphviz', 'dot', 'javascript', 'html', 'html5', 'svg', 'lilypond']);
const NEW_TAB_EXECUTABLE_LANGUAGES = new Set(['airplay', 'mermaid', 'graphviz', 'dot', 'javascript', 'html', 'html5', 'svg', 'css']);
const VSCODE_SUPPORTED_LANGUAGES = new Set(['python', 'latex', 'vue', 'html', 'svg', 'javascript', 'typescript', 'css', 'scss', 'less', 'json', 'yaml', 'markdown', 'java', 'csharp', 'php', 'ruby', 'go', 'rust', 'shell', 'bash', 'powershell']);
const INPUT_DEBOUNCE_MS = 300;
const SEARCH_UPDATE_DEBOUNCE_MS = 150;

function getHighlightedHtml(code, language) {
  const codeToHighlight = typeof code === 'string' ? code : '';
  try {
      const effectiveLang = hljs.getLanguage(language) ? language : 'plaintext';
      const result = hljs.highlight(codeToHighlight, { language: effectiveLang, ignoreIllegals: true });
      return result.value.replace(/\n/g, '<br>');
  } catch (e) {
      console.warn("Highlighting error (output):", e, "Lang:", language);
      const escaped = codeToHighlight.replace(/</g, "<").replace(/>/g, ">");
      return escaped.replace(/\n/g, '<br>');
  }
}

export default defineComponent({
  name: 'CodeBlock',
  props: {
      host: { type: String, required: false, default: "" },
      language: { type: String, required: true },
      code: { type: String, required: true },
      client_id: { type: String, required: true },
      discussion_id: { type: [String, Number], required: true },
      message_id: { type: [String, Number], required: true },
      autoScrollOnContentChange: { type: Boolean, default: true },
      initialSvgTab: {
          type: String,
          default: 'render',
          validator: (value) => ['code', 'render'].includes(value),
      },
  },
  emits: ['update-code'],
  data() {
      return {
          isExecuting: false,
          isCopied: false,
          executionOutput: '',
          copyTimeout: null,
          isFunctionDetailsVisible: false,
          isEditing: false,
          isSearchVisible: false,
          searchQuery: '',
          replaceQuery: '',
          cmView: null,
          languageCompartment: new Compartment(),
          editableCompartment: new Compartment(),
          themeCompartment: new Compartment(),
          updateListenerCompartment: new Compartment(),
          debouncedEmitUpdate: null,
          debouncedUpdateSearchQuery: null,
          undoDepth: 0,
          redoDepth: 0,
          searchMatchCount: 0,
          currentMatchIndex: -1,
          darkModeObserver: null,
          isDarkMode: false,
          svgActiveTab: this.initialSvgTab,
      };
  },
  computed: {
      safeCodeProp() { return typeof this.code === 'string' ? this.code : ''; },
      safeLanguageProp() { return typeof this.language === 'string' ? this.language : ''; },
      normalizedLanguage() { return this.safeLanguageProp.trim().toLowerCase(); },
      isFunctionLanguage() { return this.normalizedLanguage === 'function'; },
      isSvgLanguage() { return this.normalizedLanguage === 'svg'; },
      cmLanguage() {
          const lang = this.normalizedLanguage;
          switch (lang) {
              case 'python': case 'py': return python();
              case 'javascript': case 'js': return javascript();
              case 'typescript': case 'ts': return javascript({ typescript: true });
              case 'jsx': return javascript({ jsx: true });
              case 'tsx': return javascript({ jsx: true, typescript: true });
              case 'html': case 'html5': return html();
              case 'css': return css();
              case 'json': return json();
              case 'markdown': case 'md': return markdown();
              case 'shell': case 'bash': case 'sh': case 'zsh': case 'cmd': case 'powershell': return StreamLanguage.define(shell);
              case 'sql': return sql();
              case 'yaml': case 'yml': return yaml();
              case 'vue': case 'vue.js': return vue();
              case 'java': return java();
              case 'csharp': case 'cs': return cpp();
              case 'c': case 'cpp': return cpp();
              case 'php': return php();
              case 'rust': case 'rs': return rust();
              case 'xml': return xml();
              case 'svg': return xml();
              case 'go': return StreamLanguage.define(go);
              case 'ruby': case 'rb': return StreamLanguage.define(ruby);
              case 'lua': return StreamLanguage.define(lua);
              case 'latex':
              case 'mermaid':
              case 'graphviz':
              case 'dot':
              case 'lilypond':
              case 'plaintext':
              case 'text':
              default: return null;
          }
      },
      canExecute() { return EXECUTABLE_LANGUAGES.has(this.normalizedLanguage); },
      canExecuteInNewTab() { return NEW_TAB_EXECUTABLE_LANGUAGES.has(this.normalizedLanguage); },
      canOpenFolderInVsCode() { return VSCODE_SUPPORTED_LANGUAGES.has(this.normalizedLanguage); },
      canOpenInVsCode() { return VSCODE_SUPPORTED_LANGUAGES.has(this.normalizedLanguage); },
      effectiveLanguageDisplay() {
          const lang = this.normalizedLanguage;
          if (this.isFunctionLanguage) return 'json';
          if (['shell', 'sh', 'bash', 'cmd', 'powershell'].includes(lang)) return 'shell';
          if (lang === 'html5') return 'html';
          if (lang === 'dot') return 'graphviz';
          return this.cmLanguage ? lang : 'plaintext';
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
      sanitizedExecutionOutputHtml() {
          if (!this.executionOutput) return '';
          const config = { USE_PROFILES: { html: true }, ADD_TAGS: ['iframe', 'svg', 'path', 'g', 'circle', 'rect', 'line', 'polyline', 'polygon', 'text', 'tspan', 'style', 'defs', 'marker', 'use', 'a'], ADD_ATTS: ['style', 'transform', 'cx', 'cy', 'r', 'x', 'y', 'width', 'height', 'fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'points', 'd', 'marker-start', 'marker-end', 'viewBox', 'preserveAspectRatio', 'class', 'id', 'href', 'target', 'text-anchor', 'dominant-baseline', 'font-size', 'font-family', 'dy', 'aria-label'], ALLOW_DATA_ATTR: true, ALLOW_UNKNOWN_PROTOCOLS: false, FORBID_TAGS: ['script'], FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur'] };
          const looksLikeCode = !this.executionOutput.trim().startsWith('<');
          const contentToSanitize = looksLikeCode ? getHighlightedHtml(this.executionOutput, 'plaintext') : this.executionOutput;
          return DOMPurify.sanitize(contentToSanitize, config);
      },
      sanitizedSvgContent() {
          if (!this.isSvgLanguage) return '';
          const svgCode = this.getActualCode();
          if (!svgCode || typeof svgCode !== 'string') return '<!-- Invalid SVG code -->';
          const config = { USE_PROFILES: { html: true, svg: true, svgFilters: true }, ADD_TAGS: ['iframe', 'svg', 'path', 'g', 'circle', 'rect', 'line', 'polyline', 'polygon', 'text', 'tspan', 'style', 'defs', 'marker', 'use', 'a', 'filter', 'feGaussianBlur', 'feOffset', 'feMerge', 'feMergeNode', 'image'], ADD_ATTS: ['style', 'transform', 'cx', 'cy', 'r', 'x', 'y', 'width', 'height', 'fill', 'stroke', 'stroke-width', 'stroke-dasharray', 'points', 'd', 'marker-start', 'marker-end', 'viewBox', 'preserveAspectRatio', 'class', 'id', 'href', 'target', 'text-anchor', 'dominant-baseline', 'font-size', 'font-family', 'dy', 'aria-label', 'filter', 'stdDeviation', 'dx', 'dy', 'result', 'in', 'in2', 'xlink:href', 'xmlns', 'version', 'xmlns:xlink'], ALLOW_DATA_ATTR: true, ALLOW_UNKNOWN_PROTOCOLS: true, FORBID_TAGS: ['script'], FORBID_ATTR: ['onerror', 'onload', 'onclick', 'onmouseover', 'onfocus', 'onblur'] };
          config.ADD_ATTS = [...new Set(config.ADD_ATTS)];
          if (!svgCode.trim().startsWith('<svg')) {
               return '<!-- Invalid SVG: Missing <svg> tag -->';
          }
          try {
            return DOMPurify.sanitize(svgCode, config);
          } catch (e) {
            console.error("SVG Sanitization Error:", e);
            return '<!-- SVG Sanitization Error -->';
          }
      },
      copyIcon() { return this.isCopied ? 'check' : 'copy'; },
      copyTitle() { return this.isCopied ? 'Copied!' : (this.isSvgLanguage ? 'Copy SVG Code' : 'Copy code'); },
      executeIcon() { return this.isExecuting ? 'loader' : 'play-circle'; },
      executeTitle() { return this.isExecuting ? 'Executing...' : (this.isFunctionLanguage ? 'Execute Function Call' : 'Execute Code'); },
      executeNewTabIcon() { return this.isExecuting ? 'loader' : 'airplay'; },
      executeNewTabTitle() { return this.isExecuting ? 'Executing...' : 'Execute Code in New Tab'; },
      canUndo() { return this.undoDepth > 0; },
      canRedo() { return this.redoDepth > 0; },
      hasMatches() { return this.searchMatchCount > 0; },
      hasActiveMatch() { return this.currentMatchIndex >= 0 && this.currentMatchIndex < this.searchMatchCount; },
      searchStatusText() {
          if (!this.searchQuery) return ' \u00A0 ';
          if (!this.hasMatches) return 'Not found';
          if (this.hasActiveMatch) return `${this.currentMatchIndex + 1} / ${this.searchMatchCount}`;
          return `${this.searchMatchCount} found`;
      },
  },
  watch: {
    code(newCode, oldCode) {
        // Ensure we have a CodeMirror instance and that the code has actually changed.
        const currentEditorCode = this.cmView ? this.cmView.state.doc.toString() : this.safeCodeProp;
        if (!this.cmView || this.isFunctionLanguage || newCode === currentEditorCode || newCode === oldCode) {
            // Exit if:
            // - CodeMirror view (this.cmView) isn't initialized.
            // - It's a 'function' language block (which doesn't use CodeMirror for display).
            // - The new code is identical to what's already in the editor or the previous prop value.
            return;
        }

        // --- Auto-scroll Logic ---
        // Determine if auto-scroll should occur *before* updating the editor's content.
        let shouldAutoScroll = false;
        if (this.autoScrollOnContentChange && !this.isEditing) {
            try {
                // Attempt to get CodeMirror's native scroll DOM element.
                const scrollElement = this.cmView.scrollDOM;
                if (scrollElement) {
                    // Define a threshold (in pixels) from the bottom. If the user is scrolled
                    // within this threshold, we consider them "at the bottom".
                    const scrollThreshold = 50; // px
                    // Calculation: (total content height - current scroll position from top - visible height of editor)
                    // This gives the distance from the bottom of the visible area to the actual bottom of the content.
                    // If this distance is less than the threshold, we should auto-scroll.
                    shouldAutoScroll = (scrollElement.scrollHeight - scrollElement.scrollTop - scrollElement.clientHeight) < scrollThreshold;
                } else {
                    // If scrollElement is not available, default to not auto-scrolling.
                    shouldAutoScroll = false;
                    console.warn("CodeMirror: scrollDOM not available for auto-scroll check.");
                }
            } catch (e) {
                // Catch any errors during scroll DOM access and default to no auto-scroll.
                shouldAutoScroll = false;
                console.warn("CodeMirror: Error accessing scrollDOM for auto-scroll check.", e);
            }
        }

        // Update the editor's content with the new code, but only if not in editing mode.
        // If in editing mode, the user is in control, and prop changes shouldn't override their input.
        if (!this.isEditing) {
            this.updateEditorContent(newCode); // This method dispatches changes to CodeMirror.
        }

        // If it was determined (before the content update) that auto-scroll is needed,
        // then proceed to scroll the editor to the new end of the document.
        // This is done in `nextTick` to ensure the DOM has updated after the content change.
        if (shouldAutoScroll) {
            nextTick(() => {
                // Double-check that cmView still exists, as it might be destroyed during rapid updates.
                if (this.cmView) {
                    try {
                        // Use CodeMirror's effect to scroll the end of the document into view.
                        this.cmView.dispatch({
                            effects: EditorView.scrollIntoView(this.cmView.state.doc.length, {
                                y: "end",    // Align the bottom of the new content with the bottom of the viewport.
                                yMargin: 10  // Add a small margin below the last line for better visibility.
                            })
                        });
                    } catch (e) {
                        console.error("CodeMirror: Failed to execute scrollIntoView effect.", e);
                    }
                }
            });
        }
        // Note: Any parent-level scrolling (e.g., this.$el.scrollIntoView) should be avoided here
        // as we want to control scrolling *within* the CodeMirror editor itself.
    },
      isEditing(editing) {
          if (this.cmView) {
              this.cmView.dispatch({ effects: this.editableCompartment.reconfigure(EditorView.editable.of(editing)) });
              if (editing) { nextTick(() => this.cmView?.focus()); }
          }
      },
      cmLanguage(newLang) {
          if (this.cmView) {
              this.cmView.dispatch({ effects: this.languageCompartment.reconfigure(newLang ? [newLang, syntaxHighlighting(defaultHighlightStyle, { fallback: true })] : [syntaxHighlighting(defaultHighlightStyle, { fallback: true })]) });
          }
      },
      searchQuery() {
          if (this.isEditing && this.isSearchVisible) { this.debouncedUpdateSearchQuery(); }
      },
      replaceQuery() {
          if (this.isEditing && this.isSearchVisible) { this.debouncedUpdateSearchQuery(); }
      },
      isDarkMode(isDark) {
          if (this.cmView) {
               this.cmView.dispatch({ effects: this.themeCompartment.reconfigure(isDark ? oneDark : []) });
               this.cmView.dispatch({
                    effects: EditorView.theme({
                        ".cm-gutters": { backgroundColor: isDark ? "#374151" : "#f3f4f6", color: isDark ? "#9ca3af" : "#6b7280", borderRight: `1px solid ${isDark ? '#4b5563' : '#d1d5db'}` },
                    }, {dark: isDark})
                });
           }
      }
  },
  methods: {
      triggerIconUpdate() { nextTick(() => { try { feather.replace(); } catch (e) { /* Ignore */ } }); },
      getActualCode() {
          if (this.isFunctionLanguage) { return this.safeCodeProp; }
          return this.cmView ? this.cmView.state.doc.toString() : this.safeCodeProp;
      },
      async copyCode() {
          if (this.isCopied) return;
          const codeToCopy = this.getActualCode();
          try {
              await navigator.clipboard.writeText(codeToCopy);
              this.isCopied = true;
              this.triggerIconUpdate();
              if (this.copyTimeout) clearTimeout(this.copyTimeout);
              this.copyTimeout = setTimeout(() => { this.isCopied = false; this.triggerIconUpdate(); this.copyTimeout = null; }, 1500);
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
                      else if (typeof responseData?.output === 'string' && responseData.output.length > 0) errorDetails += `, Body: ${responseData.output.substring(0, 100)}...`;
                      else if (responseData?.detail) errorDetails += `, Detail: ${responseData.detail}`;
                      const error = new Error(errorDetails); error.response = responseData; throw error;
                  }
                  return responseData;
              })
              .then(data => {
                  if (typeof data?.output === 'string') this.executionOutput = data.output;
                  else if (typeof data?.message === 'string') this.executionOutput = data.message;
                  else if (data !== null && typeof data === 'object' && Object.keys(data).length > 0) {
                      try { this.executionOutput = JSON.stringify(data, null, 2); } catch { this.executionOutput = "[Object response]"; }
                  } else if (typeof data === 'string') this.executionOutput = data;
                  else this.executionOutput = "Execution successful (no specific output).";

                  if (shouldOpenInNewTab && data?.url) {
                      try { window.open(data.url, '_blank', 'noopener,noreferrer'); }
                      catch(e) { console.error("Failed to open URL:", e); this.executionOutput += `\n(Failed to open URL: ${data.url})`; }
                  }
              })
              .catch(error => { console.error('Code execution failed:', error); this.executionOutput = `Execution Error: ${error.message}`; })
              .finally(() => {
                  this.isExecuting = false; this.triggerIconUpdate();
                  nextTick(() => { this.$el.querySelector('.execution-output-content')?.scrollIntoView({ behavior: 'smooth', block: 'nearest' }); });
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
              .then(data => { if(data){console.log("ok")}/* Optional success handling */ })
              .catch(error => { console.error(`Fetch error during ${endpointUrl}:`, error); alert(`Operation failed: ${error.message}`); });
      },
      openFolderVsCode() { this.postRequest('open_discussion_folder_in_vs_code'); },
      openVsCode() { this.postRequest('open_code_in_vs_code'); },
      openFolder() { this.postRequest('open_discussion_folder'); },
      toggleFunctionDetails() { this.isFunctionDetailsVisible = !this.isFunctionDetailsVisible; this.triggerIconUpdate(); },
        updateEditorContent(newCode) {
            // Ensure this check exists here too, just in case
            if (!this.cmView || this.isFunctionLanguage) return;

            const currentDoc = this.cmView.state.doc.toString();
            if (newCode !== currentDoc) {
                // This dispatch updates the content
                this.cmView.dispatch({
                    changes: { from: 0, to: currentDoc.length, insert: newCode }
                    // DO NOT put scrollIntoView effect here, it should happen *after*
                    // the state update and DOM render triggered by this dispatch.
                });
            }
        },
        createUpdateListener() {
            return EditorView.updateListener.of((update) => {
                const histState = update.state.field(historyField, false);
                if (histState) {
                    this.undoDepth = histState.done.length;
                    this.redoDepth = histState.undone.length;
                }

                // --- Robust Search State Update ---
                if (this.isSearchVisible) { // Only process if search is active
                    const currentCmQuery = getSearchQuery(update.state);
                    // Ensure currentCmQuery and its spec property exist before trying to access .search
                    const currentQueryString = currentCmQuery && currentCmQuery.spec ? currentCmQuery.spec.search : '';

                    if (this.searchQuery && currentQueryString === this.searchQuery) {
                        // If our internal searchQuery matches what's in CM,
                        // try to update counts/index.
                        // This part is an approximation as searchState is not directly exported.
                        // We rely on findNext/Previous to update selection, and then
                        // updateSearchMatchStateAfterFind will try to determine the index.
                        // No direct count update here is perfectly reliable without searchState.
                    } else if (this.searchQuery === '' && currentQueryString === '') {
                        // If both are empty, reset our internal counts.
                        this.searchMatchCount = 0;
                        this.currentMatchIndex = -1;
                    } else if (this.searchQuery && currentQueryString !== this.searchQuery) {
                        // If our internal query differs from CM's (e.g., CM cleared it or changed it),
                        // it's usually safer to re-evaluate the search state.
                        // However, this listener is mostly for reacting to history changes and doc changes.
                        // The primary search state update is handled by debouncedUpdateSearchQuery.
                        // For now, if there's a mismatch and our searchQuery is set, we might
                        // defer to updateSearchQueryState to re-sync if needed.
                    }
                }
                // --- End Robust Search State Update ---


                if (update.docChanged && this.isEditing) {
                    this.debouncedEmitUpdate(update.state.doc.toString());
                }
            });
        },
      setupCodeMirror() {
        // Add a guard to prevent re-initialization if already done
        if (this.cmView) {
            console.warn("Attempted to re-initialize CodeMirror.");
            return;
        }
        // Ensure the ref exists before proceeding
        if (!this.$refs.cmEditorRef || this.isFunctionLanguage) {
            console.warn("CodeMirror setup skipped: Ref not found or is function language.");
            return;
        }

        console.log("Setting up CodeMirror for:", this.normalizedLanguage, "Is SVG:", this.isSvgLanguage, "Target Element:", this.$refs.cmEditorRef);

        const state = EditorState.create({
            doc: this.safeCodeProp,
            extensions: [
                // ... (keep all your existing extensions)
                lineNumbers(),
                highlightActiveLineGutter(),
                highlightSpecialChars(),
                history(),
                foldGutter({ /* ... */ }),
                drawSelection(),
                dropCursor(),
                EditorState.allowMultipleSelections.of(true),
                indentOnInput(),
                bracketMatching(),
                closeBrackets(),
                autocompletion(),
                rectangularSelection(),
                crosshairCursor(),
                highlightActiveLine(),
                search({ top: false, createPanel() { return { dom: document.createElement('div'), top: false }; } }),
                keymap.of([...closeBracketsKeymap, ...defaultKeymap, ...searchKeymap, ...historyKeymap, ...foldKeymap, ...completionKeymap, ...lintKeymap, indentWithTab ]),
                this.languageCompartment.of(this.cmLanguage ? [this.cmLanguage, syntaxHighlighting(defaultHighlightStyle, { fallback: true })] : [syntaxHighlighting(defaultHighlightStyle, { fallback: true })]),
                this.editableCompartment.of(EditorView.editable.of(this.isEditing)),
                this.themeCompartment.of(this.isDarkMode ? oneDark : []),
                this.updateListenerCompartment.of(this.createUpdateListener()),
                EditorView.theme({ /* ... your theme styles ... */ })
            ]
        });

        try {
            this.cmView = new EditorView({ state, parent: this.$refs.cmEditorRef });
            console.log("CodeMirror initialized successfully.");
            // Update history state after initialization
             const histState = this.cmView?.state.field(historyField, false);
             if (histState) {
                 this.undoDepth = histState.done.length;
                 this.redoDepth = histState.undone.length;
             }
        } catch (error) {
            console.error("Failed to initialize CodeMirror:", error);
             // Fallback or error display logic if needed
             if (this.$refs.cmEditorRef) {
                 this.$refs.cmEditorRef.textContent = `Error initializing code editor: ${error.message}`;
             }
        }
    },

    destroyCodeMirror() {
        if (this.cmView) {
            console.log("Destroying CodeMirror instance.");
            this.cmView.destroy();
            this.cmView = null;
            // Reset history counts
            this.undoDepth = 0;
            this.redoDepth = 0;
        }
    },
      toggleEditMode() {
          if (this.isFunctionLanguage) return;
          const newState = !this.isEditing;
          this.isEditing = newState;

          if (this.isSvgLanguage && this.isEditing) {
              this.setSvgTab('code');
          }

          if (this.cmView) {
               this.cmView.dispatch({ effects: this.editableCompartment.reconfigure(EditorView.editable.of(this.isEditing)) });
          }

          if (!this.isEditing) {
              this.isSearchVisible = false;
              this.debouncedEmitUpdate.flush();
          } else {
             nextTick(() => {
                 this.cmView?.focus();
                 const histState = this.cmView?.state.field(historyField, false);
                 if (histState) {
                     this.undoDepth = histState.done.length;
                     this.redoDepth = histState.undone.length;
                 }
             });
          }
          this.triggerIconUpdate();
      },
      undo() { if (this.cmView && this.canUndo) { cmUndo(this.cmView); this.cmView.focus(); } },
      redo() { if (this.cmView && this.canRedo) { cmRedo(this.cmView); this.cmView.focus(); } },
      toggleSearch() {
          if (!this.cmView) return;
          this.isSearchVisible = !this.isSearchVisible;
          if (this.isSearchVisible) {
              nextTick(() => { this.$refs.searchInputRef?.focus(); this.debouncedUpdateSearchQuery(); });
          } else {
              setSearchQuery(this.cmView, new SearchQuery({ search: '' }));
              this.searchQuery = '';
              this.replaceQuery = '';
              this.searchMatchCount = 0;
              this.currentMatchIndex = -1;
          }
          this.triggerIconUpdate();
      },
      findNextAndHighlight() { if (this.cmView && this.searchQuery) { findNext(this.cmView); this.updateSearchMatchStateAfterFind(); this.cmView.focus(); } },
      findPreviousAndHighlight() { if (this.cmView && this.searchQuery) { findPrevious(this.cmView); this.updateSearchMatchStateAfterFind(); this.cmView.focus(); } },
      replaceCurrent() { if (this.cmView && this.hasActiveMatch) { replaceNext(this.cmView); this.cmView.focus(); } },
      replaceCurrentAndFindNext() { this.replaceCurrent(); },
      replaceAllMatches() { if (this.cmView && this.hasMatches) { replaceAll(this.cmView); this.updateSearchQueryState(); this.cmView.focus(); } },
      updateSearchQueryState() {
          if (!this.cmView || !this.isSearchVisible) return;
          const newQuery = new SearchQuery({ search: this.searchQuery, replace: this.replaceQuery, caseSensitive: false });
          setSearchQuery(this.cmView, newQuery);

          this.searchMatchCount = 0; // Reset count
          this.currentMatchIndex = -1; // Reset index

          if (this.searchQuery) {
              let count = 0;
              const cursor = newQuery.getCursor(this.cmView.state.doc);
              while (!cursor.next().done) { count++; }
              this.searchMatchCount = count;

              if (this.searchMatchCount > 0) {
                  findNext(this.cmView); // Move to the first match
                  this.updateSearchMatchStateAfterFind(); // Update index
              }
          }
     },
     updateSearchMatchStateAfterFind() {
         // Get current selection and try to find which match it corresponds to
         if (!this.cmView || !this.searchQuery || this.searchMatchCount === 0) {
             this.currentMatchIndex = -1;
             return;
         }
         const currentSelection = this.cmView.state.selection.main;
         if (currentSelection.empty) {
             // If selection is just a cursor, we don't know the index reliably
             // Keep the previous index unless it's invalid
             if (this.currentMatchIndex < 0 || this.currentMatchIndex >= this.searchMatchCount) {
                 // Maybe try to find the *next* match from cursor pos? Could be complex.
                 // For simplicity, let's just reset if unsure.
                 // this.currentMatchIndex = -1; // Or try to find nearest?
             }
             return;
         }

         const currentQuery = getSearchQuery(this.cmView.state);
         if (!currentQuery) { this.currentMatchIndex = -1; return; }

         let matchIndex = -1;
         let count = 0;
         const cursor = currentQuery.getCursor(this.cmView.state.doc);
          while (!cursor.next().done) {
              const match = cursor.value;
              if (match.from === currentSelection.from && match.to === currentSelection.to) {
                  matchIndex = count;
                  break;
              }
              count++;
          }
          this.currentMatchIndex = matchIndex; // Will be -1 if not found
     },

     setSvgTab(tabName) {
         const previousTab = this.svgActiveTab;
         this.svgActiveTab = tabName;

         // If switching TO the code tab and CM isn't initialized yet
         if (tabName === 'code' && previousTab !== 'code' && !this.cmView) {
             // Use nextTick to ensure the v-show directive has potentially updated the display
             nextTick(() => {
                 if (this.$refs.cmEditorRef) { // Double check ref exists
                      console.log("Initializing CodeMirror on SVG code tab activation.");
                      this.setupCodeMirror();
                      if (this.isEditing) { // Focus if editing was already active
                          this.cmView?.focus();
                      }
                 } else {
                     console.error("Cannot initialize CodeMirror for SVG code tab: ref is missing.");
                 }
             });
         }
         // Always focus the editor when switching to code tab if it exists and is in edit mode
         else if (tabName === 'code' && this.cmView && this.isEditing) {
             nextTick(() => this.cmView?.focus());
         }

         this.triggerIconUpdate();
     },
     observeDarkMode() {
          this.isDarkMode = document.documentElement.classList.contains('dark');
          this.darkModeObserver = new MutationObserver((mutationsList) => {
              for (let mutation of mutationsList) {
                  if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                      this.isDarkMode = document.documentElement.classList.contains('dark');
                      break;
                  }
              }
          });
          this.darkModeObserver.observe(document.documentElement, { attributes: true });
      }
  },
  created() {
      this.debouncedEmitUpdate = debounce((code) => { this.$emit('update-code', code); }, INPUT_DEBOUNCE_MS);
      this.debouncedUpdateSearchQuery = debounce(this.updateSearchQueryState, SEARCH_UPDATE_DEBOUNCE_MS);
  },
  mounted() {
    this.triggerIconUpdate(); // Move icon update earlier maybe
    if (!this.isFunctionLanguage) {
        this.observeDarkMode();
        nextTick(() => {
            // Initialize immediately ONLY if it's NOT SVG, OR if it's SVG and starts on the 'code' tab.
            if (!this.isSvgLanguage || (this.isSvgLanguage && this.svgActiveTab === 'code')) {
                console.log("Initializing CodeMirror on mount.");
                this.setupCodeMirror();
            } else if (this.isSvgLanguage && this.svgActiveTab !== 'code') {
                console.log("Deferring CodeMirror initialization for SVG block (render tab active).");
            }
            // this.triggerIconUpdate(); // Already called above
        });
    }
  },
  beforeUnmount() {
      this.destroyCodeMirror();
      if (this.copyTimeout) clearTimeout(this.copyTimeout);
      this.debouncedEmitUpdate?.cancel();
      this.debouncedUpdateSearchQuery?.cancel();
      this.darkModeObserver?.disconnect();
  },
  updated() { this.triggerIconUpdate(); }
});
</script>

<style>
.code-block-button { /* Basic button styling, adjust as needed */
  padding: 0.25rem;
  border-radius: 0.25rem;
  background-color: transparent;
  color: #4b5563; /* text-gray-600 */
  transition: background-color 0.2s, color 0.2s;
}
.dark .code-block-button {
  color: #d1d5db; /* dark:text-gray-300 */
}
.code-block-button:hover {
  background-color: #e5e7eb; /* hover:bg-gray-200 */
  color: #1f2937; /* hover:text-gray-800 */
}
.dark .code-block-button:hover {
  background-color: #4b5563; /* dark:hover:bg-gray-600 */
  color: #f9fafb; /* dark:hover:text-gray-50 */
}
.code-block-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.code-block-button i.feather {
  display: block; /* Prevents layout shifts */
  width: 1rem; /* 16px */
  height: 1rem; /* 16px */
  stroke-width: 2;
}
.code-block-button.execute-button i.feather {
   width: 1.125rem; /* 18px */
   height: 1.125rem;
}
.feather-small {
  width: 0.75rem !important; /* 12px */
  height: 0.75rem !important;
  stroke-width: 2;
}

.code-block-button.active-search-button {
  background-color: #e0f2fe; /* Tailwind blue-100 */
  color: #0ea5e9; /* Tailwind sky-500 */
}
.dark .code-block-button.active-search-button {
  background-color: #374151; /* Tailwind gray-700 */
  color: #38bdf8; /* Tailwind sky-400 */
}

#svg-render-panel > div > svg {
  max-width: 100%;
  height: auto;
  display: block;
}

.cm-editor-wrapper-svg .cm-editor { height: 100%; }
.cm-editor-wrapper-svg { min-height: 150px; }

.editing-border {
  border-color: #3b82f6; /* Tailwind blue-500 */
  box-shadow: 0 0 0 1px #3b82f6;
}
.dark .editing-border {
  border-color: #60a5fa; /* Tailwind blue-400 */
   box-shadow: 0 0 0 1px #60a5fa;
}

.search-input, .replace-input {
  padding: 2px 6px;
  border: 1px solid #d1d5db; /* Tailwind gray-300 */
  border-radius: 4px;
  font-size: 0.8rem;
  background-color: #fff;
  color: #1f2937; /* Tailwind gray-800 */
}
.dark .search-input, .dark .replace-input {
  background-color: #4b5563; /* Tailwind gray-600 */
  border-color: #6b7280; /* Tailwind gray-500 */
  color: #e5e7eb; /* Tailwind gray-200 */
}
.search-status {
  color: #6b7280; /* Tailwind gray-500 */
  font-size: 0.75rem;
  white-space: nowrap;
  min-width: 50px;
  text-align: center;
}
.dark .search-status { color: #9ca3af; /* Tailwind gray-400 */ }
.search-button {
  padding: 2px 6px !important;
  font-size: 0.8rem;
  line-height: 1;
}

/* Scrollbar */
.scrollbar-thin { scrollbar-width: thin; }
.scrollbar-thumb-gray-300 { --scrollbar-thumb: #d1d5db; scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track); }
.dark .scrollbar-thumb-gray-600 { --scrollbar-thumb: #4b5563; scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track); }
.scrollbar-track-bg-light-tone { --scrollbar-track: #f9fafb; } /* Adjust track color */
.dark .scrollbar-track-bg-dark-tone { --scrollbar-track: #1f2937; } /* Adjust dark track color */
.hover\:scrollbar-thumb-primary:hover { --scrollbar-thumb: #3b82f6; scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track); } /* Adjust primary color */
.dark\:hover\:scrollbar-thumb-primary:hover { --scrollbar-thumb: #60a5fa; scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track); } /* Adjust dark primary color */
.active\:scrollbar-thumb-secondary:active { --scrollbar-thumb: #10b981; scrollbar-color: var(--scrollbar-thumb) var(--scrollbar-track); } /* Adjust secondary color */

/* Tailwind utility classes for scrollbars */
@tailwind utilities;
@layer utilities {
.scrollbar-thin { scrollbar-width: thin; }
.scrollbar-thumb-gray-300 { scrollbar-color: #d1d5db transparent; } /* Light thumb */
.dark .scrollbar-thumb-gray-600 { scrollbar-color: #4b5563 transparent; } /* Dark thumb */
/* Add more variations if needed */
}

/* Ensure primary colors are defined if not using Tailwind directly */
:root {
  --lmo-color-primary: #3b82f6; /* Example blue */
  --lmo-color-primary-dark: #60a5fa;
  --lmo-color-primary-background: #eff6ff;
  --lmo-color-primary-dark-background: #374151;
  --bg-light-tone-panel: #f9fafb; /* gray-50 */
  --bg-dark-tone-panel: #1f2937; /* gray-800 */
  --bg-light-tone: #ffffff;
  --bg-dark-tone: #111827; /* gray-900 */
}

/* Use CSS variables in tab styles */
.border-primary { border-color: var(--lmo-color-primary); }
.text-primary { color: var(--lmo-color-primary); }
.dark .border-primary-dark { border-color: var(--lmo-color-primary-dark); }
.dark .text-primary-dark { color: var(--lmo-color-primary-dark); }
.bg-bg-light-tone { background-color: var(--bg-light-tone); }
.dark .bg-bg-dark-tone { background-color: var(--bg-dark-tone); }

</style>