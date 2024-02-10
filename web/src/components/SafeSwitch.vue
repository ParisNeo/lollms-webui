<template>
    <div>
      <label class="switch">
        <input type="checkbox" v-bind:checked="isChecked" @change="$emit('update:isChecked', $event.target.checked)">
        <span class="slider round"></span>
      </label>
    </div>
  </template>
  
<script>
  export default {
    name: 'SafeSwitch',
    props: ['isChecked'],    
    data() {
      return {
      }
    },
    methods: {
      toggleSwitch() {
        // Handle the switch toggle logic here
        console.log('Switch toggled:', this.isChecked);
      }
    }
  }
</script>
  