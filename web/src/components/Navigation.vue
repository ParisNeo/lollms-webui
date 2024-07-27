<template>
    <div v-if="$store.state.ready" class="container z-60 flex flex-col sm:flex-row items-center">
      <div class="w-full text-center">
        <div class="m-0 flex border-b w-full items-center justify-center  flex flex-row font-medium nav-ul text-center">
            <RouterLink 
              :to="{ name: 'discussions' }" 
              class="inline-block border-l border-t border-r rounded-t py-2 px-4 text-blue-700 font-semibold" 
              :class="{ 
                'text-green-600 hover:text-green-500 dark:text-green-100 font-bold bg-bg-secondary shadow-no-bottom': isRouteActive('discussions'),
                'bounce-in': isRouteActive('discussions'),
                }">
              Discussions
            </RouterLink>
            <RouterLink 
              :to="{ name: 'playground' }" 
              class="inline-block border-l border-t border-r rounded-t py-2 px-4 text-blue-700 font-semibold"
              :class="{ 
                'text-green-600 hover:text-green-500 dark:text-green-100 font-bold bg-bg-secondary shadow-no-bottom': isRouteActive('playground'),
                'bounce-in': isRouteActive('playground'),
              }"
              >
              Playground
            </RouterLink>
            <RouterLink 
              :to="{ name: 'AppsZoo' }" 
              class="inline-block border-l border-t border-r rounded-t py-2 px-4 text-blue-700 font-semibold"
              :class="{ 
                'text-green-600 hover:text-green-500 dark:text-green-100 font-bold bg-bg-secondary shadow-no-bottom': isRouteActive('AppsZoo'),
                'bounce-in': isRouteActive('AppsZoo'),
              }"
              >
              Apps Zoo
            </RouterLink>
            <RouterLink 
              v-if="$store.state.config.enable_sd_service | $store.state.config.active_tti_service== 'autosd'" 
              :to="{ name: 'AutoSD' }" 
              class="inline-block border-l border-t border-r rounded-t py-2 px-4 text-blue-700 font-semibold"
              :class="{ 
                'text-green-600 hover:text-green-500 dark:text-green-100 font-bold bg-bg-secondary shadow-no-bottom': isRouteActive('AutoSD'),
                'bounce-in': isRouteActive('AutoSD'),
              }"
              >
              Auto111-SD
            </RouterLink>
            <RouterLink 
              v-if="$store.state.config.enable_comfyui_service | $store.state.config.active_tti_service== 'comfyui'" 
              :to="{ name: 'ComfyUI' }" 
              class="inline-block border-l border-t border-r rounded-t py-2 px-4 text-blue-700 font-semibold"
              :class="{ 
                'text-green-600 hover:text-green-500 dark:text-green-100 font-bold bg-bg-secondary shadow-no-bottom': isRouteActive('ComfyUI'),
                'bounce-in': isRouteActive('ComfyUI'),
              }"
              >
              ComfyUI
            </RouterLink>
            <RouterLink 
              v-if="$store.state.config.active_tts_service!='None' & $store.state.config.active_stt_service!='None'" 
              :to="{ name: 'interactive' }" 
              class="inline-block border-l border-t border-r rounded-t py-2 px-4 text-blue-700 font-semibold"
              :class="{ 
                'text-green-600 hover:text-green-500 dark:text-green-100 font-bold bg-bg-secondary shadow-no-bottom': isRouteActive('interactive'),
                'bounce-in': isRouteActive('interactive'),
              }"
              >
              interactive
            </RouterLink>
            <!--
            <RouterLink :to="{ name: 'nodes' }" class="link-item dark:link-item-dark">
              Nodes (under construction)
            </RouterLink>
            -->
            <!--

            <RouterLink :to="{ name: 'training' }" class="link-item dark:link-item-dark">
              Training
            </RouterLink>
            <RouterLink :to="{ name: 'quantizing' }" class="link-item dark:link-item-dark">
              Quantizing
            </RouterLink>

            -->
            <RouterLink 
              :to="{ name: 'settings' }" 
              class="inline-block border-l border-t border-r rounded-t py-2 px-4 text-blue-700 font-semibold"
              :class="{ 
                'text-green-600 hover:text-green-500 dark:text-green-100 font-bold bg-bg-secondary shadow-no-bottom': isRouteActive('settings'),
                'bounce-in': isRouteActive('settings'),
              }"              
              >
              Settings
            </RouterLink>
            <RouterLink 
              :to="{ name: 'help_view' }" 
              class="inline-block border-l border-t border-r rounded-t py-2 px-4 text-blue-700 font-semibold"
              :class="{ 
                'text-green-600 hover:text-green-500 dark:text-green-100 font-bold bg-bg-secondary shadow-no-bottom': isRouteActive('help_view'),
                'bounce-in': isRouteActive('help_view'),
              }"
              >
              Help
            </RouterLink>
                                                               

          </div>
      </div>
    </div>
</template>

<script setup>
  import { nextTick } from 'vue';
  import feather from 'feather-icons';
  import { RouterLink } from 'vue-router';
  import { store } from '../main';
</script>
<script>
  export default {
    name: 'Navigation',
    data() {
      return {
        // component data
      };
    },
    methods: {
      isRouteActive(routeName) {
        try{
          return this.$route.name === routeName;
        }
        catch{
          console.log("routeName not found")
          return False;
        }
      }
      // your methods
    },
    // other options
  };
</script>
  
<style>

  .container {
    /* Remove margin and padding */
    margin: 0;
    padding: 0;
  }
  
  .link-item {
    height: 25px;
    margin-top: 5px;
    /* Thin out the links */
    padding: 0px 20px;
    margin-bottom: -5px; /* Removes the gap between li elements */
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid transparent; /* Ensure all links have the same height */
    border-radius: 5px 5px 0 0; /* Rounded corners on the top */
    font-weight: bold; /* Optional: Add font-weight for emphasis */
 
    /* Animate the links when hovered */
    transition: duration-300 ease-in-out transform;


  }
  
  .link-item-dark {
    /* Thin out the links */
    padding: 0px 20px;
    color: aliceblue;
    margin-bottom: -5px; /* Removes the gap between li elements */
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid transparent; /* Ensure all links have the same height */
    border-radius: 5px 5px 0 0; /* Rounded corners on the top */
    font-weight: bold; /* Optional: Add font-weight for emphasis */
 
    /* Animate the links when hovered */
    transition: duration-300 ease-in-out transform;


  }

  /* Ensure each li extends to the bottom of its container */

  .nav-ul {
    list-style: none;
    padding: 0;
    margin: 0;
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  
  .nav-li {
    cursor: pointer;
    display: flex;
    align-items: center;
    padding: 5px;
  }

  .fade-in {
    animation: fadeInAnimation 0.5s;
  }

  @keyframes fadeInAnimation {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }


  .bounce-in {
    animation: bounceInAnimation 0.5s;
  }
  .bounce-out {
    animation: bounceOutAnimation 0.5s;
  }



  @keyframes bounceInAnimation {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.2);
    }
    100% {
      transform: scale(1);
    }
  }
  .shadow-no-bottom {
    box-shadow: 0px -4px 6px -1px rgba(0, 0, 0, 0.1), 0px 2px 4px -1px rgba(0, 0, 0, 0.06);
  }

</style>
  