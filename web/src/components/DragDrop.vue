<template>
    <div  class="sticky top-0 mx-auto my-auto h-3/5 w-3/5  bg-red-500">
asdasdas
    </div>
</template>

<script>
export default {
    setup () {
        

        return {}
    },
    methods: {
    startDrag(event, item) {
      event.dataTransfer.dropEffect = 'move'
      event.dataTransfer.effectAllowed = 'move'
      event.dataTransfer.setData('itemID', item.id)
    },
    onDrop(event, list) {
      const itemID = event.dataTransfer.getData('itemID')
      const item = this.items.find((item) => item.id == itemID)
      item.list = list
    },
  },
}
</script>

