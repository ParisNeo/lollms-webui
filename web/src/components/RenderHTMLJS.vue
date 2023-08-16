<template>
    <div>
      <div v-html="htmlContent"></div>
    </div>
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
