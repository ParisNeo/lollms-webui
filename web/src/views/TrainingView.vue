<template>
    <div class="container overflow-y-scroll flex flex-col no-scrollbar shadow-lg p-10 pt-0">
      <form @submit.prevent="submitForm" class="max-w-md mx-auto">
        <!-- Model/Tokenizer -->
        <div class="mb-4">
          <label for="model_name" class="text-sm">Model Name:</label>
          <input
            type="text"
            id="model_name"
            v-model="model_name"
            required
            class="w-full mt-1 px-2 py-1 border border-gray-300 rounded"
          >
        </div>
        <div class="mb-4">
          <label for="tokenizer_name" class="text-sm">Tokenizer Name:</label>
          <input
            type="text"
            id="tokenizer_name"
            v-model="tokenizer_name"
            required
            class="w-full mt-1 px-2 py-1 border border-gray-300 rounded"
          >
        </div>
  
        <!-- Dataset -->
        <div class="mb-4">
          <label for="dataset_path" class="text-sm">Dataset:</label>
          <input
            type="file"
            id="dataset_path"
            ref="dataset_path"
            accept=".parquet"
            v-on:change="selectDatasetPath"
            class="w-full mt-1 px-2 py-1 border border-gray-300 rounded"
          >
          <p class="mt-2 text-xs">Selected File: {{ selectedDatasetPath }}</p>
        </div>
        <div class="mb-4">
          <label for="max_length" class="text-sm">Max Length:</label>
          <input
            type="number"
            id="max_length"
            v-model.number="max_length"
            required
            class="w-full mt-1 px-2 py-1 border border-gray-300 rounded"
          >
        </div>
        <div class="mb-4">
          <label for="batch_size" class="text-sm">Batch Size:</label>
          <input
            type="number"
            id="batch_size"
            v-model.number="batch_size"
            required
            class="w-full mt-1 px-2 py-1 border border-gray-300 rounded"
          >
        </div>
  
        <!-- Train Dynamics -->
        <div class="mb-4">
          <label for="lr" class="text-sm">Learning Rate:</label>
          <input
            type="number"
            id="lr"
            v-model.number="lr"
            required
            class="w-full mt-1 px-2 py-1 border border-gray-300 rounded"
          >
        </div>
        <div class="mb-4">
          <label for="num_epochs" class="text-sm">Number of Epochs:</label>
          <input
            type="number"
            id="num_epochs"
            v-model.number="num_epochs"
            required
            class="w-full mt-1 px-2 py-1 border border-gray-300 rounded"
          >
        </div>
  
        <!-- Logging -->
        <div class="mb-4">
        <label for="output_dir" class="text-sm">Output Directory:</label>
        <input
          type="text"
          id="output_dir"
          v-model="selectedFolder"
          class="w-full mt-1 px-2 py-1 border border-gray-300 rounded"
          placeholder="Enter or select the output folder"
        >
        <input
          type="file"
          id="folder_selector"
          ref="folder_selector"
          style="display: none"
          webkitdirectory
          v-on:change="selectOutputDirectory"
        >
        <button type="button" @click="openFolderSelector" class="bg-blue-500 text-white px-4 py-2 rounded">Select Folder</button>
      </div>
  
        <button type="submit" class="bg-blue-500 text-white px-4 py-2 rounded">Train LLM</button>
      </form>
    </div>
  </template>
  
  <script>
  export default {
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
  