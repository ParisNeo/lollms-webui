<template>
    <div>
      <div v-if="show" class="fixed top-0 left-0 w-full h-full flex justify-center items-center bg-black bg-opacity-50">
        <div class="bg-white p-8 rounded">
          <h2 class="text-xl font-bold mb-4">{{ promptText }}</h2>
          <input type="text" v-model="inputText" class="border border-gray-300 px-4 py-2 rounded mb-4" />
          <button @click="ok" class="bg-blue-500 text-white px-4 py-2 rounded mr-2">OK</button>
          <button @click="cancel" class="bg-gray-500 text-white px-4 py-2 rounded">Cancel</button>
        </div>
      </div>
    </div>
</template>

<script>
    export default {
        data() {
            return {
            show: false,
            prompt: "",
            inputText: ""
            };
        },
        methods: {
            showPanel() {
            this.show = true;
            },
            ok() {
            this.show = false;
            this.$emit("ok", this.inputText);
            },
            cancel() {
            this.show = false;
            this.inputText = "";
            }
        },
        props: {
            promptText: {
            type: String,
            required: true
            }
        },
        watch: {
            promptText(newPrompt) {
            this.prompt = newPrompt;
            }
        }
    };
</script>
