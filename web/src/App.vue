<template>
  <div
    class="flex flex-col h-screen max-h-screen font-sans bg-bg-light text-slate-950 dark:bg-bg-dark dark:text-slate-50">

    <TopBar />

    <div class="flex overflow-hidden flex-grow">
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
import TopBar from './components/TopBar.vue';
import Footer from './components/Footer.vue';


</script>
<!-- <script src="../node_modules/feather-icons/dist/feather"></script> -->