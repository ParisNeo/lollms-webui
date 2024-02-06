<template>
  <div v-if="show"  class="fixed top-50 left-0 right-0 bottom-50 flex items-center justify-center bg-black bg-opacity-50 z-20">
    <div class="relative w-full max-h-full ">
      <button type="button" @click="hide()"
        class="absolute top-3 right-2.5 text-gray-400 bg-transparent hover:bg-gray-200 hover:text-gray-900 rounded-lg text-sm p-1.5 ml-auto inline-flex items-center dark:hover:bg-gray-800 dark:hover:text-white">
        <svg aria-hidden="true" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"
          xmlns="http://www.w3.org/2000/svg">
          <path fill-rule="evenodd"
            d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
            clip-rule="evenodd"></path>
        </svg>
        <span class="sr-only">Close modal</span>
      </button>
      <form class="mb-4">
        <div class="container relative bg-white rounded-lg shadow dark:bg-gray-700 overflow-y-scroll">
          <table>
          <tr>
            <td><label for="personalityConditioning">Personality Conditioning:</label></td><td><textarea id="personalityConditioning" class="w-full" v-model="config.personality_conditioning"></textarea></td>
          </tr>
          <tr>
            <td><label for="userMessagePrefix">User Message Prefix:</label></td><td><input type="text" id="userMessagePrefix" class="w-full" v-model="config.user_message_prefix"></td>
          </tr>
          <tr>
            <td><label for="aiMessagePrefix">AI Message Prefix:</label></td><td><input type="text" id="aiMessagePrefix" class="w-full" v-model="config.ai_message_prefix"></td>
          </tr>

          <tr>
            <td><label for="linkText">Link Text:</label></td><td><input type="text" id="linkText" class="w-full" v-model="config.link_text"></td>
          </tr>
          <tr>
            <td><label for="welcomeMessage">Welcome Message:</label></td><td><textarea id="welcomeMessage" class="w-full" v-model="config.welcome_message"></textarea></td>
          </tr>
          <tr>
            <td><label for="modelTemperature">Model Temperature:</label></td><td><input type="number" id="modelTemperature" class="w-full" v-model="config.model_temperature"></td>
          </tr>
          <tr>
            <td><label for="modelNPredicts">Model N Predicts:</label></td>
            <td><input type="number" id="modelNPredicts" class="w-full" v-model="config.model_n_predicts"></td>
          </tr>   
          <tr>
            <td><label for="modelNPredicts">Model N Predicts:</label></td>
            <td><input type="number" id="modelNPredicts" class="w-full" v-model="config.model_n_predicts"></td>
          </tr>
          <tr>
            <td><label for="modelTopK">Model Top K:</label></td>
            <td><input type="number" id="modelTopK" class="w-full" v-model="config.model_top_k"></td>
          </tr>
          <tr>
            <td><label for="modelTopP">Model Top P:</label></td>
            <td><input type="number" id="modelTopP" class="w-full" v-model="config.model_top_p"></td>
          </tr>
          <tr>
            <td><label for="modelRepeatPenalty">Model Repeat Penalty:</label></td>
            <td><input type="number" id="modelRepeatPenalty" class="w-full" v-model="config.model_repeat_penalty"></td>
          </tr>
          <tr>
            <td><label for="modelRepeatLastN">Model Repeat Last N:</label></td>
            <td><input type="number" id="modelRepeatLastN" class="w-full" v-model="config.model_repeat_last_n"></td>
          </tr>
          <tr>
            <td><label for="recommendedBinding">Recommended Binding:</label></td>
            <td><input type="text" id="recommendedBinding" class="w-full" v-model="config.recommended_binding"></td>
          </tr>
          <tr>
            <td><label for="recommendedModel">Recommended Model:</label></td>
            <td><input type="text" id="recommendedModel" class="w-full" v-model="config.recommended_model"></td>
          </tr>
          <tr>
            <td><label for="dependencies">Dependencies:</label></td>
            <td><textarea id="dependencies" class="w-full" v-model="config.dependencies"></textarea></td>
          </tr>
          <tr>
            <td><label for="antiPrompts">Anti Prompts:</label></td>
            <td><textarea id="antiPrompts" class="w-full" v-model="config.anti_prompts"></textarea></td>
          </tr>                 
          </table>
        </div>        
        <div class="flex flex-row">
          <button type="submit" @click.prevent="submitForm" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Commit AI to Server
          </button>
          <button @click.prevent="hide()" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Close
          </button>

        </div>
      </form>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    personality: {
      type: Object,
      required: true
    },
    config: {
      type: Object,
      required: true
    },
  },
  data() {
    return {
      show:false,
      title: 'Add AI Agent',
      iconUrl: '',
      file: null,
      tempConfig: {} // Create a temporary copy of the 'config' prop
    };
  },
  methods: {
    showForm() {
      this.showDialog = true;
    },
    hideForm() {
      this.showDialog = false;
    },
    selectIcon(event) {
      if (event.target.files) {
        this.file = event.target.files[0];
        this.iconUrl = URL.createObjectURL(this.file);
      }
    },
    showPanel(){
      this.show = true;
    },
    hide(){
      self.show = false;
    },
    submitForm() {
      axios.post('/set_personality_config', {
                category: this.personality.category,
                name: this.personality.folder,
                config: this.config
            })
            .then(response => {
            const data = response.data;
            console.log("Done")
            if (data.status) {
                // Update the currentPersonConfig with the received data
                this.currentPersonConfig = data.config;
                this.showPersonalityEditor = true;
            } else {
                // Handle the error
                console.error(data.error);
            }
            })
            .catch(error => {
            // Handle the error
            console.error(error);
            });

    },
  },
};
</script>
