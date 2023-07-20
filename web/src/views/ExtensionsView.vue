<template>
<div>
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
export default {
data() {
    return {
    activeExtension: null,
    };
},
computed: {
    activeExtensions() {
    // Filter the extensions to get only active ones
    return this.$store.state.extensionsZoo.filter((extension) => extension.is_active);
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
  