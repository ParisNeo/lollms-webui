<template>
    <transition name="fade-smooth">
      <div
        v-if="!isReady"
        class="fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-gradient-welcome text-blue-800 dark:text-blue-100"
      >
        <div
          v-if="$store.state.theme_vars.activate_dropping_animation"
          class="absolute inset-0 pointer-events-none overflow-hidden opacity-70"
        >
          <div
            v-for="n in 60"
            :key="n"
            class="absolute animate-fall text-xs text-blue-300 dark:text-blue-500"
            :style="{
              left: `${Math.random() * 100}%`,
              top: `-30px`,
              animationDuration: `${4 + Math.random() * 8}s`,
              animationDelay: `${Math.random() * 6}s`,
              opacity: `${0.3 + Math.random() * 0.5}`
            }"
          >
             {{ $store.state.theme_vars.falling_object || '·' }}
          </div>
        </div>

        <div class="relative z-10 flex w-full max-w-4xl flex-col items-center px-6 text-center">
          <div class="mb-10 w-full">
            <h1 class="lollms-title-style mb-3 text-5xl font-extrabold tracking-tight drop-shadow-md md:text-7xl transition-transform duration-300 hover:scale-[1.03]">
              {{ appName }}
            </h1>
            <p class="text-xl italic md:text-2xl text-subtitle">
              {{ appSlogan }}
            </p>
            <p v-if="shouldShowLollmsParagraphs" class="mt-4 text-base text-author">
              by ParisNeo
            </p>
             <p class="mt-1 text-sm text-author">
               {{ versionInfo }}
             </p>
          </div>

           <div v-if="shouldShowLollmsFunFacts && randomFact"
                class="mb-8 w-full max-w-xl cursor-pointer rounded-lg border p-4 shadow-lg backdrop-blur-sm transition-all duration-300 card border-blue-300 dark:border-blue-600 hover:bg-blue-200 dark:hover:bg-blue-700 hover:border-blue-400 dark:hover:border-blue-500"
                @click="updateRandomFact">
               <p class="text-base text-blue-800 dark:text-blue-200">
                   <span class="font-semibold text-blue-600 dark:text-blue-400">🤔 Fun Fact: </span>
                   <span v-html="randomFact" class="italic"></span>
               </p>
           </div>

          <div class="w-full max-w-lg">
            <div class="mb-3 h-3 w-full overflow-hidden rounded-full shadow-inner animated-progressbar-bg">
              <div
                class="h-full rounded-full shadow-md transition-all duration-500 ease-out animated-progressbar-fg"
                :style="{ width: `${loadingProgress}%` }"
              ></div>
            </div>

            <div role="status" class="w-full">
              <p class="mb-1 text-lg transition-opacity duration-300 text-loading" :key="loadingInfos">
                {{ loadingInfos }}...
              </p>
              <p class="text-2xl font-semibold text-progress">
                {{ Math.round(loadingProgress) }}%
              </p>
            </div>
          </div>
        </div>
      </div>
    </transition>
</template>

<script>
import { mapState } from 'vuex';

export default {
  name: 'WelcomeScreen',
  props: {
    isReady: {
      type: Boolean,
      required: true
    },
    loadingProgress: {
      type: Number,
      required: true
    },
    loadingInfos: {
      type: String,
      required: true
    },
    versionInfo: {
      type: String,
      required: true
    },
    interestingFacts: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      randomFact: ""
    };
  },
  computed: {
    ...mapState(['config', 'theme_vars']),
    appName() {
      return this.config?.app_custom_name || this.theme_vars?.lollms_title || 'LoLLMs';
    },
    appSlogan() {
      return this.config?.app_custom_slogan || 'One tool to rule them all';
    },
    shouldShowLollmsParagraphs() {
      return !(this.config?.app_custom_name);
    },
    shouldShowLollmsFunFacts() {
      return this.config?.app_show_fun_facts;
    }
  },
  methods: {
    updateRandomFact() {
      let newFact;
      if (this.interestingFacts.length <= 1) {
          this.randomFact = this.interestingFacts.length === 1 ? this.interestingFacts[0] : "";
          return;
      }
      do {
        newFact = this.interestingFacts[Math.floor(Math.random() * this.interestingFacts.length)];
      } while (newFact === this.randomFact);
      this.randomFact = newFact;
    }
  },
  mounted() {
    this.updateRandomFact();
  },
  watch: {
    interestingFacts: {
        handler() {
            this.updateRandomFact();
        },
        immediate: true
    }
  }
};
</script>

<style scoped>

</style>
