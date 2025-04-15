<template>
    <div :class="['markdown-editor-container border border-gray-300 dark:border-gray-600 rounded-md overflow-hidden', editorClass]">
        <div :class="['toolbar bg-gray-100 dark:bg-gray-700 p-1 border-b border-gray-300 dark:border-gray-600 flex flex-wrap items-center gap-1', toolbarClass]">

            <ToolbarButton :title="getButtonTitle('bold')" @click="applyFormat('bold')" icon="bold" :button-class="toolbarButtonBaseClass" :svg-size-class="svgIconSizeClass" />
            <ToolbarButton :title="getButtonTitle('italic')" @click="applyFormat('italic')" icon="italic" :button-class="toolbarButtonBaseClass" :svg-size-class="svgIconSizeClass" />
            <ToolbarButton :title="getButtonTitle('link')" @click="insertLink" icon="link" :button-class="toolbarButtonBaseClass" :svg-size-class="svgIconSizeClass" />

            <DropdownMenu title="Text Formatting" icon="type" :button-class="toolbarButtonBaseClass" :svg-size-class="svgIconSizeClass">
                 <ToolbarButton @click.stop="applyFormat('strikethrough')" title="Strikethrough" icon="strikethrough" :svg-size-class="svgIconSizeClass" />
                 <ToolbarButton @click.stop="applyFormat('inlinecode')" title="Inline Code" icon="code" :svg-size-class="svgIconSizeClass"><span class="ml-1 text-xs">(inline)</span></ToolbarButton>
                 <ToolbarButton @click.stop="applyFormat('latex')" title="Inline LaTeX ($...$)" icon="latex" :svg-size-class="svgIconSizeClass" />
            </DropdownMenu>

            <DropdownMenu title="Headings" icon="hash" :button-class="toolbarButtonBaseClass" :svg-size-class="svgIconSizeClass">
                 <ToolbarButton @click.stop="applyFormat('h1')" title="Heading 1" :svg-size-class="svgIconSizeClass" class="font-semibold">H1</ToolbarButton>
                 <ToolbarButton @click.stop="applyFormat('h2')" title="Heading 2" :svg-size-class="svgIconSizeClass" class="font-semibold">H2</ToolbarButton>
                 <ToolbarButton @click.stop="applyFormat('h3')" title="Heading 3" :svg-size-class="svgIconSizeClass" class="font-semibold">H3</ToolbarButton>
            </DropdownMenu>

            <DropdownMenu title="Lists" icon="list" :button-class="toolbarButtonBaseClass" :svg-size-class="svgIconSizeClass">
                 <ToolbarButton @click.stop="applyFormat('ul')" title="Unordered List" icon="list" :svg-size-class="svgIconSizeClass" />
                 <ToolbarButton @click.stop="applyFormat('ol')" title="Ordered List" :svg-size-class="svgIconSizeClass"><span class="font-semibold text-sm">1.</span></ToolbarButton>
            </DropdownMenu>

            <DropdownMenu title="Blocks" icon="layout" :button-class="toolbarButtonBaseClass" :svg-size-class="svgIconSizeClass">
                 <ToolbarButton @click.stop="applyFormat('blockquote')" title="Blockquote" icon="blockquote" :svg-size-class="svgIconSizeClass" />
                 <ToolbarButton @click.stop="applyFormat('hr')" title="Horizontal Rule" icon="minus" :svg-size-class="svgIconSizeClass" />
                 <ToolbarButton @click.stop="applyFormat('latexBlock')" title="LaTeX Block ($$...$$)" icon="latexBlock" :svg-size-class="svgIconSizeClass" />
            </DropdownMenu>

            <DropdownMenu title="Insert Code Block" icon="code" :button-class="toolbarButtonBaseClass" :svg-size-class="svgIconSizeClass">
                <ToolbarButton @click.stop="applyFormat('codeblock')" title="Generic Code Block" icon="terminal" :svg-size-class="svgIconSizeClass" />
                <div class="my-1 border-t border-gray-200 dark:border-gray-600"></div>
                <DropdownSubmenu title="Programming Languages" icon="code" :svg-size-class="svgIconSizeClass">
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'python' })" title="Python" icon="python" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'javascript' })" title="JavaScript" icon="js" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'typescript' })" title="TypeScript" icon="typescript" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'java' })" title="Java" icon="java" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'c++' })" title="C++" icon="cplusplus" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'csharp' })" title="C#" icon="csharp" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'go' })" title="Go" icon="go" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'rust' })" title="Rust" icon="rust" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'swift' })" title="Swift" icon="swift" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'kotlin' })" title="Kotlin" icon="kotlin" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'r' })" title="R" icon="r-project" :svg-size-class="svgIconSizeClass" />
                </DropdownSubmenu>
                <DropdownSubmenu title="Web Technologies" icon="chrome" :svg-size-class="svgIconSizeClass">
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'html' })" title="HTML" icon="html5" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'css' })" title="CSS" icon="css3" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'vue' })" title="Vue.js" icon="vuejs" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'react' })" title="React" icon="react" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'angular' })" title="Angular" icon="angular" :svg-size-class="svgIconSizeClass" />
                </DropdownSubmenu>
                <DropdownSubmenu title="Markup and Data" icon="file-text" :svg-size-class="svgIconSizeClass">
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'xml' })" title="XML" icon="xml" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'json' })" title="JSON" icon="json" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'yaml' })" title="YAML" icon="yaml" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'markdown' })" title="Markdown" icon="markdown" :svg-size-class="svgIconSizeClass" />
                </DropdownSubmenu>
                <DropdownSubmenu title="Scripting and Shell" icon="terminal" :svg-size-class="svgIconSizeClass">
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'bash' })" title="Bash" icon="bash" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'powershell' })" title="PowerShell" icon="powershell" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'perl' })" title="Perl" icon="perl" :svg-size-class="svgIconSizeClass" />
                </DropdownSubmenu>
                <DropdownSubmenu title="Diagramming" icon="git-branch" :svg-size-class="svgIconSizeClass">
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'mermaid' })" title="Mermaid" icon="mermaid" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'graphviz' })" title="Graphviz" icon="graphviz" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'plantuml' })" title="PlantUML" icon="plantuml" :svg-size-class="svgIconSizeClass" />
                </DropdownSubmenu>
                <DropdownSubmenu title="Database" icon="database" :svg-size-class="svgIconSizeClass">
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'sql' })" title="SQL" icon="sql" :svg-size-class="svgIconSizeClass" />
                    <ToolbarButton @click.stop="applyFormat('codeblock', { language: 'mongodb' })" title="MongoDB" icon="mongodb" :svg-size-class="svgIconSizeClass" />
                </DropdownSubmenu>
            </DropdownMenu>

            <DropdownMenu title="LaTeX Equations" icon="sigma" :button-class="toolbarButtonBaseClass" :svg-size-class="svgIconSizeClass">
                 <ToolbarButton @click.stop="applyFormat('latex')" title="Inline Math ($...$)" icon="latex" :svg-size-class="svgIconSizeClass" />
                 <ToolbarButton @click.stop="applyFormat('latexBlock')" title="Display Math ($$...$$)" icon="latexBlock" :svg-size-class="svgIconSizeClass" />
                 <div class="my-1 border-t border-gray-200 dark:border-gray-600"></div>
                 <DropdownSubmenu title="Numbered Environments" icon="hash" :svg-size-class="svgIconSizeClass">
                     <ToolbarButton @click.stop="applyFormat('latexEnvEquation')" title="Equation (Single line, numbered)" icon="equation" :svg-size-class="svgIconSizeClass" />
                     <ToolbarButton @click.stop="applyFormat('latexEnvAlign')" title="Align (Multiple lines, aligned, numbered)" icon="align" :svg-size-class="svgIconSizeClass" />
                     <ToolbarButton @click.stop="applyFormat('latexEnvGather')" title="Gather (Multiple lines, centered, numbered)" icon="gather" :svg-size-class="svgIconSizeClass" />
                 </DropdownSubmenu>
                  <DropdownSubmenu title="Unnumbered Environments" icon="minus-circle" :svg-size-class="svgIconSizeClass">
                      <ToolbarButton @click.stop="applyFormat('latexEnvEquationStar')" title="Equation* (Single line, unnumbered)" icon="equation" :svg-size-class="svgIconSizeClass" />
                      <ToolbarButton @click.stop="applyFormat('latexEnvAlignStar')" title="Align* (Multiple lines, aligned, unnumbered)" icon="align" :svg-size-class="svgIconSizeClass" />
                      <ToolbarButton @click.stop="applyFormat('latexEnvGatherStar')" title="Gather* (Multiple lines, centered, unnumbered)" icon="gather" :svg-size-class="svgIconSizeClass" />
                  </DropdownSubmenu>
            </DropdownMenu>

            <DropdownMenu title="Insert" icon="paperclip" :button-class="toolbarButtonBaseClass" :svg-size-class="svgIconSizeClass">
                 <ToolbarButton @click.stop="insertImage" title="Image" icon="image" :svg-size-class="svgIconSizeClass" />
            </DropdownMenu>
        </div>
        <div ref="editorRef" class="editor-wrapper"></div>
    </div>
</template>

<script>
import { nextTick } from 'vue';
import { basicSetup } from "codemirror";
import { EditorView, keymap } from "@codemirror/view";
import { EditorState } from "@codemirror/state";
import { markdown, markdownLanguage } from "@codemirror/lang-markdown";
import { languages } from "@codemirror/language-data";
import { indentWithTab } from "@codemirror/commands";
import DropdownMenu from '@/components/DropdownMenu.vue';
import DropdownSubmenu from '@/components/DropdownSubmenu.vue';
import ToolbarButton from '@/components/ToolbarButton.vue';

const getSelectedLines = (state) => {
    let lines = [];
    for (let range of state.selection.ranges) {
      const fromLine = state.doc.lineAt(range.from);
      const toLine = state.doc.lineAt(range.to);
      for (let i = fromLine.number; i <= toLine.number; i++) {
        if (!lines.some(l => l.number === i)) lines.push(state.doc.line(i));
      }
    }
    return lines;
};

const needsNewline = (state, pos, isBefore) => {
    if ((isBefore && pos === 0) || (!isBefore && pos === state.doc.length)) return false;
    const surroundingChar = isBefore ? state.doc.sliceString(pos - 1, pos) : state.doc.sliceString(pos, pos + 1);
    return surroundingChar !== '\n';
};

export default {
    name: 'MarkdownEditor',
    components: { DropdownMenu, DropdownSubmenu, ToolbarButton },
    props: {
        modelValue: { type: String, required: true },
        editorClass: { type: [String, Object, Array], default: '' },
        toolbarClass: { type: [String, Object, Array], default: '' },
        buttonClass: { type: [String, Object, Array], default: '' },
        toolbarButtonIconSize: { type: Number, default: 16 },
        theme: { type: Object, required: true }
    },
    emits: ['update:modelValue'],
    data() {
        return {
            editorView: null,
            updatingFromSelf: false,
        };
    },
    computed: {
        toolbarButtonBaseClass() {
            return this.buttonClass || 'px-1.5 py-1 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded hover:bg-gray-200 dark:hover:bg-gray-500 text-sm focus:outline-none focus:ring-1 focus:ring-blue-400 dark:text-gray-200 flex items-center justify-center w-7 h-7';
        },
        iconSize() {
            return this.toolbarButtonIconSize;
        },
        svgIconSizeClass() {
            const size = Math.round(this.iconSize / 4);
            return `w-${size} h-${size}`;
        }
    },
    methods: {
        getButtonTitle(type) {
            const map = {
                bold: 'Bold (Ctrl+B)', italic: 'Italic (Ctrl+I)', strikethrough: 'Strikethrough',
                h1: 'Heading 1', h2: 'Heading 2', h3: 'Heading 3', blockquote: 'Blockquote',
                ul: 'Unordered List', ol: 'Ordered List', codeblock: 'Code Block',
                inlinecode: 'Inline Code', link: 'Insert Link', image: 'Insert Image',
                hr: 'Horizontal Rule', latex: 'Inline LaTeX ($...$)', latexBlock: 'LaTeX Block ($$...$$)',
                latexEnvEquation: 'Equation Environment', latexEnvAlign: 'Align Environment', latexEnvGather: 'Gather Environment',
                latexEnvEquationStar: 'Equation* Environment (Unnumbered)', latexEnvAlignStar: 'Align* Environment (Unnumbered)', latexEnvGatherStar: 'Gather* Environment (Unnumbered)',
            };
            return map[type] || type;
        },
        initializeEditor() {
            if (this.editorView) this.editorView.destroy();

            const state = EditorState.create({
                doc: this.modelValue,
                extensions: [
                    basicSetup,
                    keymap.of([indentWithTab]),
                    markdown({ base: markdownLanguage, codeLanguages: languages }),
                    this.theme,
                    EditorView.lineWrapping,
                    EditorView.updateListener.of((update) => {
                        if (update.docChanged && !this.updatingFromSelf) {
                            this.$emit('update:modelValue', update.state.doc.toString());
                        }
                    }),
                    EditorView.contentAttributes.of({ 'aria-label': 'Markdown editor content' })
                ],
            });
            this.editorView = new EditorView({ state, parent: this.$refs.editorRef });
        },
        destroyEditor() {
            if (this.editorView) {
                this.editorView.destroy();
                this.editorView = null;
            }
        },
        applyFormat(type, options = {}) {
            if (!this.editorView) return;
            const view = this.editorView, state = view.state;
            let changes = [];
            const selection = state.selection.main;
            const selectedText = state.doc.sliceString(selection.from, selection.to);
            let prefix = '', suffix = '', blockPrefix = '';
            let isBlockEnv = false;

            switch (type) {
                case 'bold': prefix = '**'; suffix = '**'; break;
                case 'italic': prefix = '_'; suffix = '_'; break;
                case 'strikethrough': prefix = '~~'; suffix = '~~'; break;
                case 'inlinecode': prefix = '`'; suffix = '`'; break;
                case 'latex': prefix = '$'; suffix = '$'; break;
                case 'h1': blockPrefix = '# '; break;
                case 'h2': blockPrefix = '## '; break;
                case 'h3': blockPrefix = '### '; break;
                case 'blockquote': blockPrefix = '> '; break;
                case 'ul': blockPrefix = '- '; break;
                case 'ol': blockPrefix = '1. '; break;
                case 'latexBlock': prefix = '$$\n'; suffix = '\n$$'; isBlockEnv = true; break;
                case 'codeblock': prefix = '```' + (options.language || '') + '\n'; suffix = '\n```'; isBlockEnv = true; break;
                case 'hr':
                    changes.push({ from: selection.from, insert: (needsNewline(state, selection.from, true) ? '\n' : '') + '---\n' });
                    break;
                case 'latexEnvEquation': isBlockEnv = true; prefix = '\\begin{equation}\n'; suffix = '\n\\end{equation}'; break;
                case 'latexEnvAlign': isBlockEnv = true; prefix = '\\begin{align}\n'; suffix = '\n\\end{align}'; break;
                case 'latexEnvGather': isBlockEnv = true; prefix = '\\begin{gather}\n'; suffix = '\n\\end{gather}'; break;
                case 'latexEnvEquationStar': isBlockEnv = true; prefix = '\\begin{equation*}\n'; suffix = '\n\\end{equation*}'; break;
                case 'latexEnvAlignStar': isBlockEnv = true; prefix = '\\begin{align*}\n'; suffix = '\n\\end{align*}'; break;
                case 'latexEnvGatherStar': isBlockEnv = true; prefix = '\\begin{gather*}\n'; suffix = '\n\\end{gather*}'; break;
            }

            let effectivePrefix = prefix;
            let effectiveSuffix = suffix;

            if (isBlockEnv) {
                 if (needsNewline(state, selection.from, true)) effectivePrefix = '\n' + prefix;
                 if (needsNewline(state, selection.to, false)) effectiveSuffix = suffix + '\n';
            }

            if (blockPrefix) {
                 const lines = getSelectedLines(state);
                 let headDelta = 0;
                 lines.forEach(line => {
                     const currentPrefixMatch = line.text.match(/^([#>\-\*]|\d+\.)\s*/);
                     const prefixLen = currentPrefixMatch ? currentPrefixMatch[0].length : 0;
                     const linePrefixStart = line.from;
                     const linePrefixEnd = linePrefixStart + prefixLen;

                     if (currentPrefixMatch && currentPrefixMatch[0].trim() === blockPrefix.trim()) {
                         changes.push({ from: linePrefixStart, to: linePrefixEnd, insert: '' });
                         if (line.number === state.doc.lineAt(selection.head).number && selection.head >= linePrefixEnd) {
                             headDelta -= prefixLen;
                         }
                     } else {
                         const insert = blockPrefix;
                         changes.push({ from: linePrefixStart, to: linePrefixEnd, insert });
                          if (line.number === state.doc.lineAt(selection.head).number) {
                              if (selection.head >= linePrefixEnd) {
                                 headDelta += insert.length - prefixLen;
                              } else {
                                 headDelta = insert.length; // Cursor inside/before old prefix
                              }
                          }
                     }
                 });
                 if (changes.length > 0) {
                    const finalHead = Math.max(selection.anchor, selection.head + headDelta);
                    view.dispatch({ changes, selection: { anchor: selection.anchor, head: finalHead } });
                 }
            } else if (prefix || suffix) {
                 const insert = effectivePrefix + selectedText + effectiveSuffix;
                 let finalSelection;

                 if (selection.empty) {
                    let cursorPos = selection.from + effectivePrefix.length;
                    // For block envs, cursor goes after the opening marker's newline if it exists
                    // For inline math, cursor goes inside the markers
                    if (!isBlockEnv && type === 'latex') cursorPos = selection.from + prefix.length;

                    finalSelection = { anchor: cursorPos };
                 } else {
                     finalSelection = {
                         anchor: selection.from + effectivePrefix.length,
                         head: selection.to + effectivePrefix.length
                     };
                 }
                 view.dispatch({
                     changes: { from: selection.from, to: selection.to, insert: insert },
                     selection: finalSelection
                 });
            } else if (type === 'hr' && changes.length > 0) {
                 view.dispatch({ changes, selection: { anchor: selection.from + changes[0].insert.length } });
            }

            view.focus();
        },
        insertLink() {
            if (!this.editorView) return;
            const url = prompt("Enter link URL:", "https://");
            if (!url) return;

            const view = this.editorView, state = view.state, selection = state.selection.main;
            const selectedText = state.doc.sliceString(selection.from, selection.to);
            const linkText = selectedText || 'link text';
            const textToInsert = `[${linkText}](${url})`;

            view.dispatch({
                changes: { from: selection.from, to: selection.to, insert: textToInsert },
                selection: selection.empty
                    ? { anchor: selection.from + 1, head: selection.from + 1 + linkText.length}
                    : { anchor: selection.from + textToInsert.length }
            });
            view.focus();
        },
        insertImage() {
             if (!this.editorView) return;
             const url = prompt("Enter image URL:", "https://");
             if (!url) return;
             const altText = prompt("Enter alt text:", "image");

             const view = this.editorView, state = view.state, selection = state.selection.main;
             const textToInsert = `![${altText || ''}](${url})`;
             let effectiveInsert = textToInsert;
             let prefixNewlineOffset = 0;

             if (needsNewline(state, selection.from, true)) {
                 effectiveInsert = '\n' + effectiveInsert;
                 prefixNewlineOffset = 1;
             }
             if (needsNewline(state, selection.to, false) || (selection.empty && needsNewline(state, selection.from, false))) {
                 effectiveInsert = effectiveInsert + '\n';
             }

             const finalCursorPos = selection.from + prefixNewlineOffset + textToInsert.length;

             view.dispatch({
                 changes: { from: selection.from, to: selection.to, insert: effectiveInsert },
                 selection: { anchor: finalCursorPos }
             });
             view.focus();
        }
    },
    watch: {
        modelValue(newValue) {
            if (this.editorView && newValue !== this.editorView.state.doc.toString()) {
                this.updatingFromSelf = true;
                this.editorView.dispatch({
                    changes: { from: 0, to: this.editorView.state.doc.length, insert: newValue }
                });
                nextTick(() => { this.updatingFromSelf = false; });
            }
        },
        theme() {
            this.initializeEditor();
        }
    },
    mounted() {
        this.initializeEditor();
    },
    beforeUnmount() {
        this.destroyEditor();
    },
};
</script>

<style>
.cm-editor {
    min-height: 150px;
    max-height: 70vh;
    height: auto;
    outline: none !important;
    font-size: 0.9rem;
}
.cm-scroller {
    overflow: auto;
}
.cm-content ul, .cm-content ol {
    list-style: revert;
    margin: revert;
    padding: revert;
}
.toolbar .svg-button > span,
.toolbar .toolbar-button > span { /* Target text spans within buttons */
    vertical-align: middle;
    margin-left: 0.125rem; /* Small gap */
}
.toolbar .svg-button > .font-semibold,
.toolbar .toolbar-button > .font-semibold {
    font-weight: 600; /* Ensure font-semibold applies */
}
.toolbar .svg-button .font-mono {
    background-color: rgba(100, 116, 139, 0.1);
    padding: 0 3px;
    border-radius: 3px;
    font-size: 0.8em;
}
</style>