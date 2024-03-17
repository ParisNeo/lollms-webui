<template>
  <div :class="{ 'hidden': !isVisible }" class="absolute top-20 left-20 bottom-20 right-20 bg-bg-light shadow-lg rounded">
    <div id="leftPanel" class="flex flex-row flex-grow overflow-y-scroll no-scrollbar shadow-lg rounded">
      <div class=" sticky z-10 top-0  bg-bg-light-tone dark:bg-bg-dark-tone shadow-md ">
        <div class="search p-4">
          <input type="text" v-model="searchQuery" placeholder="Search skills" class="border border-gray-300 rounded px-2 py-1 mr-2">
          <button @click="searchSkills" class="bg-blue-500 text-white rounded px-4 py-1">Search</button>
        </div>

        <div class="w-1/4 p-4 ">
          <h2 class="text-xl font-bold m-4">Categories</h2>
          <TransitionGroup v-if="categories.length > 0" name="list">
              <Discussion v-for="category in categories" :key="category" :id="category" :title="category"
                  :selected="fetchTitles(category)" :loading="loading" :isCheckbox="isCheckbox"
                  :checkBoxValue="false" 
                  @select="fetchTitles(category)"
                  @delete="deleteCategory(category)" 
                  @editTitle="editCategory" 
                  @makeTitle="makeCategory"
                  @checked="checkUncheckCategory" />
          </TransitionGroup>
        </div>
        <div class="w-1/4 p-4">
          <h2 class="text-xl font-bold m-4">Titles</h2>
          <TransitionGroup v-if="categories.length > 0" name="list">
              <Discussion v-for="title in titles" :key="title.id" :id="title.id" :title="title.title"
                  :selected="fetchTitles(title)" :loading="loading" :isCheckbox="isCheckbox"
                  :checkBoxValue="false" 
                  @select="fetchContent(title.id)"
                  @delete="deleteSkill(title.id)" 
                  @editTitle="editTitle" 
                  @makeTitle="makeTitle"
                  @checked="checkUncheckTitle" />
          </TransitionGroup>
        </div>

      </div>

      <div class="w-full z-0 flex flex-col  flex-grow  overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
        <h2 class="text-xl font-bold m-4">Content</h2>
        <p class="m-4">{{ content }}</p>
      </div>
    </div>

    <button @click="closeComponent" class="absolute top-2 right-2 bg-red-500 text-white rounded px-2 py-1">Close</button>
  </div>
</template>

<script>
import axios from 'axios';
import Discussion from '../components/Discussion.vue'


export default {
  data() {
    return {
      loading: false,
      isCheckbox: false,
      isVisible: false,
      categories: [],
      titles: [],
      content: '',
      searchQuery: ''
    };
  },
  components:{
    Discussion
  },
  methods: {
    showSkillsLibrary() {
      this.isVisible = true;
      this.fetchCategories();
    },
    closeComponent() {
      this.isVisible = false;
    },
    fetchCategories() {
      axios.post('/get_skills_library_categories', { client_id: this.$store.state.client_id })
        .then(response => {
          this.categories = response.data.categories;
        })
        .catch(error => {
          console.error('Error fetching categories:', error);
        });
    },
    fetchTitles(category) {
      console.log("Fetching categories")
      axios.post('/get_skills_library_titles', { client_id: this.$store.state.client_id, category: category })
        .then(response => {
          this.titles = response.data.titles;
        })
        .catch(error => {
          console.error('Error fetching titles:', error);
        });
    },
    fetchContent(skillId) {
      axios.post('/get_skills_library_content', { client_id: this.$store.state.client_id, skill_id: skillId })
        .then(response => {
          const skill = response.data.contents[0];
          this.content = skill.content;
        })
        .catch(error => {
          console.error('Error fetching content:', error);
        });
    },
    deleteCategory(category) {
      console.log("Delete category")

    },
    editCategory(category){
      console.log("Edit category")

    },
    checkUncheckCategory(category){
      console.log("Unchecked category")

    },
    deleteSkill(id){
      console.log("Delete skill")
    },

    editTitle(id){
      console.log("Edit title")
    },
    makeTitle(id){
      console.log("Make title")

    },
    checkUncheckTitle(id){

    },
    searchSkills() {
      // Implement the search functionality by making an API call with the searchQuery
      // Update the titles and content based on the search results
    }
  }
};
</script>
