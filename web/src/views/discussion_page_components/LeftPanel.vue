<template>
    <transition name="slide-right">
        <div v-if="showLeftPanel" class="relative flex flex-col no-scrollbar shadow-lg w-[16rem] panels-color scrollbar h-full">
            <!-- Header -->
            <RouterLink :to="{ name: 'discussions' }" class="flex items-center space-x-2 p-2 border-b border-blue-200 dark:border-blue-700 hover:bg-blue-50 dark:hover:bg-blue-800 transition duration-150 ease-in-out">
                <div class="logo-container w-12 h-12 flex-shrink-0">
                    <img class="w-full h-full rounded-full object-cover logo-image border-2 border-blue-300 dark:border-blue-600 shadow-sm"
                         :src="logoSrc"
                         alt="Logo" :title="logoTitle">
                </div>
                <div class="flex flex-col justify-center overflow-hidden">
                    <div class="text-left p-1">
                        <div class="text-md relative inline-block">
                            <span class="relative inline-block font-bold tracking-wide text-blue-800 dark:text-blue-100 text-gradient-title truncate">
                                {{ appName }}
                            </span>
                        </div>
                    </div>
                    <p class="text-blue-600 dark:text-blue-400 text-sm text-subtitle truncate">
                        {{ appSlogan }}
                    </p>
                </div>
            </RouterLink>

            <!-- Toolbar -->
            <Toolbar
                :loading="toolbarLoading"
                :is-checkbox="isCheckbox"
                @create-new-discussion="$emit('create-new-discussion')"
                @add-discussion-to-skills-library="$emit('add-discussion-to-skills-library')"
                @toggle-skills-lib="$emit('toggle-skills-lib')"
                @show-skills-lib="$emit('show-skills-lib')"
                @toggle-edit-mode="isCheckbox = !isCheckbox"
                @reset-database="$emit('reset-database')"
                @export-database="$emit('export-database')"
                @import-discussions="$emit('import-discussions', $event)"
                @import-discussions-bundle="$emit('import-discussions-bundle', $event)"
                @show-model-config="$emit('show-model-config', $event)"
                @set-binding="$emit('set-binding', $event)"
                @copy-model-name="$emit('copy-model-name', $event)"
                @set-model="$emit('set-model', $event)"
                @personality-selected="$emit('personality-selected', $event)"
                @unmount-personality="$emit('unmount-personality', $event)"
                @remount-personality="$emit('remount-personality', $event)"
                @talk-personality="$emit('talk-personality', $event)"
                @personalities-ready="$emit('personalities-ready')"
                @show-personality-list="$emit('show-personality-list')"
            />

            <!-- Search & Sort -->
            <div class="w-full max-w-md mx-auto p-2 border-b border-blue-100 dark:border-blue-800">
                <form @submit.prevent class="relative">
                    <div class="flex items-center space-x-1">
                        <div class="relative flex-grow">
                            <input
                                type="search"
                                id="discussion-search"
                                class="block w-full h-8 pl-8 pr-4 text-sm input"
                                placeholder="Search discussions..."
                                title="Filter discussions by title"
                                v-model="filterTitle"
                                @input="handleSearchInput"
                            />
                            <div class="absolute left-2 top-1/2 -translate-y-1/2 pointer-events-none">
                                <i data-feather="search" class="w-4 h-4 text-gray-400 dark:text-gray-500"></i>
                            </div>
                        </div>
                        <button @click="cycleSortOrder" class="svg-button p-1" :title="`Sort by ${sortBy}: ${sortOrder === 'asc' ? 'Ascending' : 'Descending'}`">
                            <i :data-feather="sortIcon" class="w-4 h-4"></i>
                        </button>
                         <button @click="cycleSortBy" class="svg-button p-1" :title="`Sorting by: ${sortByLabel}`">
                            <i :data-feather="sortBy === 'date' ? 'calendar' : 'type'" class="w-4 h-4"></i>
                        </button>
                    </div>
                </form>
            </div>

            <!-- Bulk Actions (Checkbox Mode) -->
            <div v-if="isCheckbox" class="w-full p-2 bg-blue-100 dark:bg-blue-900 border-b border-blue-200 dark:border-blue-700">
                <div class="flex flex-col space-y-1">
                    <p v-if="selectedDiscussions.length > 0" class="text-sm text-blue-700 dark:text-blue-200">Selected: {{ selectedDiscussions.length }}</p>
                    <div class="flex space-x-1 items-center">
                        <!-- Delete -->
                        <button v-if="!showConfirmation && selectedDiscussions.length > 0" class="svg-button text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-200" title="Remove selected" type="button" @click.stop="showConfirmation = true">
                            <i data-feather="trash" class="w-5 h-5"></i>
                        </button>
                        <div v-if="showConfirmation" class="flex space-x-1 items-center">
                            <button class="svg-button text-green-500 hover:text-green-700 dark:text-green-400 dark:hover:text-green-200" title="Confirm removal" type="button" @click.stop="deleteSelectedDiscussions">
                                <i data-feather="check" class="w-5 h-5"></i>
                            </button>
                            <button class="svg-button text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-200" title="Cancel removal" type="button" @click.stop="showConfirmation = false">
                                <i data-feather="x" class="w-5 h-5"></i>
                            </button>
                        </div>
                        <!-- Export -->
                         <button v-if="selectedDiscussions.length > 0" class="svg-button text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 rotate-90" title="Export selected to a json file" type="button" @click.stop="$emit('export-discussions-as-json', selectedDiscussions)">
                            <i data-feather="codepen" class="w-5 h-5"></i>
                        </button>
                        <button v-if="selectedDiscussions.length > 0" class="svg-button text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 rotate-90" title="Export selected to a folder" type="button" @click.stop="$emit('export-discussions-to-folder', selectedDiscussions)">
                            <i data-feather="folder" class="w-5 h-5"></i>
                        </button>
                        <button v-if="selectedDiscussions.length > 0" class="svg-button text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200" title="Export selected to a markdown file" type="button" @click.stop="$emit('export-discussions-as-markdown', selectedDiscussions)">
                            <i data-feather="bookmark" class="w-5 h-5"></i>
                        </button>
                         <!-- Select All / Deselect All -->
                         <button class="svg-button text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200" :title="isAllSelected ? 'Deselect All Visible' : 'Select All Visible'" type="button" @click.stop="selectAllDiscussions">
                             <i :data-feather="isAllSelected ? 'minus-square' : 'check-square'" class="w-5 h-5"></i>
                         </button>
                         <!-- Star/Unstar Selected -->
                          <button v-if="selectedDiscussions.length > 0" class="svg-button text-yellow-500 hover:text-yellow-700 dark:text-yellow-400 dark:hover:text-yellow-200" :title="selectedDiscussions.some(d=>d.isStarred) ? 'Unstar Selected':'Star Selected'" type="button" @click.stop="toggleStarSelectedDiscussions">
                             <i :data-feather="selectedDiscussions.some(d=>d.isStarred) ? 'star' : 'star'" :fill="selectedDiscussions.some(d=>d.isStarred) ? 'currentColor' : 'none'" class="w-5 h-5"></i>
                         </button>
                    </div>
                </div>
            </div>

            <!-- Discussions List -->
            <div id="leftPanelScroll" class="flex flex-col flex-grow overflow-y-auto overflow-x-hidden scrollbar"
                 @dragover.prevent="isDragOverDiscussion = true" @dragleave="isDragOverDiscussion = false" @drop.prevent="handleDrop">
                 <div class="relative flex flex-col flex-grow mb-10 z-0 w-full">
                    <div class="mx-0 flex flex-col flex-grow w-full" :class="isDragOverDiscussion ? 'opacity-50 border-2 border-dashed border-blue-500' : ''">
                         <div id="dis-list" :class="(filterInProgress || toolbarLoading) ? 'opacity-20 pointer-events-none' : ''" class="flex flex-col flex-grow w-full pb-10">
                             <TransitionGroup name="discussionsList">
                                <template v-for="item in groupedDiscussions" :key="item.key">
                                    <!-- Group Header -->
                                    <div v-if="item.type === 'header'"
                                         class="sticky top-0 z-10 px-2 py-1 bg-gray-100 dark:bg-gray-800 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider shadow-sm flex items-center justify-between cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                                         @click="toggleSection(item.key)">
                                        <span>{{ item.label }}</span>
                                        <i :data-feather="item.collapsed ? 'chevron-right' : 'chevron-down'" class="w-4 h-4"></i>
                                    </div>
                                    <!-- Discussion Item -->
                                    <Discussion
                                        v-if="item.type === 'discussion' && !item.collapsed"
                                        :id="item.data.id"
                                        :title="item.data.title"
                                        :selected="currentDiscussion && currentDiscussion.id === item.data.id"
                                        :loading="item.data.loading"
                                        :isCheckbox="isCheckbox"
                                        :checkBoxValue="item.data.checkBoxValue"
                                        :is-starred="item.data.isStarred"
                                        :openfolder_enabled="true"
                                        @select="selectDiscussion(item.data)"
                                        @delete="deleteDiscussion(item.data)"
                                        @openFolder="$emit('open-folder', item.data)"
                                        @editTitle="$emit('edit-title', $event)"
                                        @makeTitle="$emit('make-title', item.data)"
                                        @checked="checkUncheckDiscussion"
                                        @toggle-star="toggleStarDiscussion(item.data)"
                                    />
                                </template>
                            </TransitionGroup>
                            <div v-if="groupedDiscussions.length === 0 && !filterInProgress && !toolbarLoading" class="p-4 text-center text-blue-600 dark:text-blue-400">
                                <p>No discussions found.</p>
                                <p v-if="filterTitle" class="text-sm">Try adjusting your search or filters.</p>
                            </div>
                            <div v-if="filterInProgress" class="p-4 text-center text-blue-500 dark:text-blue-400">
                                <p>Loading discussions...</p>
                            </div>
                         </div>
                    </div>
                </div>
            </div>

            <!-- Footer -->
            <div class="flex flex-row items-center justify-center border-t border-blue-200 dark:border-blue-700 p-1">
                <div class="chat-bar text-center flex items-center justify-center w-full cursor-pointer hover:bg-blue-100 dark:hover:bg-blue-700 rounded transition duration-150 ease-in-out" @click="$emit('show-database-selector')">
                    <button class="svg-button p-1">
                        <i data-feather="database" class="w-4 h-4 mr-1"></i>
                    </button>
                    <p class="text-center font-semibold text-xs drop-shadow-md align-middle text-blue-700 dark:text-blue-300 truncate">
                        {{ formattedDatabaseName }}
                    </p>
                </div>
            </div>
        </div>
    </transition>
</template>

<script>
import feather from 'feather-icons';
import { nextTick } from 'vue';
import { mapState } from 'vuex'; // Removed mapGetters
import { RouterLink } from 'vue-router';
import storeLogo from '@/assets/logo.png';
import Discussion from './Discussion.vue';
import Toolbar from './Toolbar.vue';

const isToday = (someDate) => {
    const today = new Date();
    return someDate.getDate() === today.getDate() &&
           someDate.getMonth() === today.getMonth() &&
           someDate.getFullYear() === today.getFullYear();
};

const isYesterday = (someDate) => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    return someDate.getDate() === yesterday.getDate() &&
           someDate.getMonth() === yesterday.getMonth() &&
           someDate.getFullYear() === yesterday.getFullYear();
};

export default {
    name: 'LeftPanel',
    components: { Discussion, RouterLink, Toolbar },
    props: {
        showLeftPanel: Boolean,
        discussionsList: Array, // Expects array with { id, title, created_at, loading, isStarred }
        currentDiscussion: Object,
        toolbarLoading: Boolean,
        formattedDatabaseName: String,
    },
    emits: [
        'select-discussion', 'delete-discussion', 'open-folder', 'edit-title', 'make-title',
        'create-new-discussion', 'add-discussion-to-skills-library', 'toggle-skills-lib', 'show-skills-lib',
        'reset-database', 'export-database', 'import-discussions', 'import-discussions-bundle',
        'show-model-config', 'set-binding', 'copy-model-name', 'set-model', 'personality-selected',
        'unmount-personality', 'remount-personality', 'talk-personality', 'personalities-ready', 'show-personality-list',
        'delete-selected', 'export-discussions-as-json', 'export-discussions-to-folder', 'export-discussions-as-markdown',
        'show-database-selector', 'import-discussion-file', 'toggle-star-discussion'
    ],
    data() {
        return {
            filterTitle: '',
            filterInProgress: false,
            isCheckbox: false,
            showConfirmation: false,
            isDragOverDiscussion: false,
            searchTimeout: null,
            localDiscussionsState: [], // Holds { id, checkBoxValue }
            sortBy: 'date',
            sortOrder: 'desc',
            collapsedSections: { starred: false, today: false, yesterday: true, older: true }, // Keep track of collapsed state for each group
        };
    },
    computed: {
        ...mapState(['config', 'theme_vars']),

        logoSrc() {
            return this.config?.app_custom_logo ? `/user_infos/${this.config.app_custom_logo}` : storeLogo;
        },
        logoTitle() {
            return this.config?.app_custom_name || 'LoLLMs WebUI';
        },
        appName() {
            return this.config?.app_custom_name || 'LoLLMS WebUI';
        },
        appSlogan() {
            return this.config?.app_custom_slogan || 'One tool to rule them all';
        },
        sortIcon() {
            return this.sortOrder === 'asc' ? 'arrow-up' : 'arrow-down';
        },
         sortByLabel() {
            const labels = { date: 'Date', title: 'Title' };
            return labels[this.sortBy] || 'Date';
        },
        // Enhance the prop list with local checkbox state and parsed date
        enhancedDiscussions() {
            return (this.discussionsList || []).map(disc => {
                const localState = this.localDiscussionsState.find(ld => ld.id === disc.id);
                const creationDate = disc.created_at ? new Date(disc.created_at) : new Date(0);
                return {
                    ...disc, // Includes id, title, created_at, loading, isStarred (from prop)
                    checkBoxValue: localState ? localState.checkBoxValue : false,
                    creationDate: creationDate, // Parsed date for sorting/grouping
                };
            });
        },
        // Primarily used for 'Select All' logic and determining if all *visible* items are selected
         filteredDiscussions() {
             if (!this.filterTitle.trim()) {
                return this.enhancedDiscussions;
            }
            const query = this.filterTitle.toLowerCase();
            return this.enhancedDiscussions.filter(item => item.title && item.title.toLowerCase().includes(query));
        },
        // Groups discussions by Starred, Today, Yesterday, Older, applies filtering and sorting
        groupedDiscussions() {
            const starred = [];
            const today = [];
            const yesterday = [];
            const older = [];

            // Filter first based on search query using the enhanced list
            const filtered = this.enhancedDiscussions.filter(item => {
                if (!this.filterTitle.trim()) return true;
                const query = this.filterTitle.toLowerCase();
                return item.title && item.title.toLowerCase().includes(query);
            });

            // Separate into groups (Starred first, then by date)
            filtered.forEach(disc => {
                if (disc.isStarred) { // Use isStarred from the enhanced list (which came from props)
                    starred.push(disc);
                } else {
                    const creationDate = disc.creationDate;
                    if (isToday(creationDate)) {
                        today.push(disc);
                    } else if (isYesterday(creationDate)) {
                        yesterday.push(disc);
                    } else {
                        older.push(disc);
                    }
                }
            });

            // Sort within each group based on current settings
            const sortFn = (a, b) => {
                let comparison = 0;
                if (this.sortBy === 'date') {
                    comparison = b.creationDate - a.creationDate; // Descending by date default
                } else if (this.sortBy === 'title') {
                    comparison = (a.title || '').localeCompare(b.title || ''); // Ascending by title default
                }
                const orderMultiplier = (this.sortBy === 'date' && this.sortOrder === 'asc') || (this.sortBy === 'title' && this.sortOrder === 'desc') ? -1 : 1;
                return comparison * orderMultiplier;
            };

            starred.sort(sortFn);
            today.sort(sortFn);
            yesterday.sort(sortFn);
            older.sort(sortFn);

            const groups = [];
            const addGroup = (label, key, items) => {
                 if (items.length > 0) {
                     const isCollapsed = this.collapsedSections[key] || false;
                     groups.push({ type: 'header', label: label, key: key, collapsed: isCollapsed });
                     items.forEach(item => groups.push({ type: 'discussion', data: item, key: `disc-${item.id}`, collapsed: isCollapsed }));
                 }
            }

            addGroup('Starred', 'starred', starred);
            addGroup('Today', 'today', today);
            addGroup('Yesterday', 'yesterday', yesterday);
            addGroup('Older', 'older', older);

            return groups;
        },
        // Determines which discussions are currently selected based on local checkbox state
        selectedDiscussions() {
            // We need to filter enhancedDiscussions based on local checkbox state
             return this.enhancedDiscussions.filter(item => {
                 const localState = this.localDiscussionsState.find(ld => ld.id === item.id);
                 return localState && localState.checkBoxValue;
            });
        },
        // Determines if all *visible* (filtered) discussions are currently selected
        isAllSelected() {
            const targetList = this.filteredDiscussions; // Discussions matching the current filter
            if (targetList.length === 0) return false;
            const selectedIds = new Set(this.selectedDiscussions.map(d => d.id));
            return targetList.every(item => selectedIds.has(item.id));
        }
    },
    methods: {
        toggleSection(key) {
            if (key in this.collapsedSections) {
                this.collapsedSections[key] = !this.collapsedSections[key];
                // Force reactivity update if needed, though computed should handle it
                // this.$forceUpdate(); // Avoid if possible
                this.$nextTick(() => feather.replace());
            }
        },
        handleSearchInput() {
             this.filterInProgress = true;
             clearTimeout(this.searchTimeout);
             this.searchTimeout = setTimeout(() => {
                 this.filterInProgress = false;
                 this.$nextTick(() => feather.replace());
             }, 300);
        },
        cycleSortOrder() {
            this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
            this.$nextTick(() => feather.replace());
        },
        cycleSortBy() {
            this.sortBy = this.sortBy === 'date' ? 'title' : 'date';
            this.$nextTick(() => feather.replace());
        },
        selectDiscussion(item) {
             if (this.toolbarLoading || this.filterInProgress) return;
             this.$emit('select-discussion', item);
        },
        deleteDiscussion(item) {
             this.localDiscussionsState = this.localDiscussionsState.filter(d => d.id !== item.id);
             this.$emit('delete-discussion', item.id); // Emit ID to parent
        },
        checkUncheckDiscussion({ id, checked }) {
            const index = this.localDiscussionsState.findIndex(d => d.id === id);
            if (index !== -1) {
                this.localDiscussionsState[index].checkBoxValue = checked;
            } else {
                 // Check if the item actually exists in the main list before adding local state
                 if (this.discussionsList.some(d => d.id === id)) {
                    this.localDiscussionsState.push({ id: id, checkBoxValue: checked });
                 } else {
                     console.warn("Tried to check/uncheck an item not present in discussionsList:", id);
                 }
            }
        },
        selectAllDiscussions() {
            const targetState = !this.isAllSelected;
            const filteredIds = new Set(this.filteredDiscussions.map(d => d.id)); // Get IDs of currently visible/filtered items

             // Update local state only for visible items
             this.enhancedDiscussions.forEach(item => {
                 if (filteredIds.has(item.id)) { // Apply only to filtered items
                     const index = this.localDiscussionsState.findIndex(d => d.id === item.id);
                     if (index !== -1) {
                         this.localDiscussionsState[index].checkBoxValue = targetState;
                     } else if (targetState) {
                         // Only add if setting to true and wasn't already in local state
                         this.localDiscussionsState.push({ id: item.id, checkBoxValue: targetState });
                     }
                 }
             });
            this.$nextTick(() => feather.replace());
        },
        deleteSelectedDiscussions() {
             const idsToDelete = this.selectedDiscussions.map(d => d.id);
             // Clear local checkbox state for deleted items
             this.localDiscussionsState = this.localDiscussionsState.filter(ld => !idsToDelete.includes(ld.id));
             this.$emit('delete-selected', idsToDelete); // Emit array of IDs
             this.showConfirmation = false;
             this.isCheckbox = false; // Exit checkbox mode after deletion
        },
        handleDrop(event) {
            this.isDragOverDiscussion = false;
            const files = event.dataTransfer.files;
            if (files.length === 1 && files[0].type === 'application/json') {
                 this.$emit('import-discussion-file', files[0]);
            } else {
                 this.$store.state.toast.showToast("Please drop a single JSON file to import.", 4, false);
            }
        },
        toggleStarDiscussion(item) {
             this.$emit('toggle-star-discussion', item); // Emit the discussion item itself
        },
        toggleStarSelectedDiscussions() {
            const selected = this.selectedDiscussions;
            if (selected.length === 0) return;
            // Determine target state: if ANY selected are NOT starred, we STAR all. If ALL selected ARE starred, we UNSTAR all.
            const shouldStar = selected.some(item => !item.isStarred);

             selected.forEach(item => {
                 // Emit toggle only if the item's current state needs changing
                 if (item.isStarred !== shouldStar) {
                    this.toggleStarDiscussion(item);
                 }
            });
            this.$nextTick(() => feather.replace());
        },
        // Syncs local checkbox state with the incoming discussions list prop
        syncLocalState(newList) {
            const currentIds = new Set((newList || []).map(d => d.id));
            // Keep state for items that still exist, discard state for removed items
            const updatedLocalState = this.localDiscussionsState.filter(ld => currentIds.has(ld.id));
            // Add default (unchecked) state for new items
            (newList || []).forEach(disc => {
                if (!updatedLocalState.some(ld => ld.id === disc.id)) {
                    updatedLocalState.push({ id: disc.id, checkBoxValue: false });
                }
            });
            this.localDiscussionsState = updatedLocalState;
        }
    },
    watch: {
        discussionsList: {
            handler(newList) {
                 this.syncLocalState(newList); // Keep local checkbox state aligned
                 this.$nextTick(() => feather.replace()); // Refresh icons after list changes
            },
            immediate: true, // Sync on initial load
            deep: false // Shallow watch is enough if parent guarantees object identity changes
        },
        isCheckbox(newVal) {
             this.$nextTick(() => feather.replace());
             if (!newVal) {
                 this.showConfirmation = false;
                 // Optionally clear selections when exiting checkbox mode
                 // this.localDiscussionsState.forEach(state => state.checkBoxValue = false);
             }
        },
        // Watch computed properties only if necessary, often nextTick in methods is better
        // groupedDiscussions() { this.$nextTick(() => feather.replace()); },
        // filterTitle() { /* handled by handleSearchInput */ },
        // sortBy() { this.$nextTick(() => feather.replace()); },
        // sortOrder() { this.$nextTick(() => feather.replace()); }
    },
    mounted() {
        this.syncLocalState(this.discussionsList); // Initial sync
        nextTick(() => {
            feather.replace();
        });
    },
    updated() {
        // Generally avoid feather.replace() here unless absolutely necessary.
        // Prefer calling it specifically in methods/watchers after DOM changes.
        // nextTick(() => { feather.replace(); });
    }
};
</script>

<style scoped>
/* Transitions for list items */
.discussionsList-move,
.discussionsList-enter-active,
.discussionsList-leave-active {
  transition: all 0.3s ease;
}

.discussionsList-enter-from,
.discussionsList-leave-to {
  opacity: 0;
  transform: translateX(-20px); /* Adjusted transform */
}

.discussionsList-leave-active {
  position: absolute;
  width: calc(100% - 1rem); /* Adjust based on padding/margins inside the scroll container */
  box-sizing: border-box;
}

/* Transition for the panel itself */
.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease-out;
}

.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(-100%);
}

/* Ensure sticky headers work well */
.sticky {
    position: -webkit-sticky; /* For Safari */
    position: sticky;
}
</style>