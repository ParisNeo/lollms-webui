<template>
    <div class="relative" @mouseleave="hideMenu">
        <div @mouseenter="showMenu" class="hover-trigger flex items-center justify-center w-8 h-8">
            <!-- Slot for the trigger element (e.g., button with icon/image) -->
            <slot name="trigger"></slot>
        </div>
        <transition name="fade-and-fly">
            <div v-show="isMenuVisible"
                 @mouseenter="showMenu"
                 :class="['absolute top-full left-0 mt-1 z-50 transform panels-color rounded-md shadow-lg ring-1 ring-blue-300 dark:ring-slate-700 ring-opacity-50 focus:outline-none', menuWidthClass]">
                <div class="p-2 border-b border-blue-200 dark:border-slate-700">
                    <input type="text" v-model="searchQuery" :placeholder="searchPlaceholder" class="w-full input input-sm">
                </div>
                <!-- **** ADJUSTED PADDING & OVERFLOW **** -->
                <div :class="['px-4 py-3 pb-10 max-h-80 overflow-y-auto scrollbar', gridLayoutClass]">
                    <div v-for="item in filteredItems" :key="getItemKey(item)" class="relative group/item flex flex-col items-center">
                        <button @click.prevent="selectItem(item)" :title="getItemName(item)" class="w-12 h-12 rounded-md overflow-hidden transition-transform duration-200 transform group-hover/item:scale-110 focus:outline-none border-2 mb-1" :class="isActive(item) ? activeItemClass : 'border-transparent hover:border-blue-300 dark:hover:border-slate-600'">
                            <img :src="getItemIcon(item)" :alt="getItemName(item)" class="w-full h-full object-cover">
                        </button>
                        <div class="animated-thought-bubble text-center">
                            <!-- **** REMOVED TEXT COLOR CLASSES **** - Inherits from parent or global styles -->
                            <span class="text-xs font-medium mb-1 block cursor-pointer" @click.prevent="selectItem(item)">{{ getItemName(item) }}</span>
                            <!-- Slot for item-specific action buttons -->
                            <slot name="item-actions" :item="item"></slot>
                        </div>
                    </div>
                    <div v-if="filteredItems.length === 0" class="col-span-full text-center text-gray-500 dark:text-gray-400 py-4">
                        No items found.
                    </div>
                </div>
            </div>
        </transition>
    </div>
</template>

<script>
import feather from 'feather-icons';
import { nextTick } from 'vue';

export default {
    name: 'HoverMenu',
    props: {
        items: {
            type: Array,
            required: true
        },
        // Function to determine if an item is the 'active' one for styling
        isActive: {
            type: Function,
            default: () => false
        },
        // Function to extract the unique key for v-for
        itemKeyExtractor: {
            type: Function,
            default: (item) => item.id || item.name // Default assumes 'id' or 'name' as key
        },
        // Function to extract the display name
        itemNameExtractor: {
            type: Function,
            default: (item) => item.name
        },
        // Function to extract the icon URL
        itemIconExtractor: {
            type: Function,
            required: true
        },
        placeholderIcon: {
            type: String,
            required: true
        },
        searchPlaceholder: {
            type: String,
            default: 'Search...'
        },
        menuWidthClass: {
            type: String,
            default: 'w-80' // Default width
        },
        gridLayoutClass: {
            type: String,
            default: 'grid grid-cols-3 gap-x-4 gap-y-4' // Default grid layout
        },
        activeItemClass: {
            type: String,
            default: 'border-blue-500 dark:border-sky-500' // Default active border
        }
    },
    emits: ['select-item'],
    data() {
        return {
            isMenuVisible: false,
            searchQuery: '',
            hideMenuTimeout: null,
        };
    },
    computed: {
        filteredItems() {
            const query = this.searchQuery.toLowerCase().trim();
            if (!query) {
                return this.items;
            }
            return this.items.filter(item =>
                this.getItemName(item)?.toLowerCase().includes(query)
            );
        }
    },
    methods: {
        getItemKey(item) {
           return this.itemKeyExtractor(item);
        },
        getItemName(item) {
            return this.itemNameExtractor(item);
        },
        getItemIcon(item) {
            const icon = this.itemIconExtractor(item);
            return icon || this.placeholderIcon;
        },
        showMenu() {
            clearTimeout(this.hideMenuTimeout);
            this.isMenuVisible = true;
            this.$nextTick(() => feather.replace());
        },
        hideMenu() {
            this.hideMenuTimeout = setTimeout(() => {
                this.isMenuVisible = false;
                // Optionally reset search query on hide:
                // this.searchQuery = '';
            }, 300); // 300ms delay
        },
        selectItem(item) {
            this.$emit('select-item', item);
            // Optionally hide menu on selection
            // this.isMenuVisible = false;
        }
    },
    mounted() {
        nextTick(() => feather.replace());
    },
    updated() {
         // Ensure icons render correctly when items change or menu appears
         if (this.isMenuVisible) {
            nextTick(() => feather.replace());
         }
    }
};
</script>

<style scoped>
/* Replicated fade-and-fly transition if not globally defined */
.fade-and-fly-enter-active,
.fade-and-fly-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-and-fly-enter-from,
.fade-and-fly-leave-to {
  opacity: 0;
  transform: translateY(-10px); /* Fly from slightly above */
}

.fade-and-fly-enter-to,
.fade-and-fly-leave-from {
  opacity: 1;
  transform: translateY(0);
}

/* Scoped styles specific to HoverMenu if needed */
.animated-thought-bubble {
    /* Potential styling for the bubble appearance if desired */
    /* Example: background-color: white; border-radius: 8px; padding: 4px; */
}
/* Ensure trigger area covers the button */
.hover-trigger {
    cursor: pointer; /* Indicate interactivity */
}
</style>