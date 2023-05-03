<script setup>
import { Modal } from 'flowbite-vue'
import { ref } from 'vue'

// const isShowModal = ref(false)
// function closeModal() {
//     isShowModal.value = false
    
// }
// function showModal() {
//     isShowModal.value = true
// }
</script>
<template>
    <!-- <button @click="showModal" type="button"
        class="mt-5 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
        Show modal
    </button> -->
    <Modal :size="size" v-if="ShowModal" @close="closeModal()">
        <template #header>
            <div class="flex items-center text-lg">
                <slot name="header"></slot>
            </div>
        </template>
        <template #body>
            <slot name="body"></slot>
        </template>
        <template #footer>
            <slot name="footer"></slot>
        </template>
    </Modal>
</template>
<script>
export default {
    name: 'ModalSimple',
    props: {
        ShowModal: Boolean
    },methods:{
        closeModal(){
            this.ShowModal  = false
        }
    },
    
}
    </script>