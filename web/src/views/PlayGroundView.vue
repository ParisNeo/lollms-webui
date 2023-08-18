<template>
  <div class="container mx-auto p-4 bg-gray-100 shadow-lg">
    <div class="flex justify-between">
      <div class="m-0">
        <button id="generate-button" @click="generate" class="bg-blue-500 hover:bg-blue-600 active:bg-blue-700 text-white font-bold py-2 px-4 rounded ml-2">Generate Text</button>
        <button v-if="!generating" id="stop-button" @click="stopGeneration" class="bg-red-500 hover:bg-red-600 active:bg-red-700 text-white font-bold py-2 px-4 rounded hidden ml-2 ">Stop Generation</button>
        <button v-else id="export-button" @click="exportText" class="bg-green-500 hover:bg-green-600 active:bg-green-700 text-white font-bold py-2 px-4 rounded ml-2">Export Text</button>
      </div>
    </div>
    <div class="flex flex-row h-full">
      <div class="flex-grow ml-2">
        <div class="mt-4 d-flex justify-content-space-between flex-row">
          <label class="mt-2">Presets</label>
          <select v-model="selectedPreset" class="w-25 m-2">
            <option v-for="preset in Object.keys(presets)" :key="preset" :value="preset">
              {{ preset }}
            </option>
          </select>
          <button class="bg-red-500 hover:bg-red-600 active:bg-red-700 text-white font-bold py-2 px-4 rounded ml-2 " @click="setPreset">Use preset</button>
          <button class="bg-green-500 hover:bg-green-600 active:bg-red-700 text-white font-bold py-2 px-4 rounded ml-2 " @click="addPreset">Add preset</button>
          <button class="bg-red-500 hover:bg-red-600 active:bg-red-700 text-white font-bold py-2 px-4 rounded ml-2" @click="removePreset">Remove preset</button>
          <button class="bg-red-500 hover:bg-red-600 active:bg-red-700 text-white font-bold py-2 px-4 rounded ml-2" @click="removePreset">Save preset</button>
        </div>
        <div class="flex-grow">
          <textarea v-model="text" id="text_element" class="mt-4 p-2 border border-gray-300 rounded-md h-64 overflow-y-scroll w-full" type="text"></textarea>
        </div>
      </div>
      <div id="settings" class="border border-blue-300 bg-blue-200 mt-4 w-25 mr-2 h-full mb-10" style="align-items: center; height: fit-content; margin: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); border-radius: 4px;">
          <div id="title" class="border border-blue-600 bg-blue-300 m-0" style="align-items: center; height: fit-content; margin: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); border-radius: 4px;">
          <h3 class="text-gray-600 mb-4 text-center m-0">Settings</h3>
          </div>
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
            <input type="range" v-model="repeat_penalty" min="0" max="5" step="0.1" class="w-full">
            <span class="slider-value text-gray-500">Current value: {{ repeat_penalty }}</span>
          </div>
          <div class="slider-container ml-2 mr-2">
            <h3 class="text-gray-600">Repeat Last N</h3>
            <input type="range" v-model="repeat_last_n" min="0" max="100" step="1" class="w-full">
            <span class="slider-value text-gray-500">Current value: {{ repeat_last_n }}</span>
          </div>
          <div class="slider-container ml-2 mr-2">
            <h3 class="text-gray-600">Seed</h3>
            <input type="number" v-model="seed" class="w-full">
            <span class="slider-value text-gray-500">Current value: {{ seed }}</span>
          </div>
        </div>


    </div>
  </div>
  <Toast ref="toast"/>
</template>

<script>
import axios from "axios";
import socket from '@/services/websocket.js'
import Toast from '../components/Toast.vue'
export default {
  name: 'PlayGroundView',
  data() {
    return {
      generating:false,
      presets:{},
      selectedPreset: '',      
      text:"",
      temperature: 0.1,
      top_k: 50,
      top_p: 0.9,
      repeat_penalty: 1.3,
      repeat_last_n: 50,
      seed: -1,
    };
  },
  components:{    
    Toast,
  },
  created(){
        axios.get('./presets.json').then(response => {
          console.log(response.data)
          this.presets=response.data
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
            this.$refs.text_element.scrollTop = this.$refs.text_element.scrollHeight;
            // Toggle button visibility
            this.generating=false
        });

        // Event handler for error during text generation
        socket.on('generation_canceled', error => {
            // Toggle button visibility
            this.generating=false
            console.log("Generation canceled OK")
        });

        
  },
  methods:{
    appendToOutput(chunk){
      this.text += chunk
    },
    generate(){
      
      var prompt = this.text
      console.log(prompt)
      // Trigger the 'generate_text' event with the prompt
      socket.emit('generate_text', { prompt: prompt, personality: -1, n_predicts: 1024 ,
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
      socket.emit('cancel_generation',{});
    },
    exportText(){
      
    },
    setPreset() {
      this.text = this.presets[this.selectedPreset];
    },
    addPreset() {
      let title = prompt('Enter the title of the preset:');
      this.presets[title] =  this.text
    },
    removePreset() {
      if (this.selectedPreset) {
        delete this.presets[this.selectedPreset];
      }
    },
    savePreset() {
      axios.post("/save_preset", presets).then((response) => {
          console.log(response);
          this.$refs.toast.showToast(`Preset saved`,4,true)
        });
    }
  }
};
</script>

<style>

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
    width: 250px;
    background-color: #fff;
    z-index: 1000;
    display: none;
  }

  .settings-button {
    cursor: pointer;
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 5px;
    color: #333;
    font-size: 14px;
  }

  .settings-button:hover {
    background-color: #eee;
  }

  .settings-button:active {
    background-color: #ddd;
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
  