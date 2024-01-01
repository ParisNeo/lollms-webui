<template>
  <div class="flex flex-col items-center justify-center min-h-screen">
    <h1 class="text-4xl font-bold mb-4">Install lollms</h1>
    <div class="flex flex-col gap-2">
      <label class="flex items-center">
        <input type="radio" value="nvidia" v-model="selectedOption" class="mr-2">
        Use NVIDIA GPU with CUDA
      </label>
      <label class="flex items-center">
        <input type="radio" value="amd" v-model="selectedOption" class="mr-2">
        Use AMD GPU with ROCm
      </label>
      <label class="flex items-center">
        <input type="radio" value="cpu" v-model="selectedOption" class="mr-2">
        Use CPU (no GPU)
      </label>
      <label class="flex items-center">
        <input type="radio" value="metal" v-model="selectedOption" class="mr-2">
        Use Metal (for Apple Silicon like M1 and M2)
      </label>
    </div>
    <button @click="install" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 mt-4 rounded">
      Install
    </button>
  </div>
</template>

<script>
import axios from 'axios';
export default {
  data() {
    return {
      selectedOption: "cpu",
    };
  },
  methods: {
    install() {
      axios.post({install_option:this.selectedOption}).then(()=>{

      });
    },
  },
};
</script>

<style>
/* Add any additional styling here */
</style>
