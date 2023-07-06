<template>
  <div class="step flex items-center mb-4">
    <div class="checkbox flex items-center justify-center w-6 h-6 rounded border border-gray-300 mr-2">
      <i
        data-feather="square"
        v-if="!done"
        class="text-gray-400 w-4 h-4"
      ></i>
      <i
        data-feather="check-square"
        v-if="done"
        class="text-green-500 w-4 h-4"
      ></i>
    </div>
    <div class="content flex-1" :class="{'text-green-500': done, 'text-yellow-500': !done}">{{ message }}</div>
    <div class="loader w-6 h-6 border-t-4 border-b-4 border-blue-500 rounded-full animate-spin ml-2" v-if="!done"></div>
  </div>
</template>




  
  <script>
  export default {
    props: {
      done: {
        type: Boolean,
        required: true
      },
      message: {
        type: String,
        required: true
      }
    }
  };
  </script>
  
  <style>
 
  </style>
  