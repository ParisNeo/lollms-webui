<template>
  <div class="flex flex-col h-screen font-sans bg-bg-light text-slate-950 dark:bg-bg-dark dark:text-slate-50  overflow-y-scroll w-full dark:bg-bg-dark scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
    <TopBar />

    <div class="flex overflow-hidden flex-grow ">
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
