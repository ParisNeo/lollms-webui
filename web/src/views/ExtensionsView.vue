<template>
    <div class="container overflow-y-scroll flex flex-col shadow-lg p-10 pt-0 overflow-y-scroll w-full dark:bg-bg-dark scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
        <div v-if="activeExtensions.length > 0">
        <div v-for="extension in activeExtensions" :key="extension.name" @click="showExtensionPage(extension)">
            <div :class="{ 'active-tab': extension === activeExtension }">{{ extension.name }}</div>
        </div>
        <div v-if="activeExtension">
            <!-- Render the selected extension's page here -->
            <iframe :src="activeExtension.page" width="100%" height="500px" frameborder="0"></iframe>
        </div>
        </div>
        <div v-else>
        <p>No extension is active. Please install and activate an extension.</p>
        </div>
    </div>
</template>

<script>
import axios from "axios";
import feather from 'feather-icons'
import {flattenObject} from '../main.js'
export default {
data() {
    return {
    activeExtension: null,
    };
},
computed: {
    activeExtensions() {
    // Filter the extensions to get only active ones
    console.log(this.$store.state.extensionsZoo)
    console.log(flattenObject(this.$store.state.extensionsZoo))
    return this.$store.state.extensionsZoo;
    },
},
methods: {
    showExtensionPage(extension) {
    // Set the selected extension as active to render its page
    this.activeExtension = extension;
    },
},
};
</script>

<style>
.active-tab {
/* Style the active tab as you like */
font-weight: bold;
}
</style>
  