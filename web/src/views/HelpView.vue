<template>

    <div class="container flex-row mx-auto p-4 bg-bg-light-tone dark:bg-bg-dark-tone  shadow-lg overflow-y-auto no-scrollbar p-2 pb-0 grid lg:grid-cols-1 md:grid-cols-2 gap-4">
      <Card  :disableHoverAnimation="true" :disableFocus="true">
        <h2 class="text-2xl font-bold mb-2">About Lord of large Language Models</h2>
        <p class="mb-4"> Lollms version {{ version }}</p>
        <p>Discord link: <a class="text-blue-500 hover:text-blue-400 duration-150" href="https://discord.gg/C73K7hjy">https://discord.gg/C73K7hjy</a></p>
      </Card>
      
      <Card  :disableHoverAnimation="true" :disableFocus="true">
        <h2 class="text-2xl font-bold mb-2">Frequently Asked Questions</h2>
        <ul class="list-disc pl-4">
          <li v-for="(faq, index) in faqs" :key="index">
            <h3 class="text-xl font-bold mb-1">{{ faq.question }}</h3>
            <p class="mb-4" v-html="parseMultiline(faq.answer)"></p>
          </li>
        </ul>
      </Card>
      <Card  :disableHoverAnimation="true" :disableFocus="true">
        <h2 class="text-2xl font-bold mb-2">Contact Us</h2>
        <p class="mb-4">If you have any further questions or need assistance, feel free to reach out to me.</p>
        <p>Discord link: <a class="text-blue-500 hover:text-blue-400 duration-150" href="https://discord.gg/C73K7hjy">https://discord.gg/C73K7hjy</a></p>
      </Card>
      <Card   :disableHoverAnimation="true" :disableFocus="true">
        <h2 class="text-2xl font-bold mb-2">Credits</h2>
        <p class="mb-4">This project is developed by <span class="font-bold">ParisNeo</span> With help from the community.</p>
        <p class="mb-4"><span class="font-bold"><a href="https://github.com/ParisNeo/lollms-webui/graphs/contributors">Check out the full list of developers here and show them some love.</a></span></p>
        <p>Check out the project on <a class="text-blue-500 hover:text-blue-400 duration-150" :href="githubLink" target="_blank" rel="noopener noreferrer">GitHub</a>.</p>
      </Card>
    </div>
</template>
  
  <script>
  import axios from 'axios';
  import Papa from 'papaparse'; // Import the Papa Parse library for CSV parsing
  import Card from "@/components/Card.vue"
  import { store } from '../main';  

  export default {
    components:{
      Card
    }
    ,
    name: 'HelpPage',
    data() {
      return {
        lollmsVersion: "unknown",
        faqs: [], // Array to store the loaded FAQs
        githubLink: 'https://github.com/ParisNeo/lollms-webui', // Replace with your project's GitHub link
      };
    },
    mounted() {
      this.loadFAQs(); // Call the method to load FAQs when the component is mounted
    },
    computed: {
      // This will be triggered whenever lollmsVersion is updated
      // but it will not be directly used in the template.
      version: {
        get(){
          return this.$store.version
        }        
      },
    },
    async created() {
      // Fetch the data when the component is created
    },
    methods: {
      async api_get_req(endpoint) {
            try {
                const res = await axios.get("/" + endpoint);

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'api_get_req')
                return
            }
      },
      loadFAQs() {
        // Fetch and parse the CSV file
        fetch('/help/faqs.csv')
          .then((response) => response.text())
          .then((csv) => {
            const { data } = Papa.parse(csv, { header: true }); // Parse the CSV and extract data
            console.log("Recovered data")
            console.log(data)
            this.faqs = data; // Assign the parsed data to the faqs array
          })
          .catch((error) => {
            console.error('Error loading FAQs:', error);
          });
      },
      parseMultiline(text) {
        // Replace newline characters with HTML line breaks
        return text.replace(/\n/g, '<br>');
      },
    },
  };
  </script>
  
  <style scoped>
  .scrollbar {
    /* Add your scrollbar container styles here */
    scrollbar-width: thin;
    scrollbar-color: var(--scrollbar-thumb-color) var(--scrollbar-track-color);
    white-space: pre-wrap; /* Preserve line breaks */
    overflow-wrap: break-word; /* Break words if necessary */
  }
  
  .scrollbar::-webkit-scrollbar {
    width: 8px;
  }
  
  .scrollbar::-webkit-scrollbar-track {
    background-color: var(--scrollbar-track-color);
  }
  
  .scrollbar::-webkit-scrollbar-thumb {
    background-color: var(--scrollbar-thumb-color);
    border-radius: 4px;
  }
  
  .scrollbar::-webkit-scrollbar-thumb:hover {
    background-color: var(--scrollbar-thumb-hover-color);
  }
  
  </style>
  