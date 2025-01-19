<template>
  <div class="container w-full background-color shadow-lg overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
    <div class="container flex flex-row m-2 w-full ">
      <div class="flex-grow w-full m-2">
        <div class="flex panels-color gap-3 flex-1 items-center flex-grow flex-row rounded-md border-2 border-blue-300 m-2 p-4">
          <div class="flex items-center space-x-2">
            <ChatBarButton v-show="!generating" @click="generate" title="Generate from the current cursor position">
      <template #icon>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z" />
        </svg>
      </template>
    </ChatBarButton>

    <ChatBarButton v-show="!generating" @click="generate_in_placeholder" title="Generate from the next placeholder">
      <template #icon>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
        </svg>
      </template>
    </ChatBarButton>

    <ChatBarButton v-show="!generating" @click="tokenize_text" title="Tokenize the text">
      <template #icon>
        <img :src="tokenize_icon" alt="Tokenize" class="h-5 w-5" />
      </template>
    </ChatBarButton>

    <span class="w-80"></span>

    <ChatBarButton v-show="generating" @click="stopGeneration" title="Stop generation">
      <template #icon>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
        </svg>
      </template>
    </ChatBarButton>

    <ChatBarButton @click="startSpeechRecognition" :class="{ 'text-red-500': isListeningToVoice }" title="Dictate (using your browser's transcription)">
      <template #icon>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      </template>
    </ChatBarButton>

    <ChatBarButton @click="speak" :class="{ 'text-red-500': isTalking }" title="Convert text to audio (not saved, uses your browser's TTS service)">
      <template #icon>
        🪶
      </template>
    </ChatBarButton>

    <ChatBarButton @click="triggerFileUpload" title="Upload a voice">
      <template #icon>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      </template>
    </ChatBarButton>

    <ChatBarButton @click="startRecordingAndTranscribing" :class="{ 'text-green-500': isLesteningToVoice }" title="Start audio to audio">
      <template #icon>
        <img v-if="!pending" :src="is_deaf_transcribing ? deaf_on : deaf_off" alt="Deaf" class="h-5 w-5" />
        <img v-else :src="loading_icon" alt="Loading" class="h-5 w-5" />
      </template>
    </ChatBarButton>

    <ChatBarButton @click="startRecording" :class="{ 'text-green-500': isLesteningToVoice }" title="Start audio recording">
      <template #icon>
        <img v-if="!pending" :src="is_recording ? rec_on : rec_off" alt="Record" class="h-5 w-5" />
        <img v-else :src="loading_icon" alt="Loading" class="h-5 w-5" />
      </template>
    </ChatBarButton>

    <ChatBarButton v-if="!isSynthesizingVoice" @click="read" title= "Generate audio from text">
      <template #icon>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
        </svg>
      </template>
    </ChatBarButton>

    <div v-else class="w-6 h-6">
      <svg class="animate-spin h-5 w-5 text-secondary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
    </div>

    <ChatBarButton v-show="!generating" @click="exportText" title= "Export text">
      <template #icon>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
      </template>
    </ChatBarButton>

    <ChatBarButton v-show="!generating" @click="importText" title="Import text">
      <template #icon>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
        </svg>
      </template>
    </ChatBarButton>

    <ChatBarButton @click="showSettings = !showSettings" title="Settings">
      <template #icon>
        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
      </template>
    </ChatBarButton>
  </div>

  <input type="file" ref="fileInput" @change="handleFileUpload" style="display: none;" accept=".wav" />
        <div class="flex gap-3 flex-1 items-center flex-grow justify-end">   
            <button 
            class="border-2 text-blue-600 dark:text-white border-blue-300 p-2 rounded shadow-lg hover:border-gray-600 dark:link-item-dark cursor-pointer"
            @click="tab_id='source'" :class="{'bg-blue-200 dark:bg-blue-500':tab_id=='source'}">
              Source
            </button>
            <button 
            class="border-2 text-blue-600 dark:text-white border-blue-300 p-2 rounded shadow-lg hover:border-gray-600 dark:link-item-dark cursor-pointer"
            @click="tab_id='render'" :class="{'bg-blue-200 dark:bg-blue-500':tab_id=='render'}">
              Render
            </button>
            </div>
            <input type="file" id="import-input" class="hidden">
          </div>
          <div class="flex-grow m-2 p-2 border panels-color border-blue-300 rounded-md" :class="{ 'border-red-500': generating }">
            <div  v-if="tab_id === 'source'">
              <DropdownMenu title="Add Block">
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
                  <DropdownSubmenu title="Web Technologies" icon="web">
                      <ToolbarButton @click.stop="addBlock('html')" title="HTML" icon="html5" />
                      <ToolbarButton @click.stop="addBlock('css')" title="CSS" icon="css3" />
                      <ToolbarButton @click.stop="addBlock('vue')" title="Vue.js" icon="vuejs" />
                      <ToolbarButton @click.stop="addBlock('react')" title="React" icon="react" />
                      <ToolbarButton @click.stop="addBlock('angular')" title="Angular" icon="angular" />
                  </DropdownSubmenu>

                  <!-- Markup and Data Formats -->
                  <DropdownSubmenu title="Markup and Data" icon="file-code">
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
                  <DropdownSubmenu title="Diagramming" icon="sitemap">
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
              <ToolbarButton @click.stop="copyContentToClipboard()" title="Copy message to clipboard" icon="copy" />
              <textarea ref="mdTextarea" @keydown.tab.prevent="insertTab"
                class="block min-h-500 p-2.5 w-full text-gray-900 bg-gray-50 rounded-lg border border-gray-300 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500 overflow-y-scroll flex flex-col shadow-lg p-10 pt-0 overflow-y-scroll dark:bg-bg-dark scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary"
                :rows="4" 
                :style="{ minHeight: mdRenderHeight + `px` }" placeholder="Enter message here..."
                v-model="text"
                @click.prevent="mdTextarea_clicked"
                @change.prevent="mdTextarea_changed"
                >
                </textarea>

<span>Cursor position {{ cursorPosition }}</span>
            </div>
            <audio controls v-if="audio_url!=null"  :key="audio_url">
                <source :src="audio_url" type="audio/wav"  ref="audio_player">
                Your browser does not support the audio element.
            </audio>  
            <tokens-hilighter :namedTokens="namedTokens">

            </tokens-hilighter>
            <div  v-if="tab_id === 'render'">
              <MarkdownRenderer ref="mdRender" :client_id="this.$store.state.client_id" :message_id="0" :discussion_id="0" :markdown-text="text" class="mt-4 p-2 rounded shadow-lg dark:bg-bg-dark">
              </MarkdownRenderer>          
            </div>
          </div>
      </div>
      <div v-if="showSettings" class="settings scrollbar bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">Settings</h2>
        <Card title="Model"  class="slider-container ml-0 mr-0"  :isHorizontal="false" :disableHoverAnimation="true" :disableFocus="true">
          <select v-model="this.$store.state.selectedModel" @change="setModel" class="bg-white dark:bg-black m-0 border-2 rounded-md shadow-sm w-full">
            <option v-for="model in models" :key="model" :value="model">
              {{ model }}
            </option>
          </select>
          <div v-if="selecting_model" title="Selecting model" class="flex flex-row flex-grow justify-end">
              <!-- SPINNER -->
              <div role="status">
                  <svg aria-hidden="true" class="w-6 h-6   animate-spin  fill-secondary" viewBox="0 0 100 101"
                      fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path
                          d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                          fill="currentColor" />
                      <path
                          d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                          fill="currentFill" />
                  </svg>
                  <span class="sr-only">Selecting model...</span>
              </div>
          </div>

</Card>
        <Card  title="Presets" class="slider-container ml-0 mr-0" :is_subcard="true" :isHorizontal="false" :disableHoverAnimation="true" :disableFocus="true">
          <select v-model="selectedPreset" class="bg-white dark:bg-black mb-2 border-2 rounded-md shadow-sm w-full">
            <option v-for="preset in presets" :key="preset" :value="preset">
              {{ preset.name }}
            </option>
          </select>
          <br>
          <button class="w-6 ml-2 hover:text-secondary duration-75 active:scale-90 cursor-pointer" @click="setPreset"  title="Use preset"><i data-feather="check"></i></button>
          <button class="w-6 ml-2 hover:text-secondary duration-75 active:scale-90 cursor-pointer" @click="addPreset"  title="Add this text as a preset"><i data-feather="plus"></i></button>
          <button class="w-6 ml-2 hover:text-secondary duration-75 active:scale-90 cursor-pointer" @click="removePreset"  title="Remove preset"><i data-feather="x"></i></button>
          <button class="w-6 ml-2 hover:text-secondary duration-75 active:scale-90 cursor-pointer" @click="reloadPresets"  title="Reload presets list"><i data-feather="refresh-ccw"></i></button>
          </Card>
          <Card  title="Generation params" class="slider-container ml-0 mr-0" :is_subcard="true" :isHorizontal="false" :disableHoverAnimation="true" :disableFocus="true">

<div class="slider-container ml-2 mr-2">
              <h3 class="text-gray-600">Temperature</h3>
              <input type="range" v-model="temperature" min="0" max="5" step="0.1" class="w-full">
              <span class="slider-value text-gray-500">Current value: {{ temperature }}</span>
            </div>
            <div class="slider-container ml-2 mr-2">
              <h3 class="text-gray-600">Top K</h3>
              <input type="range" v-model="top_k" min="1" max="100" step="1" class="w-full">
              <span class="slider-value text-gray-500">Current value: {{ top_k }}</span>
            </div>
            <div class="slider-container ml-2 mr-2">
              <h3 class="text-gray-600">Top P</h3>
              <input type="range" v-model="top_p" min="0" max="1" step="0.1" class="w-full">
              <span class="slider-value text-gray-500">Current value: {{ top_p }}</span>
            </div>
            <div class="slider-container ml-2 mr-2">
              <h3 class="text-gray-600">Repeat Penalty</h3>
              <input type="range" v-model="repeat_penalty" min="0" max="5" step="0.1" class="bg-white dark:bg-black m-0 border-2 rounded-md shadow-sm w-full">
              <span class="slider-value text-gray-500">Current value: {{ repeat_penalty }}</span>
            </div>
            <div class="slider-container ml-2 mr-2">
              <h3 class="text-gray-600">Repeat Last N</h3>
              <input type="range" v-model="repeat_last_n" min="0" max="100" step="1" class="bg-white dark:bg-black m-0 border-2 rounded-md shadow-sm w-full">
              <span class="slider-value text-gray-500">Current value: {{ repeat_last_n }}</span>
            </div>
            <div class="slider-container ml-2 mr-2">
              <h3 class="text-gray-600">Number of tokens to crop the text to</h3>
              <input type="number" v-model="n_crop" class="bg-white dark:bg-black m-0 border-2 rounded-md shadow-sm w-full">
              <span class="slider-value text-gray-500">Current value: {{ n_crop }}</span>
            </div>          
            <div class="slider-container ml-2 mr-2">
              <h3 class="text-gray-600">Number of tokens to generate</h3>
              <input type="number" v-model="n_predicts" class="bg-white dark:bg-black m-0 border-2 rounded-md shadow-sm w-full">
              <span class="slider-value text-gray-500">Current value: {{ n_predicts }}</span>
            </div>
            <div class="slider-container ml-2 mr-2">
              <h3 class="text-gray-600">Seed</h3>
              <input type="number" v-model="seed" class="bg-white dark:bg-black m-0 border-2 rounded-md shadow-sm w-full">
              <span class="slider-value text-gray-500">Current value: {{ seed }}</span>
            </div>
          </Card>
        </div>
    </div>
  </div>
  <Toast ref="toast"/>
</template>

<script>
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
        panel.className = "fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50";
        if(options.length===0){
          panel.innerHTML = `
            <div class="bg-white p-6 rounded-md shadow-md w-80">
                <h2 class="text-lg font-semibold mb-3">${name}</h2>
                <textarea id="replacementInput" class="w-full h-32 border rounded p-2 mb-3">${default_value}</textarea>
                <div class="flex justify-end">
                    <button id="cancelButton" class="mr-2 px-4 py-2 border rounded">Cancel</button>
                    <button id="okButton" class="px-4 py-2 bg-blue-500 text-white rounded">OK</button>
                </div>
            </div>
        `;
        }
        else{
          panel.innerHTML = `
            <div class="bg-white p-6 rounded-md shadow-md w-80">
                <h2 class="text-lg font-semibold mb-3">${name}</h2>
                <select id="options_selector" class="form-control w-full h-25 border rounded p-2 mb-3">
                  ${options.map(option => `<option value="${option}">${option}</option>`)}
                </select>
                <div class="flex justify-end">
                    <button id="cancelButton" class="mr-2 px-4 py-2 border rounded">Cancel</button>
                    <button id="okButton" class="px-4 py-2 bg-blue-500 text-white rounded">OK</button>
                </div>
            </div>
        `;          
        }


        document.body.appendChild(panel);

        const cancelButton = panel.querySelector("#cancelButton");
        const okButton = panel.querySelector("#okButton");

        cancelButton.addEventListener("click", () => {
            document.body.removeChild(panel);
            resolve(null);
        });

        okButton.addEventListener("click", () => {
            if(options.length===0){
              const input = panel.querySelector("#replacementInput");
              const value = input.value.trim();
              document.body.removeChild(panel);
              resolve(value);
            }
            else{
              const input = panel.querySelector("#options_selector");
              const value = input.value.trim();
              document.body.removeChild(panel);
              resolve(value);
            }
        });
    });
}

function replaceInText(text, callback) {
  console.log(text)
    let replacementDict = {};
    let delimiterRegex = /@<([^>]+)>@/g;
    let matches = [];
    let match;

    while ((match = delimiterRegex.exec(text)) !== null) {
      matches.push("@<"+match[1]+">@"); // The captured group is at index 1
    }
    console.log("matches")
    console.log(matches)
    matches =  [...new Set(matches)]

    async function handleReplacement(match) {
        console.log(match)
        let placeholder = match.toLowerCase().substring(2,match.length-2);
        if (placeholder !== "generation_placeholder") {
          if (placeholder.includes(":")) {
            // Special key words
            let key_words_dict={
              "all_language_options":"english:french:german:chinese:japanese:spanish:italian:russian:portuguese:swedish:danish:dutch:norwegian:slovak:czech:hungarian:polish:ukrainian:bulgarian:latvian:lithuanian:estonian:maltese:irish:galician:basque:welsh:breton:georgian:turkmen:kazakh:uzbek:tajik:afghan:sri-lankan:filipino:vietnamese:lao:cambodian:thai:burmese:kenyan:botswanan:zimbabwean:malawian:mozambican:angolan:namibian:south-african:madagascan:seychellois:mauritian:haitian:peruvian:ecuadorian:bolivian:paraguayan:chilean:argentinean:uruguayan:brazilian:colombian:venezuelan:puerto-rican:cuban:dominican:honduran:nicaraguan:salvadorean:guatemalan:el-salvadoran:belizean:panamanian:costa-rican:antiguan:barbudan:dominica's:grenada's:st-lucia's:st-vincent's:gibraltarian:faroe-islander:greenlandic:icelandic:jamaican:trinidadian:tobagonian:barbadian:anguillan:british-virgin-islander:us-virgin-islander:turkish:israeli:palestinian:lebanese:egyptian:libyan:tunisian:algerian:moroccan:bahraini:kuwaiti:saudi-arabian:yemeni:omani:irani:iraqi:afghanistan's:pakistani:indian:nepalese:sri-lankan:maldivan:burmese:thai:lao:vietnamese:kampuchean:malaysian:bruneian:indonesian:australian:new-zealanders:fijians:tongans:samoans:vanuatuans:wallisians:kiribatians:tuvaluans:solomon-islanders:marshallese:micronesians:hawaiians",
              "all_programming_language_options":"python:c:c++:java:javascript:php:ruby:go:swift:kotlin:rust:haskell:erlang:lisp:scheme:prolog:cobol:fortran:pascal:delphi:d:eiffel:h:basic:visual_basic:smalltalk:objective-c:html5:node.js:vue.js:svelte:react:angular:ember:clipper:stex:arduino:brainfuck:r:assembly:mason:lepton:seacat:bbc_microbit:raspberry_pi_gpio:raspberry_pi_spi:raspberry_pi_i2c:raspberry_pi_uart:raspberry_pi_adc:raspberry_pi_ddio"
            }
            Object.entries(key_words_dict).forEach(([key, value]) => {
              console.log(`Key: ${key}, Value: ${value}`);
              function escapeRegExp(string) {
                  return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // Escape special characters
              }

              const escapedKey = escapeRegExp(key);
              const regex = new RegExp(escapedKey, 'g');
              placeholder = placeholder.replace(regex, value);
              //text = text.replace(new RegExp(key, 'g'), value);
            });

            let splitResult = placeholder.split(":");
            let name = splitResult[0];
            let defaultValue = splitResult[1] || "";
            let options = [];
            if (splitResult.length>2) {
              options = splitResult.slice(1);
            }
            let replacement = await showInputPanel(name, defaultValue, options);
            if (replacement !== null) {
                replacementDict[match] = replacement;
            }
          }
          else{
            let replacement = await showInputPanel(placeholder);
            if (replacement !== null) {
                replacementDict[match] = replacement;
            }
          }
        }else{
          //var result = confirm("generation placeholder found. Do you want to generate?\nIf you skip generation, you still can generate manually after wards");
        }
    }
    let promiseChain = Promise.resolve();

    matches.forEach(match => {
      promiseChain = promiseChain.then(() => {
        return handleReplacement(match);
      }).then(result => {
        console.log(result);
      });
    });
    promiseChain.then(() => {
      Object.entries(replacementDict).forEach(([key, value]) => {
        console.log(`Key: ${key}, Value: ${value}`);
        function escapeRegExp(string) {
            return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // Escape special characters
        }

        const escapedKey = escapeRegExp(key);
        const regex = new RegExp(escapedKey, 'g');
        text = text.replace(regex, value);
        //text = text.replace(new RegExp(key, 'g'), value);
      });
      callback(text); // Call the callback after all matches are processed
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
      showSettings: false,
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
      mdRenderHeight:300,
      selecting_model:false,
      tab_id:"source",
      generating:false,
      isSpeaking:false,
      voices: [],    
      isLesteningToVoice:false,
      presets:[],
      selectedPreset: '',
      cursorPosition:0,
      namedTokens:[],
      text:"",
      pre_text:"",
      post_text:"",
      temperature: 0.1,
      top_k: 50,
      top_p: 0.9,
      repeat_penalty: 1.3,
      repeat_last_n: 50,
      n_crop: -1,
      n_predicts: 2000,
      seed: -1,
      silenceTimeout:5000
    };
  },

  components:{    
    Toast,
    MarkdownRenderer,
    ClipBoardTextInput,
    TokensHilighter,
    ChatBarButton,
    Card,
    ToolbarButton,
    DropdownMenu
  },
  mounted() {
    axios.get('./get_presets').then(response => {
          console.log(response.data)
          this.presets=response.data
          this.selectedPreset = this.presets[0]
        }).catch(ex=>{
          this.$refs.toast.showToast(`Error: ${ex}`,4,false)
        });
        // Event handler for receiving generated text chunks
        socket.on('text_chunk', data => {
            this.appendToOutput(data.chunk);
        });

        // Event handler for receiving generated text chunks
        socket.on('text_generated', data => {
            // Toggle button visibility
            this.generating=false;
        });

        socket.on('generation_error', data => {
            console.log('generation_error:', data);
            this.$refs.toast.showToast(`Error: ${data}`,4,false)
            // Toggle button visibility
            this.generating=false;
        });

        

        // Event handler for successful connection
        socket.on('connect', () => {
            console.log('Connected to LoLLMs server');
            this.$store.state.isConnected=true;
            this.generating=false
        });

        // Event handler for error during text generation
        socket.on('buzzy', error => {
            console.error('Server is busy. Wait for your turn', error);
            this.$refs.toast.showToast(`Error: ${error.message}`,4,false)
            // Toggle button visibility
            this.generating=false
        });

        // Event handler for error during text generation
        socket.on('generation_canceled', error => {
            // Toggle button visibility
            this.generating=false
            console.log("Generation canceled OK")
        });



      //console.log('chatbox mnt',this.$refs)
      this.$nextTick(() => {
          feather.replace();
      });  
      
    // Speach synthesis
    // Check if speech synthesis is supported by the browser
    if ('speechSynthesis' in window) {
    this.speechSynthesis = window.speechSynthesis;

    // Load the available voices
    this.voices = this.speechSynthesis.getVoices();

    // Make sure the voices are loaded before starting speech synthesis
    if (this.voices.length === 0) {
        this.speechSynthesis.addEventListener('voiceschanged', this.onVoicesChanged);
    } else {
    }
    } else {
    console.error('Speech synthesis is not supported in this browser.');
    }


  },
  created(){

        
  },
  watch:{
    audio_url(newUrl) {
        if (newUrl) {
            console.log("Audio changed url to :",newUrl)
            this.$refs.audio_player.src = newUrl;
        }
    },
  },
  computed: {
    selectedModel: {
      get(){
        return this.$store.state.selectedModel;
      }
    },
    models: {
      get(){
        return this.$store.state.modelsArr;
      }
    },
    isTalking :{
        get(){
            return this.isSpeaking
        }
    },
  },
  methods:{
    triggerFileUpload() {
      this.$refs.fileInput.click();
    },
    handleFileUpload(event) {
      this.file = this.$refs.fileInput.files[0];
      this.buttonText = this.file.name;
      this.uploadFile()
    },
    uploadFile() {
      console.log("sending file")
      const formData = new FormData();
      formData.append('file', this.file);

      axios.post('/upload_voice/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      .then(response => {
        console.log(response);
        this.buttonText = 'Upload a voice';
      })
      .catch(error => {
        console.error(error);
      });
    },
    addBlock(bloc_name){
            let ss =this.$refs.mdTextarea.selectionStart
            let se =this.$refs.mdTextarea.selectionEnd
            if(ss==se){
                if(speechSynthesis==0 || this.text[ss-1]=="\n"){
                    this.text = this.text.slice(0, ss) + "```"+bloc_name+"\n\n```\n" + this.text.slice(ss)
                    ss = ss+4+bloc_name.length
                }
                else{
                    this.text = this.text.slice(0, ss) + "\n```"+bloc_name+"\n\n```\n" + this.text.slice(ss)
                    ss = ss+3+bloc_name.length
                }
            }
            else{
                if(speechSynthesis==0 || this.text[ss-1]=="\n"){
                    this.text = this.text.slice(0, ss) + "```"+bloc_name+"\n"+this.text.slice(ss, se)+"\n```\n" + this.text.slice(se)
                    ss = ss+4+bloc_name.length
                }
                else{
                    this.text = this.text.slice(0, ss) + "\n```"+bloc_name+"\n"+this.text.slice(ss, se)+"\n```\n" + this.text.slice(se)
                    ss = ss+3+bloc_name.length
                }
            }

            this.$refs.mdTextarea.focus();
            this.$refs.mdTextarea.selectionStart = this.$refs.mdTextarea.selectionEnd = p;
    },

    insertTab(event) {
            const textarea = event.target;
            const start = textarea.selectionStart;
            const end = textarea.selectionEnd;
    
            const textBefore = textarea.value.substring(0, start);
            const textAfter = textarea.value.substring(end);
    
            // Insert a tab character (or spaces if you prefer) at the cursor position
            const newText = textBefore + '    ' + textAfter;
    
            // Update the textarea content and cursor position
            this.text = newText;
            this.$nextTick(() => {
            textarea.selectionStart = textarea.selectionEnd = start + 4;
            });
    
            event.preventDefault();
        },    
    mdTextarea_changed(){
      console.log("mdTextarea_changed")
      this.cursorPosition = this.$refs.mdTextarea.selectionStart;
    },      
    mdTextarea_clicked(){
      console.log(`mdTextarea_clicked: ${this.$refs.mdTextarea.selectionStart}`)
      this.cursorPosition = this.$refs.mdTextarea.selectionStart;
    },    
    setModel(){
      this.selecting_model=true
      axios.post("/update_setting", {        
                client_id: this.$store.state.client_id,        
                setting_name: "model_name",
                setting_value: this.selectedModel
              }).then((response) => {
          console.log(response);
          if(response.status){
            this.$refs.toast.showToast(`Model changed to ${this.selectedModel}`,4,true)
          }
          this.selecting_model=false
        }).catch(err=>{
          this.$refs.toast.showToast(`Error ${err}`,4,true)
          this.selecting_model=false
        });
      
    },
    onVoicesChanged() {
      // This event will be triggered when the voices are loaded
      this.voices = this.speechSynthesis.getVoices();
      },
    read(){
        console.log("READING...")
        this.isSynthesizingVoice=true
        let ss =this.$refs.mdTextarea.selectionStart
        let se =this.$refs.mdTextarea.selectionEnd

        let text = this.text
        if(ss!=se){
          text = text.slice(ss,se)
        }
        axios.post("./text2Wave",{client_id:this.$store.state.client_id, text:text}).then(response => {
          console.log(response.data.url)
          let url = response.data.url
          this.audio_url = url
          this.isSynthesizingVoice=false
          nextTick(() => {
              feather.replace()
          })
        }).catch(ex=>{
          this.$refs.toast.showToast(`Error: ${ex}`,4,false)
          this.isSynthesizingVoice=false
          nextTick(() => {
              feather.replace()
          })
        });
      },
      speak() {
          if (this.msg) {
              this.speechSynthesis.cancel();
              this.msg = null;
              this.isSpeaking = false;
              return;
          }
          let startIndex =0;
          // Set isSpeaking to true before starting synthesis
          console.log("voice on")
          this.isSpeaking = true;

          const chunkSize = 200; // You can adjust the chunk size as needed

          // Create a new SpeechSynthesisUtterance instance
          this.msg = new SpeechSynthesisUtterance();
          this.msg.pitch = this.$store.state.config.audio_pitch;

          // Optionally, set the voice and other parameters as before
          if (this.voices.length > 0) {
              this.msg.voice = this.voices.filter(voice => voice.name === this.$store.state.config.audio_out_voice)[0];
          }


          // Function to find the index of the last sentence that fits within the chunk size
          const findLastSentenceIndex = (startIndex) => {
              let txt = this.text.substring(startIndex, startIndex+chunkSize)
              // Define an array of characters that represent end of sentence markers.
              const endOfSentenceMarkers = ['.', '!', '?', '\n'];

              // Initialize a variable to store the index of the last end of sentence marker.
              let lastIndex = -1;

              // Iterate through the end of sentence markers and find the last occurrence in the txt string.
              endOfSentenceMarkers.forEach(marker => {
              const markerIndex = txt.lastIndexOf(marker);
              if (markerIndex > lastIndex) {
                  lastIndex = markerIndex;
              }
              });
              if(lastIndex==-1){lastIndex=txt.length}
              console.log(lastIndex)
              return lastIndex+startIndex+1;
          };

          // Function to speak a chunk of text
          const speakChunk = () => {
              const endIndex = findLastSentenceIndex(startIndex);
              const chunk = this.text.substring(startIndex, endIndex);
              this.msg.text = chunk;
              startIndex = endIndex + 1;
              this.msg.onend = (event) => {
                  if (startIndex < this.text.length-2) {
                      // Use setTimeout to add a brief delay before speaking the next chunk
                      setTimeout(() => {
                          speakChunk();
                      }, 1); // Adjust the delay as needed
                  } else {
                      this.isSpeaking = false;
                      console.log("voice off :",this.text.length,"  ",endIndex)
                  }
              };
              this.speechSynthesis.speak(this.msg);
          };

          // Speak the first chunk
          speakChunk();
      },    
    getCursorPosition() {
      return this.$refs.mdTextarea.selectionStart;
    },    
    appendToOutput(chunk){
      this.pre_text += chunk
      this.text = this.pre_text + this.post_text
    },
    generate_in_placeholder(){
      console.log("Finding cursor position")
      // Find next placeholder @<generation_placeholder>@
      let index =  this.text.indexOf("@<generation_placeholder>@")
      if(index<0){
        this.$refs.toast.showToast(`No generation placeholder found`,4,false)
        return
      }
      this.text = this.text.substring(0,index) + this.text.substring(index+"@<generation_placeholder>@".length,this.text.length)
      this.pre_text = this.text.substring(0,index)
      this.post_text = this.text.substring(index, this.text.length)
      var prompt = this.text.substring(0, index)
      console.log(prompt)
      // Trigger the 'generate_text' event with the prompt
      socket.emit('generate_text', { prompt: prompt, personality: -1, n_predicts: this.n_predicts , n_crop: this.n_crop,
      parameters: {
          temperature: this.temperature,
          top_k: this.top_k,
          top_p: this.top_p,
          repeat_penalty: this.repeat_penalty, // Update with desired repeat penalty value
          repeat_last_n: this.repeat_last_n, // Update with desired repeat_last_n value
          seed: parseInt(this.seed)
      }});

      // Toggle button visibility
      this.generating=true
    },
    async tokenize_text(){
      const output = await axios.post("/lollms_tokenize", {"prompt": this.text, "return_named": true}, {headers: this.posts_headers});
      console.log(output.data)
      this.namedTokens = output.data
    },
    generate(){
      console.log("Finding cursor position")
      this.pre_text = this.text.substring(0,this.getCursorPosition())
      this.post_text = this.text.substring(this.getCursorPosition(), this.text.length)
      var prompt = this.text.substring(0,this.getCursorPosition())
      console.log(this.text)
      console.log(`cursor position :${this.getCursorPosition()}`)
      console.log(`pretext:${this.pre_text}`)
      console.log(`post_text:${this.post_text}`)
      console.log(`prompt:${prompt}`)
      // Trigger the 'generate_text' event with the prompt
      socket.emit('generate_text', { prompt: prompt, personality: -1, n_predicts: this.n_predicts , n_crop: this.n_crop,
      parameters: {
          temperature: this.temperature,
          top_k: this.top_k,
          top_p: this.top_p,
          repeat_penalty: this.repeat_penalty, // Update with desired repeat penalty value
          repeat_last_n: this.repeat_last_n, // Update with desired repeat_last_n value
          seed: parseInt(this.seed)
      }});

      // Toggle button visibility
      this.generating=true
    },
    stopGeneration(){
      // Trigger the 'cancel_generation' event
      socket.emit('cancel_text_generation',{});
    },
    exportText(){
      const textToExport = this.text;
      const element = document.createElement('a');
      const file = new Blob([textToExport], {type: 'text/plain'});
      element.href = URL.createObjectURL(file);
      element.download = 'exported_text.txt';
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);      
    },
    importText() {
      const inputFile = document.getElementById("import-input");
      if (!inputFile) return; // If the element doesn't exist, do nothing
      inputFile.addEventListener("change", event => {
        if (event.target.files && event.target.files[0]) {
          const reader = new FileReader();
          reader.onload = () => {
            this.text = reader.result;
          };
          reader.readAsText(event.target.files[0]);
        } else {
          alert("Please select a file.");
        }
      });
      inputFile.click();
    },
    setPreset() {
      console.log("Setting preset")
      console.log(this.selectedPreset)
      this.tab_id='render'
      this.text = replaceInText(this.selectedPreset.content, (text)=>{
        console.log("Done")
        console.log(text);
        this.text= text
      });
    },
    
    addPreset() {
      let title = prompt('Enter the title of the preset:');
      this.presets[title] =  {
                                client_id:this.$store.state.client_id,
                                name:title,
                                content:this.text
                             }
      axios.post("./add_preset",this.presets[title]).then(response => {
          console.log(response.data)
        }).catch(ex=>{
          this.$refs.toast.showToast(`Error: ${ex}`,4,false)
        });
    },
    removePreset() {
      if (this.selectedPreset) {
        delete this.presets[this.selectedPreset.name];
      }
    },
    reloadPresets() {
      axios.get('./get_presets').then(response => {
          console.log(response.data)
          this.presets=response.data
          this.selectedPreset = this.presets[0]
        }).catch(ex=>{
          this.$refs.toast.showToast(`Error: ${ex}`,4,false)
        });
    },
    startRecording(){
      this.pending = true;
      if(!this.is_recording){
        axios.post('/start_recording', {client_id:this.$store.state.client_id}).then(response => {
          this.is_recording = true;
          this.pending = false;
          console.log(response.data)
        }).catch(ex=>{
          this.$refs.toast.showToast(`Error: ${ex}`,4,false)
        });
      }
      else{
        axios.post('/stop_recording', {client_id:this.$store.state.client_id}).then(response => {
          this.is_recording = false;
          this.pending = false;
          console.log(response)
          this.text += response.data
          console.log("text")
          console.log(this.text)

          console.log(response.data)
          this.presets=response.data
          this.selectedPreset = this.presets[0]
        }).catch(ex=>{
          this.$refs.toast.showToast(`Error: ${ex}`,4,false)
        });

      }

    },
    startRecordingAndTranscribing(){
      this.pending = true;
      if(!this.is_deaf_transcribing){
        axios.get('/start_recording').then(response => {
          this.is_deaf_transcribing = true;
          this.pending = false;
        }).catch(ex=>{
          this.$refs.toast.showToast(`Error: ${ex}`,4,false)
        });
      }
      else{
        axios.get('/stop_recording').then(response => {
          this.is_deaf_transcribing = false;
          this.pending = false;
          this.text = response.data.text
          this.read()
        }).catch(ex=>{
          this.$refs.toast.showToast(`Error: ${ex}`,4,false)
        });

      }

    },
    startSpeechRecognition() {
        if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
            this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            this.recognition.lang = this.$store.state.config.audio_in_language; // Set the language, adjust as needed
            this.recognition.interimResults = true; // Enable interim results to get real-time updates

            this.recognition.onstart = () => {
              this.isLesteningToVoice = true;
              this.silenceTimer = setTimeout(() => {
                  this.recognition.stop();
              }, this.silenceTimeout); // Set the silence timeout to stop recognition
            };

            this.pre_text = this.text.substring(0,this.getCursorPosition())
            this.post_text = this.text.substring(this.getCursorPosition(), this.text.length)

            this.recognition.onresult = (event) => {
              this.generated = '';

              for (let i = event.resultIndex; i < event.results.length; i++) {
                this.generated += event.results[i][0].transcript;
              }
              this.text = this.pre_text + this.generated + this.post_text; // Update the textarea with the real-time recognized words
              this.cursorPosition = this.pre_text.length + this.generated.length;
              clearTimeout(this.silenceTimer); // Clear the silence timeout on every recognized result
              this.silenceTimer = setTimeout(() => {
                  this.recognition.stop();
              }, this.silenceTimeout); // Set a new silence timeout after every recognized result
            };

            this.recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            this.isLesteningToVoice = false;
            clearTimeout(this.silenceTimer); // Clear the silence timeout on error
            };

            this.recognition.onend = () => {
              console.log('Speech recognition ended.');
              this.isLesteningToVoice = false;
              this.pre_text = this.pre_text + this.generated;
              this.cursorPosition = this.pre_text.length;
              clearTimeout(this.silenceTimer); // Clear the silence timeout when recognition ends normally
            };

            this.recognition.start();
        } else {
            console.error('Speech recognition is not supported in this browser.');
        }
        },
  }
};
</script>

<style>
  .slider-value {
      display: inline-block;
      margin-left: 10px;
      color: #6b7280;
      font-size: 14px;
    }
  .small-button {
      padding: 0.5rem 0.75rem;
      font-size: 0.875rem;
    }

  select {
    width: 200px;
  }

  body {
    background-color: #fafafa;
    font-family: sans-serif;
  }

  .container {
    margin: 4px auto;
    width: 800px;
  }

  .settings {
    position: fixed;
    top: 0;
    right: 0;
    width: 500px;
    background-color: #fff;
    z-index: 1000;
    overflow-y: auto;
    height: 100%;
  }


  .slider-container {
    margin-top: 20px;
  }

  .slider-value {
    display: inline-block;
    margin-left: 10px;
    color: #6b7280;
    font-size: 14px;
  }

  .small-button {
    padding: 0.5rem 0.75rem;
    font-size: 0.875rem;
  }
</style>
  