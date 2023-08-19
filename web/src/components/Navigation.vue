<template>
    <div v-if="$store.state.ready" class="container flex flex-col sm:flex-row items-center">
      <div class="w-full">
        <ul class="flex flex-row font-medium">
          <li>
            <RouterLink :to="{ name: 'discussions' }" class="link-item dark:link-item-dark">
              Discussions
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{ name: 'playground' }" class="link-item dark:link-item-dark">
              Playground
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{ name: 'settings' }" class="link-item dark:link-item-dark">
              Settings
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{ name: 'extensions' }" class="link-item dark:link-item-dark">
              Extensions
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{ name: 'training' }" class="link-item dark:link-item-dark">
              Training
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{ name: 'quantizing' }" class="link-item dark:link-item-dark">
              Quantizing
            </RouterLink>
          </li>
          <li>
            <RouterLink :to="{ name: 'help' }" class="link-item dark:link-item-dark">
              Help
            </RouterLink>
          </li>
        </ul>
      </div>
    </div>
  </template>
  
  <script setup>
  import { nextTick } from 'vue';
  import feather from 'feather-icons';
  import { RouterLink } from 'vue-router';
  import { store } from '../main';
  </script>
  
  <style>
  .container {
    /* Remove margin and padding */
    margin: 0;
    padding: 0;
  }
  
  .link-item {
    /* Thin out the links */
    padding: 0px 20px;
    margin-bottom: -5px; /* Removes the gap between li elements */
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid transparent; /* Ensure all links have the same height */
    border-radius: 5px 5px 0 0; /* Rounded corners on the top */
    font-weight: bold; /* Optional: Add font-weight for emphasis */
  
    /* Use different colors for dark and light modes */
    background-color: #82a1d4; /* Use your theme's 'bg-light-tone' color for light mode */
    color: #000; /* Use your theme's 'primary' color for light mode */
  
 
    /* Animate the links when hovered */
    transition: duration-300 ease-in-out transform;


  }
  
  .link-item:hover {
    background-color: #3dabff; /* Use your theme's 'primary-light' color for the hover effect */
    animation-timing-function: ease-in-out;    
    
  }
  
  /* Optional: Change the color when the link is active */
  .link-item.router-link-active {
    background-color:  #b9d2f7; /* Use your theme's 'bg-dark-tone' color for active link in dark mode */
  }
  


  .link-item-dark {
    /* Thin out the links */
    padding: 0px 20px;
    margin-bottom: -5px; /* Removes the gap between li elements */
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid transparent; /* Ensure all links have the same height */
    border-radius: 5px 5px 0 0; /* Rounded corners on the top */
    font-weight: bold; /* Optional: Add font-weight for emphasis */
  
    /* Use different colors for dark and light modes */
    background-color: #132e59; /* Use your theme's 'bg-light-tone' color for light mode */
    color: #000; /* Use your theme's 'primary' color for light mode */
  
 
    /* Animate the links when hovered */
    transition: duration-300 ease-in-out transform;


  }
  
  .link-item-dark:hover {
    background-color: #0cc96a; /* Use your theme's 'primary-light' color for the hover effect */
    animation-timing-function: ease-in-out;    
    
  }
  
  /* Optional: Change the color when the link is active */
  .link-item-dark.router-link-active {
    background-color:  #25477d; /* Use your theme's 'bg-dark-tone' color for active link in dark mode */
  }


  /* Ensure each li extends to the bottom of its container */
  ul {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  </style>
  