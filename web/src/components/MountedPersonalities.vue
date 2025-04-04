<template>
    <!-- Root container: relative for positioning context -->
    <div class="relative group/item">
        <!-- Main Personality Avatar Button -->
        <button
            @click.prevent="onSettingsPersonality(mountedPers)" 
            class="w-6 h-6 rounded-full overflow-hidden transition-transform duration-200 transform group-hover/item:scale-110 focus:outline-none relative"
            :class="{'glow-effect': $store.state.config.activate_skills_lib, 'border-2 border-primary': isActive}" 
            :title="'Configure ' + mountedPers.name"
        >
            <img
                :src="mountedPers.avatar"
                @error="personalityImgPlacehodler"
                :alt="mountedPers.name"
                class="w-full h-full object-cover"
            >
        </button>

        <!-- Hover Action Bubble -->
        <!-- 
          - positioned absolutely relative to the root div
          - bottom-full places its bottom edge at the top edge of the parent button
          - mb-2 adds margin above the button
          - left-1/2 -translate-x-1/2 centers it horizontally
          - opacity controlled by group-hover
          - z-10 to lift it above siblings if any (within its stacking context)
          - w-auto allows it to size based on content
          - Added background, padding, shadow, rounded corners for bubble appearance
         -->
        <div
            class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 w-auto
                   flex items-center justify-center space-x-1
                   opacity-0 group-hover/item:opacity-100 transition-opacity duration-200
                   p-2 rounded-md shadow-lg bg-white dark:bg-gray-800 ring-1 ring-black ring-opacity-5 z-10"
            
        >
            <!-- Settings Button -->
            <button 
                @click.prevent="onSettingsPersonality(mountedPers)" 
                class="p-1 btn-secondary btn-xs rounded-full hover:scale-110 transition-transform duration-150" 
                title="Configure"
            >
               <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826 3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            </button>
             <!-- Remount Button -->
            <button 
                @click.prevent="remount_personality()" 
                class="p-1 bg-blue-500 rounded-full text-white hover:bg-blue-600 focus:outline-none btn-xs hover:scale-110 transition-transform duration-150" 
                title="Remount"
            >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
            </button>
            <!-- Talk Button -->
            <button 
                @click.prevent="handleOnTalk()" 
                class="p-1 bg-green-500 rounded-full text-white hover:bg-green-600 focus:outline-none btn-xs hover:scale-110 transition-transform duration-150" 
                title="Talk"
            >
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
            </button>
             <!-- Removed the "+N" button as it's likely not needed for the single active personality icon -->
        </div>
    </div>
    <UniversalForm ref="universalForm" class="z-50" />
</template>

<script>
import axios from "axios";
import defaultPersonalityImgPlaceholder from "../assets/logo.svg"
import UniversalForm from '@/components/UniversalForm.vue';
import Toast from '../components/Toast.vue' // Assuming Toast is registered globally or locally if needed

import { nextTick } from "vue";
import { useStore } from 'vuex'; // Import the useStore function
import { computed } from 'vue'; // Import the computed function
// import { watch, ref } from 'vue'; // watch, ref not used directly here, remove if not needed elsewhere

import feather from 'feather-icons'
import socket from '@/services/websocket.js'

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
axios.defaults.baseURL = import.meta.env.VITE_LOLLMS_API_BASEURL

export default {
    name: 'MountedPersonalities',
    props: {
        onShowPersList: Function, // Still present but not used directly in template
        onReady: Function,
        // Add isActive prop if you need external control over the active border, otherwise compute it
        // isActive: Boolean
    },
    components: {
        // Toast, // Register Toast if used via this.$store.state.toast... otherwise remove
        UniversalForm
    },
    data() {
        return {
            bUrl: bUrl,
            isMounted: false,
            // show: false // 'show' data property not used, remove
        }
    },
    async mounted() {
        // Use setup function for composition API features if preferred
        // This component uses Options API style
        await this.constructor()
        this.isMounted = true
    },
    async activated() {
        // Keep activated hook if using <keep-alive>
        if (this.isMounted) {
            await this.constructor()
        }
    },
    computed: {
        // Use computed properties from Vuex store
        configFile() {
            return this.$store.state.config;
        },
        mountedPers() {
            // console.log("asked for mountedPers:", this.$store.state.mountedPers)
            return this.$store.state.mountedPers;
        },
        // mountedPersArr is not directly used in the template anymore
        // mountedPersArr(){
        //     return this.$store.state.mountedPersArr;
        // }
        // Determine if this personality is the active one (example logic)
        isActive() {
            // This logic assumes mountedPers holds the *currently* selected one
            // Adjust based on your actual state management for 'active'
             return this.$store.state.mountedPers && this.$store.state.config.active_personality_id === this.$store.state.config.personalities.findIndex(p => p === this.$store.state.mountedPers.full_path);
           // return this.$store.state.mountedPers?.full_path === this.$store.state.config.personalities[this.$store.state.config.active_personality_id];
        }
    },
    methods: {
        async handleOnTalk() {
            const pers = this.mountedPers;
            if (!pers) {
                 this.$store.state.toast.showToast("No personality mounted to talk with.", 3, false);
                 return;
            }
            console.log("Talking with:", pers.name);
            // this.isGenerating = true; // Manage isGenerating state if needed
            try {
                 let genStatusRes = await axios.get('/get_generation_status', {});
                 if (genStatusRes && !genStatusRes.data.status) {
                     const id = this.$store.state.config.personalities.findIndex(item => item === pers.full_path);
                     if (id !== this.$store.state.config.active_personality_id) {
                        const obj = { client_id: this.$store.state.client_id, id: id };
                        let selectRes = await axios.post('/select_personality', obj);
                        if(!selectRes.data.status){
                            console.error("Failed to select personality before talking:", selectRes.data.error);
                            this.$store.state.toast.showToast(`Error selecting ${pers.name}: ${selectRes.data.error}`, 4, false);
                            return;
                        }
                        // Update store if selection changes state
                        this.$store.commit('setActivePersonalityId', id); // Example mutation
                        this.$store.commit('setMountedPers', this.$store.state.personalities_infos[id]); // Example mutation
                     }

                    console.log('Requesting generation from:', pers.name);
                    socket.emit('generate_msg_from', { id: id }); // Use the found ID
                 } else if (genStatusRes) {
                    console.log("Already generating");
                    this.$store.state.toast.showToast("Generation is already in progress.", 3, false);
                 } else {
                    console.error("Could not get generation status.");
                    this.$store.state.toast.showToast("Error checking generation status.", 4, false);
                 }
            } catch(error){
                 console.error("Error during handleOnTalk:", error);
                 this.$store.state.toast.showToast(`Error initiating talk: ${error.message}`, 4, false);
            } finally {
                // this.isGenerating = false; // Reset generating state if needed
            }
        },
        async remount_personality() {
            const pers = this.mountedPers;
            if (!pers) {
                 this.$store.state.toast.showToast("No personality mounted to remount.", 3, false);
                 return { 'status': false, 'error': 'no personality selected' };
            }
            console.log("Remounting personality ", pers.name);
            this.$store.state.toast.showToast(`Remounting ${pers.name}...`, 4, true); // Show pending
            try {
                const obj = {
                    client_id: this.$store.state.client_id,
                    category: pers.category,
                    folder: pers.folder,
                    language: pers.language // Make sure language is available in mountedPers if needed
                };
                const res = await axios.post('/remount_personality', obj);

                if (res && res.data.status) { // Check for a success status in response
                    console.log("Personality remounted successfully:", res.data);
                    this.$store.state.toast.showToast(`${pers.name} remounted successfully!`, 4, true);
                     // Optionally trigger state update if remount changes anything
                    this.$store.dispatch('refreshPersonalityData'); // Example action
                    return res.data;
                } else {
                    const errorMsg = res?.data?.error || "Unknown error";
                    console.error("Failed remount_personality:", errorMsg);
                    this.$store.state.toast.showToast(`Failed to remount ${pers.name}: ${errorMsg}`, 4, false);
                    return res?.data || { status: false, error: errorMsg };
                }
            } catch (error) {
                console.error('Error during remount_personality:', error);
                this.$store.state.toast.showToast(`Error remounting: ${error.message}`, 4, false);
                return { status: false, error: error.message };
            }
        },
        async onSettingsPersonality(persEntry) {
            if (!persEntry) {
                 this.$store.state.toast.showToast("No personality selected for settings.", 3, false);
                 return;
            }
            console.log("Opening settings for:", persEntry.name);
             try {
                // Ensure the correct personality is active before fetching settings
                const currentIndex = this.$store.state.config.personalities.findIndex(p => p === persEntry.full_path);
                if (currentIndex !== this.$store.state.config.active_personality_id) {
                     const obj = { client_id: this.$store.state.client_id, id: currentIndex };
                     let selectRes = await axios.post('/select_personality', obj);
                     if(!selectRes.data.status){
                         console.error("Failed to select personality before opening settings:", selectRes.data.error);
                         this.$store.state.toast.showToast(`Error selecting ${persEntry.name} for settings: ${selectRes.data.error}`, 4, false);
                         return;
                     }
                      // Update store if selection changes state
                     this.$store.commit('setActivePersonalityId', currentIndex); // Example mutation
                     this.$store.commit('setMountedPers', this.$store.state.personalities_infos[currentIndex]); // Example mutation                     
                     await nextTick(); // Allow state update
                }


                const res = await axios.get('/get_active_personality_settings');
                if (res && res.data && Object.keys(res.data).length > 0) {
                    console.log('Personality settings data:', res.data);
                    const formResult = await this.$refs.universalForm.showForm(
                        res.data,
                        `Settings - ${persEntry.name}`,
                        "Save changes",
                        "Cancel"
                    );

                    if (formResult) { // Check if the user confirmed, not cancelled
                        console.log("Saving new settings:", formResult);
                        try {
                            const saveRes = await axios.post('/set_active_personality_settings', formResult);
                            if (saveRes && saveRes.data && saveRes.data.status) { // Check for success status
                                console.log('Settings saved successfully:', saveRes.data);
                                this.$store.state.toast.showToast("Personality settings updated successfully!", 4, true);
                                // Optionally trigger state update if settings change affects display
                                // e.g., this.$store.dispatch('refreshPersonalityData');
                            } else {
                                const errorMsg = saveRes?.data?.error || "Unknown error saving settings.";
                                console.error("Failed to save settings:", errorMsg);
                                this.$store.state.toast.showToast(`Failed to save settings: ${errorMsg}`, 4, false);
                            }
                        } catch (saveError) {
                            console.error("Error saving personality settings:", saveError);
                            this.$store.state.toast.showToast(`Error saving settings: ${saveError.message}`, 4, false);
                        }
                    } else {
                         console.log("Settings editing cancelled.");
                    }

                } else if (res && res.data && Object.keys(res.data).length === 0) {
                    this.$store.state.toast.showToast(`${persEntry.name} has no configurable settings.`, 4, false);
                } else {
                    console.error("Could not get personality settings response:", res);
                     this.$store.state.toast.showToast("Failed to retrieve personality settings.", 4, false);
                }
            } catch (error) {
                console.error("Error fetching/showing personality settings:", error);
                this.$store.state.toast.showToast(`Could not open settings: ${error.message}`, 4, false);
            }
        },
        async constructor() {
            // Feather icons replacement
            nextTick(() => {
                feather.replace();
            });
            // Wait for store readiness
            while (this.$store.state.ready === false) {
                await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for 100ms
            }
            // Call the onReady prop function passed from parent
            if (this.onReady) {
                this.onReady();
            }
             // No need to fetch config here, rely on store being populated
        },
        // Removed api_get_req as direct axios calls are used in methods
        personalityImgPlacehodler(event) {
            event.target.src = defaultPersonalityImgPlaceholder;
        },

    }
}
</script>

<style scoped>
.glow-effect {
    box-shadow: 0 0 5px 2px rgba(0, 255, 255, 0.7);
    animation: glow 1.5s ease-in-out infinite alternate;
}

@keyframes glow {
    from {
        box-shadow: 0 0 5px 2px rgba(0, 255, 255, 0.7);
    }
    to {
        box-shadow: 0 0 20px 2px rgba(0, 255, 255, 0.7);
    }
}
/* Add btn-xs if not globally defined in your project's CSS/Tailwind config */
/*
.btn-xs {
    padding: 0.25rem; 
}
*/
</style>