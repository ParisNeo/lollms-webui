<template>
    <div class="latex-editor-container group relative border rounded-md bg-gray-100 dark:bg-gray-800 shadow-sm" :class="[inline ? 'p-1' : 'p-2']">
        <button
            @click="toggleEditMode"
            :title="isEditing ? 'Finish Editing LaTeX' : 'Edit LaTeX'"
            class="latex-edit-toggle-button absolute top-1 right-1 z-10 p-1 rounded bg-gray-300/50 dark:bg-gray-700/50 text-gray-600 dark:text-gray-300 opacity-20 group-hover:opacity-100 focus-within:opacity-100 focus:opacity-100 transition-opacity duration-200 ease-in-out"
            :class="{ 'opacity-100': isEditing }"
            >
            <i :data-feather="isEditing ? 'check-circle' : 'edit-2'" class="w-4 h-4"></i>
        </button>

        <div v-if="isEditing" class="latex-toolbar mt-6 mb-2 pb-2 border-b border-gray-300 dark:border-gray-600">
            <div class="flex flex-wrap items-start gap-x-4 gap-y-2">

                <!-- Group: Structures -->
                <div class="flex flex-wrap gap-1">
                    <button @click="insertText('\\frac{}{}')" title="Fraction" class="latex-button"><span class="font-serif">a/b</span></button>
                    <button @click="insertText('^{}')" title="Superscript" class="latex-button"><span class="font-serif">x²</span></button>
                    <button @click="insertText('_{}')" title="Subscript" class="latex-button"><span class="font-serif">x₂</span></button>
                    <button @click="insertText('\\sqrt{}')" title="Square Root" class="latex-button"><span class="font-serif">√</span></button>
                </div>

                <!-- Group: Operators -->
                <div class="flex flex-wrap gap-1">
                     <button @click="insertText('\\sum')" title="Summation" class="latex-button"><span class="font-serif">∑</span></button>
                     <button @click="insertText('\\int')" title="Integral" class="latex-button"><span class="font-serif">∫</span></button>
                     <button @click="insertText('\\lim_{}')" title="Limit" class="latex-button"><span class="font-serif">lim</span></button>
                </div>

                <!-- Group: Symbols (Dropdown) -->
                <div class="relative" ref="symbolsMenuContainerRef">
                    <button @click="toggleSymbolsMenu" ref="symbolsMenuTriggerRef" class="latex-button flex items-center">
                        <i data-feather="sigma" class="w-4 h-4 mr-1"></i> Symbols
                    </button>
                    <div v-if="showSymbolsMenu" ref="symbolsMenuRef" class="symbols-dropdown absolute top-full left-0 mt-1 z-20 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg p-2 max-h-60 overflow-y-auto">
                        <div class="grid grid-cols-3 gap-1">
                             <button @click="insertSymbolAndClose('\\alpha')" title="Alpha" class="latex-menu-button"><span class="font-serif">α</span></button>
                             <button @click="insertSymbolAndClose('\\beta')" title="Beta" class="latex-menu-button"><span class="font-serif">β</span></button>
                             <button @click="insertSymbolAndClose('\\gamma')" title="Gamma" class="latex-menu-button"><span class="font-serif">γ</span></button>
                             <button @click="insertSymbolAndClose('\\delta')" title="Delta" class="latex-menu-button"><span class="font-serif">δ</span></button>
                             <button @click="insertSymbolAndClose('\\epsilon')" title="Epsilon" class="latex-menu-button"><span class="font-serif">ε</span></button>
                             <button @click="insertSymbolAndClose('\\zeta')" title="Zeta" class="latex-menu-button"><span class="font-serif">ζ</span></button>
                             <button @click="insertSymbolAndClose('\\eta')" title="Eta" class="latex-menu-button"><span class="font-serif">η</span></button>
                             <button @click="insertSymbolAndClose('\\theta')" title="Theta" class="latex-menu-button"><span class="font-serif">θ</span></button>
                             <button @click="insertSymbolAndClose('\\pi')" title="Pi" class="latex-menu-button"><span class="font-serif">π</span></button>
                             <button @click="insertSymbolAndClose('\\rho')" title="Rho" class="latex-menu-button"><span class="font-serif">ρ</span></button>
                             <button @click="insertSymbolAndClose('\\sigma')" title="Sigma" class="latex-menu-button"><span class="font-serif">σ</span></button>
                             <button @click="insertSymbolAndClose('\\tau')" title="Tau" class="latex-menu-button"><span class="font-serif">τ</span></button>
                             <button @click="insertSymbolAndClose('\\phi')" title="Phi" class="latex-menu-button"><span class="font-serif">φ</span></button>
                             <button @click="insertSymbolAndClose('\\psi')" title="Psi" class="latex-menu-button"><span class="font-serif">ψ</span></button>
                             <button @click="insertSymbolAndClose('\\omega')" title="Omega" class="latex-menu-button"><span class="font-serif">ω</span></button>
                             <button @click="insertSymbolAndClose('\\Gamma')" title="Gamma (Upper)" class="latex-menu-button"><span class="font-serif">Γ</span></button>
                             <button @click="insertSymbolAndClose('\\Delta')" title="Delta (Upper)" class="latex-menu-button"><span class="font-serif">Δ</span></button>
                             <button @click="insertSymbolAndClose('\\Theta')" title="Theta (Upper)" class="latex-menu-button"><span class="font-serif">Θ</span></button>
                             <button @click="insertSymbolAndClose('\\Lambda')" title="Lambda (Upper)" class="latex-menu-button"><span class="font-serif">Λ</span></button>
                             <button @click="insertSymbolAndClose('\\Pi')" title="Pi (Upper)" class="latex-menu-button"><span class="font-serif">Π</span></button>
                             <button @click="insertSymbolAndClose('\\Sigma')" title="Sigma (Upper)" class="latex-menu-button"><span class="font-serif">Σ</span></button>
                             <button @click="insertSymbolAndClose('\\Phi')" title="Phi (Upper)" class="latex-menu-button"><span class="font-serif">Φ</span></button>
                             <button @click="insertSymbolAndClose('\\Psi')" title="Psi (Upper)" class="latex-menu-button"><span class="font-serif">Ψ</span></button>
                             <button @click="insertSymbolAndClose('\\Omega')" title="Omega (Upper)" class="latex-menu-button"><span class="font-serif">Ω</span></button>
                             <button @click="insertSymbolAndClose('\\pm')" title="Plus/Minus" class="latex-menu-button"><span class="font-serif">±</span></button>
                             <button @click="insertSymbolAndClose('\\times')" title="Times" class="latex-menu-button"><span class="font-serif">×</span></button>
                             <button @click="insertSymbolAndClose('\\div')" title="Divide" class="latex-menu-button"><span class="font-serif">÷</span></button>
                             <button @click="insertSymbolAndClose('\\leq')" title="Less/Equal" class="latex-menu-button"><span class="font-serif">≤</span></button>
                             <button @click="insertSymbolAndClose('\\geq')" title="Greater/Equal" class="latex-menu-button"><span class="font-serif">≥</span></button>
                             <button @click="insertSymbolAndClose('\\neq')" title="Not Equal" class="latex-menu-button"><span class="font-serif">≠</span></button>
                             <button @click="insertSymbolAndClose('\\approx')" title="Approx Equal" class="latex-menu-button"><span class="font-serif">≈</span></button>
                             <button @click="insertSymbolAndClose('\\cdot')" title="Center Dot" class="latex-menu-button"><span class="font-serif">·</span></button>
                             <button @click="insertSymbolAndClose('\\infty')" title="Infinity" class="latex-menu-button"><span class="font-serif">∞</span></button>
                             <button @click="insertSymbolAndClose('\\partial')" title="Partial Diff" class="latex-menu-button"><span class="font-serif">∂</span></button>
                             <button @click="insertSymbolAndClose('\\nabla')" title="Nabla" class="latex-menu-button"><span class="font-serif">∇</span></button>
                             <button @click="insertSymbolAndClose('\\rightarrow')" title="Right Arrow" class="latex-menu-button"><span class="font-serif">→</span></button>
                             <button @click="insertSymbolAndClose('\\leftarrow')" title="Left Arrow" class="latex-menu-button"><span class="font-serif">←</span></button>
                             <button @click="insertSymbolAndClose('\\uparrow')" title="Up Arrow" class="latex-menu-button"><span class="font-serif">↑</span></button>
                             <button @click="insertSymbolAndClose('\\downarrow')" title="Down Arrow" class="latex-menu-button"><span class="font-serif">↓</span></button>
                        </div>
                    </div>
                </div>

            </div>
        </div>

        <div class="latex-content">
            <div v-if="!isEditing" ref="displayContainerRef" class="latex-display"
                 :class="{
                    'latex-inline': inline,
                    'p-2 min-h-[2em]': !inline,
                    'p-0 min-h-0': inline
                 }">
                <span v-if="errorMessage" class="latex-error text-red-600 dark:text-red-400 text-sm"> Error: {{ errorMessage }} </span>
            </div>

            <div v-else class="latex-edit-area">
                <textarea
                    ref="editorRef"
                    v-model="editableLatexCode"
                    class="latex-textarea w-full p-2 font-mono text-sm border rounded-md bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 focus:border-blue-500 dark:focus:border-blue-400 resize-y"
                    :class="inline ? 'min-h-[4em]' : 'min-h-[8em]'"
                    placeholder="Enter LaTeX code here..."
                    aria-label="LaTeX Code Editor"
                    @input="onInput"
                    @keydown.tab.prevent="handleTabKey"
                ></textarea>
                <div class="latex-preview-label text-xs font-semibold uppercase text-gray-500 dark:text-gray-400 mt-2 mb-1">Live Preview:</div>
                <div
                    ref="previewContainerRef"
                    class="latex-preview border rounded-md bg-gray-50 dark:bg-gray-700"
                    :class="{
                        'latex-inline': inline,
                        'p-2 min-h-[2em]': !inline,
                        'p-0 min-h-0': inline
                    }"
                    aria-live="polite"
                    >
                    <span v-if="previewErrorMessage" class="latex-error text-red-600 dark:text-red-400 text-sm"> Error: {{ previewErrorMessage }} </span>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, nextTick, computed } from 'vue';
import katex from 'katex';
import 'katex/dist/katex.min.css';
import feather from 'feather-icons';
import { debounce } from 'lodash-es';

const props = defineProps({
    initialLatexCode: {
        type: String,
        default: '',
    },
    inline: {
        type: Boolean,
        default: false,
    },
});

const emit = defineEmits(['update:latexCode']);

const isEditing = ref(false);
const editableLatexCode = ref('');
const errorMessage = ref(null);
const previewErrorMessage = ref(null);
const displayContainerRef = ref(null);
const previewContainerRef = ref(null);
const editorRef = ref(null);

const showSymbolsMenu = ref(false);
const symbolsMenuContainerRef = ref(null); // Ref for the container div of the menu+trigger
const symbolsMenuTriggerRef = ref(null); // Ref specifically for the trigger button
const symbolsMenuRef = ref(null); // Ref specifically for the dropdown menu

const katexOptions = computed(() => ({
    displayMode: !props.inline,
    throwOnError: false,
    output: 'html',
    macros: {},
}));

const renderLatex = (container, code) => {
    if (!container) return;
    // Clear previous errors specific to this container
    if (container === previewContainerRef.value) {
         previewErrorMessage.value = null;
    } else {
         errorMessage.value = null;
    }
    try {
        katex.render(code || '', container, katexOptions.value);
        return null;
    } catch (e) {
        let errorMsg = 'Unexpected rendering error.';
        if (e instanceof katex.ParseError || e instanceof TypeError) {
            errorMsg = e.message.replace(/^KaTeX parse error: /, '');
        } else {
            console.error("KaTeX rendering error:", e);
        }
         if (container === previewContainerRef.value) {
             previewErrorMessage.value = errorMsg;
         } else {
             errorMessage.value = errorMsg;
         }
        return errorMsg;
    }
};

const debouncedRenderPreview = debounce(() => {
    renderLatex(previewContainerRef.value, editableLatexCode.value);
}, 300);

const renderDisplay = () => {
    renderLatex(displayContainerRef.value, props.initialLatexCode);
};

const toggleEditMode = () => {
    isEditing.value = !isEditing.value;
    showSymbolsMenu.value = false; // Close menu when toggling edit mode
    if (isEditing.value) {
        editableLatexCode.value = props.initialLatexCode;
        nextTick(() => {
            editorRef.value?.focus();
            debouncedRenderPreview();
            feather.replace(); // Render icons including toolbar icons
        });
    } else {
        if (editableLatexCode.value !== props.initialLatexCode) {
             emit('update:latexCode', editableLatexCode.value);
        }
        nextTick(() => {
             renderDisplay();
             feather.replace(); // Update main edit icon
        });
    }
};

const onInput = () => {
    debouncedRenderPreview();
};

const handleTabKey = (event) => {
    const target = event.target;
    const start = target.selectionStart;
    const end = target.selectionEnd;
    const tab = '\t';

    target.value = target.value.substring(0, start) + tab + target.value.substring(end);
    target.selectionStart = target.selectionEnd = start + tab.length;
};

const insertText = (textToInsert) => {
    if (!editorRef.value) return;
    const editor = editorRef.value;
    editor.focus();

    const start = editor.selectionStart;
    const end = editor.selectionEnd;
    const currentText = editor.value;

    let cursorOffset = textToInsert.indexOf('{}');
    if (cursorOffset !== -1) {
        cursorOffset += 1;
    } else if (textToInsert.endsWith('}')) {
        cursorOffset = textToInsert.length -1; // Place cursor before last brace
    }
     else {
        cursorOffset = textToInsert.length;
    }

    editor.value = currentText.substring(0, start) + textToInsert + currentText.substring(end);
    editableLatexCode.value = editor.value;

    nextTick(() => {
        editor.selectionStart = editor.selectionEnd = start + cursorOffset;
        onInput();
    });
};

const toggleSymbolsMenu = () => {
    showSymbolsMenu.value = !showSymbolsMenu.value;
     nextTick(() => {
            feather.replace(); // Update icons if menu content changes visibility
     });
};

const insertSymbolAndClose = (symbol) => {
    insertText(symbol + ' '); // Add a space after inserting symbol
    showSymbolsMenu.value = false;
};

const handleClickOutside = (event) => {
    // If the menu is open and the click was outside the menu container
    if (showSymbolsMenu.value && symbolsMenuContainerRef.value && !symbolsMenuContainerRef.value.contains(event.target)) {
        showSymbolsMenu.value = false;
    }
};

watch(() => props.initialLatexCode, (newCode) => {
    if (!isEditing.value) {
        renderDisplay();
    }
});

watch(() => props.inline, () => {
    if (isEditing.value) {
        debouncedRenderPreview();
    } else {
        renderDisplay();
    }
});

onMounted(() => {
    renderDisplay();
    document.addEventListener('mousedown', handleClickOutside);
    nextTick(feather.replace);
});

onUnmounted(() => {
    document.removeEventListener('mousedown', handleClickOutside);
});

</script>

<style scoped>
.latex-button {
  @apply px-2 py-1 rounded bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 hover:bg-blue-600 hover:text-white dark:hover:bg-blue-500 transition-colors text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400 disabled:opacity-50;
}
.latex-button .font-serif {
    font-family: 'Times New Roman', Times, serif;
    font-size: 1.1em;
    display: inline-block;
    min-width: 1.5em;
    text-align: center;
}
.latex-button i[data-feather] {
    vertical-align: middle;
}

.latex-menu-button {
     @apply w-full text-center px-1 py-1 rounded bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-blue-600 hover:text-white dark:hover:bg-blue-500 transition-colors text-sm focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-400;
}
.latex-menu-button .font-serif {
     font-family: 'Times New Roman', Times, serif;
     font-size: 1.1em;
     display: inline-block;
     min-width: 1.5em;
     text-align: center;
}

.symbols-dropdown {
    min-width: 150px; /* Ensure dropdown has some width */
}


.latex-edit-toggle-button i[data-feather] {
    vertical-align: middle;
}

.latex-inline .katex-display {
  display: inline !important;
  margin: 0 0.2em !important;
  text-align: initial !important;
}
.latex-display:not(.latex-inline),
.latex-preview:not(.latex-inline) {
    display: block;
    text-align: center;
    overflow-x: auto;
    padding: 0.5em 0;
}
.latex-preview.latex-inline {
    text-align: left;
     display: block;
     padding: 0.2em 0;
}


.latex-textarea {
  line-height: 1.4;
}

.latex-error {
    display: inline-block;
    padding: 0.3em 0.5em;
    background-color: rgba(255, 0, 0, 0.1);
    border: 1px solid rgba(255, 0, 0, 0.3);
    border-radius: 4px;
    white-space: pre-wrap;
    text-align: left;
    margin: 0.2em;
}
.latex-display:not(.latex-inline) .latex-error,
.latex-preview:not(.latex-inline) .latex-error {
     display: block;
     margin: 0;
}
</style>