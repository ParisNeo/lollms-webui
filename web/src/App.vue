<template>
  <div  :class="currentTheme" class="flex flex-col h-screen font-sans background-color text-slate-950 dark:bg-bg-dark dark:text-slate-50 w-full overflow-hidden">
    <TopBar/>
    <div class="flex overflow-hidden flex-grow w-full">
      <!-- VIEW CONTAINER -->
      <RouterView v-slot="{ Component }">
        <KeepAlive>
          <component :is="Component" />
        </KeepAlive>
      </RouterView>
    </div>

    <!-- FOOTER -->
    <!-- <Footer /> -->
  </div>
</template>

<script setup>
import { RouterView } from 'vue-router'
import TopBar from './components/TopBar.vue'
</script>
