<template>
    <div class="container overflow-y-scroll flex flex-col no-scrollbar shadow-lg p-10 pt-2 bg-bg-light-tone dark:bg-bg-dark-tone">
      <form @submit.prevent="submitForm" class="max-w-md mx-auto">
        <Card title="Quantizing configuration" :isHorizontal="true" :disableHoverAnimation="true" :disableFocus="true">
          <Card title="Model" class="" :isHorizontal="false">
            <!-- Model/Tokenizer -->
            <div class="mb-4">
              <label for="model_name" class="text-sm">Model Name:</label>
              <ClipBoardTextInput id="model_path" inputType="text"  :value="model_name" />
            </div>
            <div class="mb-4">
              <label for="tokenizer_name" class="text-sm">Tokenizer Name:</label>
              <ClipBoardTextInput id="model_path" inputType="text"  :value="tokenizer_name" />
            </div>
          </Card>
        </Card>
        <Card  :disableHoverAnimation="true" :disableFocus="true">
          <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">Quantize LLM</button>
          <ProgressBar v-if="loading" :progress="progressValue" />
        </Card>
      </form>
    </div>
  </template>
  
  <script>
  import ClipBoardTextInput from "@/components/ClipBoardTextInput.vue";
  import Card from "@/components/Card.vue"
  import ProgressBar from '@/components/ProgressBar.vue';

  export default {
    components: {
      ClipBoardTextInput,
      Card,
      ProgressBar
    },      
    data() {
        return {
            model_name: 'jondurbin/airoboros-7b-gpt4',
            tokenizer_name: 'jondurbin/airoboros-7b-gpt4',
            dataset_path: '',
            max_length: 1024,
            batch_size: 4,
            lr: 5.0e-5,
            num_epochs: 2,
            selectedFolder: '',
            selectedDatasetPath: '',
        };
    },
    methods: {
      submitForm() {
        const formData = {
          model_name: this.model_name,
          tokenizer_name: this.tokenizer_name,
          dataset_path: this.selectedDatasetPath,
          max_length: this.max_length,
          batch_size: this.batch_size,
          lr: this.lr,
          num_epochs: this.num_epochs,
          output_dir: this.selectedFolder,
        };
  
        // Send the form data to the backend
        // ...
      },
      openFolderSelector() {
      this.$refs.folder_selector.click();
      },
      selectOutputDirectory(event) {
        console.log("here")
        const folderPath = event.target.files[0]?.path;
        console.log(folderPath)
        if (folderPath) {
            this.selectedFolder = folderPath;
        }
      },
      selectDatasetPath(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this.selectedDatasetPath = files[0].webkitRelativePath;
        }
      },
    },
  };
  </script>
  