<template>
  <div class="flex flex-col items-center justify-center rounded-lg m-2 shadow-lg hover:border-primary dark:hover:border-primary hover:border-solid hover:border-2 border-2 border-transparent even:bg-bg-light-discussion-odd dark:even:bg-bg-dark-discussion-odd flex flex-col flex-grow flex-wrap overflow-visible p-4 pb-2">
    <img :src = "LoLLMSLogo">
    <h1 class="text-4xl font-bold mb-4">LOLLMS installation tool</h1>
    <p class="text-left">
      Welcome to the installer of lollms. Here you can select your install profile.<br>
      Let's start by selecting the hardware.<br><br>
    </p>
    <div class="flex flex-col gap-2">
      <label class="flex items-center">
        <input type="radio" value="cpu-noavx" v-model="selectedOption" class="mr-2">
        Use CPU without AVX (for old CPUs)
      </label>
      <label class="flex items-center">
        <input type="radio" value="cpu" v-model="selectedOption" class="mr-2">
        Use CPU with AVX support (new CPUs)
      </label>
      <label class="flex items-center">
        <input type="radio" value="nvidia" v-model="selectedOption" class="mr-2">
        Use NVIDIA GPU without tensorcore (for old GPUs)
      </label>
      <label class="flex items-center">
        <input type="radio" value="nvidia-tensorcores" v-model="selectedOption" class="mr-2">
        Use NVIDIA GPU with tensorcore (new GPUs)
      </label>
      <label class="flex items-center">
        <input type="radio" value="amd-noavx" v-model="selectedOption" class="mr-2">
        Use AMD GPU with no avx
      </label>
      <label class="flex items-center">
        <input type="radio" value="amd" v-model="selectedOption" class="mr-2">
        Use AMD GPU
      </label>      
      <label class="flex items-center">
        <input type="radio" value="apple-intel" v-model="selectedOption" class="mr-2">
        Apple with intel CPU
      </label>
      <label class="flex items-center">
        <input type="radio" value="apple-silicon" v-model="selectedOption" class="mr-2">
        Apple silicon (M1, M2 M3)
      </label>
    </div>
    <button @click="install" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 mt-4 rounded">
      Install
    </button>
  </div>
  <MessageBox ></MessageBox>
</template>

<script>
import MessageBox from '../components/messageBox.vue';
import axios from 'axios';
import LoLLMSLogo from '../assets/logo.png'
export default {
  data() {
    return {
      LoLLMSLogo:LoLLMSLogo,
      selectedOption: "cpu",
    };
  },
  components:{
    MessageBox
  },
  methods: {
    install() {
      axios.post("/start_installing",{mode:this.selectedOption}).then(()=>{

      });
    },
  },
};
</script>

<style>
/* Add any additional styling here */
</style>
