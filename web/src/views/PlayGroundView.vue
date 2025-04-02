<template>
  <div class="container w-full background-color shadow-lg overflow-y-auto scrollbar">
    <div class="flex flex-col m-2 w-full gap-4">
      <!-- Main Content Area -->
      <div class="flex-grow w-full flex flex-col gap-4">
        <!-- Toolbar -->
        <div class="flex panels-color gap-2 items-center flex-wrap rounded-lg border border-blue-300 dark:border-blue-600 p-3 shadow-md">
          <!-- Generation Buttons -->
          <ChatBarButton v-show="!generating" @click="generate" title="Generate from cursor" class="svg-button group/item relative">
            <template #icon>
              <i data-feather="edit-2" class="h-5 w-5"></i>
            </template>
            <div class="animated-thought-bubble">Generate from cursor</div>
          </ChatBarButton>

          <ChatBarButton v-show="!generating" @click="generate_in_placeholder" title="Generate from placeholder" class="svg-button group/item relative">
            <template #icon>
              <!-- Using cpu as a metaphor for processing the placeholder instruction -->
              <i data-feather="cpu" class="h-5 w-5"></i>
            </template>
             <div class="animated-thought-bubble">Generate from @placeholder@</div>
          </ChatBarButton>

          <ChatBarButton v-show="!generating" @click="tokenize_text" title="Tokenize text" class="svg-button group/item relative">
            <template #icon>
              <i data-feather="hash" class="h-5 w-5"></i>
            </template>
             <div class="animated-thought-bubble">Show token count</div>
          </ChatBarButton>

          <!-- Stop Button -->
          <ChatBarButton v-show="generating" @click="stopGeneration" title="Stop generation" class="svg-button text-red-500 dark:text-red-400 hover:bg-red-100 dark:hover:bg-red-900 group/item relative">
            <template #icon>
              <i data-feather="square" class="h-5 w-5"></i>
            </template>
             <div class="animated-thought-bubble">Stop generation</div>
          </ChatBarButton>

          <!-- Spacer -->
          <div class="flex-grow"></div>

          <!-- Voice/Audio Buttons -->
          <ChatBarButton @click="startSpeechRecognition" :class="{ 'btn-on': isListeningToVoice, 'svg-button': true }" title="Dictate text (Browser STT)" class="svg-button group/item relative">
            <template #icon>
              <i data-feather="mic" class="h-5 w-5"></i>
            </template>
             <div class="animated-thought-bubble">Browser Speech-to-Text</div>
          </ChatBarButton>

          <ChatBarButton @click="speak" :class="{ 'btn-on': isSpeaking, 'svg-button': true }" title="Read text aloud (Browser TTS)" class="svg-button group/item relative">
            <template #icon>
              <i data-feather="volume-2" class="h-5 w-5"></i>
            </template>
             <div class="animated-thought-bubble">Browser Text-to-Speech</div>
          </ChatBarButton>

          <ChatBarButton @click="triggerFileUpload" title="Upload voice file (.wav)" class="svg-button group/item relative">
            <template #icon>
              <!-- Upload icon for file upload action -->
               <i data-feather="upload-cloud" class="h-5 w-5"></i>
            </template>
             <div class="animated-thought-bubble">Upload .wav voice</div>
          </ChatBarButton>
          <input type="file" ref="fileInput" @change="handleFileUpload" class="hidden" accept=".wav" />

          <ChatBarButton @click="startRecordingAndTranscribing" :class="{ 'btn-on': is_deaf_transcribing, 'svg-button': true }" title="Audio-to-Audio (Record -> Transcribe -> TTS)" class="svg-button group/item relative">
            <template #icon>
               <div v-if="!pending" class="relative">
                 <i data-feather="headphones" class="h-5 w-5"></i>
                 <span v-if="is_deaf_transcribing" class="absolute bottom-0 right-0 block h-2 w-2 rounded-full ring-2 ring-white bg-red-500 dark:ring-gray-800 dark:bg-red-400"></span>
               </div>
               <i v-else data-feather="loader" class="h-5 w-5 animate-spin"></i>
            </template>
             <div class="animated-thought-bubble">Record > Transcribe > Speak</div>
          </ChatBarButton>

          <ChatBarButton @click="startRecording" :class="{ 'btn-on': is_recording, 'svg-button': true }" title="Record Audio & Transcribe" class="svg-button group/item relative">
            <template #icon>
               <div v-if="!pending" class="relative">
                 <!-- Using radio for recording state -->
                 <i data-feather="radio" class="h-5 w-5"></i>
                 <span v-if="is_recording" class="absolute bottom-0 right-0 block h-2 w-2 rounded-full ring-2 ring-white bg-red-500 dark:ring-gray-800 dark:bg-red-400"></span>
               </div>
               <i v-else data-feather="loader" class="h-5 w-5 animate-spin"></i>
            </template>
             <div class="animated-thought-bubble">Record > Transcribe</div>
          </ChatBarButton>

          <ChatBarButton v-if="!isSynthesizingVoice" @click="read" title="Generate Audio (Backend TTS)" class="svg-button group/item relative">
            <template #icon>
              <i data-feather="speaker" class="h-5 w-5"></i>
            </template>
             <div class="animated-thought-bubble">Backend Text-to-Speech</div>
          </ChatBarButton>
          <div v-else class="w-6 h-6 flex items-center justify-center">
             <i data-feather="loader" class="h-5 w-5 animate-spin text-blue-500 dark:text-blue-400"></i>
          </div>

          <!-- Import/Export/Settings Buttons -->
          <ChatBarButton v-show="!generating" @click="exportText" title="Export text" class="svg-button group/item relative">
            <template #icon>
              <i data-feather="download" class="h-5 w-5"></i>
            </template>
             <div class="animated-thought-bubble">Download text</div>
          </ChatBarButton>

          <ChatBarButton v-show="!generating" @click="importText" title="Import text" class="svg-button group/item relative">
            <template #icon>
               <!-- Using upload for importing text file -->
               <i data-feather="upload" class="h-5 w-5"></i>
            </template>
             <div class="animated-thought-bubble">Upload text file</div>
          </ChatBarButton>
          <input type="file" id="import-input" class="hidden" accept=".txt,.md">

          <ChatBarButton @click="showSettingsModal = true" title="Settings" class="svg-button group/item relative">
            <template #icon>
              <i data-feather="settings" class="h-5 w-5"></i>
            </template>
             <div class="animated-thought-bubble">Open settings</div>
          </ChatBarButton>

          <div class="flex gap-2 justify-end">
            <button @click="tab_id='source'"
                    :class="tab_id === 'source' ? 'active-tab-button' : 'inactive-tab-button'">
              Source
            </button>
            <button @click="tab_id='render'"
                    :class="tab_id === 'render' ? 'active-tab-button' : 'inactive-tab-button'">
              Render
            </button>
          </div>
        </div>

        <!-- Text Area / Render Area -->
        <div class="flex-grow p-4 border panels-color border-blue-300 dark:border-blue-600 rounded-lg shadow-inner" :class="{ 'border-red-500 dark:border-red-400': generating }">
          <div v-if="tab_id === 'source'" class="flex flex-col h-full">
              <div class="flex items-center gap-1 mb-2">
                 <DropdownMenu title="Add Block" icon="plus-circle" buttonClass="svg-button">
                     <!-- Submenus remain the same -->
                     <!-- Programming Languages -->
                    <DropdownSubmenu title="Programming Languages" icon="code">
                        <ToolbarButton @click.stop="addBlock('python')" title="Python" icon="python" />
                        <ToolbarButton @click.stop="addBlock('javascript')" title="JavaScript" icon="js" />
                        <ToolbarButton @click.stop="addBlock('typescript')" title="TypeScript" icon="typescript" />
                        <ToolbarButton @click.stop="addBlock('java')" title="Java" icon="java" />
                        <ToolbarButton @click.stop="addBlock('c++')" title="C++" icon="cplusplus" />
                        <ToolbarButton @click.stop="addBlock('csharp')" title="C#" icon="csharp" />
                        <ToolbarButton @click.stop="addBlock('go')" title="Go" icon="go" />
                        <ToolbarButton @click.stop="addBlock('rust')" title="Rust" icon="rust" />
                        <ToolbarButton @click.stop="addBlock('swift')" title="Swift" icon="swift" />
                        <ToolbarButton @click.stop="addBlock('kotlin')" title="Kotlin" icon="kotlin" />
                        <ToolbarButton @click.stop="addBlock('r')" title="R" icon="r-project" />
                    </DropdownSubmenu>

                    <!-- Web Technologies -->
                    <DropdownSubmenu title="Web Technologies" icon="globe">
                        <ToolbarButton @click.stop="addBlock('html')" title="HTML" icon="html5" />
                        <ToolbarButton @click.stop="addBlock('css')" title="CSS" icon="css3" />
                        <ToolbarButton @click.stop="addBlock('vue')" title="Vue.js" icon="vuejs" />
                        <ToolbarButton @click.stop="addBlock('react')" title="React" icon="react" />
                        <ToolbarButton @click.stop="addBlock('angular')" title="Angular" icon="angular" />
                    </DropdownSubmenu>

                    <!-- Markup and Data Formats -->
                    <DropdownSubmenu title="Markup and Data" icon="file-text">
                        <ToolbarButton @click.stop="addBlock('xml')" title="XML" icon="xml" />
                        <ToolbarButton @click.stop="addBlock('json')" title="JSON" icon="json" />
                        <ToolbarButton @click.stop="addBlock('yaml')" title="YAML" icon="yaml" />
                        <ToolbarButton @click.stop="addBlock('markdown')" title="Markdown" icon="markdown" />
                        <ToolbarButton @click.stop="addBlock('latex')" title="LaTeX" icon="latex" />
                    </DropdownSubmenu>

                    <!-- Scripting and Shell -->
                    <DropdownSubmenu title="Scripting and Shell" icon="terminal">
                        <ToolbarButton @click.stop="addBlock('bash')" title="Bash" icon="bash" />
                        <ToolbarButton @click.stop="addBlock('powershell')" title="PowerShell" icon="powershell" />
                        <ToolbarButton @click.stop="addBlock('perl')" title="Perl" icon="perl" />
                    </DropdownSubmenu>

                    <!-- Diagramming -->
                    <DropdownSubmenu title="Diagramming" icon="share-2">
                        <ToolbarButton @click.stop="addBlock('mermaid')" title="Mermaid" icon="mermaid" />
                        <ToolbarButton @click.stop="addBlock('graphviz')" title="Graphviz" icon="graphviz" />
                        <ToolbarButton @click.stop="addBlock('plantuml')" title="PlantUML" icon="plantuml" />
                    </DropdownSubmenu>

                    <!-- Database -->
                    <DropdownSubmenu title="Database" icon="database">
                        <ToolbarButton @click.stop="addBlock('sql')" title="SQL" icon="sql" />
                        <ToolbarButton @click.stop="addBlock('mongodb')" title="MongoDB" icon="mongodb" />
                    </DropdownSubmenu>

                    <!-- Other -->
                    <ToolbarButton @click.stop="addBlock('')" title="Generic Block" icon="code" />
                 </DropdownMenu>
                 <ToolbarButton @click.stop="copyContentToClipboard()" title="Copy content to clipboard" icon="copy" buttonClass="svg-button" />
              </div>
            <textarea ref="mdTextarea" @keydown.tab.prevent="insertTab"
              class="block w-full flex-grow min-h-[400px] p-3 input rounded-lg shadow-sm focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 scrollbar text-blue-900 dark:text-blue-100 placeholder-blue-400 dark:placeholder-blue-500 resize-none"
              :style="{ minHeight: mdRenderHeight + 'px' }"
              placeholder="Enter text or drop files here..."
              v-model="text"
              @click.prevent="mdTextarea_clicked"
              @change.prevent="mdTextarea_changed">
              </textarea>
            <span class="text-xs text-blue-600 dark:text-blue-400 mt-1">Cursor position: {{ cursorPosition }}</span>
             <audio controls v-if="audio_url!=null" :key="audio_url" class="mt-4 w-full">
                <source :src="audio_url" type="audio/wav" ref="audio_player">
                Your browser does not support the audio element.
             </audio>
             <tokens-hilighter :namedTokens="namedTokens" class="mt-4"></tokens-hilighter>
          </div>

          <div v-if="tab_id === 'render'" class="h-full overflow-y-auto scrollbar">
            <MarkdownRenderer ref="mdRender"
                              :client_id="this.$store.state.client_id"
                              :message_id="0"
                              :discussion_id="0"
                              :markdown-text="text"
                              class="mt-4 p-4 rounded-lg shadow-md panels-color prose-blue dark:prose-invert">
            </MarkdownRenderer>
          </div>
        </div>
      </div>

      <!-- Settings Modal -->
      <div v-if="showSettingsModal" @click.self="showSettingsModal = false"
           class="fixed inset-0 z-50 flex items-center justify-center bg-black/50 dark:bg-black/70 p-4 backdrop-blur-sm">
          <div class="card w-full max-w-2xl max-h-[80vh] flex flex-col">
             <div class="flex justify-between items-center border-b border-blue-200 dark:border-blue-700 pb-2 mb-4">
                 <h2 class="text-2xl font-semibold">Settings</h2>
                 <button @click="showSettingsModal = false" class="svg-button">
                     <i data-feather="x" class="w-6 h-6"></i>
                 </button>
             </div>
             <div class="flex-grow overflow-y-auto scrollbar pr-2 space-y-4">
                 <!-- Model Selection Card -->
                 <Card title="Model" class="p-4" :isHorizontal="false" :disableHoverAnimation="true" :disableFocus="true">
                 <select v-model="$store.state.selectedModel" @change="setModel" class="input w-full" :disabled="selecting_model">
                     <option v-for="model in models" :key="model" :value="model">
                     {{ model }}
                     </option>
                 </select>
                 <div v-if="selecting_model" title="Selecting model" class="flex items-center justify-center my-2">
                     <div role="status" class="flex items-center gap-2 text-blue-600 dark:text-blue-400">
                     <i data-feather="loader" class="w-5 h-5 animate-spin"></i>
                     <span>Selecting...</span>
                     </div>
                 </div>
                 </Card>

                 <!-- Presets Card -->
                 <Card title="Presets" class="p-4" :isHorizontal="false" :disableHoverAnimation="true" :disableFocus="true">
                 <select v-model="selectedPreset" class="input w-full mb-2">
                     <option :value="null" disabled>-- Select a Preset --</option>
                     <option v-for="preset in presets" :key="preset.name" :value="preset">
                     {{ preset.name }}
                     </option>
                 </select>
                 <div class="flex gap-2">
                     <button class="svg-button" @click="setPreset" title="Use preset" :disabled="!selectedPreset">
                     <i data-feather="check" class="w-4 h-4"></i>
                     </button>
                     <button class="svg-button" @click="addPreset" title="Add current text as a preset">
                     <i data-feather="plus" class="w-4 h-4"></i>
                     </button>
                     <button class="svg-button" @click="removePreset" title="Remove selected preset" :disabled="!selectedPreset">
                     <i data-feather="x" class="w-4 h-4"></i>
                     </button>
                     <button class="svg-button" @click="reloadPresets" title="Reload presets list">
                     <i data-feather="refresh-ccw" class="w-4 h-4"></i>
                     </button>
                 </div>
                 </Card>

                 <!-- Generation Parameters Card -->
                 <Card title="Generation Parameters" class="p-4 space-y-4" :isHorizontal="false" :disableHoverAnimation="true" :disableFocus="true">
                 <div class="setting-item">
                     <label class="setting-label" for="temp-slider">Temperature</label>
                     <input id="temp-slider" type="range" v-model="temperature" min="0" max="5" step="0.01" class="range-input flex-grow">
                     <span class="text-sm text-blue-600 dark:text-blue-400 w-16 text-right">{{ Number(temperature).toFixed(2) }}</span>
                 </div>
                 <div class="setting-item">
                     <label class="setting-label" for="topk-slider">Top K</label>
                     <input id="topk-slider" type="range" v-model="top_k" min="1" max="200" step="1" class="range-input flex-grow">
                     <span class="text-sm text-blue-600 dark:text-blue-400 w-16 text-right">{{ top_k }}</span>
                 </div>
                 <div class="setting-item">
                     <label class="setting-label" for="topp-slider">Top P</label>
                     <input id="topp-slider" type="range" v-model="top_p" min="0" max="1" step="0.01" class="range-input flex-grow">
                     <span class="text-sm text-blue-600 dark:text-blue-400 w-16 text-right">{{ Number(top_p).toFixed(2) }}</span>
                 </div>
                 <div class="setting-item">
                     <label class="setting-label" for="repeat-penalty-slider">Repeat Penalty</label>
                     <input id="repeat-penalty-slider" type="range" v-model="repeat_penalty" min="1.0" max="3.0" step="0.01" class="range-input flex-grow">
                     <span class="text-sm text-blue-600 dark:text-blue-400 w-16 text-right">{{ Number(repeat_penalty).toFixed(2) }}</span>
                 </div>
                 <div class="setting-item">
                     <label class="setting-label" for="repeat-last-n-slider">Repeat Last N</label>
                     <input id="repeat-last-n-slider" type="range" v-model="repeat_last_n" min="0" max="256" step="1" class="range-input flex-grow">
                     <span class="text-sm text-blue-600 dark:text-blue-400 w-16 text-right">{{ repeat_last_n }}</span>
                 </div>
                 <div class="setting-item">
                     <label class="setting-label" for="n-crop-input">Crop context (tokens)</label>
                     <input id="n-crop-input" type="number" v-model.number="n_crop" class="input input-sm flex-grow">
                 </div>
                 <div class="setting-item">
                     <label class="setting-label" for="n-predicts-input">Max generation (tokens)</label>
                     <input id="n-predicts-input" type="number" v-model.number="n_predicts" class="input input-sm flex-grow">
                 </div>
                 <div class="setting-item">
                     <label class="setting-label" for="seed-input">Seed</label>
                     <input id="seed-input" type="number" v-model.number="seed" class="input input-sm flex-grow">
                 </div>
                 </Card>
             </div>
          </div>
      </div>

    </div>
  </div>
  <Toast ref="toast"/>
</template>

<script>
// Script content remains the same as provided in the previous step
// ... (Keep the existing script content including imports and methods)
import feather from 'feather-icons'
import axios from "axios";
import socket from '@/services/websocket.js'
import Toast from '../components/Toast.vue'
import MarkdownRenderer from '../components/MarkdownRenderer.vue';
import ClipBoardTextInput from "@/components/ClipBoardTextInput.vue";
import TokensHilighter from "@/components/TokensHilighter.vue"
import ChatBarButton from "@/components/ChatBarButton.vue"
import Card from "@/components/Card.vue"
import { nextTick, TransitionGroup } from 'vue'
const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL

import code_block from '@/assets/code_block.svg';
import python_block from '@/assets/python_block.png';
import javascript_block from '@/assets/javascript_block.svg';
import json_block from '@/assets/json_block.png';


import cpp_block from '@/assets/cpp_block.png';
import html5_block from '@/assets/html5_block.png';
import LaTeX_block from '@/assets/LaTeX_block.png';
import bash_block from '@/assets/bash_block.png';

import tokenize_icon from '@/assets/tokenize_icon.svg';



import deaf_on from '@/assets/deaf_on.svg';
import deaf_off from '@/assets/deaf_off.svg';

import rec_on from '@/assets/rec_on.svg';
import rec_off from '@/assets/rec_off.svg';
import loading_icon from '@/assets/loading.svg';

import ToolbarButton from '@/components/ToolbarButton.vue'
import DropdownMenu from '@/components/DropdownMenu.vue'


async function showInputPanel(name, default_value="", options=[]) {
    return new Promise((resolve, reject) => {
        const panel = document.createElement("div");
        // Added dark mode support and theme classes
        panel.className = "fixed inset-0 flex items-center justify-center bg-black/50 dark:bg-black/70 z-[1001] p-4 backdrop-blur-sm"; // Increased z-index for modal
        let contentHtml = '';

        if (options.length === 0) {
            contentHtml = `
                <textarea id="replacementInput" class="input w-full h-32 mb-3 resize-none">${default_value}</textarea>
            `;
        } else {
            contentHtml = `
                <select id="options_selector" class="input w-full mb-3">
                    ${options.map(option => `<option value="${option}" ${option === default_value ? 'selected' : ''}>${option}</option>`).join('')}
                </select>
            `;
        }

        panel.innerHTML = `
            <div class="card w-full max-w-md">
                <h3 class="mb-4">${name}</h3>
                ${contentHtml}
                <div class="flex justify-end gap-2">
                    <button id="cancelButton" class="btn btn-secondary">Cancel</button>
                    <button id="okButton" class="btn btn-primary">OK</button>
                </div>
            </div>
        `;

        document.body.appendChild(panel);

        const cardElement = panel.querySelector('.card'); // Prevent clicks inside from closing
        const cancelButton = panel.querySelector("#cancelButton");
        const okButton = panel.querySelector("#okButton");

        // Close on outside click
        panel.addEventListener('click', (event) => {
             if (!cardElement.contains(event.target)) {
                 document.body.removeChild(panel);
                 resolve(null); // Resolve with null on cancel/outside click
             }
         });

        cancelButton.addEventListener("click", () => {
            document.body.removeChild(panel);
            resolve(null);
        });

        okButton.addEventListener("click", () => {
            let value = null;
            if (options.length === 0) {
                const input = panel.querySelector("#replacementInput");
                value = input.value; // Don't trim here, let the caller decide
            } else {
                const input = panel.querySelector("#options_selector");
                value = input.value;
            }
            document.body.removeChild(panel);
            resolve(value);
        });

        // Focus the input/select element
        const inputElement = panel.querySelector('#replacementInput, #options_selector');
        if (inputElement) {
          inputElement.focus();
          // If it's a textarea, move cursor to end
          if (inputElement.tagName === 'TEXTAREA') {
              inputElement.selectionStart = inputElement.selectionEnd = inputElement.value.length;
          }
        }
    });
}

function replaceInText(text, callback) {
  console.log("Original text for replacement:",text)
    let replacementDict = {};
    let delimiterRegex = /@<([^>]+)>@/g;
    let matches = [];
    let match;

    while ((match = delimiterRegex.exec(text)) !== null) {
      matches.push("@<"+match[1]+">@"); // The captured group is at index 1
    }
    console.log("Found placeholders:", matches)
    matches =  [...new Set(matches)] // Unique placeholders

    async function handleReplacement(placeholder_full) {
        console.log("Processing placeholder:", placeholder_full)
        let placeholder_inner = placeholder_full.substring(2,placeholder_full.length-2); // Remove @< >@
        if (placeholder_inner.toLowerCase() !== "generation_placeholder") {
          if (placeholder_inner.includes(":")) {
            // Special key words handling (e.g., language options)
            let key_words_dict={
              "all_language_options":"english:french:german:chinese:japanese:spanish:italian:russian:portuguese:swedish:danish:dutch:norwegian:slovak:czech:hungarian:polish:ukrainian:bulgarian:latvian:lithuanian:estonian:maltese:irish:galician:basque:welsh:breton:georgian:turkmen:kazakh:uzbek:tajik:afghan:sri-lankan:filipino:vietnamese:lao:cambodian:thai:burmese:kenyan:botswanan:zimbabwean:malawian:mozambican:angolan:namibian:south-african:madagascan:seychellois:mauritian:haitian:peruvian:ecuadorian:bolivian:paraguayan:chilean:argentinean:uruguayan:brazilian:colombian:venezuelan:puerto-rican:cuban:dominican:honduran:nicaraguan:salvadoran:guatemalan:el-salvadoran:belizean:panamanian:costa-rican:antiguan:barbudan:dominica's:grenada's:st-lucia's:st-vincent's:gibraltarian:faroe-islander:greenlandic:icelandic:jamaican:trinidadian:tobagonian:barbadian:anguillan:british-virgin-islander:us-virgin-islander:turkish:israeli:palestinian:lebanese:egyptian:libyan:tunisian:algerian:moroccan:bahraini:kuwaiti:saudi-arabian:yemeni:omani:irani:iraqi:afghanistan's:pakistani:indian:nepalese:sri-lankan:maldivan:burmese:thai:lao:vietnamese:kampuchean:malaysian:bruneian:indonesian:australian:new-zealanders:fijians:tongans:samoans:vanuatuans:wallisians:kiribatians:tuvaluans:solomon-islanders:marshallese:micronesians:hawaiians",
              "all_programming_language_options":"python:c:c++:java:javascript:php:ruby:go:swift:kotlin:rust:haskell:erlang:lisp:scheme:prolog:cobol:fortran:pascal:delphi:d:eiffel:h:basic:visual_basic:smalltalk:objective-c:html5:node.js:vue.js:svelte:react:angular:ember:clipper:stex:arduino:brainfuck:r:assembly:mason:lepton:seacat:bbc_microbit:raspberry_pi_gpio:raspberry_pi_spi:raspberry_pi_i2c:raspberry_pi_uart:raspberry_pi_adc:raspberry_pi_ddio"
            }
            Object.entries(key_words_dict).forEach(([key, value]) => {
              console.log(`Checking keyword: ${key}`);
              function escapeRegExp(string) {
                  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // Escape special characters
              }
              const escapedKey = escapeRegExp(key);
              const regex = new RegExp(escapedKey, 'g');
              if (regex.test(placeholder_inner)) {
                console.log(`Replacing keyword ${key} with options list.`);
                placeholder_inner = placeholder_inner.replace(regex, value);
              }
            });

            let splitResult = placeholder_inner.split(":");
            let name = splitResult[0];
            let defaultValue = splitResult[1] || ""; // Default value is the first option after the name
            let options = [];
            if (splitResult.length > 1) { // If there are options provided
              options = splitResult.slice(1); // Options start from index 1
              defaultValue = options[0]; // Default to the first option unless specified differently (though current logic always makes it the first)
            }
            console.log(`Prompting for '${name}' with options: [${options.join(', ')}], default: '${defaultValue}'`)
            let replacement = await showInputPanel(name, defaultValue, options);
            if (replacement !== null) {
                replacementDict[placeholder_full] = replacement;
            } else {
                // Handle cancellation: maybe keep the placeholder or use default?
                replacementDict[placeholder_full] = defaultValue; // Replace with default if cancelled
                console.log(`Input for '${name}' cancelled, using default: '${defaultValue}'`);
            }
          }
          else{ // Simple placeholder without options
            console.log(`Prompting for '${placeholder_inner}'`)
            let replacement = await showInputPanel(placeholder_inner);
            if (replacement !== null) {
                replacementDict[placeholder_full] = replacement;
            } else {
                 replacementDict[placeholder_full] = ""; // Replace with empty string if cancelled
                 console.log(`Input for '${placeholder_inner}' cancelled, using empty string.`);
            }
          }
        }else{
          console.log("Found @<generation_placeholder>@, skipping user input.");
          // This placeholder is handled by the generation logic later
        }
    }
    let promiseChain = Promise.resolve();

    matches.forEach(match => {
      promiseChain = promiseChain.then(() => {
        return handleReplacement(match);
      });
    });
    promiseChain.then(() => {
      let processedText = text;
      Object.entries(replacementDict).forEach(([key, value]) => {
        console.log(`Replacing '${key}' with '${value}'`);
        function escapeRegExp(string) {
            return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // Escape special characters
        }

        const escapedKey = escapeRegExp(key);
        const regex = new RegExp(escapedKey, 'g');
        processedText = processedText.replace(regex, value);
      });
      console.log("Final text after replacements:", processedText);
      callback(processedText); // Call the callback with the final text
    });
}


export default {
  name: 'PlayGroundView',
  data() {
    return {
      posts_headers : {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
      showSettingsModal: false, // Changed from showSettings
      pending:false,
      is_recording:false,
      is_deaf_transcribing:false,

      cpp_block:cpp_block,
      html5_block:html5_block,
      LaTeX_block:LaTeX_block,
      javascript_block:javascript_block,
      json_block:json_block,
      code_block:code_block,
      python_block:python_block,
      bash_block:bash_block,

      tokenize_icon:tokenize_icon,

      deaf_off:deaf_off,
      deaf_on:deaf_on,

      rec_off:rec_off,
      rec_on:rec_on,
      loading_icon:loading_icon,

      isSynthesizingVoice:false,
      audio_url:null,
      mdRenderHeight:400, // Initial height
      selecting_model:false,
      tab_id:"source", // Default to source tab
      generating:false,
      isSpeaking:false,
      voices: [],
      isListeningToVoice:false, // For browser speech recognition
      presets:[],
      selectedPreset: null, // Initialize as null or first preset after loading
      cursorPosition:0,
      namedTokens:[],
      text:"",
      pre_text:"",
      post_text:"",
      // Default Generation Parameters (can be loaded/saved)
      temperature: 0.8,
      top_k: 50,
      top_p: 0.95,
      repeat_penalty: 1.1,
      repeat_last_n: 64,
      n_crop: -1,
      n_predicts: 1024,
      seed: -1,
      silenceTimeout: 3000, // Shorter timeout for speech recognition
      file: null, // For voice upload
      speechRecognition: null, // Store recognition instance
      silenceTimer: null,
      generatedSpeechText: "", // Temp store for speech-to-text
    };
  },

  components:{
    Toast,
    MarkdownRenderer,
    // ClipBoardTextInput, // Not used in template? Remove if unnecessary
    TokensHilighter,
    ChatBarButton,
    Card,
    ToolbarButton,
    DropdownMenu,
  },
  mounted() {
    this.loadPresets(); // Load presets on mount

    // Setup WebSocket listeners
    socket.on('text_chunk', data => {
        this.appendToOutput(data.chunk);
    });
    socket.on('text_generated', data => {
        this.generating = false;
    });
    socket.on('generation_error', data => {
        console.error('Generation Error:', data);
        this.$refs.toast.showToast(`Error: ${data.error || data}`, 4, false);
        this.generating = false;
    });
    socket.on('connect', () => {
        console.log('Connected to LoLLMs server via WebSocket');
        this.$store.state.isConnected = true;
        this.generating = false; // Reset generation state on connect/reconnect
    });
    socket.on('disconnect', () => {
        console.log('Disconnected from LoLLMs server via WebSocket');
        this.$store.state.isConnected = false;
        this.generating = false;
    });
    socket.on('buzzy', error => {
        console.error('Server is busy:', error);
        this.$refs.toast.showToast(`Server busy: ${error.message}`, 4, false);
        this.generating = false;
    });
    socket.on('generation_canceled', () => {
        console.log("Generation canceled by server/user.");
        this.generating = false;
    });

    this.$nextTick(() => {
        feather.replace();
        this.adjustTextareaHeight(); // Adjust height after initial render
    });

    // Initialize Speech Synthesis
    if ('speechSynthesis' in window) {
        this.speechSynthesis = window.speechSynthesis;
        this.loadVoices();
        this.speechSynthesis.onvoiceschanged = this.loadVoices; // Reload if voices change
    } else {
        console.warn('Speech synthesis is not supported in this browser.');
    }

    // Add listener to adjust textarea height on window resize (optional)
     window.addEventListener('resize', this.adjustTextareaHeight);

  },
   beforeUnmount() {
     // Clean up resize listener
     window.removeEventListener('resize', this.adjustTextareaHeight);
     // Clean up speech recognition if active
     if (this.recognition) {
         this.recognition.stop();
         this.recognition = null;
     }
     // Clean up TTS if active
      if (this.isSpeaking) {
            this.speechSynthesis.cancel();
      }
   },
  methods:{
    adjustTextareaHeight() {
      // Example: Set height relative to window, but ensure a minimum
      const topOffset = this.$refs.mdTextarea?.getBoundingClientRect().top || 200; // Estimate top offset
      const bottomPadding = 60; // Space for status bar, audio player etc.
      const calculatedHeight = window.innerHeight - topOffset - bottomPadding;
      this.mdRenderHeight = Math.max(300, calculatedHeight); // Ensure min height of 300px
      //console.log("Adjusted textarea min-height to:", this.mdRenderHeight);
    },
    loadVoices() {
        this.voices = this.speechSynthesis.getVoices();
        if (this.voices.length > 0) {
            console.log("TTS voices loaded.");
            // Filter voices if needed, e.g., by language
            // this.voices = this.voices.filter(v => v.lang.startsWith('en'));
        }
    },
    loadPresets() {
        axios.get('./get_presets').then(response => {
          console.log("Presets loaded:", response.data)
          this.presets = response.data;
          if (this.presets.length > 0) {
            // Check if selectedPreset is still valid, otherwise select the first one (or null)
            const currentPresetExists = this.presets.some(p => p.name === this.selectedPreset?.name);
            if (!currentPresetExists) {
               // Keep selectedPreset null unless you want to auto-select the first one
               // this.selectedPreset = this.presets[0];
               this.selectedPreset = null; // Default to null/prompt
            }
          } else {
              this.selectedPreset = null;
          }
        }).catch(ex => {
          console.error("Error loading presets:", ex);
          this.$refs.toast.showToast(`Error loading presets: ${ex.message || ex}`, 4, false);
        });
    },
    triggerFileUpload() {
      this.$refs.fileInput.click();
    },
    handleFileUpload(event) {
      const files = event.target.files;
      if (files && files.length > 0) {
          this.file = files[0];
          console.log(`File selected: ${this.file.name}`);
          this.uploadFile();
          // Reset file input value to allow selecting the same file again
          event.target.value = null;
      } else {
          console.log("No file selected.");
          this.file = null;
      }
    },
    uploadFile() {
      if (!this.file) {
          this.$refs.toast.showToast('No voice file selected.', 3, false);
          return;
      }
      console.log(`Uploading voice file: ${this.file.name}`);
      const formData = new FormData();
      formData.append('file', this.file);
      formData.append('client_id', this.$store.state.client_id); // Ensure client_id is sent

      this.$refs.toast.showToast(`Uploading ${this.file.name}...`, 2, true); // Show loading toast

      axios.post('/upload_voice/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then(response => {
        console.log("Voice upload response:", response.data);
        this.$refs.toast.showToast(response.data.message || `${this.file.name} uploaded successfully.`, 4, true);
        this.file = null; // Clear file after successful upload
      })
      .catch(error => {
        console.error("Voice upload error:", error);
        this.$refs.toast.showToast(`Error uploading voice: ${error.response?.data?.error || error.message || 'Unknown error'}`, 4, false);
      });
    },
    addBlock(bloc_name){
            const textarea = this.$refs.mdTextarea;
            let ss = textarea.selectionStart;
            let se = textarea.selectionEnd;
            const selectedText = this.text.slice(ss, se);
            let textToInsert = "";
            let cursorPosAfterInsert = ss;

            const prefix = (ss === 0 || this.text[ss - 1] === "\n") ? "" : "\n";
            const suffix = "\n";

            if (selectedText) {
                textToInsert = `${prefix}\`\`\`${bloc_name}\n${selectedText}\n\`\`\`${suffix}`;
                // Place cursor after the opening fence and language identifier
                cursorPosAfterInsert = ss + prefix.length + 3 + bloc_name.length + 1;
            } else {
                textToInsert = `${prefix}\`\`\`${bloc_name}\n\n\`\`\`${suffix}`;
                 // Place cursor inside the block for immediate typing
                cursorPosAfterInsert = ss + prefix.length + 3 + bloc_name.length + 1;
            }

            // Update text using Vue's reactivity
            this.text = this.text.slice(0, ss) + textToInsert + this.text.slice(se);

            // Use nextTick to ensure the DOM is updated before setting selection
            this.$nextTick(() => {
                textarea.focus();
                textarea.selectionStart = textarea.selectionEnd = cursorPosAfterInsert;
                this.cursorPosition = cursorPosAfterInsert; // Update cursor position tracker
            });
    },

    insertTab(event) {
            const textarea = event.target;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
            const tabSpaces = '    '; // 4 spaces for a tab

            // Update text using Vue's reactivity
            this.text = textarea.value.substring(0, start) + tabSpaces + textarea.value.substring(end);

            // Use nextTick to ensure the DOM is updated before setting selection
            this.$nextTick(() => {
                textarea.selectionStart = textarea.selectionEnd = start + tabSpaces.length;
                this.cursorPosition = start + tabSpaces.length; // Update cursor position tracker
            });

            event.preventDefault(); // Prevent default tab behavior (changing focus)
        },
    mdTextarea_changed(){
      // This might be redundant if click updates cursorPosition, but can be useful
      // if the content changes programmatically without a click.
      if (this.$refs.mdTextarea) {
          this.cursorPosition = this.$refs.mdTextarea.selectionStart;
      }
    },
    mdTextarea_clicked(){
      // Update cursor position whenever the textarea is clicked
      if (this.$refs.mdTextarea) {
          this.cursorPosition = this.$refs.mdTextarea.selectionStart;
          console.log(`Cursor position set to: ${this.cursorPosition}`);
      }
    },
    setModel(){
      if (!this.$store.state.selectedModel) {
          console.warn("No model selected.");
          return;
      }
      console.log(`Setting model to: ${this.$store.state.selectedModel}`);
      this.selecting_model=true;
      this.$refs.toast.showToast(`Switching model to ${this.$store.state.selectedModel}...`, 3, true);
      axios.post("/update_setting", {
                client_id: this.$store.state.client_id,
                setting_name: "model_name",
                setting_value: this.$store.state.selectedModel
              }).then((response) => {
          console.log("Set model response:", response.data);
          if(response.data.status){
            this.$refs.toast.showToast(`Model changed to ${this.$store.state.selectedModel}`, 4, true)
          } else {
             this.$refs.toast.showToast(`Failed to change model: ${response.data.error || 'Unknown error'}`, 4, false)
          }
          this.selecting_model=false;
        }).catch(err=>{
          console.error("Error setting model:", err);
          this.$refs.toast.showToast(`Error setting model: ${err.response?.data?.error || err.message}`, 4, false)
          this.selecting_model=false;
        });

    },
    read(){ // Backend TTS
        console.log("Requesting backend text-to-speech synthesis...");
        this.isSynthesizingVoice = true;
        this.audio_url = null; // Clear previous audio URL

        let ss = this.$refs.mdTextarea.selectionStart;
        let se = this.$refs.mdTextarea.selectionEnd;
        let textToSynthesize = this.text;
        if (ss !== se && se > ss) {
            textToSynthesize = this.text.slice(ss, se);
            console.log(`Synthesizing selected text (length: ${textToSynthesize.length})`);
        } else {
             console.log(`Synthesizing full text (length: ${textToSynthesize.length})`);
        }

        if (!textToSynthesize.trim()) {
             this.$refs.toast.showToast("Cannot synthesize empty text.", 3, false);
             this.isSynthesizingVoice = false;
             return;
        }

        this.$refs.toast.showToast("Synthesizing audio...", 2, true);

        axios.post("./text2Wave",{client_id:this.$store.state.client_id, text:textToSynthesize}).then(response => {
          console.log("TTS synthesis response:", response.data);
          if (response.data && response.data.url) {
              this.audio_url = response.data.url;
              this.$refs.toast.showToast("Audio ready.", 3, true);
              // Use nextTick to ensure the audio element is updated before potential play attempt
              nextTick(() => {
                 if (this.$refs.audio_player) {
                    this.$refs.audio_player.load(); // Load the new source
                    // Optional: Auto-play? Consider user experience.
                    // this.$refs.audio_player.play().catch(e => console.error("Audio autoplay failed:", e));
                 }
              });
          } else {
               this.$refs.toast.showToast(response.data.error || "Failed to generate audio.", 4, false);
          }
          this.isSynthesizingVoice = false;
          // Refresh icons after state change
          this.$nextTick(() => feather.replace());
        }).catch(ex => {
          console.error("TTS synthesis error:", ex);
          this.$refs.toast.showToast(`TTS Error: ${ex.response?.data?.error || ex.message}`, 4, false);
          this.isSynthesizingVoice = false;
           // Refresh icons after state change
           this.$nextTick(() => feather.replace());
        });
      },
      speak() { // Browser TTS
        if (!('speechSynthesis' in window)) {
            this.$refs.toast.showToast("Browser speech synthesis not supported.", 3, false);
            return;
        }

        if (this.isSpeaking) {
            this.speechSynthesis.cancel(); // Stop ongoing speech
            this.isSpeaking = false;
            console.log("Browser TTS stopped.");
             this.$nextTick(() => feather.replace()); // Update icon state
            return;
        }

        let ss = this.$refs.mdTextarea.selectionStart;
        let se = this.$refs.mdTextarea.selectionEnd;
        let textToSpeak = this.text;
        if (ss !== se && se > ss) {
            textToSpeak = this.text.slice(ss, se);
        }

        if (!textToSpeak.trim()) {
            this.$refs.toast.showToast("Cannot speak empty text.", 3, false);
            return;
        }

        console.log("Starting browser TTS...");
        this.isSpeaking = true;
         this.$nextTick(() => feather.replace()); // Update icon state
        this.speechSynthesis.cancel(); // Clear any previous utterances

        const utterance = new SpeechSynthesisUtterance(textToSpeak);
        utterance.pitch = this.$store.state.config.audio_pitch || 1; // Use config or default
        utterance.rate = this.$store.state.config.audio_rate || 1;   // Use config or default rate

        const selectedVoiceName = this.$store.state.config.audio_out_voice;
        if (selectedVoiceName && this.voices.length > 0) {
            const voice = this.voices.find(v => v.name === selectedVoiceName);
            if (voice) {
                utterance.voice = voice;
                console.log(`Using voice: ${voice.name} [${voice.lang}]`);
            } else {
                console.warn(`Voice '${selectedVoiceName}' not found. Using default.`);
            }
        } else {
             console.log("Using default browser voice.");
        }

        utterance.onend = () => {
            console.log("Browser TTS finished.");
            this.isSpeaking = false;
             this.$nextTick(() => feather.replace()); // Update icon state
        };

        utterance.onerror = (event) => {
            console.error("Browser TTS error:", event.error);
            this.$refs.toast.showToast(`Browser TTS Error: ${event.error}`, 4, false);
            this.isSpeaking = false;
             this.$nextTick(() => feather.replace()); // Update icon state
        };

        this.speechSynthesis.speak(utterance);
      },
    getCursorPosition() {
      // Ensure the ref exists before accessing selectionStart
      return this.$refs.mdTextarea ? this.$refs.mdTextarea.selectionStart : 0;
    },
    appendToOutput(chunk){
      this.pre_text += chunk;
      this.text = this.pre_text + this.post_text;
      // Auto-scroll textarea if needed (implement separately if desired)
      // Also update cursor position tracker if generating at cursor
      if (this.post_text === "") { // Only update if generating at the end
          const currentPos = this.text.length;
           this.$nextTick(() => {
             // Optional: Keep cursor at the end while generating
             // if (this.$refs.mdTextarea) {
             //    this.$refs.mdTextarea.scrollTop = this.$refs.mdTextarea.scrollHeight; // Scroll to bottom
             //    this.$refs.mdTextarea.selectionStart = this.$refs.mdTextarea.selectionEnd = currentPos;
             // }
             this.cursorPosition = currentPos; // Update logical position
           });
      }
    },
    prepareGeneration(promptText) {
        // Shared logic before emitting generate_text
        // Trim prompt slightly? Optional.
        const finalPrompt = promptText; //.trimEnd();

        // Validate parameters before sending
        const parameters = {
            temperature: Math.max(0.01, parseFloat(this.temperature) || 0.8), // Ensure temp is not 0
            top_k: Math.max(1, parseInt(this.top_k) || 50), // Ensure top_k >= 1
            top_p: Math.max(0.01, Math.min(1.0, parseFloat(this.top_p) || 0.95)), // Ensure 0 < top_p <= 1
            repeat_penalty: parseFloat(this.repeat_penalty) || 1.1,
            repeat_last_n: Math.max(0, parseInt(this.repeat_last_n) || 64), // Ensure >= 0
            seed: parseInt(this.seed) || -1
        };
        const nPredicts = Math.max(1, parseInt(this.n_predicts) || 1024); // Ensure n_predicts >= 1
        const nCrop = parseInt(this.n_crop) || -1; // Allow -1

        console.log("Starting generation with params:", { nPredicts, nCrop, parameters });

        socket.emit('generate_text', {
            prompt: finalPrompt,
            personality: -1, // Use -1 for playground/no specific personality
            n_predicts: nPredicts,
            n_crop: nCrop,
            parameters: parameters
        });
        this.generating = true;
         this.$nextTick(() => feather.replace());
        this.$refs.toast.showToast("Generating...", 2, true);
    },
    generate_in_placeholder(){
        console.log("Attempting generation from placeholder...");
        const placeholder = "@<generation_placeholder>@";
        let index = this.text.indexOf(placeholder);

        if (index < 0) {
            this.$refs.toast.showToast("No '@<generation_placeholder>@' found.", 3, false);
            return;
        }

        // Text before the placeholder becomes the prompt
        this.pre_text = this.text.substring(0, index);
        // Text after the placeholder is kept to append later
        this.post_text = this.text.substring(index + placeholder.length);

        // Remove the placeholder itself for generation display
        this.text = this.pre_text + this.post_text;
        this.cursorPosition = this.pre_text.length; // Set logical cursor where generation will start

        console.log(`Generating from placeholder (prompt length ${this.pre_text.length})`);
        this.prepareGeneration(this.pre_text);
    },
    async tokenize_text(){
      console.log("Tokenizing text...");
      if (!this.text.trim()) {
          this.namedTokens = [];
          this.$refs.toast.showToast("Cannot tokenize empty text.", 3, false);
          return;
      }
      try {
          const response = await axios.post("/lollms_tokenize", {
              prompt: this.text,
              return_named: true // Request named tokens for highlighting
          }, { headers: this.posts_headers });

          console.log("Tokenization response:", response.data);
          this.namedTokens = response.data.tokens || []; // Assuming response structure { tokens: [...] }
          this.$refs.toast.showToast(`Text tokenized (${this.namedTokens.length} tokens).`, 3, true);
      } catch (error) {
          console.error("Tokenization error:", error);
          this.namedTokens = []; // Clear previous tokens on error
          this.$refs.toast.showToast(`Tokenization failed: ${error.response?.data?.error || error.message}`, 4, false);
      }
    },
    generate(){ // Generate from cursor
      console.log("Attempting generation from cursor...");
      this.cursorPosition = this.getCursorPosition(); // Get current cursor position
      this.pre_text = this.text.substring(0, this.cursorPosition);
      this.post_text = this.text.substring(this.cursorPosition);

      console.log(`Generating from cursor (prompt length ${this.pre_text.length}), Cursor: ${this.cursorPosition}`);
      this.prepareGeneration(this.pre_text);
    },
    stopGeneration(){
      console.log("Requesting generation cancellation...");
      socket.emit('cancel_text_generation',{ client_id: this.$store.state.client_id }); // Include client_id if needed by backend
      this.generating = false; // Assume cancellation happens quickly UI-wise
       this.$nextTick(() => feather.replace());
      this.$refs.toast.showToast("Generation cancelled.", 3, true);
    },
    exportText(){
      if (!this.text.trim()) {
          this.$refs.toast.showToast("Nothing to export.", 3, false);
          return;
      }
      const textToExport = this.text;
      const element = document.createElement('a');
      const file = new Blob([textToExport], {type: 'text/plain;charset=utf-8'});
      element.href = URL.createObjectURL(file);
      // Suggest a filename, perhaps based on current date/time or first line?
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      element.download = `playground_export_${timestamp}.txt`;
      document.body.appendChild(element); // Required for Firefox
      element.click();
      document.body.removeChild(element);
      URL.revokeObjectURL(element.href); // Clean up blob URL
      this.$refs.toast.showToast("Text exported.", 3, true);
    },
    importText() {
      const inputFile = document.getElementById("import-input");
      if (!inputFile) {
          console.error("Import input element not found.");
          return;
      }

      // Define the handler function separately to remove it later if needed
      const fileHandler = (event) => {
          if (event.target.files && event.target.files[0]) {
              const reader = new FileReader();
              reader.onload = (e) => {
                  this.text = e.target.result;
                  this.$refs.toast.showToast("Text imported.", 3, true);
                  // Reset state after import
                  this.cursorPosition = this.text.length;
                  this.pre_text = this.text;
                  this.post_text = "";
                  this.namedTokens = []; // Clear tokens
                   this.$nextTick(() => this.adjustTextareaHeight()); // Adjust height
                  // Clean up listener after use
                  // inputFile.removeEventListener("change", fileHandler); // This might cause issues if clicked again quickly
                  inputFile.value = null; // Reset input value
              };
              reader.onerror = (e) => {
                  console.error("File reading error:", e);
                  this.$refs.toast.showToast("Error reading file.", 4, false);
                   inputFile.value = null; // Reset input value
              };
              reader.readAsText(event.target.files[0]);
          } else {
               console.log("No file selected for import.");
               // inputFile.removeEventListener("change", fileHandler);
               inputFile.value = null; // Reset input value
          }
      };

      // Add the event listener (consider if it should be added once or every time)
      // If added every time, ensure previous ones are removed if necessary.
      // For simplicity here, we assume it works okay being added on click.
      inputFile.addEventListener("change", fileHandler, { once: true }); // Use { once: true } to auto-remove after firing

      inputFile.click(); // Trigger the file selection dialog
    },
    setPreset() {
      if (!this.selectedPreset || !this.selectedPreset.content) {
          this.$refs.toast.showToast("No valid preset selected.", 3, false);
          return;
      }
      console.log(`Applying preset: ${this.selectedPreset.name}`);
      this.tab_id = 'source'; // Switch to source tab to see the result

      // Use the replacement function
      replaceInText(this.selectedPreset.content, (processedText) => {
        console.log("Preset content after replacements:", processedText);
        this.text = processedText;
         // Reset state after applying preset
        this.cursorPosition = this.text.length; // Move cursor to end
        this.pre_text = this.text;
        this.post_text = "";
        this.namedTokens = []; // Clear tokens
        this.$refs.toast.showToast(`Preset '${this.selectedPreset.name}' applied.`, 3, true);
        this.$nextTick(() => {
            this.$refs.mdTextarea?.focus(); // Focus textarea after applying
            this.adjustTextareaHeight(); // Adjust height
        });
      });
    },

    async addPreset() {
        const title = await showInputPanel("Enter Preset Name", "My Preset"); // Use the panel for input

        if (!title) {
            this.$refs.toast.showToast("Preset creation cancelled.", 2, true);
            return;
        }

        if (!this.text.trim()) {
            this.$refs.toast.showToast("Cannot save empty text as preset.", 3, false);
            return;
        }

        const newPreset = {
            client_id: this.$store.state.client_id,
            name: title.trim(), // Trim the title
            content: this.text
        };

        // Check if preset name already exists (case-insensitive check)
        if (this.presets.some(p => p.name.toLowerCase() === newPreset.name.toLowerCase())) {
             this.$refs.toast.showToast(`Preset name "${newPreset.name}" already exists.`, 3, false);
             return;
        }

        console.log("Adding new preset:", newPreset);
        this.$refs.toast.showToast(`Adding preset '${newPreset.name}'...`, 2, true);

        axios.post("./add_preset", newPreset).then(response => {
            console.log("Add preset response:", response.data);
            if (response.data.status) {
                this.$refs.toast.showToast(`Preset '${newPreset.name}' added.`, 4, true);
                this.loadPresets(); // Reload presets to include the new one
            } else {
                this.$refs.toast.showToast(`Failed to add preset: ${response.data.error || 'Unknown error'}`, 4, false);
            }
        }).catch(ex => {
            console.error("Error adding preset:", ex);
            this.$refs.toast.showToast(`Error adding preset: ${ex.response?.data?.error || ex.message}`, 4, false);
        });
    },
    removePreset() {
        if (!this.selectedPreset || !this.selectedPreset.name) {
            this.$refs.toast.showToast("No preset selected to remove.", 3, false);
            return;
        }

        const presetName = this.selectedPreset.name;
        // Use a confirmation dialog component if available, otherwise use browser confirm
        if (!confirm(`Are you sure you want to remove the preset "${presetName}"?`)) {
            return;
        }

        console.log(`Removing preset: ${presetName}`);
        this.$refs.toast.showToast(`Removing preset '${presetName}'...`, 2, true);

        axios.post("./delete_preset", {
            client_id: this.$store.state.client_id,
            name: presetName
        }).then(response => {
            console.log("Remove preset response:", response.data);
            if (response.data.status) {
                this.$refs.toast.showToast(`Preset '${presetName}' removed.`, 4, true);
                this.selectedPreset = null; // Clear selection
                this.loadPresets(); // Reload presets list
            } else {
                 this.$refs.toast.showToast(`Failed to remove preset: ${response.data.error || 'Unknown error'}`, 4, false);
            }
        }).catch(ex => {
            console.error("Error removing preset:", ex);
            this.$refs.toast.showToast(`Error removing preset: ${ex.response?.data?.error || ex.message}`, 4, false);
        });
    },
    reloadPresets() {
        console.log("Reloading presets list...");
        this.$refs.toast.showToast("Reloading presets...", 2, true);
        this.loadPresets();
    },
    // Combined Recording and Transcribing (Deaf mode)
    startRecordingAndTranscribing(){
        this.pending = true;
        this.$nextTick(() => feather.replace());
        if(!this.is_deaf_transcribing){
            console.log("Starting deaf transcription mode...");
            axios.get('/start_recording_audio_transcription', { params: { client_id: this.$store.state.client_id } })
            .then(response => {
                console.log("Deaf transcription started:", response.data);
                this.is_deaf_transcribing = true;
                this.pending = false;
                 this.$nextTick(() => feather.replace());
                this.$refs.toast.showToast("Listening for audio-to-audio...", 3, true);
            }).catch(ex=>{
                console.error("Error starting deaf transcription:", ex);
                this.$refs.toast.showToast(`Error starting: ${ex.response?.data?.error || ex.message}`, 4, false);
                this.pending = false;
                 this.$nextTick(() => feather.replace());
            });
        }
        else{
            console.log("Stopping deaf transcription mode...");
            axios.get('/stop_recording_audio_transcription', { params: { client_id: this.$store.state.client_id } })
            .then(response => {
                console.log("Deaf transcription stopped:", response.data);
                this.is_deaf_transcribing = false;
                this.pending = false;
                this.$nextTick(() => feather.replace());
                if (response.data && response.data.text) {
                    this.text = response.data.text; // Set transcribed text
                     this.cursorPosition = this.text.length; // Reset cursor etc.
                     this.pre_text = this.text;
                     this.post_text = "";
                     this.namedTokens = [];
                    this.$refs.toast.showToast("Transcription complete. Synthesizing...", 3, true);
                    this.read(); // Trigger backend TTS with the transcribed text
                } else {
                     this.$refs.toast.showToast(response.data.error || "Transcription failed or returned no text.", 4, false);
                }
            }).catch(ex => {
                console.error("Error stopping deaf transcription:", ex);
                this.$refs.toast.showToast(`Error stopping: ${ex.response?.data?.error || ex.message}`, 4, false);
                this.is_deaf_transcribing = false; // Ensure state reset on error
                this.pending = false;
                 this.$nextTick(() => feather.replace());
            });
        }
    },
    // Separate Recording and Transcription
    startRecording(){
        this.pending = true;
        this.$nextTick(() => feather.replace());
        if(!this.is_recording){
            console.log("Starting audio recording...");
            axios.post('/start_recording', { client_id: this.$store.state.client_id })
            .then(response => {
                console.log("Recording started:", response.data);
                this.is_recording = true;
                this.pending = false;
                this.$nextTick(() => feather.replace());
                this.$refs.toast.showToast("Recording audio...", 3, true);
            }).catch(ex => {
                console.error("Error starting recording:", ex);
                this.$refs.toast.showToast(`Error starting recording: ${ex.response?.data?.error || ex.message}`, 4, false);
                this.pending = false;
                this.$nextTick(() => feather.replace());
            });
        }
        else{
            console.log("Stopping audio recording and transcribing...");
            axios.post('/stop_recording', { client_id: this.$store.state.client_id })
            .then(response => {
                console.log("Recording stopped, transcription result:", response.data);
                this.is_recording = false;
                this.pending = false;
                this.$nextTick(() => feather.replace());
                if (response.data && response.data.text) {
                    // Append transcribed text at cursor position
                    const currentPos = this.getCursorPosition();
                    const textToInsert = response.data.text + " "; // Add space after insertion
                    this.text = this.text.slice(0, currentPos) + textToInsert + this.text.slice(currentPos);
                    this.$refs.toast.showToast("Transcription added.", 3, true);
                    // Update cursor position after insertion
                    this.$nextTick(() => {
                       const newCursorPos = currentPos + textToInsert.length;
                       this.$refs.mdTextarea.focus();
                       this.$refs.mdTextarea.selectionStart = this.$refs.mdTextarea.selectionEnd = newCursorPos;
                       this.cursorPosition = newCursorPos;
                    });
                } else {
                     this.$refs.toast.showToast(response.data.error || "Transcription failed or returned no text.", 4, false);
                }
            }).catch(ex => {
                console.error("Error stopping recording/transcribing:", ex);
                this.$refs.toast.showToast(`Error stopping recording: ${ex.response?.data?.error || ex.message}`, 4, false);
                this.is_recording = false; // Ensure state reset on error
                this.pending = false;
                this.$nextTick(() => feather.replace());
            });
        }
    },
    startSpeechRecognition() { // Browser Speech-to-Text
        if (!('SpeechRecognition' in window || 'webkitSpeechRecognition' in window)) {
            console.error('Browser speech recognition is not supported.');
            this.$refs.toast.showToast("Browser speech recognition not supported.", 4, false);
            return;
        }

        if (this.isListeningToVoice) {
            console.log("Stopping browser speech recognition manually.");
            if (this.recognition) {
                this.recognition.stop(); // This will trigger onend
            }
            // State (isListeningToVoice) is reset in onend
            return;
        }

        try {
            this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            this.recognition.lang = this.$store.state.config.audio_in_language || 'en-US'; // Use config or default
            this.recognition.interimResults = true;
            this.recognition.continuous = true; // Keep listening until stopped

            console.log(`Starting browser speech recognition (lang: ${this.recognition.lang})...`);
            this.isListeningToVoice = true;
             this.$nextTick(() => feather.replace());
            this.$refs.toast.showToast("Listening...", 2, true);

            // Store text before and after cursor for insertion
            const currentPos = this.getCursorPosition();
            this.pre_text = this.text.substring(0, currentPos);
            this.post_text = this.text.substring(currentPos);
            this.generatedSpeechText = ""; // Reset generated text

            this.recognition.onstart = () => {
                console.log("Speech recognition started.");
                // Reset silence timer on start
                clearTimeout(this.silenceTimer);
                this.silenceTimer = setTimeout(() => {
                    if (this.isListeningToVoice && this.recognition) {
                        console.log("Stopping recognition due to silence.");
                        this.recognition.stop();
                    }
                }, this.silenceTimeout);
            };

            this.recognition.onresult = (event) => {
                let interimTranscript = '';
                let finalTranscript = this.generatedSpeechText; // Build upon final from previous events

                for (let i = event.resultIndex; i < event.results.length; ++i) {
                    if (event.results[i].isFinal) {
                         // Add a space after final results for better separation
                        finalTranscript += event.results[i][0].transcript + ' ';
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }

                this.generatedSpeechText = finalTranscript; // Store the final part recognized so far

                // Update the textarea with final + interim text
                const newText = this.pre_text + finalTranscript + interimTranscript + this.post_text;
                const newCursorPos = this.pre_text.length + finalTranscript.length + interimTranscript.length;

                 // Update text reactively
                 this.text = newText;

                 // Update cursor position after DOM update
                 this.$nextTick(()=>{
                    if(this.$refs.mdTextarea){
                        this.$refs.mdTextarea.selectionStart = this.$refs.mdTextarea.selectionEnd = newCursorPos;
                    }
                     this.cursorPosition = newCursorPos; // Update logical position
                 });


                // Reset silence timer on activity
                clearTimeout(this.silenceTimer);
                this.silenceTimer = setTimeout(() => {
                    if (this.isListeningToVoice && this.recognition) {
                        console.log("Stopping recognition due to silence after result.");
                        this.recognition.stop();
                    }
                }, this.silenceTimeout);
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                let errorMsg = event.error;
                if (event.error === 'no-speech') {
                    errorMsg = "No speech detected.";
                } else if (event.error === 'audio-capture') {
                    errorMsg = "Audio capture failed (check microphone permissions).";
                } else if (event.error === 'not-allowed') {
                    errorMsg = "Microphone access denied.";
                }
                 this.$refs.toast.showToast(`Speech Recognition Error: ${errorMsg}`, 4, false);
                this.isListeningToVoice = false; // Reset state on error
                clearTimeout(this.silenceTimer);
                this.$nextTick(() => feather.replace());
                 this.recognition = null; // Clean up
            };

            this.recognition.onend = () => {
                console.log('Speech recognition ended.');
                 if (this.isListeningToVoice) { // Only show toast if it wasn't stopped manually by clicking again
                    this.$refs.toast.showToast("Speech recognition finished.", 3, true);
                 }
                this.isListeningToVoice = false; // Reset state
                // Final update with only the finalized text (with trailing space removed if needed)
                this.text = this.pre_text + this.generatedSpeechText.trimEnd() + this.post_text;
                const finalCursorPos = this.pre_text.length + this.generatedSpeechText.trimEnd().length;
                 // Update cursor position after DOM update
                 this.$nextTick(()=>{
                    if(this.$refs.mdTextarea){
                       this.$refs.mdTextarea.selectionStart = this.$refs.mdTextarea.selectionEnd = finalCursorPos;
                    }
                     this.cursorPosition = finalCursorPos; // Update logical position
                     feather.replace(); // Update icon state
                 });

                clearTimeout(this.silenceTimer);
                this.recognition = null; // Clean up instance
            };

            this.recognition.start();

        } catch (error) {
            console.error("Failed to initialize speech recognition:", error);
            this.$refs.toast.showToast("Failed to start speech recognition.", 4, false);
            this.isListeningToVoice = false;
             this.$nextTick(() => feather.replace());
        }
    },
  },
   watch: {
     // Watch for changes in text and adjust textarea height (optional)
     // text(newVal) {
     //   this.$nextTick(() => {
     //     this.adjustTextareaHeight();
     //   });
     // }
     'tab_id'(newVal) {
         // When switching tabs, ensure feather icons are re-rendered if needed,
         // especially if content within tabs uses them dynamically.
         this.$nextTick(() => {
             feather.replace();
             if (newVal === 'source') {
                this.adjustTextareaHeight(); // Re-adjust height when switching to source
             }
         });
     },
     'showSettingsModal'(newVal) {
        this.$nextTick(() => {
             feather.replace(); // Re-render icons when settings modal opens/closes
        });
     }
  }
};
</script>

<!-- No <style scoped> needed as all styles are from the theme -->