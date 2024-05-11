<template>
    <div class="w-full h-full overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary" v-html="htmlContent"></div>
</template>

<script>
export default {
props: {
    htmlContent: {
    type: String,
    required: true
    }
}
}
</script>
