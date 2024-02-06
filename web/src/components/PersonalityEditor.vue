<template>
    <div class="mx-auto max-w-xl">
      <dialog :open="showDialog" @close="hideForm" class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
        <header class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-800">{{ title }}</h2>
          <button @click="hideForm" class="text-gray-500 hover:text-gray-700 font-bold py-2 px-4 rounded">
            X
          </button>
        </header>
  
        <form class="mb-4">
          <div class="mb-4">
            <label for="ai_name" class="block text-gray-700 font-bold mb-2">
              AI Name:
            </label>
            <input type="text" id="ai_name" name="ai_name" required v-model="ai_name" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
          </div>
  
          <div class="mb-4">
            <label for="ai_author" class="block text-gray-700 font-bold mb-2">
              AI Author:
            </label>
            <input type="text" id="ai_author" name="ai_author" required v-model="ai_author" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
          </div>
  
          <div class="mb-4">
            <label for="ai_category" class="block text-gray-700 font-bold mb-2">
              AI Category:
            </label>
            <input type="text" id="ai_category" name="ai_category" required v-model="ai_category" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
          </div>
  
          <div class="mb-4">
            <label for="ai_language" class="block text-gray-700 font-bold mb-2">
              AI Language:
            </label>
            <input type="text" id="ai_language" name="ai_language" required v-model="ai_language" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
          </div>
  
          <div class="mb-4">
            <label for="ai_description" class="block text-gray-700 font-bold mb-2">
              AI Description:
            </label>
            <textarea id="ai_description" name="ai_description" required v-model="ai_description" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"></textarea>
          </div>
  
          <div class="mb-4">
            <label for="ai_conditionning" class="block text-gray-700 font-bold mb-2">
              AI Conditionning:
            </label>
            <textarea id="ai_conditionning" name="ai_conditionning" required v-model="ai_conditionning" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"></textarea>
          </div>
  
          <div class="mb-4">
            <label for="ai_disclaimer" class="block text-gray-700 font-bold mb-2">
              AI Disclaimer:
            </label>
            <textarea id="ai_disclaimer" name="ai_disclaimer" required v-model="ai_disclaimer" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"></textarea>
          </div>
  
          <div class="mb-4">
            <label for="ai_icon" class="block text-gray-700 font-bold mb-2">
              AI Icon:
            </label>
            <div class="flex items-center">
              <img :src="iconUrl" @click="selectIcon" class="w-16 h-16 object-cover mr-4">
              <input type="file" id="ai_icon" @change="selectIcon" class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline">
            </div>
          </div>
  
          <button type="submit" @click.prevent="submitForm" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Commit AI to Server
          </button>
        </form>
      </dialog>
    </div>
  </template>
  
  <script>
  export default {
    data() {
      return {
        showDialog: false,
        title: 'Add AI Agent',
        ai_name: '',
        ai_author: '',
        ai_category: '',
        ai_language: '',
        ai_description: '',
        ai_conditionning: '',
        ai_disclaimer: '',
        iconUrl: '',
        file: null,
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
      submitForm() {
        const data = {
          ai_name: this.ai_name,
          ai_author: this.ai_author,
          ai_category: this.ai_category,
          ai_language: this.ai_language,
          ai_description: this.ai_description,
          ai_conditionning: this.ai_conditionning,
          ai_disclaimer: this.ai_disclaimer,
          ai_icon: this.file,
        };
  
        // Code to handle form submission goes here
      },
    },
  };
  </script>
  