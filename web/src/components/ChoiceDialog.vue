<template>
  <transition name="fade">
    <div v-if="show" class="fixed inset-0 flex items-center justify-center bg-black bg-opacity-60 z-50 backdrop-blur-sm" @click.self="closeDialog">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-5 sm:p-6 w-full max-w-lg mx-4 sm:mx-0 flex flex-col gap-4 max-h-[90vh]">
        <h2 class="text-xl sm:text-2xl font-semibold text-gray-800 dark:text-white flex items-center gap-2 flex-shrink-0">
          <slot name="header-icon">
            <svg class="w-6 h-6 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"></path>
            </svg>
          </slot>
          <span class="truncate">{{ title }}</span>
        </h2>

        <div class="flex-grow bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 overflow-y-auto min-h-[150px] scrollbar-thin scrollbar-thumb-gray-400 scrollbar-track-gray-200 dark:scrollbar-thumb-gray-600 dark:scrollbar-track-gray-800">
          <ul v-if="displayChoices.length > 0">
            <li
              v-for="choice in displayChoices"
              :key="choice.id"
              class="hover:bg-gray-100 dark:hover:bg-gray-600/80 transition duration-150 ease-in-out border-b border-gray-200 dark:border-gray-600 last:border-b-0"
              :class="{
                'bg-blue-50 dark:bg-blue-900/40': choice.id === selectedChoiceId && !choice.isEditing,
                'ring-1 ring-inset ring-blue-500 dark:ring-blue-600': choice.isEditing,
                'cursor-pointer': !choice.isEditing
              }"
              @click="!choice.isEditing && selectChoiceInternal(choice)"
            >
              <div class="flex items-center justify-between gap-2 px-3 py-2 sm:px-4 sm:py-2.5 min-h-[48px]">
                <div class="flex-grow min-w-0">
                  <!-- Slot for custom choice rendering -->
                  <slot
                    v-if="!choice.isEditing"
                    name="choice-content"
                    :choice="choices.find(c => c.id === choice.id)"
                    :isSelected="choice.id === selectedChoiceId"
                  >
                    <!-- Default rendering if no slot provided -->
                    <span
                      :class="{'font-semibold text-blue-600 dark:text-blue-400': choice.id === selectedChoiceId}"
                      class="text-gray-800 dark:text-white block truncate"
                      :title="getChoiceDisplayValue(choice)"
                    >
                      {{ getChoiceDisplayValue(choice) }}
                    </span>
                  </slot>

                  <!-- Editing Input -->
                  <input
                    v-if="choice.isEditing && canEdit"
                    :ref="'editInput_' + choice.id"
                    v-model="editingChoiceName"
                    @blur="finishEditing"
                    @keyup="handleEditKeyup"
                    class="bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded px-2 py-1 text-sm w-full focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  >
                </div>

                <!-- Action Buttons -->
                <div class="flex items-center flex-shrink-0 gap-1">
                   <button
                     v-if="canEdit && !choice.isEditing"
                     @click.stop="startEditing(choice)"
                     class="p-1.5 text-blue-500 hover:text-blue-700 dark:hover:text-blue-300 rounded hover:bg-blue-100 dark:hover:bg-gray-700 transition-colors duration-150"
                     title="Edit choice"
                   >
                     <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                   </button>
                   <button
                     v-if="choice.isEditing && canEdit"
                     @click.stop="finishEditing"
                     class="p-1.5 text-green-500 hover:text-green-700 dark:hover:text-green-300 rounded hover:bg-green-100 dark:hover:bg-gray-700 transition-colors duration-150"
                     title="Save changes"
                   >
                     <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>
                   </button>

                  <button
                    v-if="canRemove && !choice.isEditing"
                    @click.stop="handleRemove(choice)"
                    class="p-1.5 text-red-500 hover:text-red-700 dark:hover:text-red-300 rounded hover:bg-red-100 dark:hover:bg-gray-700 transition-colors duration-150"
                    title="Remove choice"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                  </button>
                   <button
                     v-if="choice.isEditing && canEdit"
                     @click.stop="cancelEditing"
                     class="p-1.5 text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 rounded hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors duration-150"
                     title="Cancel editing"
                   >
                     <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
                   </button>
                </div>
              </div>
            </li>
          </ul>
          <div v-else class="flex items-center justify-center h-full text-gray-500 dark:text-gray-400 p-4 text-center">
            <slot name="empty-state">
              {{ emptyChoicesMessage }}
            </slot>
          </div>
        </div>

        <!-- Add New Input Area -->
        <div v-if="canAdd && showInput" class="flex flex-col sm:flex-row gap-2 flex-shrink-0">
          <input
            ref="newChoiceInput"
            v-model="newChoiceName"
            @keyup.enter="addNewChoice"
            @keyup.esc="toggleInput"
            :placeholder="addChoicePlaceholder"
            class="flex-grow border border-gray-300 dark:border-gray-600 p-2 rounded-lg bg-white dark:bg-gray-700 text-gray-800 dark:text-white focus:ring-1 focus:ring-blue-500 focus:border-blue-500 outline-none"
          >
          <button @click="addNewChoice" class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-lg transition duration-150 ease-in-out flex-shrink-0 sm:w-auto w-full">
            Add
          </button>
        </div>

        <!-- Footer Buttons -->
        <div class="flex flex-col sm:flex-row sm:justify-between items-center gap-3 pt-4 border-t border-gray-200 dark:border-gray-700 flex-shrink-0">
           <div class="w-full sm:w-auto flex-shrink-0 order-2 sm:order-1">
              <button
                 v-if="canAdd"
                 @click="toggleInput"
                 class="w-full bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded-lg transition duration-150 ease-in-out flex items-center justify-center gap-1"
               >
                 <svg v-if="!showInput" class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 5a1 1 0 011 1v3h3a1 1 0 110 2h-3v3a1 1 0 11-2 0v-3H6a1 1 0 110-2h3V6a1 1 0 011-1z" clip-rule="evenodd"></path></svg>
                 <svg v-else class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg>
                 <span>{{ showInput ? 'Cancel Add' : addButtonText }}</span>
               </button>
           </div>
           <div class="flex gap-3 w-full sm:w-auto justify-end order-1 sm:order-2">
              <button
                @click="closeDialog"
                type="button"
                class="flex-1 sm:flex-none bg-gray-300 hover:bg-gray-400 text-gray-800 dark:bg-gray-600 dark:hover:bg-gray-500 dark:text-white font-bold py-2 px-4 rounded-lg transition duration-150 ease-in-out"
              >
                Cancel
              </button>
              <button
                @click="validateSelection"
                type="button"
                :disabled="!selectedChoice"
                :class="{
                  'bg-blue-500 hover:bg-blue-600': selectedChoice,
                  'bg-gray-400 dark:bg-gray-500 cursor-not-allowed opacity-70': !selectedChoice
                }"
                class="flex-1 sm:flex-none text-white font-bold py-2 px-4 rounded-lg transition duration-150 ease-in-out"
              >
                {{ validateButtonText }}
              </button>
              <slot name="footer-actions"></slot>
           </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script>
export default {
  name: 'ChoiceDialog',
  props: {
    show: {
      type: Boolean,
      default: false,
    },
    title: {
      type: String,
      default: "Select a Choice",
    },
    choices: { // Expects Array of objects, each MUST have a unique 'id'
      type: Array,
      required: true,
      validator: (value) => {
        return Array.isArray(value) && value.every(item =>
          typeof item === 'object' &&
          item !== null &&
          (typeof item.id === 'string' || typeof item.id === 'number')
        );
      }
    },
    choiceDisplayField: { // The field in the choice object to display as primary text
      type: String,
      default: 'name',
    },
    canEdit: {
      type: Boolean,
      default: false,
    },
    canRemove: {
      type: Boolean,
      default: false,
    },
    canAdd: {
      type: Boolean,
      default: false,
    },
    addButtonText: {
      type: String,
      default: 'Add New',
    },
    validateButtonText: {
        type: String,
        default: 'Validate',
    },
    addChoicePlaceholder: {
        type: String,
        default: 'Enter new choice name',
    },
    emptyChoicesMessage: {
        type: String,
        default: 'No choices available.',
    },
    initialSelectedChoiceId: {
        type: [String, Number],
        default: null,
    }
  },
  emits: [
      'choice-selected',
      'choice-validated',
      'choice-added', // Emits the name string
      'choice-removed', // Emits the choice ID
      'choice-updated', // Emits { id: ..., [choiceDisplayField]: 'New Name' }
      'close-dialog'
  ],
  data() {
    return {
      selectedChoiceId: null,
      showInput: false,
      newChoiceName: '',
      editingChoiceId: null,
      editingChoiceName: '',
    };
  },
  computed: {
    selectedChoice() {
      // Find the choice from the prop based on the internal selected ID
      return this.choices.find(c => c.id === this.selectedChoiceId) || null;
    },
    // This computed property adds the `isEditing` flag locally
    displayChoices() {
      // Map choices for display, adding the isEditing flag
      return this.choices.map(choice => ({
        id: choice.id, // Keep ID for key and lookups
        isEditing: choice.id === this.editingChoiceId, // Check if this choice is being edited
      }));
    }
  },
  watch: {
    show(newVal) {
      // When dialog opens or closes
      if (newVal) {
        // Dialog is shown: Apply initial selection if provided
        this.selectedChoiceId = this.initialSelectedChoiceId;
        // Emit the initial selection if it exists
        if(this.selectedChoice) {
            this.$emit("choice-selected", this.selectedChoice);
        }
      } else {
        // Dialog is hidden: Reset internal state
        this.resetState();
      }
    },
    choices: {
        // Watch the choices prop for external changes
        handler(newChoices) {
            // If the currently selected choice is removed externally, deselect it
            if (this.selectedChoiceId && !newChoices.some(c => c.id === this.selectedChoiceId)) {
                this.selectedChoiceId = null;
                 this.$emit("choice-selected", null); // Notify parent of deselection
            }
            // If the choice being edited is removed externally, cancel editing
            if (this.editingChoiceId && !newChoices.some(c => c.id === this.editingChoiceId)) {
                this.cancelEditing();
            }
        },
        // deep: true // Use deep watch cautiously if needed for changes *within* choice objects
    },
    initialSelectedChoiceId(newId) {
        // If the initial ID prop changes while the dialog is open
        if(this.show) {
            this.selectedChoiceId = newId; // Update the internal selected ID
             // Emit the newly selected choice
            if(this.selectedChoice) {
                this.$emit("choice-selected", this.selectedChoice);
            }
        }
    }
  },
  methods: {
    resetState() {
        // Reset all internal state variables to their defaults
        this.selectedChoiceId = null;
        this.showInput = false;
        this.newChoiceName = '';
        this.cancelEditing(); // This also resets editingChoiceId and editingChoiceName
    },
    getChoiceDisplayValue(choice) {
      // Find the original choice object to get the display field value
      const originalChoice = this.choices.find(c => c.id === choice.id);
      // Return the value of the specified field, or a fallback string
      return originalChoice?.[this.choiceDisplayField] ?? `Choice ${choice.id}`;
    },
    selectChoiceInternal(choice) {
       // Select a choice only if it's not being edited
       if (this.editingChoiceId !== choice.id) {
          this.selectedChoiceId = choice.id; // Update the internal ID
          // Emit the full original choice object
          this.$emit("choice-selected", this.choices.find(c => c.id === choice.id));
       }
    },
    closeDialog() {
      // Emit the close event to the parent
      this.$emit("close-dialog");
    },
    validateSelection() {
      // If a choice is selected, emit the validation event with the choice object
      if (this.selectedChoice) {
        this.$emit("choice-validated", this.selectedChoice);
      }
    },
    toggleInput() {
      // Only allow toggling if adding is enabled
      if (!this.canAdd) return;
      this.showInput = !this.showInput; // Toggle visibility
      if (this.showInput) {
         this.cancelEditing(); // Ensure editing mode is closed
         this.newChoiceName = ''; // Clear previous input
         // Focus the input field after it becomes visible
         this.$nextTick(() => {
            this.$refs.newChoiceInput?.focus();
         });
      }
    },
    addNewChoice() {
      // Add a new choice if adding is enabled and name is provided
      const nameToAdd = this.newChoiceName.trim();
      if (nameToAdd && this.canAdd) {
        // Emit only the name; parent creates the full choice object
        this.$emit('choice-added', nameToAdd);
        this.newChoiceName = ''; // Clear the input
        // Focus the input again for potentially adding more items quickly
         this.$nextTick(() => {
            this.$refs.newChoiceInput?.focus();
         });
      }
    },
    handleRemove(choice) {
        // Remove a choice if allowed and not currently editing it
        if (this.canRemove && this.editingChoiceId !== choice.id) {
            // Emit only the ID of the choice to be removed
            this.$emit('choice-removed', choice.id);
        }
    },
    startEditing(choice) {
        // Start editing if allowed
        if (!this.canEdit) return;
        this.cancelEditing(); // Cancel any other ongoing edit
        this.showInput = false; // Hide the 'add new' input
        this.selectedChoiceId = null; // Deselect visually while editing
        this.editingChoiceId = choice.id; // Set the ID of the choice being edited
        this.editingChoiceName = this.getChoiceDisplayValue(choice); // Pre-fill input with current name
        // Focus and select the text in the input field
        this.$nextTick(() => {
           const inputRef = this.$refs[`editInput_${choice.id}`];
           const inputElement = inputRef?.$el ?? inputRef?.[0] ?? inputRef; // Handle ref types
           inputElement?.focus();
           inputElement?.select();
        });
    },
    finishEditing() {
        // Finish editing if allowed and an edit is in progress
        if (this.editingChoiceId !== null && this.canEdit) {
            const finalName = this.editingChoiceName.trim(); // Get trimmed name
            const originalChoice = this.choices.find(c => c.id === this.editingChoiceId);
            const originalName = originalChoice?.[this.choiceDisplayField] ?? '';

            // Check if the name is valid and actually changed
            if (originalChoice && finalName && finalName !== originalName) {
                // Emit the update event with ID and the modified field/value
                this.$emit('choice-updated', { id: this.editingChoiceId, [this.choiceDisplayField]: finalName });
            } else {
                 // Log if edit was cancelled or name was empty/unchanged
                 console.log("ChoiceDialog: Edit cancelled or name unchanged/empty.");
            }
            this.cancelEditing(); // Always reset editing state afterwards
        }
    },
    cancelEditing() {
        // Reset editing state variables
        this.editingChoiceId = null;
        this.editingChoiceName = '';
    },
    handleEditKeyup(event) {
        // Handle key events in the edit input if editing is allowed
        if (!this.canEdit) return;
        if (event.key === 'Enter') {
            event.preventDefault(); // Prevent default Enter behavior (like form submission)
            this.finishEditing(); // Finish editing on Enter
        } else if (event.key === 'Escape') {
            this.cancelEditing(); // Cancel editing on Escape
        }
    }
  },
};
</script>

<style scoped>
/* Styles remain the same */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}

.scrollbar-thin {
  scrollbar-width: thin; /* Firefox */
  scrollbar-color: var(--scrollbar-thumb, #a0aec0) var(--scrollbar-track, #edf2f7); /* Firefox */
}
.scrollbar-thin::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: var(--scrollbar-track, #edf2f7);
  border-radius: 4px;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background-color: var(--scrollbar-thumb, #a0aec0);
  border-radius: 4px;
  border: 2px solid var(--scrollbar-track, #edf2f7);
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
    background-color: var(--scrollbar-thumb-hover, #718096);
}

.scrollbar-thumb-gray-400 { --scrollbar-thumb: #a0aec0; --scrollbar-thumb-hover: #718096; }
.scrollbar-track-gray-200 { --scrollbar-track: #edf2f7; }
.dark .dark\:scrollbar-thumb-gray-600 { --scrollbar-thumb: #718096; --scrollbar-thumb-hover: #a0aec0; }
.dark .dark\:scrollbar-track-gray-800 { --scrollbar-track: #2d3748; }
</style>