<template>
    <div class="p-4">
      <div class="flex items-center mb-4">
        <img :src="avatar" class="w-12 h-12 rounded-full mr-2" alt="Avatar">
        <h2 class="text-lg font-semibold">{{ personalityName }}</h2>
      </div>
      <p><strong>Author:</strong> {{ personalityAuthor }}</p>
      <p><strong>Description:</strong> {{ personalityDescription }}</p>
      <p><strong>Language:</strong> {{ personalityLanguage }}</p>
      <p><strong>Category:</strong> {{ personalityCategory }}</p>
      <p v-if="disclaimer"><strong>Disclaimer:</strong> {{ disclaimer }}</p>
      <p><strong>Conditioning Text:</strong> {{ conditioningText }}</p>
      <p><strong>AI Prefix:</strong> {{ aiPrefix }}</p>
      <p><strong>User Prefix:</strong> {{ userPrefix }}</p>
      <div>
        <strong>Antiprompts:</strong>
        <ul>
          <li v-for="antiprompt in antipromptsList" :key="antiprompt.id">
            {{ antiprompt.text }}
          </li>
        </ul>
      </div>
      <button @click="editMode = true" class="mt-4 bg-blue-500 text-white px-4 py-2 rounded">
        Edit
      </button>
      <button @click="commitChanges" v-if="editMode" class="mt-4 bg-green-500 text-white px-4 py-2 rounded">
        Commit
      </button>
    </div>
  </template>
  
  <script>
  
  export default {
    data() {
      return {
        editMode: false,
        avatar: 'path/to/avatar.jpg',
        personalityName: 'Personality Name',
        personalityAuthor: 'Author Name',
        personalityDescription: 'Personality Description',
        personalityLanguage: 'English',
        personalityCategory: 'Category',
        disclaimer: 'Disclaimer text',
        conditioningText: 'Conditioning Text',
        aiPrefix: 'AI Prefix',
        userPrefix: 'User Prefix',
        antipromptsList: [
          { id: 1, text: 'Antiprompt 1' },
          { id: 2, text: 'Antiprompt 2' },
          { id: 3, text: 'Antiprompt 3' }
        ]
      };
    },
    methods: {
      commitChanges() {
        // Send the modified personality to the backend
        // Implement your backend integration here
        console.log('Personality changes committed');
        this.editMode = false;
      }
    }
  };
  </script>
  