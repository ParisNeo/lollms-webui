<template>
  <div :class="{ 'hidden': !isVisible }" class="absolute flex flex-col no-scrollbar shadow-lg bg-bg-light dark:bg-bg-dark top-20 left-20 bottom-20 right-20 shadow-lg rounded">
    
    <div id="leftPanel" class="flex flex-row h-full flex-grow shadow-lg rounded">
      <div class="w-[15rem] z-10 top-0 bg-bg-light-tone dark:bg-bg-dark-tone shadow-md overflow-y-scroll  no-scrollbar">
        <!-- Search input -->
        <input 
            type="search" 
            id="default-search" 
            class="block w-full h-8 px-8 text-sm border border-gray-300 rounded-md
                bg-bg-light focus:ring-1 focus:ring-secondary focus:border-secondary 
                dark:bg-bg-dark dark:border-gray-600 dark:placeholder-gray-400 
                dark:focus:ring-secondary dark:focus:border-secondary
                transition-all duration-200"
            placeholder="Search discussions..." 
            title="Filter skills by title" 
            v-model="searchQuery"
            @keyup.enter="searchSkills"
        />        
     
        <div classclass="absolute flex flex-col no-scrollbar shadow-lg w-[15rem] bg-bg-light-tone dark:bg-bg-dark-tone top-20 left-20 bottom-20 right-20 bg-bg-light shadow-lg rounded">
          <h2 class="text-xl font-bold m-4">Titles</h2>
          <TransitionGroup v-if="titles.length > 0" name="list">
              <Discussion v-for="title in titles" :key="title.id" :id="title.id" :title="title.title"
                  :selected="fetchContent(title.id)" :loading="loading" :isCheckbox="isCheckbox"
                  :checkBoxValue="false" 
                  :openfolder_enabled="false"
                  @select="fetchContent(title.id)"
                  @delete="deleteSkill(title.id)" 
                  @editTitle="editTitle" 
                  @makeTitle="makeTitle"
                  @checked="checkUncheckTitle" />
          </TransitionGroup>
        </div>

      </div>

      <div class="z-0 flex flex-col  flex-grow  overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
        <h2 class="text-xl font-bold m-4">Content</h2>
        <MarkdownRenderer  :host="host" :markdown-text="content" :message_id="id" :discussion_id="id" :client_id="this.$store.state.client_id"></MarkdownRenderer>
      </div>
    </div>

    <button @click="closeComponent" class="absolute top-2 right-2 bg-red-500 text-white rounded px-2 py-1 hover:bg-red-300">Close</button>
  </div>
</template>

<script>
import axios from 'axios';
import Discussion from '../components/Discussion.vue'
import MarkdownRenderer from '../components/MarkdownRenderer.vue'


export default {
  data() {
    return {
      id: 0,
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
    Discussion,
    MarkdownRenderer
  },
    props: {
        host: {
            type: String,
            required: false,
            default: "http://localhost:9600",
        },            
    },
  methods: {
    showSkillsLibrary() {
      this.isVisible = true;
      this.fetchTitles();
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
    fetchTitles() {
      console.log("Fetching categories")
      axios.post('/get_skills_library_titles', { client_id: this.$store.state.client_id })
        .then(response => {
          this.titles = response.data.titles;
          console.log("titles recovered")
        })
        .catch(error => {
          console.error('Error fetching titles:', error);
        });
    },
    fetchContent(skillId) {
      console.log("loading skill", skillId)
      axios.post('/get_skills_library_content', { client_id: this.$store.state.client_id, skill_id: skillId })
        .then(response => {
          const skill = response.data.contents[0];
          this.id = skill.id
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
      console.log("Delete skill ",id)
      axios.post("/delete_skill",{"client_id":this.$store.state.client_id,"skill_id":id}).then(
        ()=>{
          this.fetchTitles();
        }
      )
    },

    editTitle(id){
      axios.post("/edit_skill_title",{"client_id":this.$store.state.client_id,"skill_id":id,"title":id}).then(
        ()=>{
          this.fetchTitles();
        }
      )
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
