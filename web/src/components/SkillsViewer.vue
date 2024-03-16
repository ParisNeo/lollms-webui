<template>
    <div class="skills-viewer">
        <div class="categories">
        <ul>
            <li v-for="category in categories" :key="category.id" @click="fetchTitles(category)">
            {{ category.name }}
            </li>
        </ul>
        </div>

        <div class="titles">
        <ul>
            <li v-for="title in titles" :key="title.id" @click="fetchContent(title)">
            {{ title.name }}
            </li>
        </ul>
        </div>

        <div class="content">
        <p>{{ content }}</p>
        </div>

        <div class="search">
        <input type="text" v-model="searchQuery" placeholder="Search skills">
        <button @click="searchSkills">Search</button>
        </div>

    </div>
  </template>
<script>
export default {
  data() {
    return {
      categories: [],
      selectedCategory: null,
      titles: [],
      selectedTitle: null,
      content: '',
      searchQuery: ''
    };
  },
  methods: {
    fetchCategories() {
    axios.get('/api/categories')
        .then(response => {
        this.categories = response.data;
        })
        .catch(error => {
        console.error('Error fetching categories:', error);
        });
    }

    fetchTitles(category) {
      // Make an API call to fetch the titles for the selected category
      // Update the `titles` data property with the fetched data
    },
    fetchContent(title) {
      // Make an API call to fetch the content for the selected title
      // Update the `content` data property with the fetched data
    },
    searchSkills() {
      // Make an API call to search for skills based on the `searchQuery`
      // Update the `titles` and `content` data properties with the search results
    }
  },
  created() {
    this.fetchCategories();
  }
};
</script>
  