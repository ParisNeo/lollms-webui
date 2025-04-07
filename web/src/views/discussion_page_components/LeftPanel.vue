<template>
    <transition name="slide-right">
        <div v-if="showLeftPanel" class="relative flex flex-col no-scrollbar shadow-lg w-[16rem] panels-color scrollbar h-full">
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

            <div v-if="isCheckbox" class="w-full p-2 bg-blue-100 dark:bg-blue-900 border-b border-blue-200 dark:border-blue-700">
                <div class="flex flex-col space-y-1">
                    <p v-if="selectedDiscussions.length > 0" class="text-sm text-blue-700 dark:text-blue-200">Selected: {{ selectedDiscussions.length }}</p>
                    <div v-if="selectedDiscussions.length > 0" class="flex space-x-1 items-center">
                        <button v-if="!showConfirmation" class="svg-button text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-200" title="Remove selected" type="button" @click.stop="showConfirmation = true">
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
                    </div>
                    <div class="flex space-x-1 items-center">
                        <button class="svg-button text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 rotate-90" title="Export selected to a json file" type="button" @click.stop="$emit('export-discussions-as-json', selectedDiscussions)">
                            <i data-feather="codepen" class="w-5 h-5"></i>
                        </button>
                        <button class="svg-button text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 rotate-90" title="Export selected to a folder" type="button" @click.stop="$emit('export-discussions-to-folder', selectedDiscussions)">
                            <i data-feather="folder" class="w-5 h-5"></i>
                        </button>
                        <button class="svg-button text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200" title="Export selected to a markdown file" type="button" @click.stop="$emit('export-discussions-as-markdown', selectedDiscussions)">
                            <i data-feather="bookmark" class="w-5 h-5"></i>
                        </button>
                         <button class="svg-button text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200" title="Select/Deselect All" type="button" @click.stop="selectAllDiscussions">
                             <i :data-feather="isAllSelected ? 'minus-square' : 'check-square'" class="w-5 h-5"></i>
                         </button>
                    </div>
                </div>
            </div>

            <div id="leftPanelScroll" class="flex flex-col flex-grow overflow-y-auto overflow-x-hidden scrollbar"
                 @dragover.prevent="isDragOverDiscussion = true" @dragleave="isDragOverDiscussion = false" @drop.prevent="handleDrop">
                 <div class="relative flex flex-col flex-grow mb-10 z-0 w-full">
                    <div class="mx-0 flex flex-col flex-grow w-full" :class="isDragOverDiscussion ? 'opacity-50 border-2 border-dashed border-blue-500' : ''">
                         <div id="dis-list" :class="(filterInProgress || toolbarLoading) ? 'opacity-20 pointer-events-none' : ''" class="flex flex-col flex-grow w-full pb-10">
                             <TransitionGroup name="discussionsList">
                                <template v-for="item in groupedDiscussions" :key="item.key">
                                    <div v-if="item.type === 'header'"
                                         class="sticky top-0 z-10 px-2 py-1 bg-gray-100 dark:bg-gray-800 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider shadow-sm flex items-center justify-between cursor-pointer hover:bg-gray-200 dark:hover:bg-gray-700"
                                         @click="toggleSection(item.key)">
                                        <span>{{ item.label }}</span>
                                        <i :data-feather="item.collapsed ? 'chevron-right' : 'chevron-down'" class="w-4 h-4"></i>
                                    </div>
                                    <!-- Inside LeftPanel.vue's TransitionGroup -->
                                    <Discussion
                                        v-if="item.type === 'discussion'"
                                        :id="`dis-${item.data.id}`"
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
                            <div v-if="filterInProgress || toolbarLoading" class="p-4 text-center text-blue-500 dark:text-blue-400">
                                <p>Loading discussions...</p>
                            </div>
                         </div>
                    </div>
                </div>
            </div>

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
import { mapState, mapGetters } from 'vuex';
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
        discussionsList: Array,
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
            localDiscussionsState: [],
            sortBy: 'date',
            sortOrder: 'desc',
            collapsedSections: { starred: false, today: false, yesterday: true, older: true },
        };
    },
    computed: {
        ...mapState(['config', 'theme_vars']),
        ...mapGetters(['getStarredDiscussionsSet']),

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
        starredSet() {
            return this.getStarredDiscussionsSet || new Set();
        },
        sortIcon() {
            return this.sortOrder === 'asc' ? 'arrow-up' : 'arrow-down';
        },
         sortByLabel() {
            const labels = { date: 'Date', title: 'Title' };
            return labels[this.sortBy] || 'Date';
        },
        enhancedDiscussions() {
            return (this.discussionsList || []).map(disc => {
                const localState = this.localDiscussionsState.find(ld => ld.id === disc.id);
                const creationDate = disc.created_at ? new Date(disc.created_at) : new Date(0); // Use created_at
                return {
                    ...disc,
                    checkBoxValue: localState ? localState.checkBoxValue : false,
                    isStarred: this.starredSet.has(String(disc.id)),
                    creationDate: creationDate,
                };
            });
        },
        filteredDiscussions() {
            // This is primarily used for 'Select All' logic now, filtering happens inside groupedDiscussions
             if (!this.filterTitle.trim()) {
                return this.enhancedDiscussions;
            }
            const query = this.filterTitle.toLowerCase();
            return this.enhancedDiscussions.filter(item => item.title && item.title.toLowerCase().includes(query));
        },
        groupedDiscussions() {
            const starred = [];
            const today = [];
            const yesterday = [];
            const older = [];

            // Filter first based on search query
            const filtered = this.enhancedDiscussions.filter(item => {
                if (!this.filterTitle.trim()) return true;
                const query = this.filterTitle.toLowerCase();
                return item.title && item.title.toLowerCase().includes(query);
            });

            // Separate starred from unstarred
            filtered.forEach(disc => {
                if (disc.isStarred) {
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
                // Apply sort order direction
                const orderMultiplier = (this.sortBy === 'date' && this.sortOrder === 'asc') || (this.sortBy === 'title' && this.sortOrder === 'desc') ? -1 : 1;
                return comparison * orderMultiplier;
            };

            starred.sort(sortFn);
            today.sort(sortFn);
            yesterday.sort(sortFn);
            older.sort(sortFn);

            const groups = [];

            // Add Starred section
            if (starred.length > 0) {
                groups.push({ type: 'header', label: 'Starred', key: 'starred', collapsed: this.collapsedSections.starred });
                if (!this.collapsedSections.starred) {
                    starred.forEach(item => groups.push({ type: 'discussion', data: item, key: `disc-${item.id}` }));
                }
            }

            // Add Today section
            if (today.length > 0) {
                groups.push({ type: 'header', label: 'Today', key: 'today', collapsed: this.collapsedSections.today });
                 if (!this.collapsedSections.today) {
                    today.forEach(item => groups.push({ type: 'discussion', data: item, key: `disc-${item.id}` }));
                }
            }

            // Add Yesterday section
            if (yesterday.length > 0) {
                 groups.push({ type: 'header', label: 'Yesterday', key: 'yesterday', collapsed: this.collapsedSections.yesterday });
                if (!this.collapsedSections.yesterday) {
                    yesterday.forEach(item => groups.push({ type: 'discussion', data: item, key: `disc-${item.id}` }));
                }
            }

            // Add Older section
            if (older.length > 0) {
                groups.push({ type: 'header', label: 'Older', key: 'older', collapsed: this.collapsedSections.older });
                 if (!this.collapsedSections.older) {
                    older.forEach(item => groups.push({ type: 'discussion', data: item, key: `disc-${item.id}` }));
                }
            }
            return groups;
        },

        selectedDiscussions() {
            // Selected items are based on the local checkbox state, across all filtered items
            return this.filteredDiscussions.filter(item => {
                 const localState = this.localDiscussionsState.find(ld => ld.id === item.id);
                 return localState && localState.checkBoxValue;
            });
        },
        isAllSelected() {
            // Check if all items matching the current filter are selected
            const targetList = this.filteredDiscussions;
            if (targetList.length === 0) return false;
            const selectedIds = new Set(this.selectedDiscussions.map(d => d.id));
            return targetList.every(item => selectedIds.has(item.id));
        }
    },
    methods: {
        toggleSection(key) {
            if (key in this.collapsedSections) {
                this.collapsedSections[key] = !this.collapsedSections[key];
                // Recompute groupedDiscussions implicitly updates the view
                this.$nextTick(() => feather.replace());
            }
        },
        handleSearchInput() {
             this.filterInProgress = true;
             clearTimeout(this.searchTimeout);
             this.searchTimeout = setTimeout(() => {
                 this.filterInProgress = false;
                 // Vue reactivity handles the update, feather needs refresh
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
             this.$emit('delete-discussion', item.id);
        },
        checkUncheckDiscussion({ id, checked }) {
            const index = this.localDiscussionsState.findIndex(d => d.id === id);
            if (index !== -1) {
                this.localDiscussionsState[index].checkBoxValue = checked;
            } else {
                 // Ensure item exists in discussionsList before adding to local state if needed
                 if (this.discussionsList.some(d => d.id === id)) {
                    this.localDiscussionsState.push({ id: id, checkBoxValue: checked });
                 }
            }
        },
        selectAllDiscussions() {
            const targetState = !this.isAllSelected;
            const filteredIds = new Set(this.filteredDiscussions.map(d => d.id)); // Use filtered list

            // Update local state for all items matching the filter
             this.enhancedDiscussions.forEach(item => {
                 if (filteredIds.has(item.id)) {
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
             this.localDiscussionsState = this.localDiscussionsState.filter(ld => !idsToDelete.includes(ld.id));
             this.$emit('delete-selected', idsToDelete);
             this.showConfirmation = false;
             this.isCheckbox = false; // Exit checkbox mode after deletion
        },
        handleDrop(event) {
            this.isDragOverDiscussion = false;
            const files = event.dataTransfer.files;
            if (files.length === 1 && files[0].type === 'application/json') {
                 this.$emit('import-discussion-file', files[0]);
            } else {
                 // Consider using a more integrated notification system if available
                 alert("Please drop a single JSON file to import.");
                 // this.$store.dispatch('showToast', { message: "Please drop a single JSON file.", type: 'warning' });
            }
        },
        toggleStarDiscussion(item) {
             this.$emit('toggle-star-discussion', item);
             // Assuming the parent/Vuex handles the actual state change and prop update
        },
        toggleStarSelectedDiscussions() {
            const selected = this.selectedDiscussions;
            if (selected.length === 0) return;
            // Determine if we are starring or unstarring based on the first selected item's state
            const isStarring = selected.length > 0 ? !selected[0].isStarred : true; // Default to starring if unsure
             selected.forEach(item => {
                 // Only emit toggle if the item's current state doesn't match the target state
                 if (item.isStarred !== isStarring) {
                    this.toggleStarDiscussion(item);
                 }
            });
        },
        syncLocalState(newList) {
            // Ensure localDiscussionsState reflects the current discussionsList, preserving checkbox values
            const currentIds = new Set((newList || []).map(d => d.id));
            const updatedLocalState = this.localDiscussionsState.filter(ld => currentIds.has(ld.id)); // Keep existing states for current items
            (newList || []).forEach(disc => {
                 // Add state for new items if they don't exist
                if (!updatedLocalState.some(ld => ld.id === disc.id)) {
                    updatedLocalState.push({ id: disc.id, checkBoxValue: false });
                }
            });
            this.localDiscussionsState = updatedLocalState;
        }
    },
    watch: {
        discussionsList: {
            handler(newList, oldList) {
                 // Check if lists differ significantly before syncing to avoid unnecessary updates
                 if (JSON.stringify(newList) !== JSON.stringify(oldList)) {
                     this.syncLocalState(newList);
                 }
                 // Always refresh icons after data changes that might affect layout/content
                 this.$nextTick(() => feather.replace());
            },
            immediate: true,
            deep: true // Watch for changes within discussion objects if necessary (e.g., title changes externally)
        },
        isCheckbox(newVal) {
             this.$nextTick(() => feather.replace());
             if (!newVal) {
                 this.showConfirmation = false;
                 // Optionally clear local checkbox state when exiting checkbox mode
                 // this.localDiscussionsState.forEach(state => state.checkBoxValue = false);
             }
        },
        showConfirmation() {
             this.$nextTick(() => feather.replace());
        },
        // Watch groupedDiscussions might be too expensive, rely on reactivity + nextTick in methods
        // groupedDiscussions() {
        //      this.$nextTick(() => feather.replace());
        // }
        filterTitle() {
             // No need for explicit feather call here, handleSearchInput does it after debounce
        },
        sortBy() {
            this.$nextTick(() => feather.replace());
        },
        sortOrder() {
            this.$nextTick(() => feather.replace());
        }
    },
    mounted() {
        // Initial sync and icon replacement
        this.syncLocalState(this.discussionsList);
        nextTick(() => {
            feather.replace();
        });
    },
    updated() {
        // Ensure icons are replaced after any reactive update
        // Be cautious with this, might cause performance issues if updates are frequent.
        // Often better to call feather.replace() specifically after actions that change icons.
        // nextTick(() => {
        //     feather.replace();
        // });
    }
};
</script>

<style scoped>
.discussionsList-move,
.discussionsList-enter-active,
.discussionsList-leave-active {
  transition: all 0.3s ease;
}

.discussionsList-enter-from,
.discussionsList-leave-to {
  opacity: 0;
  transform: translateX(-15px);
}

/* Ensure leaving items don't disrupt layout */
.discussionsList-leave-active {
  position: absolute;
  /* Adjust width based on actual panel width minus padding/margins if necessary */
  width: calc(16rem - 1rem); /* Example: panel width 16rem, padding x 0.5rem each side */
  /* Or use percentage if parent width is reliable */
  /* width: 100%; */
}


.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease-out;
}

.slide-right-enter-from,
.slide-right-leave-to {
  transform: translateX(-100%);
}
</style>