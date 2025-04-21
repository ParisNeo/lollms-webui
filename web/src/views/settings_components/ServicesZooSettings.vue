<template>
    <div class="user-settings-panel space-y-6">
        <h2 class="text-xl font-semibold text-blue-800 dark:text-blue-100 border-b border-blue-300 dark:border-blue-600 pb-2">
            Services Zoo & Audio
        </h2>

        <!-- TTS Section -->
        <section class="space-y-3 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-1">Text-to-Speech (TTS)</h3>
            <p class="text-xs text-blue-500 dark:text-blue-400 mb-3">Select the default service for converting text into speech.</p>
             <div v-if="ttsServices.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <ServiceEntry
                    v-for="service in ttsServicesWithDefaults" :key="`tts-${service.name}`"
                    :service="service"
                    serviceType="tts"
                    :baseUrl="baseUrl"
                    :isActive="config.active_tts_service === service.name"
                    @select="handleServiceSelect"
                    @configure="showServiceSettings"
                 />
             </div>
             <p v-else class="text-sm text-gray-500 dark:text-gray-400 italic">No TTS services available.</p>
        </section>

        <!-- STT Section -->
        <section class="space-y-3 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-1">Speech-to-Text (STT)</h3>
             <p class="text-xs text-blue-500 dark:text-blue-400 mb-3">Select the default service for converting speech into text.</p>
            <div v-if="sttServices.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                 <ServiceEntry
                    v-for="service in sttServicesWithDefaults" :key="`stt-${service.name}`"
                    :service="service"
                    serviceType="stt"
                    :baseUrl="baseUrl"
                    :isActive="config.active_stt_service === service.name"
                    @select="handleServiceSelect"
                    @configure="showServiceSettings"
                 />
            </div>
             <p v-else class="text-sm text-gray-500 dark:text-gray-400 italic">No STT services available.</p>
        </section>

        <!-- TTI Section -->
        <section class="space-y-3 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-1">Text-to-Image (TTI)</h3>
             <p class="text-xs text-blue-500 dark:text-blue-400 mb-3">Select the default service for generating images from text.</p>
            <div v-if="ttiServices.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <ServiceEntry
                    v-for="service in ttiServicesWithDefaults" :key="`tti-${service.name}`"
                    :service="service"
                    serviceType="tti"
                    :baseUrl="baseUrl"
                    :isActive="config.active_tti_service === service.name"
                    @select="handleServiceSelect"
                    @configure="showServiceSettings"
                 />
            </div>
             <p v-else class="text-sm text-gray-500 dark:text-gray-400 italic">No TTI services available.</p>
        </section>

        <!-- TTM Section -->
        <section class="space-y-3 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-1">Text-to-Music (TTM)</h3>
             <p class="text-xs text-blue-500 dark:text-blue-400 mb-3">Select the default service for generating music from text.</p>
            <div v-if="ttmServices.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                <ServiceEntry
                    v-for="service in ttmServicesWithDefaults" :key="`ttm-${service.name}`"
                    :service="service"
                    serviceType="ttm"
                    :baseUrl="baseUrl"
                    :isActive="config.active_ttm_service === service.name"
                    @select="handleServiceSelect"
                    @configure="showServiceSettings"
                 />
            </div>
            <p v-else class="text-sm text-gray-500 dark:text-gray-400 italic">No TTM services available.</p>
        </section>

        <!-- TTV Section -->
         <section class="space-y-3 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
             <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-1">Text-to-Video (TTV)</h3>
              <p class="text-xs text-blue-500 dark:text-blue-400 mb-3">Select the default service for generating videos from text.</p>
             <div v-if="ttvServices.length > 0" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
                 <ServiceEntry
                     v-for="service in ttvServicesWithDefaults" :key="`ttv-${service.name}`"
                     :service="service"
                     serviceType="ttv"
                     :baseUrl="baseUrl"
                     :isActive="config.active_ttv_service === service.name"
                     @select="handleServiceSelect"
                     @configure="showServiceSettings"
                  />
             </div>
             <p v-else class="text-sm text-gray-500 dark:text-gray-400 italic">No TTV services available.</p>
         </section>


        <!-- Audio Input / STT Settings -->
        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Audio Input / STT Settings</h3>
             <div class="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-4">
                 <div class="setting-item !items-center">
                     <label for="stt_listening_threshold" class="setting-label">Listening Threshold</label>
                    <input id="stt_listening_threshold" :value="config.stt_listening_threshold" @input="handleNumberInput('stt_listening_threshold', $event.target.value, true)" type="number" min="0" step="10" class="input-sm w-24">
                </div>
                <div class="setting-item !items-center">
                    <label for="stt_silence_duration" class="setting-label">Silence Duration (s)</label>
                    <input id="stt_silence_duration" :value="config.stt_silence_duration" @input="handleNumberInput('stt_silence_duration', $event.target.value, true)" type="number" min="0" step="1" class="input-sm w-24">
                </div>
                <div class="setting-item !items-center">
                     <label for="stt_sound_threshold_percentage" class="setting-label">Min Sound Percentage</label>
                     <input id="stt_sound_threshold_percentage" :value="config.stt_sound_threshold_percentage" @input="handleNumberInput('stt_sound_threshold_percentage', $event.target.value, true)" type="number" min="0" max="100" step="1" class="input-sm w-24">
                </div>
                <div class="setting-item !items-center">
                     <label for="stt_gain" class="setting-label">Volume Amplification</label>
                    <input id="stt_gain" :value="config.stt_gain" @input="handleNumberInput('stt_gain', $event.target.value, true)" type="number" min="0" step="1" class="input-sm w-24">
                </div>
                <div class="setting-item !items-center">
                    <label for="stt_rate" class="setting-label">Audio Rate (Hz)</label>
                    <input id="stt_rate" :value="config.stt_rate" @input="handleNumberInput('stt_rate', $event.target.value, true)" type="number" min="8000" step="1000" class="input-sm w-24">
                </div>
                 <div class="setting-item !items-center">
                     <label for="stt_channels" class="setting-label">Channels</label>
                    <input id="stt_channels" :value="config.stt_channels" @input="handleNumberInput('stt_channels', $event.target.value, true)" type="number" min="1" max="2" step="1" class="input-sm w-24">
                </div>
                <div class="setting-item !items-center">
                     <label for="stt_buffer_size" class="setting-label">Buffer Size</label>
                    <input id="stt_buffer_size" :value="config.stt_buffer_size" @input="handleNumberInput('stt_buffer_size', $event.target.value, true)" type="number" min="512" step="512" class="input-sm w-24">
                </div>
                <div class="toggle-item md:col-span-2">
                    <label for="stt_activate_word_detection" class="toggle-label">Activate Wake Word Detection</label>
                     <ToggleSwitch id="stt_activate_word_detection" :checked="config.stt_activate_word_detection" @update:checked="updateValue('stt_activate_word_detection', $event)" />
                </div>
                <div class="setting-item md:col-span-2" :class="{ 'opacity-50 pointer-events-none': !config.stt_activate_word_detection }">
                    <label for="stt_word_detection_file" class="setting-label">Wake Word File (.wav)</label>
                     <input type="text" id="stt_word_detection_file" :value="config.stt_word_detection_file" @input="updateValue('stt_word_detection_file', $event.target.value)" class="input flex-grow" placeholder="Path to wake word wav file" :disabled="!config.stt_activate_word_detection">
                 </div>
             </div>
        </section>

        <section class="space-y-4 p-4 border border-blue-300 dark:border-blue-600 rounded-lg panels-color">
            <h3 class="text-lg font-medium text-blue-700 dark:text-blue-300 mb-3">Audio Devices</h3>
             <button @click="refreshAudioDevices" class="btn btn-secondary btn-sm mb-2" title="Rescan for audio devices">
                 <i data-feather="refresh-cw" class="w-4 h-4 mr-1"></i>
                 Refresh Devices
            </button>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                 <div class="setting-item">
                    <label for="stt_input_device" class="setting-label">Audio Input Device</label>
                     <select id="stt_input_device" :value="config.stt_input_device" @change="handleNumberInput('stt_input_device', $event.target.value, true)" class="input flex-grow">
                         <option v-for="(device, index) in audioInputDevices" :key="`in-${index}`" :value="audioInputDeviceIndexes[index]">
                             {{ device }}
                         </option>
                     </select>
                 </div>
                <div class="setting-item">
                     <label for="tts_output_device" class="setting-label">Audio Output Device</label>
                    <select id="tts_output_device" :value="config.tts_output_device" @change="handleNumberInput('tts_output_device', $event.target.value, true)" class="input flex-grow">
                        <option v-for="(device, index) in audioOutputDevices" :key="`out-${index}`" :value="audioOutputDeviceIndexes[index]">
                             {{ device }}
                         </option>
                     </select>
                 </div>
            </div>
        </section>
    </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, defineProps, defineEmits, onUpdated } from 'vue';
import feather from 'feather-icons';
import ToggleSwitch from '@/components/ToggleSwitch.vue';
import ServiceEntry from '@/components/ServiceEntry.vue'; // Import the new component

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL || '';

export default {
    name: 'ServicesZooSettings',
    components: {
        ToggleSwitch,
        ServiceEntry // Register the new component
    },
    props: {
        config: { type: Object, required: true },
        loading: { type: Boolean, default: false },
        api_post_req: { type: Function, required: true },
        api_get_req: { type: Function, required: true },
        show_toast: { type: Function, required: true },
        show_universal_form: { type: Function, required: true },
        client_id: { type: String, required: true }
    },
    emits: ['setting-updated'],

    setup(props, { emit }) {
        const baseUrl = ref(bUrl);
        const ttsServices = ref([]);
        const sttServices = ref([]);
        const ttiServices = ref([]);
        const ttmServices = ref([]);
        const ttvServices = ref([]);
        const audioInputDevices = ref([]);
        const audioInputDeviceIndexes = ref([]);
        const audioOutputDevices = ref([]);
        const audioOutputDeviceIndexes = ref([]);

        // Add default/placeholder service entries
         const defaultNoneService = { name: 'None', caption: 'None', icon: null, description: 'No service selected.' };
         const browserTTSService = { name: 'browser', caption: 'Browser TTS', icon: null, description: 'Uses the built-in browser text-to-speech capability.' }; // Add icon path if you have one

         // Computed properties to add defaults to the lists for display
         const ttsServicesWithDefaults = computed(() => [defaultNoneService, browserTTSService, ...ttsServices.value]);
         const sttServicesWithDefaults = computed(() => [defaultNoneService, ...sttServices.value]);
         const ttiServicesWithDefaults = computed(() => [defaultNoneService, ...ttiServices.value]);
         const ttmServicesWithDefaults = computed(() => [defaultNoneService, ...ttmServices.value]);
         const ttvServicesWithDefaults = computed(() => [defaultNoneService, ...ttvServices.value]);


        const updateValue = (key, value) => {
            emit('setting-updated', { key, value });
        };

        const handleNumberInput = (key, value, isInt = false) => {
            let parsedValue = isInt ? parseInt(value) : parseFloat(value);
            if (isNaN(parsedValue)) {
                // For device dropdowns, value should be index (int)
                if (key === 'stt_input_device' || key === 'tts_output_device') {
                     console.warn(`Invalid device index selected for ${key}: ${value}`);
                     // Optionally reset to a default like -1 or the current value if invalid selection occurs
                     // parsedValue = -1; // Example: reset to default/invalid index
                     return; // Or just don't emit if invalid
                } else {
                    // Handle other number inputs if they become NaN
                     console.warn(`Invalid number for ${key}: ${value}`);
                     return; // Don't emit NaN
                }
            }
            updateValue(key, parsedValue);
        };

        const handleServiceSelect = ({ serviceType, serviceName }) => {
            console.log("Service selected ")
            console.log(serviceType)
            console.log(serviceName)
            const configKeyMap = {
                tts: 'active_tts_service',
                stt: 'active_stt_service',
                tti: 'active_tti_service',
                ttm: 'active_ttm_service',
                ttv: 'active_ttv_service'
            };
            const key = configKeyMap[serviceType];
            if (key) {
                updateValue(key, serviceName);
            }
        };


        const fetchServiceLists = async () => {
            try {
                const [ttsRes, sttRes, ttiRes, ttmRes, ttvRes] = await Promise.all([
                    props.api_post_req('list_tts_services'), props.api_post_req('list_stt_services'),
                    props.api_post_req('list_tti_services'), props.api_post_req('list_ttm_services'),
                    props.api_post_req('list_ttv_services')
                ]);
                // Assuming the response is the array of services
                ttsServices.value = Array.isArray(ttsRes) ? ttsRes : [];
                sttServices.value = Array.isArray(sttRes) ? sttRes : [];
                ttiServices.value = Array.isArray(ttiRes) ? ttiRes : [];
                ttmServices.value = Array.isArray(ttmRes) ? ttmRes : [];
                ttvServices.value = Array.isArray(ttvRes) ? ttvRes : [];
            } catch (error) {
                props.show_toast("Failed to fetch service lists.", 4, false);
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
            }
        };

        const refreshAudioDevices = () => {
            props.show_toast("Refreshing audio devices...", 2, true);
            fetchAudioDevices();
        };

        const showServiceSettings = async ({ serviceType, serviceName }) => {
            // Logic remains the same, triggered by the event from ServiceEntry
            if (!serviceName || serviceName === 'None' || serviceName === 'browser') {
                props.show_toast(`No configurable settings for '${serviceName}'.`, 3, false);
                return;
            }
             const endpointMap = {
                 tts: 'get_active_tts_settings', stt: 'get_active_stt_settings',
                 tti: 'get_active_tti_settings', ttm: 'get_active_ttm_settings',
                 ttv: 'get_active_ttv_settings'
             };
             const setEndpointMap = {
                 tts: 'set_active_tts_settings', stt: 'set_active_stt_settings',
                 tti: 'set_active_tti_settings', ttm: 'set_active_ttm_settings',
                 ttv: 'set_active_ttv_settings'
             };
             const getEndpoint = endpointMap[serviceType];
             const setEndpoint = setEndpointMap[serviceType];
            if (!getEndpoint || !setEndpoint) return;

            try {
                 // Fetch settings for the *currently selected* service for this type
                 // Need to map serviceType back to the config key to check props.config
                 const configKey = `active_${serviceType}_service`;
                 const currentService = props.config[configKey];

                 // Ensure we are fetching settings for the service whose button was clicked
                 // This is important if the UI allows clicking configure on non-active services (though disabled now)
                 if (currentService !== serviceName) {
                      props.show_toast(`Please select ${serviceName} first to configure its settings.`, 3, false);
                      return;
                 }

                 const settingsData = await props.api_post_req(getEndpoint); // Fetches settings of the *active* one server-side

                 if (settingsData && Object.keys(settingsData).length > 0) {
                     const result = await props.show_universal_form(settingsData, `${serviceName} Settings`, "Save", "Cancel");
                      if (result !== null && result !== undefined) {
                         const setResponse = await props.api_post_req(setEndpoint, { settings: result });
                          if (setResponse && setResponse.status) {
                             props.show_toast(`${serviceName} settings updated!`, 4, true);
                          } else {
                             props.show_toast(`Failed to update ${serviceName} settings: ${setResponse?.error || 'Error'}`, 4, false);
                          }
                     }
                 } else {
                     props.show_toast(`${serviceName} has no configurable settings.`, 3, false);
                 }
             } catch (error) {
                 props.show_toast(`Error with ${serviceName} settings: ${error.message}`, 4, false);
             }
        };

        const replaceFeatherIcons = () => {
             nextTick(() => { try { feather.replace(); } catch (e) {} });
        };

        onMounted(() => {
            fetchServiceLists();
            fetchAudioDevices();
            replaceFeatherIcons();
        });

        onUpdated(() => {
             replaceFeatherIcons();
        });

        return {
            baseUrl,
            ttsServices,
            sttServices,
            ttiServices,
            ttmServices,
            ttvServices,
            audioInputDevices,
            audioInputDeviceIndexes,
            audioOutputDevices,
            audioOutputDeviceIndexes,
            ttsServicesWithDefaults,
            sttServicesWithDefaults,
            ttiServicesWithDefaults,
            ttmServicesWithDefaults,
            ttvServicesWithDefaults,
            updateValue,
            handleNumberInput,
            handleServiceSelect, // Expose handler for template
            refreshAudioDevices,
            showServiceSettings
        };
    }
}
</script>

<style scoped>
.setting-item { @apply flex flex-col md:flex-row md:items-center gap-2 md:gap-4 py-2; }
.setting-label { @apply block text-sm font-medium text-gray-700 dark:text-gray-300 w-full md:w-1/3 lg:w-1/4 flex-shrink-0; }
.input { @apply block w-full px-3 py-2 bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-900 sm:text-sm disabled:opacity-50 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500; }
.input-sm { @apply block w-full px-2.5 py-1.5 text-sm bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-offset-gray-900 sm:text-sm disabled:opacity-50 dark:text-gray-100 placeholder-gray-400 dark:placeholder-gray-500; }
.panels-color { @apply bg-white dark:bg-gray-800; }
.toggle-item { @apply flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors; }
.toggle-label { @apply text-sm font-medium text-gray-700 dark:text-gray-300 cursor-pointer flex-1 mr-4; }
.toggle-description { @apply block text-xs text-gray-500 dark:text-gray-400 mt-1 font-normal; }
.btn { @apply inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-gray-900 disabled:opacity-50 transition-colors duration-150 whitespace-nowrap; }
.btn-sm { @apply px-2.5 py-1.5 text-xs; }
.btn-secondary { @apply text-gray-700 dark:text-gray-200 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 focus:ring-blue-500 border-gray-300 dark:border-gray-500 disabled:hover:bg-gray-100 dark:disabled:hover:bg-gray-700; }
</style>