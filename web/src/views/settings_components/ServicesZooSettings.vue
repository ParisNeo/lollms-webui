<template>
    <div class="user-settings-panel space-y-6">
        <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 border-b border-blue-300 dark:border-blue-600 pb-2">
            Services Zoo & Audio
        </h2>

         <!-- Default Service Selection -->
        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Default Service Selection</h3>
             <p class="text-xs text-blue-500 dark:text-blue-400 mb-4">
                 Choose the default services LoLLMs will use for various tasks. Specific personalities might override these.
            </p>

            <div class="grid grid-cols-1 gap-4">
                <!-- TTS Service -->
                <div class="setting-item"> <!-- Adjusted from setting-item-grid for consistency -->
                    <label for="active_tts_service" class="setting-label">Text-to-Speech (TTS)</label>
                    <div class="flex items-center gap-2 flex-grow"> <!-- Adjusted from setting-input-group -->
                        <select id="active_tts_service" :value="$store.state.config.active_tts_service" @change="updateValue('active_tts_service', $event.target.value)" class="input flex-grow">
                             <option value="None">None</option>
                             <option value="browser">Browser TTS</option>
                             <option v-for="service in ttsServices" :key="`tts-${service.name}`" :value="service.name">{{ service.caption || service.name }}</option>
                        </select>
                         <button @click="showServiceSettings('tts', $store.state.config.active_tts_service)" :disabled="!$store.state.config.active_tts_service || $store.state.config.active_tts_service === 'None' || $store.state.config.active_tts_service === 'browser'" class="btn btn-secondary btn-sm p-2 flex-shrink-0" title="Configure Selected TTS Service">
                             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 feather feather-settings"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                        </button>
                    </div>
                </div>

                 <!-- STT Service -->
                 <div class="setting-item">
                    <label for="active_stt_service" class="setting-label">Speech-to-Text (STT)</label>
                    <div class="flex items-center gap-2 flex-grow">
                         <select id="active_stt_service" :value="$store.state.config.active_stt_service" @change="updateValue('active_stt_service', $event.target.value)" class="input flex-grow">
                             <option value="None">None</option>
                             <option v-for="service in sttServices" :key="`stt-${service.name}`" :value="service.name">{{ service.caption || service.name }}</option>
                        </select>
                         <button @click="showServiceSettings('stt', $store.state.config.active_stt_service)" :disabled="!$store.state.config.active_stt_service || $store.state.config.active_stt_service === 'None'" class="btn btn-secondary btn-sm p-2 flex-shrink-0" title="Configure Selected STT Service">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 feather feather-settings"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                        </button>
                    </div>
                </div>

                 <!-- TTI Service -->
                 <div class="setting-item">
                    <label for="active_tti_service" class="setting-label">Text-to-Image (TTI)</label>
                     <div class="flex items-center gap-2 flex-grow">
                        <select id="active_tti_service" :value="$store.state.config.active_tti_service" @change="updateValue('active_tti_service', $event.target.value)" class="input flex-grow">
                             <option value="None">None</option>
                             <option v-for="service in ttiServices" :key="`tti-${service.name}`" :value="service.name">{{ service.caption || service.name }}</option>
                        </select>
                        <button @click="showServiceSettings('tti', $store.state.config.active_tti_service)" :disabled="!$store.state.config.active_tti_service || $store.state.config.active_tti_service === 'None'" class="btn btn-secondary btn-sm p-2 flex-shrink-0" title="Configure Selected TTI Service">
                             <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 feather feather-settings"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                         </button>
                    </div>
                </div>

                 <!-- TTM Service -->
                 <div class="setting-item">
                    <label for="active_ttm_service" class="setting-label">Text-to-Music (TTM)</label>
                     <div class="flex items-center gap-2 flex-grow">
                        <select id="active_ttm_service" :value="$store.state.config.active_ttm_service" @change="updateValue('active_ttm_service', $event.target.value)" class="input flex-grow">
                             <option value="None">None</option>
                             <option v-for="service in ttmServices" :key="`ttm-${service.name}`" :value="service.name">{{ service.caption || service.name }}</option>
                        </select>
                        <button @click="showServiceSettings('ttm', $store.state.config.active_ttm_service)" :disabled="!$store.state.config.active_ttm_service || $store.state.config.active_ttm_service === 'None'" class="btn btn-secondary btn-sm p-2 flex-shrink-0" title="Configure Selected TTM Service">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 feather feather-settings"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                        </button>
                    </div>
                </div>

                <!-- TTV Service -->
                <div class="setting-item">
                     <label for="active_ttv_service" class="setting-label">Text-to-Video (TTV)</label>
                     <div class="flex items-center gap-2 flex-grow">
                        <select id="active_ttv_service" :value="$store.state.config.active_ttv_service" @change="updateValue('active_ttv_service', $event.target.value)" class="input flex-grow">
                             <option value="None">None</option>
                             <option v-for="service in ttvServices" :key="`ttv-${service.name}`" :value="service.name">{{ service.caption || service.name }}</option>
                        </select>
                        <button @click="showServiceSettings('ttv', $store.state.config.active_ttv_service)" :disabled="!$store.state.config.active_ttv_service || $store.state.config.active_ttv_service === 'None'" class="btn btn-secondary btn-sm p-2 flex-shrink-0" title="Configure Selected TTV Service">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 feather feather-settings"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
                         </button>
                    </div>
                </div>
            </div>
        </section>

         <!-- STT / Audio Input Settings -->
        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Audio Input / STT Settings</h3>

             <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                 <!-- Listening Threshold -->
                 <div class="setting-item !items-center"> <!-- Use setting-item and !items-center -->
                     <label for="stt_listening_threshold" class="setting-label">Listening Threshold</label>
                    <input id="stt_listening_threshold" :value="$store.state.config.stt_listening_threshold" @input="updateValue('stt_listening_threshold', parseInt($event.target.value))" type="number" min="0" step="10" class="input-sm w-24">
                </div>
                 <!-- Silence Duration -->
                <div class="setting-item !items-center">
                    <label for="stt_silence_duration" class="setting-label">Silence Duration (s)</label>
                    <input id="stt_silence_duration" :value="$store.state.config.stt_silence_duration" @input="updateValue('stt_silence_duration', parseInt($event.target.value))" type="number" min="0" step="1" class="input-sm w-24">
                </div>
                 <!-- Sound Threshold % -->
                <div class="setting-item !items-center">
                     <label for="stt_sound_threshold_percentage" class="setting-label">Min Sound Percentage</label>
                     <input id="stt_sound_threshold_percentage" :value="$store.state.config.stt_sound_threshold_percentage" @input="updateValue('stt_sound_threshold_percentage', parseInt($event.target.value))" type="number" min="0" max="100" step="1" class="input-sm w-24">
                </div>
                 <!-- Volume Amplification -->
                <div class="setting-item !items-center">
                     <label for="stt_gain" class="setting-label">Volume Amplification</label>
                    <input id="stt_gain" :value="$store.state.config.stt_gain" @input="updateValue('stt_gain', parseInt($event.target.value))" type="number" min="0" step="1" class="input-sm w-24">
                </div>
                <!-- Audio Rate -->
                <div class="setting-item !items-center">
                    <label for="stt_rate" class="setting-label">Audio Rate (Hz)</label>
                    <input id="stt_rate" :value="$store.state.config.stt_rate" @input="updateValue('stt_rate', parseInt($event.target.value))" type="number" min="8000" step="1000" class="input-sm w-24">
                </div>
                <!-- Channels -->
                 <div class="setting-item !items-center">
                     <label for="stt_channels" class="setting-label">Channels</label>
                    <input id="stt_channels" :value="$store.state.config.stt_channels" @input="updateValue('stt_channels', parseInt($event.target.value))" type="number" min="1" max="2" step="1" class="input-sm w-24">
                </div>
                <!-- Buffer Size -->
                <div class="setting-item !items-center">
                     <label for="stt_buffer_size" class="setting-label">Buffer Size</label>
                    <input id="stt_buffer_size" :value="$store.state.config.stt_buffer_size" @input="updateValue('stt_buffer_size', parseInt($event.target.value))" type="number" min="512" step="512" class="input-sm w-24">
                </div>

                 <!-- Activate Word Detection -->
                <div class="toggle-item md:col-span-2">
                    <label for="stt_activate_word_detection" class="toggle-label">Activate Wake Word Detection</label>
                     <ToggleSwitch id="stt_activate_word_detection" :checked="$store.state.config.stt_activate_word_detection" @update:checked="updateBoolean('stt_activate_word_detection', $event)" />
                </div>
                 <!-- Word Detection File -->
                <div class="setting-item md:col-span-2" :class="{ 'opacity-50 pointer-events-none': !$store.state.config.stt_activate_word_detection }">
                    <label for="stt_word_detection_file" class="setting-label">Wake Word File (.wav)</label>
                     <input type="text" id="stt_word_detection_file" :value="$store.state.config.stt_word_detection_file" @input="updateValue('stt_word_detection_file', $event.target.value)" class="input flex-grow" placeholder="Path to wake word wav file" :disabled="!$store.state.config.stt_activate_word_detection">
                 </div>
             </div>
        </section>

        <!-- Audio Devices -->
        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Audio Devices</h3>
             <button @click="refreshAudioDevices" class="btn btn-secondary btn-sm mb-2" title="Rescan for audio devices">
                 <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-4 h-4 mr-1 feather feather-refresh-cw"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
                 Refresh Devices
            </button>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <!-- Input Device -->
                 <div class="setting-item">
                    <label for="stt_input_device" class="setting-label">Audio Input Device</label>
                     <select id="stt_input_device" :value="$store.state.config.stt_input_device" @change="updateValue('stt_input_device', parseInt($event.target.value))" class="input flex-grow">
                         <option v-for="(device, index) in audioInputDevices" :key="`in-${index}`" :value="audioInputDeviceIndexes[index]">
                             {{ device }}
                         </option>
                     </select>
                 </div>
                 <!-- Output Device -->
                <div class="setting-item">
                     <label for="tts_output_device" class="setting-label">Audio Output Device</label>
                    <select id="tts_output_device" :value="$store.state.config.tts_output_device" @change="updateValue('tts_output_device', parseInt($event.target.value))" class="input flex-grow">
                        <option v-for="(device, index) in audioOutputDevices" :key="`out-${index}`" :value="audioOutputDeviceIndexes[index]">
                             {{ device }}
                         </option>
                     </select>
                 </div>
            </div>
        </section>
    </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick, defineProps, defineEmits, onUpdated } from 'vue';
import feather from 'feather-icons';
import ToggleSwitch from '@/components/ToggleSwitch.vue';

// Props
const props = defineProps({
    loading: { type: Boolean, default: false },
    api_post_req: { type: Function, required: true },
    api_get_req: { type: Function, required: true },
    show_toast: { type: Function, required: true },
    show_yes_no_dialog: { type: Function, required: true },
    show_universal_form: { type: Function, required: true },
    client_id: { type: String, required: true }
});

// Emits
const emit = defineEmits(['settings-changed']);

// Reactive State
const ttsServices = ref([]);
const sttServices = ref([]);
const ttiServices = ref([]);
const ttmServices = ref([]);
const ttvServices = ref([]);
const audioInputDevices = ref([]);
const audioInputDeviceIndexes = ref([]);
const audioOutputDevices = ref([]);
const audioOutputDeviceIndexes = ref([]);

// --- Methods ---
const updateValue = (key, value) => {
    // Handle potential parsing for numbers if needed from text inputs

    emit('settings-changed');
};

const updateBoolean = (key, value) => {
    emit('settings-changed');
};

const fetchServiceLists = async () => {
    try {
        const [ttsRes, sttRes, ttiRes, ttmRes, ttvRes] = await Promise.all([
            props.api_post_req('list_tts_services'),
            props.api_post_req('list_stt_services'),
            props.api_post_req('list_tti_services'),
            props.api_post_req('list_ttm_services'),
            props.api_post_req('list_ttv_services')
        ]);
        ttsServices.value = ttsRes || [];
        sttServices.value = sttRes || [];
        ttiServices.value = ttiRes || [];
        ttmServices.value = ttmRes || [];
        ttvServices.value = ttvRes || [];
    } catch (error) {
        props.show_toast("Failed to fetch service lists.", 4, false);
        console.error("Error fetching service lists:", error);
    }
};

const fetchAudioDevices = async () => {
    try {
        const [inputRes, outputRes] = await Promise.all([
            props.api_get_req("get_snd_input_devices"),
            props.api_get_req("get_snd_output_devices")
        ]);
        audioInputDevices.value = inputRes?.device_names || [];
        audioInputDeviceIndexes.value = inputRes?.device_indexes || [];
        audioOutputDevices.value = outputRes?.device_names || [];
        audioOutputDeviceIndexes.value = outputRes?.device_indexes || [];
    } catch (error) {
        props.show_toast("Failed to fetch audio devices.", 4, false);
        console.error("Error fetching audio devices:", error);
    }
};

const refreshAudioDevices = () => {
    props.show_toast("Refreshing audio devices...", 2, true);
    fetchAudioDevices();
};

const showServiceSettings = async (serviceType, serviceName) => {
    if (!serviceName || serviceName === 'None' || serviceName === 'browser') {
        props.show_toast(`No configurable settings for '${serviceName}'.`, 3, false);
        return;
    }
    const endpointMap = {
        tts: 'get_active_tts_settings',
        stt: 'get_active_stt_settings',
        tti: 'get_active_tti_settings',
        ttm: 'get_active_ttm_settings',
        ttv: 'get_active_ttv_settings'
    };
    const setEndpointMap = {
        tts: 'set_active_tts_settings',
        stt: 'set_active_stt_settings',
        tti: 'set_active_tti_settings',
        ttm: 'set_active_ttm_settings',
        ttv: 'set_active_ttv_settings'
    };

    const getEndpoint = endpointMap[serviceType];
    const setEndpoint = setEndpointMap[serviceType];
    if (!getEndpoint || !setEndpoint) return;

    try {
        const settingsData = await props.api_post_req(getEndpoint);

        if (settingsData && Object.keys(settingsData).length > 0) {
            const result = await props.show_universal_form(settingsData, `${serviceName} Settings`, "Save", "Cancel");
            // If user confirmed (didn't cancel)
            const setResponse = await props.api_post_req(setEndpoint, { settings: result });
             if (setResponse && setResponse.status) {
                props.show_toast(`${serviceName} settings updated successfully!`, 4, true);
                // Maybe refresh config locally or trigger parent refresh if needed
             } else {
                props.show_toast(`Failed to update ${serviceName} settings: ${setResponse?.error || 'Unknown error'}`, 4, false);
             }

        } else {
            props.show_toast(`${serviceName} has no configurable settings.`, 4, false);
        }
    } catch (error) {
        props.show_toast(`Error fetching/setting ${serviceName} settings: ${error.message}`, 4, false);
        console.error(`Error with ${serviceName} settings:`, error);
    }
};

const manageService = async (actionEndpoint) => {
     props.show_toast(`Performing action: ${actionEndpoint}...`, 5, true);
     try {
         // Add disclaimer/confirmation if needed for installs/upgrades
        // if (actionEndpoint.includes('install')) { ... }

        const response = await props.api_post_req(actionEndpoint);
         // Success/failure feedback depends heavily on the backend response structure
        // and whether the action is immediate or backgrounded.
        // A generic message is often best unless specific feedback is provided.
        if (response && response.status !== false) { // Check for explicit false status if backend uses it
             props.show_toast(`Action '${actionEndpoint}' initiated successfully.`, 4, true);
         } else {
            props.show_toast(`Action '${actionEndpoint}' failed: ${response?.error || 'Check logs'}`, 4, false);
        }
     } catch (error) {
         props.show_toast(`Error during action '${actionEndpoint}': ${error.message}`, 4, false);
         console.error(`Error managing service (${actionEndpoint}):`, error);
     }
};


// Lifecycle Hooks
onMounted(() => {
    fetchServiceLists();
    fetchAudioDevices();
    nextTick(() => {
        feather.replace();
    });
});

onUpdated(() => {
     // Use this cautiously - might cause excessive re-renders if not careful
     nextTick(() => {
        feather.replace();
     });
});

</script>

<style scoped>
/* Using shared styles defined in previous components or globally */
.setting-item-grid {
    /* Grid layout for label on left, input/group on right */
    @apply grid grid-cols-1 md:grid-cols-[minmax(150px,25%)_1fr] gap-x-4 gap-y-1 items-center py-1;
}
.setting-label {
    /* Label alignment */
    @apply text-sm font-medium text-gray-700 dark:text-gray-300 text-left md:text-right pr-2;
}
.setting-input-group {
    /* Grouping for input/select + button */
    @apply flex items-center gap-2;
}
.input-field {
     /* Standard focus, background, border */
     @apply block w-full px-3 py-2 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-800 disabled:opacity-50;
}
.input-field-sm {
     /* Standard focus, background, border - smaller version */
     @apply block w-full px-2.5 py-1.5 text-xs bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-800 disabled:opacity-50;
}

.toggle-item {
    @apply flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors;
}
.toggle-label {
    @apply text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer flex-1 mr-4;
}
.toggle-description {
     @apply block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal;
}

/* Shared Button Styles (Tailwind) - Standardized */
.button-base {
    @apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 transition-colors duration-150;
}
.button-base-sm {
     @apply inline-flex items-center justify-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-800 disabled:opacity-50 transition-colors duration-150;
}

/* Use standard blue for primary, green for success etc. */
.button-primary { @apply button-base text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500; }
.button-secondary { @apply button-base text-gray-700 dark:text-gray-200 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 focus:ring-gray-400; }
.button-success { @apply button-base text-white bg-green-600 hover:bg-green-700 focus:ring-green-500; }
.button-danger { @apply button-base text-white bg-red-600 hover:bg-red-700 focus:ring-red-500; }

.button-primary-sm { @apply button-base-sm text-white bg-blue-600 hover:bg-blue-700 focus:ring-blue-500; }
.button-secondary-sm { @apply button-base-sm text-gray-700 dark:text-gray-200 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 focus:ring-gray-400; }
.button-success-sm { @apply button-base-sm text-white bg-green-600 hover:bg-green-700 focus:ring-green-500; }

</style>