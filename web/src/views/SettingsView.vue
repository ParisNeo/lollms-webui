<template>
    <div class="container pt-12 flex flex-row shadow-lg p-10 pt-0 overflow-y-scroll w-full background-color scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
        <!-- CONTROL PANEL -->
        <div
            class="sticky top-0 z-10 flex flex-row mb-2 p-3 gap-3 w-full rounded-b-lg  panels-color  shadow-lg">
            <!-- SAVE CONFIG -->
            <div v-if="showConfirmation" class="flex gap-3 flex-1 items-center duration-75">
                <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Cancel" type="button"
                    @click.stop="showConfirmation = false">
                    <i data-feather="x"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Confirm save changes"
                    type="button" @click.stop="save_configuration()">
                    <i data-feather="check"></i>
                </button>
            </div>
            <!-- SAVE AND RESET -->
            <div v-if="!showConfirmation" class="flex gap-3 flex-1 items-center">
                <button title="Reset configuration" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    @click="reset_configuration()">
                    <i data-feather="refresh-ccw"></i>
                </button>
                <button class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    title="Collapse / Expand all panels" type="button" @click.stop="all_collapsed = !all_collapsed">
                    <i data-feather="list"></i>
                </button>
            </div>
            
            <div class="flex gap-3 flex-1 items-center justify-end">
                <button
                    title="Clear uploads"
                    class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    @click="api_get_req('clear_uploads').then((res)=>{if(res.status){this.$store.state.toast.showToast('Success!', 4, true)}else{this.$store.state.toast.showToast(['failed!'], 4, false)}})"
                    >
                    <i data-feather="trash-2"></i>
                    </button>
                    <button
                    title="Restart program"
                    class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    @click="api_post_req('restart_program').then((res)=>{if(res.status){this.$store.state.toast.showToast('Success!', 4, true)}else{this.$store.state.toast.showToast(['failed!'], 4, false)}})"
                    >
                    <i data-feather="refresh-ccw"></i>
                    </button>
                    <button v-if="has_updates"
                    title="Upgrade program "
                    class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    @click="api_post_req('update_software').then((res)=>{if(res.status){this.$store.state.toast.showToast('Success!', 4, true)}else{this.$store.state.toast.showToast('Success!', 4, true)}})"
                    >
                    <i data-feather="arrow-up-circle"></i>
                    <i data-feather="alert-circle"></i>
                   </button>
                <div class="flex gap-3 items-center">
                    <div v-if="settingsChanged" class="flex gap-3 items-center">
                        <button v-if="!isLoading" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                            title="Apply changes" type="button" @click.stop="applyConfiguration()">
                            <div class="flex flex-row">
                                <p class="text-green-600 font-bold hover:text-green-300 ml-4 pl-4 mr-4 pr-4">Apply changes:</p>
                                <i data-feather="check"></i>
                            </div>
                        </button>
                        <button v-if="!isLoading" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                            title="Cancel changes" type="button" @click.stop="cancelConfiguration()">
                            <div class="flex flex-row">
                                <p class="text-red-600 font-bold hover:text-red-300 ml-4 pl-4 mr-4 pr-4">Cancel changes:</p>
                                <i data-feather="x"></i>
                            </div>
                        </button>
                    </div>

                    <!-- SPINNER -->
                    <div v-if="isLoading" role="status">
                        <p>{{ loading_text }}</p>
                        <svg aria-hidden="true" class="w-6 h-6   animate-spin  fill-secondary" viewBox="0 0 100 101"
                            fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path
                                d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                                fill="currentColor" />
                            <path
                                d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                                fill="currentFill" />
                        </svg>
                        <span class="sr-only">Loading...</span>
                    </div>

                </div>
            </div>
        </div>

        <div :class="isLoading ? 'pointer-events-none opacity-30 w-full' : 'w-full'">
            <!-- DISK AND RAM USAGE -->
            <div class="flex flex-col mb-2  rounded-lg panels-color hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="sc_collapsed = !sc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 w-full text-left flex flex-row items-center ">
                        <div v-show="sc_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!sc_collapsed" ><i data-feather='chevron-down'></i></div>


                        <p class="text-lg font-semibold cursor-pointer select-none mr-2">
                            System status</p>
                        <div class="mr-2">|</div>

                        <div class=" text-base font-semibold cursor-pointer select-none items-center">

                            <div class="flex gap-2 items-center ">
                                <div>
                                    <div v-if="vramUsage&&vramUsage.gpus && vramUsage.gpus.length == 1">
                                        <div class="flex gap-2 items-center " v-for="item in vramUsage.gpus" :key="item">
                                            <!-- GPU IMAGE  -->
                                            <img :src="SVGGPU"  width="25" height="25">

                                            <p class="font-bold font-large text-lg">
                                                <div>{{ computedFileSize(item.used_vram) }} / {{ computedFileSize(item.total_vram) }} ({{ item.percentage }}%)
                                                </div>
                                            </p>
                                        </div>
                                    </div>
                                    <div v-if="vramUsage&& vramUsage.gpus && vramUsage.gpus.length >1">
                                        <div class="flex gap-2 items-center ">

                                            <!-- GPU IMAGE  -->
                                            <img :src="SVGGPU"  width="25" height="25">
                                            <p class="font-bold font-large text-lg">
                                                <div> {{ vramUsage.gpus.length }}x
                                                </div>
                                            </p>

                                        </div>
                                    </div>
                                </div>
                                <i data-feather="cpu" title="CPU Ram" class="w-5 h-5 mx-1 flex-shrink-0"></i>
                                <p class="font-bold font-large text-lg">
                                    <div>{{ ram_usage }} / {{ ram_total_space }} ({{ ram_percent_usage }}%)</div>
                                </p>
                                <i data-feather="hard-drive" title="Hard drive" class="w-5 h-5 mx-1 flex-shrink-0"></i>
                                <p class="font-bold font-large text-lg">
                                    <div> {{ disk_binding_models_usage }} / {{ disk_total_space }} ({{ disk_percent_usage
                                    }}%)</div>
                                </p>
                            </div>
                        </div>
                    </button>
                </div>
                <div :class="{ 'hidden': sc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">

                    <div class="mb-2">

                        <label class=" flex items-center gap-1 ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                                <path fill="currentColor"
                                    d="M17 17H7V7h10m4 4V9h-2V7a2 2 0 0 0-2-2h-2V3h-2v2h-2V3H9v2H7c-1.11 0-2 .89-2 2v2H3v2h2v2H3v2h2v2a2 2 0 0 0 2 2h2v2h2v-2h2v2h2v-2h2a2 2 0 0 0 2-2v-2h2v-2h-2v-2m-6 2h-2v-2h2m2-2H9v6h6V9Z" />
                            </svg>
                            CPU Ram usage:
                        </label>
                        <div class="flex flex-col mx-2">
                            <div><b>Avaliable ram:&nbsp;</b>{{ ram_available_space }}</div>
                            <div><b>Ram usage:&nbsp;</b> {{ ram_usage }} / {{ ram_total_space }} ({{ ram_percent_usage }})%
                            </div>
                        </div>
                        <div class="p-2 ">
                            <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                                <div class="bg-blue-600 h-2.5 rounded-full" :style="'width: ' + ram_percent_usage + '%;'">
                                </div>
                            </div>

                        </div>
                    </div>
                    <div class="mb-2">
                        <label class="flex items-center gap-1 ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            <i data-feather="hard-drive" class="w-5 h-5"></i>
                            Disk usage:
                        </label>
                        <div class="flex flex-col mx-2">
                            <div><b>Avaliable disk space:&nbsp;</b>{{ disk_available_space }}</div>
                            <div><b>Disk usage:&nbsp;</b> {{ disk_binding_models_usage }} / {{ disk_total_space }}
                                ({{ disk_percent_usage }}%)</div>
                        </div>
                        <div class="p-2 ">
                            <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                                <div class="bg-blue-600 h-2.5 rounded-full" :style="'width: ' + disk_percent_usage + '%;'">
                                </div>
                            </div>

                        </div>
                    </div>
                    <div class="mb-2" v-for="item in vramUsage.gpus" :key="item">
                        <label class="flex items-center gap-1 ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            <!-- GPU IMAGE  -->
                            <img :src="SVGGPU"  width="25" height="25">

                            GPU usage:
                        </label>
                        <div class="flex flex-col mx-2">
                            <div><b>Model:&nbsp;</b>{{ item.gpu_model }}</div>
                            <div><b>Avaliable vram:&nbsp;</b>{{  this.computedFileSize(item.available_space) }}</div>
                            <div><b>GPU usage:&nbsp;</b> {{ this.computedFileSize(item.used_vram) }} / {{ this.computedFileSize(item.total_vram) }} ({{ item.percentage
                            }}%)</div>
                        </div>
                        <div class="p-2 ">
                            <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                                <div class="bg-blue-600 h-2.5 rounded-full" :style="'width: ' + item.percentage + '%;'">
                                </div>
                            </div>

                        </div>
                    </div>


                </div>
            </div>
            <!-- Router CONFIGS -->
            <div
                class="flex flex-col mb-2  rounded-lg panels-color hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="smartrouterconf_collapsed = !smartrouterconf_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <div v-show="smartrouterconf_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!smartrouterconf_collapsed" ><i data-feather='chevron-down'></i></div>

                        <div class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Smart routing configurations</div>
                    </button>
                </div>
                <div :class="{ 'hidden': smartrouterconf_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <div class="flex flex-col mb-2 px-3 pb-2">
                        <Card title="Smart Routing Settings" :is_shrunk="false" :is_subcard="true" class="pb-2 m-2">
                            <div class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <div class="flex flex-col space-y-4">
                                    <div class="flex items-center">
                                        <label for="use_smart_routing" class="text-sm font-bold w-64">Use Smart Routing:</label>
                                        <input
                                            type="checkbox"
                                            id="use_smart_routing"
                                            v-model="configFile.use_smart_routing"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                        >
                                    </div>
                                    
                                    <div class="flex items-center">
                                        <label for="restore_model_after_smart_routing" class="text-sm font-bold w-64">Restore model after smart routing:</label>
                                        <input
                                            type="checkbox"
                                            id="restore_model_after_smart_routing"
                                            v-model="configFile.restore_model_after_smart_routing"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                        >
                                    </div>
                                    
                                    <div class="flex items-center">
                                        <label for="smart_routing_router_model" class="text-sm font-bold w-64">Router Model:</label>
                                        <input
                                            type="text"
                                            id="smart_routing_router_model"
                                            v-model="configFile.smart_routing_router_model"
                                            @change="settingsChanged=true"
                                            class="flex-grow mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                        >
                                    </div>
                                    
                                    <div class="flex items-start">
                                        <label for="smart_routing_models_description" class="text-sm font-bold w-64 mt-1">Models with description:</label>
                                        <DictManager
                                            v-model="configFile.smart_routing_models_description"
                                            @change="settingsChanged = true"
                                            key-name="Model Path"
                                            value-name="Model description"
                                            placeholder="Enter model name"
                                            class="flex-grow"
                                        />
                                    </div>
                                </div>
                            </div>
                        </Card>

                    </div>
                </div>
            </div>
            <!-- MAIN CONFIGS -->
            <div
                class="flex flex-col mb-2  rounded-lg panels-color hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="mainconf_collapsed = !mainconf_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <div v-show="mainconf_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!mainconf_collapsed" ><i data-feather='chevron-down'></i></div>

                        <p class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Main configurations</p>
                    </button>
                </div>
                <div :class="{ 'hidden': mainconf_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <div class="flex flex-col mb-2 px-3 pb-2">
                        <Card title="General" :is_subcard="true" class="pb-2 m-2">
                            <div class="settings-container grid gap-6 p-6 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-300 dark:border-gray-600">
                                <!-- Existing sections remain unchanged -->
                                
                                <!-- User Information Section -->
                                <div class="setting-section">
                                    <h3 class="font-bold text-lg text-gray-800 dark:text-gray-200 mb-4">User Information</h3>
                                    <div class="settings-grid grid gap-4">
                                        <!-- User Name -->
                                        <div class="setting-row flex items-center gap-4">
                                            <div class="setting-label w-64">
                                                <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Username:</label>
                                            </div>
                                            <input type="text"
                                                v-model="configFile.user_name"
                                                @change="settingsChanged=true"
                                                class="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 
                                                        text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500">
                                        </div>
                                        
                                        <!-- User Description -->
                                        <div class="setting-row flex items-center gap-4">
                                            <div class="setting-label w-64">
                                                <label class="font-bold text-sm text-gray-700 dark:text-gray-200">User Description:</label>
                                            </div>
                                            <textarea
                                                v-model="configFile.user_description"
                                                @change="settingsChanged=true"
                                                class="flex-1 px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 
                                                        text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-blue-500"
                                                rows="3">
                                            </textarea>
                                        </div>

                                        <!-- User Avatar -->
                                        <div class="setting-row flex items-center gap-4">
                                            <div class="setting-label w-64">
                                                <label class="font-bold text-sm text-gray-700 dark:text-gray-200">User Avatar:</label>
                                            </div>
                                            <div class="setting-content flex items-center gap-4">
                                                <label for="avatar-upload" class="cursor-pointer">
                                                    <img :src="configFile.user_avatar ? `/user_infos/${configFile.user_avatar}` : defaultAvatar" 
                                                        class="w-12 h-12 rounded-full object-cover border-2 border-gray-300 hover:border-blue-500 transition-all">
                                                </label>
                                                <input type="file" id="avatar-upload" class="hidden" @change="uploadAvatar">
                                                <button @click.stop="resetAvatar()" 
                                                        class="text-gray-500 hover:text-red-600 p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-all"
                                                        title="Remove avatar">
                                                    <i data-feather="x"></i>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Discussion Settings -->
                                <div class="setting-section">
                                    <h3 class="font-bold text-lg text-gray-800 dark:text-gray-200 mb-4">Discussion Settings</h3>
                                    <div class="settings-grid grid gap-4">
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Use username in discussions</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.use_user_name_in_discussions"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Use assistant name in discussion</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.use_assistant_name_in_discussion"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Use model name in discussions</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.use_model_name_in_discussions"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Use user information in discussions</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.use_user_informations_in_discussion"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Debug Settings -->
                                <div class="setting-section">
                                    <h3 class="font-bold text-lg text-gray-800 dark:text-gray-200 mb-4">Debug Settings</h3>
                                    <div class="settings-grid grid gap-4">
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Enable Debug Mode</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.debug"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Show Final Full Prompt</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.debug_show_final_full_prompt"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Show Chunks</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.debug_show_chunks"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <!-- Auto-sync Settings -->
                                <div class="setting-section">
                                    <h3 class="font-bold text-lg text-gray-800 dark:text-gray-200 mb-4">Auto-sync Settings</h3>
                                    <div class="settings-grid grid gap-4">
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Auto Update</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.auto_update"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Auto Sync Personalities</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.auto_sync_personalities"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Auto Sync Extensions</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.auto_sync_extensions"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Auto Sync Bindings</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.auto_sync_bindings"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Auto Sync Models</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.auto_sync_models"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <!-- Webui Settings -->
                                <div class="setting-section">
                                    <h3 class="font-bold text-lg text-gray-800 dark:text-gray-200 mb-4">Webui Settings</h3>
                                    <div class="settings-grid grid gap-4">
                                        <!-- Logo Upload Section -->
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <div class="flex items-center space-x-4">
                                                <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Application Logo</label>
                                                <!-- Logo Preview -->
                                                <div class="w-10 h-10 rounded-full overflow-hidden bg-gray-200 dark:bg-gray-700">
                                                    <img v-if="configFile.app_custom_logo" 
                                                        :src="'/user_infos/' + configFile.app_custom_logo" 
                                                        class="w-full h-full object-cover"
                                                        alt="Custom Logo">
                                                    <img v-else 
                                                        :src="defaultImgPlaceholder" 
                                                        class="w-full h-full object-cover"
                                                        alt="Default Logo">
                                                </div>
                                            </div>
                                            <div class="flex items-center space-x-2">
                                                <!-- Remove logo button (only show if custom logo exists) -->
                                                <button v-if="configFile.app_custom_logo"
                                                        @click="removeLogo"
                                                        class="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg">
                                                    Remove Logo
                                                </button>
                                                <label class="cursor-pointer bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg">
                                                    Upload Logo
                                                    <input type="file" 
                                                        @change="uploadLogo" 
                                                        accept="image/*"
                                                        class="hidden">
                                                </label>
                                            </div>
                                        </div>
                                        <!-- Auto Title Setting -->
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <div class="flex items-center space-x-2">
                                                <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Automatic Discussion Naming</label>
                                                <div class="text-xs text-gray-500 dark:text-gray-400">(Let AI name your discussions automatically)</div>
                                            </div>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.auto_title"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>

                                        <!-- Auto Show Browser Setting -->
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <div class="flex items-center space-x-2">
                                                <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Auto-launch Browser</label>
                                                <div class="text-xs text-gray-500 dark:text-gray-400">(Open browser automatically when starting LOLLMS)</div>
                                            </div>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.auto_show_browser"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>

                                        <!-- Remote Access Warning -->
                                        <div class="setting-row flex flex-col p-4 bg-red-50 dark:bg-red-900/20 rounded-lg shadow-sm border-2 border-red-200 dark:border-red-800">
                                            <div class="flex items-center justify-between">
                                                <div class="flex items-center space-x-2">
                                                    <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                                                    </svg>
                                                    <label class="font-bold text-sm text-red-700 dark:text-red-400">Remote Access</label>
                                                </div>
                                                <div class="relative inline-block w-12 h-6">
                                                    <input type="checkbox"
                                                        v-model="configFile.force_accept_remote_access"
                                                        @change="settingsChanged=true"
                                                        class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                    <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                                </div>
                                            </div>
                                            <p class="mt-2 text-sm text-red-600 dark:text-red-400">
                                                <strong>Security Warning:</strong> Enabling remote access poses significant security risks. Only enable this if you:
                                                <ul class="list-disc ml-6 mt-1">
                                                    <li>Fully understand the security implications</li>
                                                    <li>Have proper network security measures in place</li>
                                                    <li>Are in a trusted network environment</li>
                                                </ul>
                                            </p>
                                        </div>

                                        <!-- Copy with Details Setting -->
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <div class="flex items-center space-x-2">
                                                <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Enhanced Message Copy</label>
                                                <div class="text-xs text-gray-500 dark:text-gray-400">
                                                    (Include metadata like sender name and model info when copying messages)
                                                </div>
                                            </div>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.copy_to_clipboard_add_all_details"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>

                                        <!-- Headless Mode -->
                                        <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                            <label class="font-bold text-sm text-gray-700 dark:text-gray-200">Headless server mode (DEACTIVATES the WEBUI)</label>
                                            <div class="relative inline-block w-12 h-6">
                                                <input type="checkbox"
                                                    v-model="configFile.headless_server_mode"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </Card>

                                <Card  title="Model template" :is_subcard="true" class="pb-2  m-2">
                                    <div class="grid gap-6 bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
                                        <!-- Template Selection -->
                                        <div class="flex flex-col space-y-2">
                                            <label class="text-sm font-semibold text-gray-700 dark:text-gray-300">Template Type</label>
                                            <select @change="handleTemplateSelection" 
                                                    class="form-select w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                                <option value="lollms">Lollms communication template</option>
                                                <option value="lollms_simplified">Lollms simplified communication template</option>
                                                <option value="bare">Bare, useful when in chat mode</option>
                                                <option value="llama3">LLama3 communication template</option>
                                                <option value="mistral">Mistral communication template</option>
                                                <option value="deepseek">DeepSeek communication template</option>
                                            </select>
                                        </div>

                                        <!-- Header Templates -->
                                        <div class="grid md:grid-cols-2 gap-4">
                                            <div class="space-y-2">
                                                <label for="start_header_id_template" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                    Start Header Template
                                                </label>
                                                <input type="text" id="start_header_id_template"
                                                    v-model="configFile.start_header_id_template"
                                                    @change="settingsChanged=true"
                                                    class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                            </div>
                                            <div class="space-y-2">
                                                <label for="end_header_id_template" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                    End Header Template
                                                </label>
                                                <input type="text" id="end_header_id_template"
                                                    v-model="configFile.end_header_id_template"
                                                    @change="settingsChanged=true"
                                                    class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                            </div>
                                        </div>

                                        <!-- User Templates -->
                                        <div class="grid md:grid-cols-2 gap-4">
                                            <div class="space-y-2">
                                                <label for="start_user_header_id_template" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                    Start User Header Template
                                                </label>
                                                <input type="text" id="start_user_header_id_template"
                                                    v-model="configFile.start_user_header_id_template"
                                                    @change="settingsChanged=true"
                                                    class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                            </div>
                                            <div class="space-y-2">
                                                <label for="end_user_header_id_template" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                    End User Header Template
                                                </label>
                                                <input type="text" id="end_user_header_id_template"
                                                    v-model="configFile.end_user_header_id_template"
                                                    @change="settingsChanged=true"
                                                    class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                            </div>
                                        </div>

                                        <!-- AI Templates -->
                                        <div class="grid md:grid-cols-2 gap-4">
                                            <div class="space-y-2">
                                                <label for="start_ai_header_id_template" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                    Start AI Header Template
                                                </label>
                                                <input type="text" id="start_ai_header_id_template"
                                                    v-model="configFile.start_ai_header_id_template"
                                                    @change="settingsChanged=true"
                                                    class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                            </div>
                                            <div class="space-y-2">
                                                <label for="end_ai_header_id_template" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                    End AI Header Template
                                                </label>
                                                <input type="text" id="end_ai_header_id_template"
                                                    v-model="configFile.end_ai_header_id_template"
                                                    @change="settingsChanged=true"
                                                    class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                            </div>
                                        </div>

                                        <!-- Message End Templates -->
                                        <div class="grid md:grid-cols-2 gap-4">
                                            <div class="space-y-2">
                                                <label for="end_user_message_id_template" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                    End User Message Template
                                                </label>
                                                <input type="text" id="end_user_message_id_template"
                                                    v-model="configFile.end_user_message_id_template"
                                                    @change="settingsChanged=true"
                                                    class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                            </div>
                                            <div class="space-y-2">
                                                <label for="end_ai_message_id_template" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                    End AI Message Template
                                                </label>
                                                <input type="text" id="end_ai_message_id_template"
                                                    v-model="configFile.end_ai_message_id_template"
                                                    @change="settingsChanged=true"
                                                    class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                            </div>
                                        </div>

                                        <!-- Separator and System Templates -->
                                        <div class="space-y-2">
                                            <label for="separator_template" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                Separator Template
                                            </label>
                                            <textarea id="separator_template"
                                                    v-model="configFile.separator_template"
                                                    @change="settingsChanged=true"
                                                    class="w-full h-24 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                            </textarea>
                                        </div>

                                        <div class="space-y-2">
                                            <label for="system_message_template" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                System Template
                                            </label>
                                            <input type="text" id="system_message_template"
                                                v-model="configFile.system_message_template"
                                                @change="settingsChanged=true"
                                                class="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-300 focus:border-blue-500 focus:ring-blue-500">
                                        </div>

                                        <!-- Full Template Preview -->
                                        <div class="space-y-2">
                                            <label class="text-sm font-semibold text-gray-700 dark:text-gray-300">Full Template Preview</label>
                                            <div class="p-4 bg-gray-100 dark:bg-gray-900 rounded-md">
                                                <div v-html="full_template"></div>
                                            </div>
                                        </div>

                                        <!-- Continue Message Toggle -->
                                        <div class="flex items-center space-x-4">
                                            <label for="use_continue_message" class="text-sm font-semibold text-gray-700 dark:text-gray-300">
                                                Use Continue Message
                                            </label>
                                            <div class="relative inline-block w-10 mr-2 align-middle select-none transition duration-200 ease-in">
                                                <input type="checkbox" 
                                                    id="use_continue_message"
                                                    v-model="configFile.use_continue_message"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                <label for="use_continue_message" 
                                                    class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer">
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </Card>

                                <Card  title="User" :is_subcard="true" class="pb-2  m-2">
                                    <div class="grid gap-6 bg-gray-50 dark:bg-gray-700 p-6 rounded-lg shadow-md">
                                        <!-- User Name -->
                                        <div class="flex flex-col md:flex-row md:items-center gap-4">
                                            <label for="user_name" class="text-sm font-bold text-gray-700 dark:text-gray-200 min-w-[200px]">
                                                User Name
                                            </label>
                                            <input
                                                type="text"
                                                id="user_name"
                                                required
                                                v-model="configFile.user_name"
                                                @change="settingsChanged=true"
                                                class="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white"
                                            >
                                        </div>

                                        <!-- User Description -->
                                        <div class="flex flex-col md:flex-row md:items-start gap-4">
                                            <label for="user_description" class="text-sm font-bold text-gray-700 dark:text-gray-200 min-w-[200px]">
                                                User Description
                                            </label>
                                            <textarea
                                                id="user_description"
                                                required
                                                v-model="configFile.user_description"
                                                @change="settingsChanged=true"
                                                class="flex-1 h-[300px] px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white resize-none"
                                            ></textarea>
                                        </div>

                                        <!-- Toggles Group -->
                                        <div class="space-y-4">
                                            <div class="flex flex-col md:flex-row md:items-center gap-4">
                                                <label class="text-sm font-bold text-gray-700 dark:text-gray-200 min-w-[200px]">
                                                    Discussion Settings
                                                </label>
                                                <div class="flex-1 space-y-3">
                                                    <label class="flex items-center space-x-3 cursor-pointer">
                                                        <input
                                                            type="checkbox"
                                                            v-model="configFile.use_user_informations_in_discussion"
                                                            @change="settingsChanged=true"
                                                            class="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:bg-gray-600"
                                                        >
                                                        <span class="text-sm text-gray-700 dark:text-gray-200">Use user description in discussion</span>
                                                    </label>
                                                    <label class="flex items-center space-x-3 cursor-pointer">
                                                        <input
                                                            type="checkbox"
                                                            v-model="configFile.use_model_name_in_discussions"
                                                            @change="settingsChanged=true"
                                                            class="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:bg-gray-600"
                                                        >
                                                        <span class="text-sm text-gray-700 dark:text-gray-200">Use model name in discussion</span>
                                                    </label>
                                                    <label class="flex items-center space-x-3 cursor-pointer">
                                                        <input
                                                            type="checkbox"
                                                            v-model="configFile.use_user_name_in_discussions"
                                                            @change="settingsChanged=true"
                                                            class="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:bg-gray-600"
                                                        >
                                                        <span class="text-sm text-gray-700 dark:text-gray-200">Use User Name in discussions</span>
                                                    </label>
                                                </div>
                                            </div>
                                        </div>

                                        <!-- User Avatar -->
                                        <div class="flex flex-col md:flex-row md:items-center gap-4">
                                            <label class="text-sm font-bold text-gray-700 dark:text-gray-200 min-w-[200px]">
                                                User Avatar
                                            </label>
                                            <div class="flex items-center gap-4">
                                                <label for="avatar-upload" class="cursor-pointer">
                                                    <img 
                                                        :src="configFile.user_avatar!=null && configFile.user_avatar!=''?'/user_infos/'+configFile.user_avatar: storeLogo" 
                                                        class="w-16 h-16 rounded-full object-cover border-2 border-gray-300 hover:border-blue-500"
                                                    >
                                                </label>
                                                <input type="file" id="avatar-upload" class="hidden" @change="uploadAvatar">
                                                <button 
                                                    @click.stop="resetAvatar()"
                                                    class="p-2 text-gray-500 hover:text-red-500 transition-colors duration-200"
                                                    title="Remove avatar"
                                                >
                                                    <i data-feather="x" class="w-5 h-5"></i>
                                                </button>
                                            </div>
                                        </div>

                                        <!-- Token Settings -->
                                        <div class="space-y-4">
                                            <div class="flex flex-col md:flex-row md:items-center gap-4">
                                                <label for="max_n_predict" class="text-sm font-bold text-gray-700 dark:text-gray-200 min-w-[200px]">
                                                    Maximum Token Space
                                                </label>
                                                <input
                                                    type="number"
                                                    id="max_n_predict"
                                                    required
                                                    v-model="configFile.max_n_predict"
                                                    @change="settingsChanged=true"
                                                    class="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white"
                                                >
                                            </div>
                                            <div class="flex flex-col md:flex-row md:items-center gap-4">
                                                <label for="min_n_predict" class="text-sm font-bold text-gray-700 dark:text-gray-200 min-w-[200px]">
                                                    Minimum Token Space
                                                </label>
                                                <input
                                                    type="number"
                                                    id="min_n_predict"
                                                    required
                                                    v-model="configFile.min_n_predict"
                                                    @change="settingsChanged=true"
                                                    class="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:border-gray-500 dark:text-white"
                                                >
                                            </div>
                                        </div>
                                    </div>
                                </Card>  
                                <Card  title="Security settings" :is_subcard="true" class="pb-2  m-2">
                                    <div class="settings-container p-6 space-y-4 bg-gray-50 dark:bg-gray-800 rounded-xl shadow-md">
                                        <div class="setting-row flex items-center justify-between p-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                                            <label for="turn_on_code_execution" class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                                Turn on code execution
                                            </label>
                                            <div class="relative">
                                                <input
                                                    type="checkbox"
                                                    id="turn_on_code_execution"
                                                    required
                                                    v-model="configFile.turn_on_code_execution"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500"
                                                >
                                            </div>
                                        </div>

                                        <div class="setting-row flex items-center justify-between p-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                                            <label for="turn_on_code_validation" class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                                Turn on code validation
                                                <span class="block text-xs text-gray-500 dark:text-gray-400">Very recommended for security reasons</span>
                                            </label>
                                            <div class="relative">
                                                <input
                                                    type="checkbox"
                                                    id="turn_on_code_validation"
                                                    required
                                                    v-model="configFile.turn_on_code_validation"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500"
                                                >
                                            </div>
                                        </div>

                                        <div class="setting-row flex items-center justify-between p-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                                            <label for="turn_on_setting_update_validation" class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                                Turn on apply settings validation
                                                <span class="block text-xs text-gray-500 dark:text-gray-400">Very recommended for security reasons</span>
                                            </label>
                                            <div class="relative">
                                                <input
                                                    type="checkbox"
                                                    id="turn_on_setting_update_validation"
                                                    required
                                                    v-model="configFile.turn_on_setting_update_validation"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500"
                                                >
                                            </div>
                                        </div>

                                        <div class="setting-row flex items-center justify-between p-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                                            <label for="turn_on_open_file_validation" class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                                Turn on open file/folder validation
                                            </label>
                                            <div class="relative">
                                                <input
                                                    type="checkbox"
                                                    id="turn_on_open_file_validation"
                                                    required
                                                    v-model="configFile.turn_on_open_file_validation"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500"
                                                >
                                            </div>
                                        </div>

                                        <div class="setting-row flex items-center justify-between p-3 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                                            <label for="turn_on_send_file_validation" class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                                Turn on send file validation
                                            </label>
                                            <div class="relative">
                                                <input
                                                    type="checkbox"
                                                    id="turn_on_send_file_validation"
                                                    required
                                                    v-model="configFile.turn_on_send_file_validation"
                                                    @change="settingsChanged=true"
                                                    class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500"
                                                >
                                            </div>
                                        </div>
                                    </div>
                                </Card>         
                                <Card title="Knowledge database" :is_subcard="true" class="pb-2  m-2">
                                    <div class="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg p-4 space-y-4">
                                        <!-- Skills Library Activation -->
                                        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                                            <label 
                                                for="activate_skills_lib" 
                                                class="text-sm font-bold text-gray-900 dark:text-white min-w-[200px]"
                                            >
                                                Activate Skills library:
                                            </label>
                                            <div class="flex items-center">
                                                <label class="relative inline-flex items-center cursor-pointer">
                                                    <input
                                                        type="checkbox"
                                                        id="activate_skills_lib"
                                                        required
                                                        v-model="configFile.activate_skills_lib"
                                                        @change="settingsChanged=true"
                                                        class="sr-only peer"
                                                    >
                                                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 
                                                            peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full 
                                                            peer dark:bg-gray-600 peer-checked:after:translate-x-full 
                                                            peer-checked:after:border-white after:content-[''] after:absolute 
                                                            after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 
                                                            after:border after:rounded-full after:h-5 after:w-5 after:transition-all 
                                                            dark:border-gray-600 peer-checked:bg-blue-600">
                                                    </div>
                                                </label>
                                            </div>
                                        </div>

                                        <!-- Database Name Input -->
                                        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                                            <label 
                                                for="skills_lib_database_name" 
                                                class="text-sm font-bold text-gray-900 dark:text-white min-w-[200px]"
                                            >
                                                Skills library database name:
                                            </label>
                                            <div class="flex-1">
                                                <input
                                                    type="text"
                                                    id="skills_lib_database_name"
                                                    required
                                                    v-model="configFile.skills_lib_database_name"
                                                    @change="settingsChanged=true"
                                                    class="w-full px-3 py-2 bg-white dark:bg-gray-600 border border-gray-300 
                                                        dark:border-gray-500 rounded-md focus:ring-2 focus:ring-blue-500 
                                                        focus:border-blue-500 dark:focus:ring-blue-500 dark:focus:border-blue-500 
                                                        text-gray-900 dark:text-white transition-colors duration-200"
                                                    placeholder="Enter database name"
                                                >
                                            </div>
                                        </div>
                                    </div>

                                </Card>
                                <Card title="Latex" :is_subcard="true" class="pb-2  m-2">
                                    <div class="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg shadow-sm border border-gray-200 dark:border-gray-600">
                                        <div class="flex flex-col sm:flex-row items-start sm:items-center gap-2">
                                            <div class="min-w-[200px]">
                                                <label 
                                                    for="pdf_latex_path" 
                                                    class="block text-sm font-semibold text-gray-700 dark:text-gray-200"
                                                >
                                                    PDF LaTeX Path:
                                                </label>
                                            </div>
                                            <div class="flex-1 w-full">
                                                <input
                                                    type="text"
                                                    id="pdf_latex_path"
                                                    required
                                                    v-model="configFile.pdf_latex_path"
                                                    @change="settingsChanged=true"
                                                    class="w-full px-4 py-2 text-sm bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:text-white dark:placeholder-gray-400 transition-colors duration-200"
                                                    placeholder="Enter PDF LaTeX path..."
                                                >
                                            </div>
                                        </div>
                                    </div>
                                </Card>
                                <Card title="Boost" :is_subcard="true" class="pb-2  m-2">
                                    <div class="settings-container bg-gray-50 dark:bg-gray-700 p-6 rounded-lg shadow-md">
                                        <div class="setting-row mb-4">
                                            <div class="flex items-center justify-between">
                                                <label for="positive_boost" class="text-sm font-bold text-gray-700 dark:text-gray-200">
                                                    Positive Boost
                                                </label>
                                                <div class="w-64">
                                                    <input
                                                        type="text"
                                                        id="positive_boost"
                                                        required
                                                        v-model="configFile.positive_boost"
                                                        @change="settingsChanged=true"
                                                        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-600 dark:border-gray-500 dark:text-white transition-all duration-200"
                                                    >
                                                </div>
                                            </div>
                                        </div>

                                        <div class="setting-row mb-4">
                                            <div class="flex items-center justify-between">
                                                <label for="negative_boost" class="text-sm font-bold text-gray-700 dark:text-gray-200">
                                                    Negative Boost
                                                </label>
                                                <div class="w-64">
                                                    <input
                                                        type="text"
                                                        id="negative_boost"
                                                        required
                                                        v-model="configFile.negative_boost"
                                                        @change="settingsChanged=true"
                                                        class="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-600 dark:border-gray-500 dark:text-white transition-all duration-200"
                                                    >
                                                </div>
                                            </div>
                                        </div>

                                        <div class="setting-row">
                                            <div class="flex items-center justify-between">
                                                <label for="fun_mode" class="text-sm font-bold text-gray-700 dark:text-gray-200">
                                                    Fun Mode
                                                </label>
                                                <div class="w-64">
                                                    <label class="inline-flex items-center cursor-pointer">
                                                        <input
                                                            type="checkbox"
                                                            id="fun_mode"
                                                            required
                                                            v-model="configFile.fun_mode"
                                                            @change="settingsChanged=true"
                                                            class="sr-only peer"
                                                        >
                                                        <div class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                                    </label>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </Card>
                    </div>
                </div>
            </div>

            <!-- Data settings-->

            <div
                class="flex flex-col mb-2  rounded-lg panels-color hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="data_conf_collapsed = !data_conf_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <div v-show="data_conf_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!data_conf_collapsed" ><i data-feather='chevron-down'></i></div>

                        <p class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Data management settings</p>
                    </button>
                </div>
                <div :class="{ 'hidden': data_conf_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <Card title="Data Lakes" :is_subcard="true" class="p-4 m-2">
                        <div class="space-y-6">
                            <div class="flex items-center mb-4">
                                <h3 class="text-lg font-semibold dark:text-white">Data Lakes Configuration</h3>
                            </div>
                            
                            <div class="space-y-4">
                                <div v-for="(source, index) in configFile.datalakes" :key="index" 
                                    class="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                                    
                                    <!-- Main Controls Grid -->
                                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
                                        <!-- Data Lake Alias -->
                                        <div class="flex flex-col">
                                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Data Lake Alias</label>
                                            <input
                                                type="text"
                                                :value="getDataLakeAlias(index)"
                                                @input="updateAlias(index, $event.target.value)"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                                placeholder="Enter alias"
                                            >
                                        </div>

                                        <!-- Data Lake Type -->
                                        <div class="flex flex-col">
                                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Type</label>
                                            <select
                                                required
                                                :value="getDataLakeType(index)"
                                                @input="updateDatabaseType(index, $event.target.value)"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                            >
                                                <option value="lollmsvectordb">Lollms VectorDB Folder</option>
                                                <option value="lightrag">Light Rag</option>
                                                <option value="elasticdsearch">Elastic Search</option>
                                            </select>
                                        </div>

                                        <!-- Conditional URL/Path Input -->
                                        <div class="flex flex-col lg:col-span-2">
                                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                                {{ source.type === 'lightrag' ? 'DataLake URL' : 'DataLake Path' }}
                                            </label>
                                            <input
                                                v-if="source.type === 'lightrag'"
                                                type="text"
                                                :value="getDataLakeUrl(index)"
                                                @input="updateDataLakeUrl(index, $event.target.value)"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                                placeholder="Enter DataLake URL"
                                            >
                                            <input
                                                v-if="source.type === 'lollmsvectordb'"
                                                type="text"
                                                :value="getDataLakePath(index)"
                                                @input="updateDataLakePath(index, $event.target.value)"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                                placeholder="Enter DataLake Path"
                                            >
                                        </div>

                                        <!-- API Key (for lightrag only) -->
                                        <div v-if="source.type === 'lightrag'" class="flex flex-col lg:col-span-2">
                                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">API Key</label>
                                            <input
                                                type="text"
                                                :value="getDataLakeKey(index)"
                                                @input="updateDatabaseKey(index, $event.target.value)"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                                placeholder="Enter API key"
                                            >
                                        </div>
                                    </div>

                                    <!-- Actions Row -->
                                    <div class="flex flex-wrap items-center justify-between mt-4 pt-3 border-t border-gray-200 dark:border-gray-700 gap-2">
                                        <div class="flex flex-wrap items-center gap-3">
                                            <!-- Mounted Toggle -->
                                            <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                                <label class="font-bold text-sm text-gray-700 dark:text-gray-200 mr-4">Mounted</label>
                                                <div class="relative inline-block w-12 h-6">
                                                    <input type="checkbox"
                                                        v-model="configFile.datalakes[index].mounted"
                                                        @change="settingsChanged=true"
                                                        class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                                transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                    <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                                </div>
                                            </div>


                                            <!-- VectorDB Specific Controls -->
                                            <div v-if="source.type === 'lollmsvectordb'" class="flex gap-2">
                                                <button @click="vectorize_folder(index)" 
                                                    class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-offset-2 focus:ring-green-500"
                                                    title="Vectorize or re-vectorize the selected folder">
                                                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                                                    </svg>
                                                    Vectorize
                                                </button>

                                                <button @click="lollms_vectordb_select_folder(index)" 
                                                    class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                                    title="Select a folder as data source">
                                                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                                                    </svg>
                                                    Select Folder
                                                </button>
                                            </div>

                                            <!-- File Upload -->
                                            <div class="inline-flex">
                                                <input type="file" ref="fileInput" @change="handleFileUpload" 
                                                    accept=".pdf,.txt,.doc,.docx,.csv,.md" class="hidden" multiple />
                                                <button @click="triggerFileInput" 
                                                    class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                                                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                                                    </svg>
                                                    Upload Files
                                                </button>
                                            </div>
                                        </div>

                                        <!-- Remove Button -->
                                        <button @click="removeDataLake(index)" 
                                            class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                                            </svg>
                                            Remove Data Lake
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <!-- Add New Data Lake Button -->
                            <button @click="addDataLake" 
                                class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                                </svg>
                                Add New Data Lake
                            </button>
                        </div>
                    </Card>
            
                    <Card title="Data Servers" :is_subcard="true" class="p-4 m-2">
                        <div class="space-y-6">
                            <div class="flex items-center mb-4">
                                <h3 class="text-lg font-semibold dark:text-white">Database Servers</h3>
                            </div>
                            
                            <div class="space-y-4">
                                <div v-for="(source, index) in configFile.rag_local_services" :key="index" 
                                    class="p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700">
                                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                                        <!-- Database Alias -->
                                        <div class="flex flex-col">
                                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Database Alias</label>
                                            <input
                                                type="text"
                                                :value="getServedDatabaseAlias(index)"
                                                @input="updateAlias(index, $event.target.value)"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                                placeholder="Enter alias"
                                            >
                                        </div>

                                        <!-- Database Type -->
                                        <div class="flex flex-col">
                                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Type</label>
                                            <select
                                                required
                                                :value="getServedDatabaseType(index)"
                                                @input="updateDatabaseType(index, $event.target.value)"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                            >
                                                <option value="lightrag">Light Rag</option>
                                                <option value="elasticdsearch">Elastic Search</option>
                                            </select>
                                        </div>

                                        <!-- Database URL -->
                                        <div class="flex flex-col lg:col-span-2">
                                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Database URL</label>
                                            <input
                                                type="text"
                                                :value="getServedDatabaseUrl(index)"
                                                @input="updateDataLakeUrl(index, $event.target.value)"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                                placeholder="Enter database URL"
                                            >
                                        </div>

                                        <!-- API Key -->
                                        <div class="flex flex-col lg:col-span-2">
                                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">API Key</label>
                                            <input
                                                type="text"
                                                :value="getServedDatabaseKey(index)"
                                                @input="updateDatabaseKey(index, $event.target.value)"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                                placeholder="Enter API key"
                                            >
                                        </div>

                                        <div class="flex flex-col lg:col-span-2">
                                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Input folder</label>
                                            <input
                                                type="text"
                                                v-model="configFile.rag_local_services[index].input_path"
                                                @change="settingsChanged=true"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                                placeholder="Input folder"
                                            >
                                        </div>
                                        <div class="flex flex-col lg:col-span-2">
                                            <label class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Input folder</label>
                                            <input
                                                type="text"
                                                v-model="configFile.rag_local_services[index].working_path"
                                                @change="settingsChanged=true"
                                                class="px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                                placeholder="Output folder"
                                            >
                                        </div>

                                    </div>

                                    <!-- Actions Row -->
                                    <div class="flex items-center justify-between mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
                                        <div class="flex items-center space-x-4">
                                            <div class="setting-row flex items-center justify-between p-4 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
                                                <label class="font-bold text-sm text-gray-700 dark:text-gray-200 mr-4">Start at Startup</label>
                                                <div class="relative inline-block w-12 h-6">
                                                    <input type="checkbox"
                                                        v-model="configFile.rag_local_services[index].start_at_startup"
                                                        @change="settingsChanged=true"
                                                        class="absolute block w-6 h-6 rounded-full bg-white border-4 appearance-none cursor-pointer
                                                            transition-transform duration-200 ease-in-out checked:translate-x-6 checked:bg-blue-500">
                                                    <label class="toggle-label block overflow-hidden h-6 rounded-full bg-gray-300 dark:bg-gray-600 cursor-pointer"></label>
                                                </div>
                                            </div>


                                            
                                            <input type="file" ref="fileInput2" @change="handleFileUpload" 
                                                accept=".pdf,.txt,.doc,.docx,.csv,.md" class="hidden" multiple />
                                            
                                            <button @click="triggerFileInput" 
                                                class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-green-600 rounded-md hover:bg-green-700 focus:ring-2 focus:ring-offset-2 focus:ring-green-500">
                                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"/>
                                                </svg>
                                                Upload Files
                                            </button>
                                        </div>
                                        
                                        <button @click="lightrag_select_input_folder(index)" 
                                            class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                            title="Select a folder as data source">
                                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                                            </svg>
                                            Select input Folder
                                        </button>
                                        <button @click="lightrag_select_output_folder(index)" 
                                            class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                                            title="Select a folder as data source">
                                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z"></path>
                                            </svg>
                                            Select work Folder
                                        </button>

                                        <button @click="removeServedDataBase(index)" 
                                            class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 focus:ring-2 focus:ring-offset-2 focus:ring-red-500">
                                            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                                            </svg>
                                            Remove Database
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <button @click="addDatabaseService" 
                                class="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
                                </svg>
                                Add New Database Server
                            </button>
                        </div>
                    </Card>


                    <Card title="LollmsVectordb Configuration" :is_subcard="true" class="pb-2  m-2">
                        <div class="bg-gray-50 dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg p-6 space-y-6">
                            <!-- RAG Vectorizer -->
                            <div class="flex flex-col md:flex-row md:items-center gap-4">
                                <label for="rag_vectorizer" class="text-sm font-bold w-64">RAG Vectorizer:</label>
                                <select
                                    id="rag_vectorizer"
                                    required
                                    v-model="configFile.rag_vectorizer"
                                    @change="settingsChanged=true"
                                    class="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:border-gray-500"
                                >
                                    <option value="semantic">Semantic Vectorizer</option>
                                    <option value="tfidf">TFIDF Vectorizer</option>
                                    <option value="openai">OpenAI Vectorizer</option>
                                    <option value="ollama">Ollama Vectorizer</option>
                                </select>
                            </div>

                            <!-- Allow executing remote code -->
                            <div class="flex flex-col md:flex-row md:items-center gap-4">
                                <label class="text-sm font-bold w-64">Allow executing remote code:</label>
                                <div class="flex-1">
                                    <label class="inline-flex items-center">
                                        <input 
                                            v-model="configFile.rag_vectorizer_execute_remote_code"
                                            type="checkbox"
                                            @change="settingsChanged=true"
                                            class="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:bg-gray-600"
                                        >
                                    </label>
                                </div>
                            </div>

                            <!-- RAG Vectorizer model -->
                            <div class="flex flex-col md:flex-row md:items-start gap-4">
                                <label class="text-sm font-bold w-64 pt-2">RAG Vectorizer model:</label>
                                <div class="flex-1 space-y-2">
                                    <select
                                        id="rag_vectorizer_model"
                                        required
                                        v-model="configFile.rag_vectorizer_model"
                                        @change="settingsChanged=true"
                                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:border-gray-500"
                                        :disabled="configFile.rag_vectorizer === 'tfidf'"
                                    >
                                        <!-- Semantic Vectorizer Models -->
                                        <optgroup v-if="configFile.rag_vectorizer === 'semantic'" label="Semantic Models">
                                            <option value="BAAI/bge-m3">BAAI/bge-m3</option>
                                            <option value="nvidia/NV-Embed-v2">nvidia/NV-Embed-v2</option>
                                            <option value="sentence-transformers/all-MiniLM-L6-v2">sentence-transformers/all-MiniLM-L6-v2</option>
                                            <option value="sentence-transformers/all-MiniLM-L12-v2">sentence-transformers/all-MiniLM-L12-v2</option>
                                            <option value="sentence-transformers/all-distilroberta-v1">sentence-transformers/all-distilroberta-v1</option>
                                            <option value="sentence-transformers/all-mpnet-base-v2">sentence-transformers/all-mpnet-base-v2</option>
                                        </optgroup>

                                        <!-- OpenAI Models -->
                                        <optgroup v-if="configFile.rag_vectorizer === 'openai'" label="OpenAI Models">
                                            <option value="text-embedding-ada-002">text-embedding-ada-002</option>
                                            <option value="text-embedding-babbage-001">text-embedding-babbage-001</option>
                                            <option value="text-embedding-curie-001">text-embedding-curie-001</option>
                                            <option value="text-embedding-davinci-001">text-embedding-davinci-001</option>
                                        </optgroup>

                                        <!-- Ollama Models -->
                                        <optgroup v-if="configFile.rag_vectorizer === 'ollama'" label="Ollama Models">
                                            <option value="bge-m3">bge-m3</option>
                                            <option value="NV-Embed-v2">nvidia/NV-Embed-v2</option>
                                            <option value="nomic-embed-text">nomic-embed-text</option>
                                            <option value="mxbai-embed-large">mxbai-embed-large</option>
                                            <option value="snowflake-arctic-embed">snowflake-arctic-embed</option>
                                            <option value="all-minilm">all-minilm</option>
                                            <option value="bge-large">bge-large</option>
                                        </optgroup>

                                        <option v-if="configFile.rag_vectorizer === 'tfidf'" disabled>No models available for TFIDF</option>
                                    </select>
                                    <input 
                                        v-model="configFile.rag_vectorizer_model" 
                                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:border-gray-500"
                                    >

                                </div>
                            </div>
                            <div class="flex flex-col md:flex-row md:items-start gap-4">
                                <label class="text-sm font-bold w-64 pt-2">RAG server address:</label>
                                <input v-if="configFile.rag_vectorizer === 'ollama'"
                                        v-model="configFile.rag_service_url" 
                                        class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:border-gray-500"
                                    >
                            </div>
                            <!-- Numeric inputs with sliders -->
                            <div class="space-y-6">
                                <!-- Chunk Size -->
                                <div class="flex flex-col md:flex-row md:items-start gap-4">
                                    <label class="text-sm font-bold w-64">RAG chunk size:</label>
                                    <div class="flex-1 space-y-2">
                                        <input 
                                            id="rag_chunk_size" 
                                            v-model="configFile.rag_chunk_size"
                                            @change="settingsChanged=true"
                                            type="range" 
                                            min="2" 
                                            max="64000" 
                                            step="1"
                                            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600"
                                        >
                                        <input 
                                            v-model="configFile.rag_chunk_size"
                                            type="number"
                                            @change="settingsChanged=true"
                                            class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-600 dark:border-gray-500"
                                        >
                                    </div>
                                </div>

                                <!-- Similar structure for other numeric inputs... -->
                            </div>

                            <!-- Checkboxes -->
                            <div class="space-y-4">
                                <div class="flex items-center gap-4">
                                    <label class="text-sm font-bold w-64">Clean chunks:</label>
                                    <div class="flex-1">
                                        <label class="inline-flex items-center">
                                            <input 
                                                v-model="configFile.rag_clean_chunks"
                                                type="checkbox"
                                                @change="settingsChanged=true"
                                                class="w-5 h-5 rounded border-gray-300 text-blue-600 focus:ring-blue-500 dark:bg-gray-600"
                                            >
                                        </label>
                                    </div>
                                </div>

                                <!-- Similar structure for other checkboxes... -->
                            </div>
                        </div>
                    </Card>
                    <Card title="Data Vectorization" :is_subcard="true" class="pb-2  m-2">
                        <div class="space-y-4 bg-gray-50 dark:bg-gray-800 rounded-lg p-6 shadow-sm border border-gray-200 dark:border-gray-700">
                            <!-- Reformulate Prompt Option -->
                            <div class="flex items-center justify-between hover:bg-gray-100 dark:hover:bg-gray-700 p-3 rounded-lg transition-colors">
                                <div class="flex-grow">
                                    <label for="rag_build_keys_words" class="font-medium text-gray-700 dark:text-gray-200">
                                        Reformulate prompt before querying database
                                        <span class="text-sm text-gray-500 dark:text-gray-400 block mt-1">
                                            (Recommended for better search results)
                                        </span>
                                    </label>
                                </div>
                                <div class="flex items-center">
                                    <label class="relative inline-flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            id="rag_build_keys_words"
                                            v-model="configFile.rag_build_keys_words"
                                            @change="settingsChanged=true"
                                            class="sr-only peer"
                                        >
                                        <div class="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                    </label>
                                </div>
                            </div>

                            <!-- Chunk Information Option -->
                            <div class="flex items-center justify-between hover:bg-gray-100 dark:hover:bg-gray-700 p-3 rounded-lg transition-colors">
                                <div class="flex-grow">
                                    <label for="rag_put_chunk_informations_into_context" class="font-medium text-gray-700 dark:text-gray-200">
                                        Put Chunk Information Into Context
                                    </label>
                                </div>
                                <div class="flex items-center">
                                    <label class="relative inline-flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            id="rag_put_chunk_informations_into_context"
                                            v-model="configFile.rag_put_chunk_informations_into_context"
                                            @change="settingsChanged=true"
                                            class="sr-only peer"
                                        >
                                        <div class="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                    </label>
                                </div>
                            </div>

                            <!-- Save Database Option -->
                            <div class="flex items-center justify-between hover:bg-gray-100 dark:hover:bg-gray-700 p-3 rounded-lg transition-colors">
                                <div class="flex-grow">
                                    <label for="data_vectorization_save_db" class="font-medium text-gray-700 dark:text-gray-200">
                                        Save new files to database
                                        <span class="text-sm text-gray-500 dark:text-gray-400 block mt-1">
                                            Database will persist and grow across sessions
                                        </span>
                                    </label>
                                </div>
                                <div class="flex items-center">
                                    <label class="relative inline-flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            id="data_vectorization_save_db"
                                            v-model="configFile.data_vectorization_save_db"
                                            @change="settingsChanged=true"
                                            class="sr-only peer"
                                        >
                                        <div class="w-11 h-6 bg-gray-200 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                    </label>
                                </div>
                            </div>
                        </div>
                    </Card>
                
                
                
                </div>
            </div>

            <div
                class="flex flex-col mb-2  rounded-lg panels-color hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="internet_conf_collapsed = !internet_conf_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <div v-show="internet_conf_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!internet_conf_collapsed" ><i data-feather='chevron-down'></i></div>

                        <p class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Internet</p>
                    </button>
                </div>


                                
                <div :class="{ 'hidden': internet_conf_collapsed }" class="flex flex-col mb-2 px-3 pb-0">

                    <Card title="Internet search" :is_subcard="true" class="pb-2  m-2">
                        <div class="grid gap-6 bg-gray-50 dark:bg-gray-700 rounded-lg p-6 border border-gray-300 dark:border-gray-600">
                            <!-- Internet Search Toggle -->
                            <div class="flex items-center justify-between">
                                <label for="activate_internet_search" class="text-sm font-bold text-gray-900 dark:text-white">
                                    Activate automatic internet search
                                </label>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" 
                                        id="fun_mode"
                                        v-model="configFile.activate_internet_search"
                                        @change="settingsChanged=true"
                                        class="sr-only peer">
                                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                </label>
                            </div>

                            <!-- Pages Judgement Toggle -->
                            <div class="flex items-center justify-between">
                                <label for="activate_internet_pages_judgement" class="text-sm font-bold text-gray-900 dark:text-white">
                                    Activate internet pages judgement
                                </label>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" 
                                        id="activate_internet_pages_judgement"
                                        v-model="configFile.activate_internet_pages_judgement"
                                        @change="settingsChanged=true"
                                        class="sr-only peer">
                                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                </label>
                            </div>

                            <!-- Quick Search Toggle -->
                            <div class="flex items-center justify-between">
                                <label for="internet_quick_search" class="text-sm font-bold text-gray-900 dark:text-white">
                                    Activate quick search
                                </label>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" 
                                        id="internet_quick_search"
                                        v-model="configFile.internet_quick_search"
                                        @change="settingsChanged=true"
                                        class="sr-only peer">
                                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                </label>
                            </div>

                            <!-- Search Decision Toggle -->
                            <div class="flex items-center justify-between">
                                <label for="internet_activate_search_decision" class="text-sm font-bold text-gray-900 dark:text-white">
                                    Activate search decision
                                </label>
                                <label class="relative inline-flex items-center cursor-pointer">
                                    <input type="checkbox" 
                                        id="internet_activate_search_decision"
                                        v-model="configFile.internet_activate_search_decision"
                                        @change="settingsChanged=true"
                                        class="sr-only peer">
                                    <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-600 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                </label>
                            </div>

                            <!-- Slider Controls -->
                            <div class="space-y-6">
                                <!-- Vectorization Chunk Size -->
                                <div class="flex flex-col gap-2">
                                    <label for="internet_vectorization_chunk_size" class="text-sm font-bold text-gray-900 dark:text-white">
                                        Internet vectorization chunk size
                                    </label>
                                    <div class="flex flex-col gap-4">
                                        <input id="internet_vectorization_chunk_size" 
                                            v-model="configFile.internet_vectorization_chunk_size"
                                            @change="settingsChanged=true"
                                            type="range" min="0" max="64000" step="1"
                                            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600">
                                        <input v-model="configFile.internet_vectorization_chunk_size"
                                            type="number"
                                            @change="settingsChanged=true"
                                            class="w-24 px-3 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-md text-sm">
                                    </div>
                                </div>

                                <!-- Overlap Size -->
                                <div class="flex flex-col gap-2">
                                    <label for="internet_vectorization_overlap_size" class="text-sm font-bold text-gray-900 dark:text-white">
                                        Internet vectorization overlap size
                                    </label>
                                    <div class="flex flex-col gap-4">
                                        <input id="internet_vectorization_overlap_size" 
                                            v-model="configFile.internet_vectorization_overlap_size"
                                            @change="settingsChanged=true"
                                            type="range" min="0" max="1000" step="1"
                                            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600">
                                        <input v-model="configFile.internet_vectorization_overlap_size"
                                            type="number"
                                            @change="settingsChanged=true"
                                            class="w-24 px-3 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-md text-sm">
                                    </div>
                                </div>

                                <!-- Number of Chunks -->
                                <div class="flex flex-col gap-2">
                                    <label for="internet_vectorization_nb_chunks" class="text-sm font-bold text-gray-900 dark:text-white">
                                        Internet vectorization number of chunks
                                    </label>
                                    <div class="flex flex-col gap-4">
                                        <input id="internet_vectorization_nb_chunks" 
                                            v-model="configFile.internet_vectorization_nb_chunks"
                                            @change="settingsChanged=true"
                                            type="range" min="0" max="100" step="1"
                                            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600">
                                        <input v-model="configFile.internet_vectorization_nb_chunks"
                                            type="number"
                                            @change="settingsChanged=true"
                                            class="w-24 px-3 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-md text-sm">
                                    </div>
                                </div>

                                <!-- Number of Search Pages -->
                                <div class="flex flex-col gap-2">
                                    <label for="internet_nb_search_pages" class="text-sm font-bold text-gray-900 dark:text-white">
                                        Internet number of search pages
                                    </label>
                                    <div class="flex flex-col gap-4">
                                        <input id="internet_nb_search_pages" 
                                            v-model="configFile.internet_nb_search_pages"
                                            @change="settingsChanged=true"
                                            type="range" min="1" max="100" step="1"
                                            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-600">
                                        <input v-model="configFile.internet_nb_search_pages"
                                            type="number"
                                            @change="settingsChanged=true"
                                            class="w-24 px-3 py-2 bg-white dark:bg-gray-600 border border-gray-300 dark:border-gray-500 rounded-md text-sm">
                                    </div>
                                </div>
                            </div>
                        </div>
                    </Card>
                </div>
            </div>

            <!-- Servers CONFIGS -->
            <div
                class="flex flex-col mb-2  rounded-lg panels-color hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="servers_conf_collapsed = !servers_conf_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <div v-show="servers_conf_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!servers_conf_collapsed" ><i data-feather='chevron-down'></i></div>

                        <p class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Services Zoo</p>
                    </button>
                </div>


                                
                <div :class="{ 'hidden': servers_conf_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <Card title="Default services selection" :is_subcard="true" class="pb-2  m-2">
                        <div class="grid gap-6 p-6 bg-white dark:bg-gray-800 rounded-xl shadow-lg">
                            <!-- TTS Service -->
                            <div class="flex flex-col md:flex-row md:items-center space-y-2 md:space-y-0 md:space-x-6">
                                <div class="w-full md:w-1/3">
                                    <label for="active_tts_service" class="block text-sm font-semibold text-gray-700 dark:text-gray-300" title="Default Text to speech engine">
                                        Active TTS Service
                                    </label>
                                </div>
                                <div class="w-full md:w-2/3">
                                    <select
                                        id="active_tts_service"
                                        required
                                        v-model="configFile.active_tts_service"
                                        @change="settingsChanged=true"
                                        class="w-full px-4 py-2 rounded-lg border border-gray-300 bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white transition-all duration-200"
                                    >
                                        <option value="None">None</option>
                                        <option value="browser">Use Browser TTS (doesn't work in realtime mode)</option>
                                        <option value="xtts">XTTS</option>
                                        <option value="parler-tts">Parler-TTS</option>
                                        <option value="openai_tts">Open AI TTS</option>
                                        <option value="eleven_labs_tts">ElevenLabs TTS</option>
                                        <option value="fish_tts">Fish TTS</option>
                                    </select>
                                </div>
                            </div>

                            <!-- STT Service -->
                            <div class="flex flex-col md:flex-row md:items-center space-y-2 md:space-y-0 md:space-x-6">
                                <div class="w-full md:w-1/3">
                                    <label for="active_stt_service" class="block text-sm font-semibold text-gray-700 dark:text-gray-300" title="Default Speech to Text engine">
                                        Active STT Service
                                    </label>
                                </div>
                                <div class="w-full md:w-2/3">
                                    <select
                                        id="active_stt_service"
                                        required
                                        v-model="configFile.active_stt_service"
                                        @change="settingsChanged=true"
                                        class="w-full px-4 py-2 rounded-lg border border-gray-300 bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white transition-all duration-200"
                                    >
                                        <option value="None">None</option>
                                        <option value="whisper">Whisper</option>
                                        <option value="openai_whisper">Open AI Whisper</option>
                                    </select>
                                </div>
                            </div>

                            <!-- TTI Service -->
                            <div class="flex flex-col md:flex-row md:items-center space-y-2 md:space-y-0 md:space-x-6">
                                <div class="w-full md:w-1/3">
                                    <label for="active_tti_service" class="block text-sm font-semibold text-gray-700 dark:text-gray-300" title="Default Text to image engine">
                                        Active TTI Service
                                    </label>
                                </div>
                                <div class="w-full md:w-2/3">
                                    <select
                                        id="active_tti_service"
                                        required
                                        v-model="configFile.active_tti_service"
                                        @change="settingsChanged=true"
                                        class="w-full px-4 py-2 rounded-lg border border-gray-300 bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white transition-all duration-200"
                                    >
                                        <option value="None">None</option>
                                        <option value="diffusers">Diffusers</option>
                                        <option value="diffusers_client">Diffusers Client</option>
                                        <option value="autosd">AUTO1111's SD</option>
                                        <option value="dall-e">Open AI DALL-E</option>
                                        <option value="midjourney">Midjourney</option>
                                        <option value="comfyui">Comfyui</option>
                                        <option value="fooocus">Fooocus</option>
                                    </select>
                                </div>
                            </div>

                            <!-- TTM Service -->
                            <div class="flex flex-col md:flex-row md:items-center space-y-2 md:space-y-0 md:space-x-6">
                                <div class="w-full md:w-1/3">
                                    <label for="active_ttm_service" class="block text-sm font-semibold text-gray-700 dark:text-gray-300" title="Default Text to Music engine">
                                        Active TTM Service
                                    </label>
                                </div>
                                <div class="w-full md:w-2/3">
                                    <select
                                        id="active_ttm_service"
                                        required
                                        v-model="configFile.active_ttm_service"
                                        @change="settingsChanged=true"
                                        class="w-full px-4 py-2 rounded-lg border border-gray-300 bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white transition-all duration-200"
                                    >
                                        <option value="None">None</option>
                                        <option value="musicgen">Music Gen</option>
                                    </select>
                                </div>
                            </div>

                            <!-- TTV Service -->
                            <div class="flex flex-col md:flex-row md:items-center space-y-2 md:space-y-0 md:space-x-6">
                                <div class="w-full md:w-1/3">
                                    <label for="active_ttv_service" class="block text-sm font-semibold text-gray-700 dark:text-gray-300" title="Default Text to Video engine">
                                        Active TTV Service
                                    </label>
                                </div>
                                <div class="w-full md:w-2/3">
                                    <select
                                        id="active_ttv_service"
                                        required
                                        v-model="configFile.active_ttv_service"
                                        @change="settingsChanged=true"
                                        class="w-full px-4 py-2 rounded-lg border border-gray-300 bg-gray-50 focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white transition-all duration-200"
                                    >
                                        <option value="None">None</option>
                                        <option value="cog_video_x">Cog Video X</option>
                                        <option value="diffusers">Diffusers</option>
                                        <option value="lumalab">Lumalab</option>
                                    </select>
                                </div>
                            </div>
                        </div>                  
                    </Card>
                    <Card title="TTI settings" :is_subcard="true" class="pb-2  m-2">
                        <div class="space-y-6 bg-gray-50 dark:bg-gray-800 p-6 rounded-lg shadow-md">
                            <!-- Use negative prompt -->
                            <div class="flex items-center space-x-4">
                                <div class="w-1/3">
                                    <label for="use_negative_prompt" class="text-sm font-semibold text-gray-700 dark:text-gray-200">
                                        Use negative prompt
                                    </label>
                                </div>
                                <div class="w-2/3">
                                    <label class="inline-flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            id="use_negative_prompt"
                                            v-model="configFile.use_negative_prompt"
                                            @change="settingsChanged=true"
                                            class="sr-only peer"
                                        >
                                        <div class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                    </label>
                                </div>
                            </div>

                            <!-- Use AI generated negative prompt -->
                            <div class="flex items-center space-x-4">
                                <div class="w-1/3">
                                    <label for="use_ai_generated_negative_prompt" class="text-sm font-semibold text-gray-700 dark:text-gray-200">
                                        Use AI generated negative prompt
                                    </label>
                                </div>
                                <div class="w-2/3">
                                    <label class="inline-flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            id="use_ai_generated_negative_prompt"
                                            v-model="configFile.use_ai_generated_negative_prompt"
                                            @change="settingsChanged=true"
                                            class="sr-only peer"
                                        >
                                        <div class="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                    </label>
                                </div>
                            </div>

                            <!-- Negative prompt generation prompt -->
                            <div class="flex items-center space-x-4">
                                <div class="w-1/3">
                                    <label for="negative_prompt_generation_prompt" class="text-sm font-semibold text-gray-700 dark:text-gray-200">
                                        Negative prompt generation prompt
                                    </label>
                                </div>
                                <div class="w-2/3">
                                    <input
                                        type="text"
                                        id="negative_prompt_generation_prompt"
                                        v-model="configFile.negative_prompt_generation_prompt"
                                        @change="settingsChanged=true"
                                        class="w-full px-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 text-sm text-gray-900 dark:text-white placeholder-gray-400"
                                        required
                                    >
                                </div>
                            </div>

                            <!-- Default negative prompt -->
                            <div class="flex items-center space-x-4">
                                <div class="w-1/3">
                                    <label for="default_negative_prompt" class="text-sm font-semibold text-gray-700 dark:text-gray-200">
                                        Default negative prompt
                                    </label>
                                </div>
                                <div class="w-2/3">
                                    <input
                                        type="text"
                                        id="default_negative_prompt"
                                        v-model="configFile.default_negative_prompt"
                                        @change="settingsChanged=true"
                                        class="w-full px-4 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors duration-200 text-sm text-gray-900 dark:text-white placeholder-gray-400"
                                        required
                                    >
                                </div>
                            </div>
                        </div>
                    </Card>
                    <Card title="Full Audio settings" :is_subcard="true" class="pb-2  m-2">
                        <div class="grid gap-6 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
                            <!-- Listening Threshold -->
                            <div class="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-4 items-center">
                                <div class="flex items-center">
                                    <label for="stt_listening_threshold" class="font-medium text-gray-700 dark:text-gray-200" title="Listening threshold">
                                        Listening threshold
                                    </label>
                                    <span class="ml-1 text-gray-400 hover:text-gray-600 cursor-help" title="Controls the sensitivity of voice detection">
                                        <i class="fas fa-info-circle"></i>
                                    </span>
                                </div>
                                <input
                                    type="number"
                                    step="1"
                                    id="stt_listening_threshold"
                                    required
                                    v-model="configFile.stt_listening_threshold"
                                    @change="settingsChanged=true"
                                    class="px-4 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                >
                            </div>

                            <!-- Silence Duration -->
                            <div class="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-4 items-center">
                                <div class="flex items-center">
                                    <label for="stt_silence_duration" class="font-medium text-gray-700 dark:text-gray-200">
                                        Silence duration (s)
                                    </label>
                                    <span class="ml-1 text-gray-400 hover:text-gray-600 cursor-help" title="Duration of silence before stopping recording">
                                        <i class="fas fa-info-circle"></i>
                                    </span>
                                </div>
                                <input
                                    type="number"
                                    step="1"
                                    id="stt_silence_duration"
                                    required
                                    v-model="configFile.stt_silence_duration"
                                    @change="settingsChanged=true"
                                    class="px-4 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                >
                            </div>

                            <!-- Sound Threshold Percentage -->
                            <div class="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-4 items-center">
                                <div class="flex items-center">
                                    <label for="stt_sound_threshold_percentage" class="font-medium text-gray-700 dark:text-gray-200">
                                        Minimum sound percentage
                                    </label>
                                    <span class="ml-1 text-gray-400 hover:text-gray-600 cursor-help" title="Minimum required sound percentage in recorded segment">
                                        <i class="fas fa-info-circle"></i>
                                    </span>
                                </div>
                                <input
                                    type="number"
                                    step="1"
                                    id="stt_sound_threshold_percentage"
                                    required
                                    v-model="configFile.stt_sound_threshold_percentage"
                                    @change="settingsChanged=true"
                                    class="px-4 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                >
                            </div>

                            <!-- Volume Amplification -->
                            <div class="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-4 items-center">
                                <div class="flex items-center">
                                    <label for="stt_gain" class="font-medium text-gray-700 dark:text-gray-200">
                                        Volume amplification
                                    </label>
                                    <span class="ml-1 text-gray-400 hover:text-gray-600 cursor-help" title="Audio input gain adjustment">
                                        <i class="fas fa-info-circle"></i>
                                    </span>
                                </div>
                                <input
                                    type="number"
                                    step="1"
                                    id="stt_gain"
                                    required
                                    v-model="configFile.stt_gain"
                                    @change="settingsChanged=true"
                                    class="px-4 py-2 bg-gray-50 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                >
                            </div>

                            <!-- Audio Settings Group -->
                            <div class="space-y-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                                <h3 class="font-semibold text-gray-900 dark:text-white mb-4">Audio Settings</h3>
                                
                                <!-- Audio Rate -->
                                <div class="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-4 items-center">
                                    <label for="stt_rate" class="font-medium text-gray-700 dark:text-gray-200">Audio rate</label>
                                    <input
                                        type="number"
                                        step="1"
                                        id="stt_rate"
                                        required
                                        v-model="configFile.stt_rate"
                                        @change="settingsChanged=true"
                                        class="px-4 py-2 bg-white border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-600 dark:border-gray-500 dark:text-white"
                                    >
                                </div>

                                <!-- Channels -->
                                <div class="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-4 items-center">
                                    <label for="stt_channels" class="font-medium text-gray-700 dark:text-gray-200">Number of channels</label>
                                    <input
                                        type="number"
                                        step="1"
                                        id="stt_channels"
                                        required
                                        v-model="configFile.stt_channels"
                                        @change="settingsChanged=true"
                                        class="px-4 py-2 bg-white border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-600 dark:border-gray-500 dark:text-white"
                                    >
                                </div>

                                <!-- Buffer Size -->
                                <div class="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-4 items-center">
                                    <label for="stt_buffer_size" class="font-medium text-gray-700 dark:text-gray-200">Buffer size</label>
                                    <input
                                        type="number"
                                        step="1"
                                        id="stt_buffer_size"
                                        required
                                        v-model="configFile.stt_buffer_size"
                                        @change="settingsChanged=true"
                                        class="px-4 py-2 bg-white border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-600 dark:border-gray-500 dark:text-white"
                                    >
                                </div>
                            </div>

                            <!-- Word Detection Settings -->
                            <div class="space-y-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                                <h3 class="font-semibold text-gray-900 dark:text-white mb-4">Word Detection</h3>
                                
                                <!-- Activate Word Detection -->
                                <div class="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-4 items-center">
                                    <label for="stt_activate_word_detection" class="font-medium text-gray-700 dark:text-gray-200">
                                        Activate word detection
                                    </label>
                                    <div class="flex items-center">
                                        <label class="relative inline-flex items-center cursor-pointer">
                                            <input
                                                type="checkbox"
                                                id="stt_activate_word_detection"
                                                v-model="configFile.stt_activate_word_detection"
                                                @change="settingsChanged=true"
                                                class="sr-only peer"
                                            >
                                            <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                        </label>
                                    </div>
                                </div>

                                <!-- Word Detection File -->
                                <div class="grid grid-cols-1 md:grid-cols-[300px,1fr] gap-4 items-center">
                                    <label for="stt_word_detection_file" class="font-medium text-gray-700 dark:text-gray-200">
                                        Word detection wav file
                                    </label>
                                    <input
                                        type="text"
                                        id="stt_word_detection_file"
                                        required
                                        v-model="configFile.stt_word_detection_file"
                                        @change="settingsChanged=true"
                                        class="px-4 py-2 bg-white border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-600 dark:border-gray-500 dark:text-white"
                                    >
                                </div>
                            </div>
                        </div>               
                    </Card>
                    <Card title="Audio devices settings" :is_subcard="true" class="pb-2  m-2">
                        <div class="space-y-4 p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md">
                            <!-- Audio Input Device -->
                            <div class="flex flex-col md:flex-row md:items-center space-y-2 md:space-y-0 md:space-x-4">
                                <div class="md:w-1/3">
                                    <label 
                                        for="stt_input_device" 
                                        class="block text-sm font-semibold text-gray-700 dark:text-gray-200"
                                        title="Input device"
                                    >
                                        Audio Input Device
                                    </label>
                                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                        Select your microphone or audio input source
                                    </p>
                                </div>
                                <div class="md:w-2/3">
                                    <select
                                        id="stt_input_device"
                                        required
                                        v-model="configFile.stt_input_device"
                                        @change="settingsChanged=true"
                                        class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white transition-colors duration-200"
                                    >
                                        <option 
                                            v-for="(snd_input_device, index) in snd_input_devices" 
                                            :key="snd_input_device" 
                                            :value="snd_input_devices_indexes[index]"
                                        >
                                            {{ snd_input_device }}
                                        </option>
                                    </select>
                                </div>
                            </div>

                            <!-- Audio Output Device -->
                            <div class="flex flex-col md:flex-row md:items-center space-y-2 md:space-y-0 md:space-x-4 pt-4 border-t dark:border-gray-700">
                                <div class="md:w-1/3">
                                    <label 
                                        for="tts_output_device" 
                                        class="block text-sm font-semibold text-gray-700 dark:text-gray-200"
                                        title="Output device"
                                    >
                                        Audio Output Device
                                    </label>
                                    <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                        Select your speakers or audio output device
                                    </p>
                                </div>
                                <div class="md:w-2/3">
                                    <select
                                        id="tts_output_device"
                                        required
                                        v-model="configFile.tts_output_device"
                                        @change="settingsChanged=true"
                                        class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md shadow-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white transition-colors duration-200"
                                    >
                                        <option 
                                            v-for="(tts_output_device, index) in snd_output_devices" 
                                            :key="tts_output_device" 
                                            :value="snd_output_devices_indexes[index]"
                                        >
                                            {{ tts_output_device }}
                                        </option>
                                    </select>
                                </div>
                            </div>
                        </div>       
                    </Card>

                    <Card title="Lollms service" :is_shrunk="true" :is_subcard="true" class="pb-2 m-2">
                        <div class="grid gap-4 p-4 bg-gray-50 dark:bg-gray-800 rounded-lg shadow-md">
                            <div class="grid grid-cols-[200px,1fr] items-center gap-4">
                                <label for="host" class="font-semibold text-gray-700 dark:text-gray-200">Host:</label>
                                <input
                                    type="text"
                                    id="host"
                                    required
                                    v-model="configFile.host"
                                    @change="settingsChanged=true"
                                    class="input-field"
                                >
                            </div>

                            <div class="grid grid-cols-[200px,1fr] items-center gap-4">
                                <label for="lollms_access_keys" class="font-semibold text-gray-700 dark:text-gray-200">Access keys:</label>
                                <StringListManager
                                    v-model="configFile.lollms_access_keys"
                                    @change="settingsChanged = true"
                                    placeholder="Enter access key"
                                />
                            </div>

                            <div class="grid grid-cols-[200px,1fr] items-center gap-4">
                                <label for="port" class="font-semibold text-gray-700 dark:text-gray-200">Port:</label>
                                <input
                                    type="number"
                                    step="1"
                                    id="port"
                                    required
                                    v-model="configFile.port"
                                    @change="settingsChanged=true"
                                    class="input-field"
                                >
                            </div>

                            <div class="grid grid-cols-[200px,1fr] items-center gap-4">
                                <span class="font-semibold text-gray-700 dark:text-gray-200">Server Configuration:</span>
                                <div class="space-y-3">
                                    <label class="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            v-model="configFile.headless_server_mode"
                                            @change="settingsChanged=true"
                                            class="w-4 h-4 rounded accent-blue-500"
                                        >
                                        <span class="text-sm text-gray-600 dark:text-gray-300">Headless Server Mode</span>
                                    </label>

                                    <label class="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            v-model="configFile.activate_lollms_server"
                                            @change="settingsChanged=true"
                                            class="w-4 h-4 rounded accent-blue-500"
                                        >
                                        <span class="text-sm text-gray-600 dark:text-gray-300">LoLLMS Server</span>
                                    </label>

                                    <!-- LoLLMS Services -->
                                    <div class="pl-6 space-y-2 border-l-2 border-gray-200 dark:border-gray-600">
                                        <label v-for="service in ['rag', 'tts', 'stt', 'tti', 'itt', 'ttm']" 
                                            :key="service"
                                            class="flex items-center space-x-2 cursor-pointer">
                                            <input
                                                type="checkbox"
                                                :id="`activate_lollms_${service}_server`"
                                                v-model="configFile[`activate_lollms_${service}_server`]"
                                                @change="settingsChanged=true"
                                                class="w-4 h-4 rounded accent-blue-500"
                                            >
                                            <span class="text-sm text-gray-600 dark:text-gray-300">{{ service.toUpperCase() }} Server</span>
                                        </label>
                                    </div>
                                </div>
                            </div>

                            <div class="grid grid-cols-[200px,1fr] items-center gap-4">
                                <span class="font-semibold text-gray-700 dark:text-gray-200">Emulators:</span>
                                <div class="space-y-3">
                                    <label v-for="emulator in ['ollama', 'openai', 'mistralai']" 
                                        :key="emulator"
                                        class="flex items-center space-x-2 cursor-pointer">
                                        <input
                                            type="checkbox"
                                            :id="`activate_${emulator}_emulator`"
                                            v-model="configFile[`activate_${emulator}_emulator`]"
                                            @change="settingsChanged=true"
                                            class="w-4 h-4 rounded accent-blue-500"
                                        >
                                        <span class="text-sm text-gray-600 dark:text-gray-300">{{ emulator.charAt(0).toUpperCase() + emulator.slice(1) }} Emulator</span>
                                    </label>
                                </div>
                            </div>
                        </div>

                    </Card>                    

                    <Card title="STT services" :is_shrunk="true" :is_subcard="true" class="pb-2  m-2">
                        <Card title="Browser Audio STT" :is_subcard="true" class="pb-2  m-2">
                            <div class="space-y-6 p-6 bg-white dark:bg-gray-800 rounded-lg shadow-md">
                                <!-- Activate Audio Infos -->
                                <div class="flex items-center justify-between">
                                    <label for="activate_audio_infos" class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                        Activate audio infos
                                    </label>
                                    <label class="relative inline-flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            id="activate_audio_infos"
                                            v-model="configFile.activate_audio_infos"
                                            @change="settingsChanged=true"
                                            class="sr-only peer"
                                        >
                                        <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                    </label>
                                </div>

                                <!-- Auto Send Audio Input -->
                                <div class="flex items-center justify-between">
                                    <label for="audio_auto_send_input" class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                        Send audio input automatically
                                    </label>
                                    <label class="relative inline-flex items-center cursor-pointer">
                                        <input
                                            type="checkbox"
                                            id="audio_auto_send_input"
                                            v-model="configFile.audio_auto_send_input"
                                            @change="settingsChanged=true"
                                            class="sr-only peer"
                                        >
                                        <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                    </label>
                                </div>

                                <!-- Silence Timer -->
                                <div class="space-y-2">
                                    <label for="audio_silenceTimer" class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                        Audio silence timer (ms): {{ configFile.audio_silenceTimer }}ms
                                    </label>
                                    <div class="flex flex-col gap-4">
                                        <input 
                                            id="audio_silenceTimer" 
                                            v-model="configFile.audio_silenceTimer"
                                            @change="settingsChanged=true"
                                            type="range" 
                                            min="0" 
                                            max="10000" 
                                            step="1"
                                            class="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700 accent-blue-600"
                                        >
                                        <input 
                                            v-model="configFile.audio_silenceTimer"
                                            @change="settingsChanged=true"
                                            type="number"
                                            class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                        >
                                    </div>
                                </div>

                                <!-- Input Audio Language -->
                                <div class="space-y-2">
                                    <label for="audio_in_language" class="text-sm font-medium text-gray-700 dark:text-gray-200">
                                        Input Audio Language
                                    </label>
                                    <select
                                        id="audio_in_language"
                                        v-model="configFile.audio_in_language"
                                        @change="settingsChanged=true"
                                        class="w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                                    >
                                        <option v-for="language in audioLanguages" :key="language.code" :value="language.code">
                                            {{ language.name }}
                                        </option>
                                    </select>
                                </div>
                            </div>

                        </Card>                           
                        <Card title="Whisper audio transcription" :is_subcard="true" class="pb-2  m-2">
                            <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 space-y-6">
                                <!-- Whisper Activation Section -->
                                <div class="flex items-center justify-between p-4 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-all">
                                    <label for="whisper_activate" class="text-gray-700 dark:text-gray-200 font-medium">
                                        Activate Whisper at startup
                                    </label>
                                    <label class="relative inline-flex items-center cursor-pointer">
                                        <input 
                                            type="checkbox" 
                                            id="whisper_activate"
                                            v-model="configFile.whisper_activate"
                                            @change="settingsChanged=true"
                                            class="sr-only peer"
                                        >
                                        <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                                    </label>
                                </div>

                                <!-- Install Whisper Button Section -->
                                <div class="p-4">
                                    <button 
                                        @click="reinstallWhisperService"
                                        class="w-full py-3 px-4 bg-gradient-to-r from-green-400 to-green-500 hover:from-green-500 hover:to-green-600 text-white font-medium rounded-lg shadow-md hover:shadow-lg transition-all duration-300 flex items-center justify-center space-x-2"
                                    >
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
                                        </svg>
                                        <span>Install Whisper</span>
                                    </button>
                                </div>

                                <!-- Whisper Model Selection Section -->
                                <div class="p-4">
                                    <label for="whisper_model" class="block text-sm font-medium text-gray-700 dark:text-gray-200 mb-2">
                                        Whisper Model
                                    </label>
                                    <div class="relative">
                                        <select
                                            id="whisper_model"
                                            v-model="configFile.whisper_model"
                                            @change="settingsChanged=true"
                                            class="block w-full px-4 py-3 text-base border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:text-white appearance-none"
                                        >
                                            <option v-for="whispermodel in whisperModels" :key="whispermodel" :value="whispermodel">
                                                {{ whispermodel }}
                                            </option>
                                        </select>
                                        <div class="pointer-events-none absolute inset-y-0 right-0 flex items-center px-2 text-gray-700 dark:text-gray-300">
                                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                                            </svg>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </Card>
                        <Card title="Open AI Whisper audio transcription" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="openai_whisper_key" class="text-sm font-bold" style="margin-right: 1rem;">openai whisper key:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="openai_whisper_key"
                                    required
                                    v-model="configFile.openai_whisper_key"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr>
                                <tr>                                    
                                <td style="min-width: 200px;">
                                    <label for="openai_whisper_model" class="text-sm font-bold" style="margin-right: 1rem;">Open Ai Whisper model:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <select
                                        id="openai_whisper_model"
                                        v-model="configFile.openai_whisper_model"
                                        @change="settingsChanged=true"
                                        class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                        <!-- Options with language codes and corresponding language names -->
                                        <option v-for="whispermodel in openaiWhisperModels" :key="whispermodel" :value="whispermodel">
                                        {{ whispermodel }}
                                        </option>
                                    </select>
                                    </div>
                                </td>
                                </tr>                                        

                            </table>
                        </Card>                        
                    </Card>
                    <Card title="TTS services" :is_shrunk="true" :is_subcard="true" class="pb-2  m-2">
                        <Card title="Browser Audio TTS" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="auto_speak" class="text-sm font-bold" style="margin-right: 1rem;">Enable auto speak:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="auto_speak"
                                    required
                                    v-model="configFile.auto_speak"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr>
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="audio_pitch" class="text-sm font-bold" style="margin-right: 1rem;">audio pitch:</label>
                                </td>
                                <td>
                                    <input id="audio_pitch" v-model="configFile.audio_pitch"
                                    @change="settingsChanged=true"
                                    type="range" min="0" max="10" step="0.1"
                                    class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    <input v-model="configFile.audio_pitch"
                                    @change="settingsChanged=true"
                                    class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                </td>
                                </tr>
                                <tr>
                                <td style="min-width: 200px;">
                                <label for="audio_out_voice" class="text-sm font-bold" style="margin-right: 1rem;">Output Audio Voice:</label>
                                </td>
                                <td>
                                <!-- Select element for choosing the output audio voice -->
                                <select
                                    id="audio_out_voice"
                                    v-model="configFile.audio_out_voice"
                                    @change="settingsChanged=true"
                                    class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                    <!-- Options with available voices in the browser -->
                                    <option v-for="voice in audioVoices" :key="voice.name" :value="voice.name">
                                    {{ voice.name }}
                                    </option>
                                </select>
                                </td>
                            </tr>                        
                                

                            </table>

                        </Card>                        
                        <Card title="XTTS service" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_current_language" class="text-sm font-bold" style="margin-right: 1rem;">Current language:</label>
                                </td>
                                <td>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallXTTSService">install xtts service</button>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_current_language" class="text-sm font-bold" style="margin-right: 1rem;">Current language:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <select v-model="xtts_current_language" @change="settingsChanged=true" >
                                        <option v-for="(value, key) in voice_languages" :key="key" :value="value">
                                            {{ key }}
                                        </option>
                                        </select>
                                    </div>
                                </td>
                                </tr>                                        

                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_current_voice" class="text-sm font-bold" style="margin-right: 1rem;">Current voice:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <select v-model="xtts_current_voice" @change="settingsChanged=true" >
                                        <option v-for="voice in voices" :key="voice" :value="voice">
                                            {{ voice }}
                                        </option>
                                        </select>
                                    </div>
                                </td>
                                </tr>
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_freq" class="text-sm font-bold" style="margin-right: 1rem;">Frequency (controls the tone):</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="number"
                                            id="xtts_freq"
                                            required
                                            v-model.number="configFile.xtts_freq"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            step="0.01"
                                        >
                                    </div>
                                </td>
                                </tr>

                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="auto_read" class="text-sm font-bold" style="margin-right: 1rem;">Enable auto read:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="checkbox"
                                            id="auto_read"
                                            required
                                            v-model="configFile.auto_read"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            
                                        >
                                    </div>
                                </td>
                                </tr>                    
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_stream_chunk_size" class="text-sm font-bold" style="margin-right: 1rem;">xtts stream chunk size:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="text"
                                            id="xtts_stream_chunk_size"
                                            required
                                            v-model="configFile.xtts_stream_chunk_size"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                        >
                                    </div>
                                </td>
                                </tr>
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_temperature" class="text-sm font-bold" style="margin-right: 1rem;">Temperature:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="number"
                                            id="xtts_temperature"
                                            required
                                            v-model.number="configFile.xtts_temperature"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            step="0.01"
                                        >
                                    </div>
                                </td>
                                </tr>

                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_length_penalty" class="text-sm font-bold" style="margin-right: 1rem;">Length Penalty:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="number"
                                            id="xtts_length_penalty"
                                            required
                                            v-model.number="configFile.xtts_length_penalty"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            step="0.1"
                                        >
                                    </div>
                                </td>
                                </tr>

                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_repetition_penalty" class="text-sm font-bold" style="margin-right: 1rem;">Repetition Penalty:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="number"
                                            id="xtts_repetition_penalty"
                                            required
                                            v-model.number="configFile.xtts_repetition_penalty"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            step="0.1"
                                        >
                                    </div>
                                </td>
                                </tr>

                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_top_k" class="text-sm font-bold" style="margin-right: 1rem;">Top K:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="number"
                                            id="xtts_top_k"
                                            required
                                            v-model.number="configFile.xtts_top_k"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                        >
                                    </div>
                                </td>
                                </tr>

                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_top_p" class="text-sm font-bold" style="margin-right: 1rem;">Top P:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="number"
                                            id="xtts_top_p"
                                            required
                                            v-model.number="configFile.xtts_top_p"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                        >
                                    </div>
                                </td>
                                </tr>

                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_speed" class="text-sm font-bold" style="margin-right: 1rem;">Speed:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="number"
                                            id="xtts_speed"
                                            required
                                            v-model.number="configFile.xtts_speed"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            step="0.1"
                                        >
                                    </div>
                                </td>
                                </tr>

                                <!-- Keeping the enable_text_splitting as is since it inherently respects the boolean data type -->
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="enable_text_splitting" class="text-sm font-bold" style="margin-right: 1rem;">Enable Text Splitting:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="checkbox"
                                            id="enable_text_splitting"
                                            v-model="configFile.enable_text_splitting"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                        >
                                    </div>
                                </td>
                                </tr>

                            </table>
                        </Card>
                        <Card title="Open AI TTS service" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="openai_tts_key" class="text-sm font-bold" style="margin-right: 1rem;">Open AI key:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="openai_tts_key"
                                    required
                                    v-model="configFile.openai_tts_key"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="openai_tts_model" class="text-sm font-bold" style="margin-right: 1rem;">openai tts model:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <select v-model="configFile.openai_tts_model" @change="settingsChanged=true">
                                        <option>
                                            tts-1
                                        </option>
                                        <option>
                                            tts-2
                                        </option>
                                        </select>
                                    </div>
                                </td>
                                </tr>                                 
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="openai_tts_voice" class="text-sm font-bold" style="margin-right: 1rem;">openai tts voice:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <select v-model="configFile.openai_tts_voice" @change="settingsChanged=true">
                                        <option>
                                            alloy
                                        </option>
                                        <option>
                                            echo
                                        </option>
                                        <option>
                                            fable
                                        </option>
                                        <option>
                                            nova
                                        </option>
                                        <option>
                                            shimmer
                                        </option>
                                        </select>
                                    </div>
                                </td>
                                </tr>                                 
                                
                            </table>
                        </Card>                        
                        <Card title="Eleven Labs TTS service" :is_subcard="true" class="pb-2 m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                    <td style="min-width: 200px;">
                                        <label for="elevenlabs_tts_key" class="text-sm font-bold" style="margin-right: 1rem;">Eleven Labs key:</label>
                                    </td>
                                    <td>
                                        <div class="flex flex-row">
                                            <input
                                                type="text"
                                                id="elevenlabs_tts_key"
                                                required
                                                v-model="configFile.elevenlabs_tts_key"
                                                @change="settingsChanged=true"
                                                class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            >
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="min-width: 200px;">
                                        <label for="elevenlabs_tts_model_id" class="text-sm font-bold" style="margin-right: 1rem;">Eleven Labs TTS model ID:</label>
                                    </td>
                                    <td>
                                        <div class="flex flex-row">
                                            <input
                                                type="text"
                                                id="elevenlabs_tts_model_id"
                                                required
                                                v-model="configFile.elevenlabs_tts_model_id"
                                                @change="settingsChanged=true"
                                                class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            >
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="min-width: 200px;">
                                        <label for="elevenlabs_tts_voice_stability" class="text-sm font-bold" style="margin-right: 1rem;">Voice Stability:</label>
                                    </td>
                                    <td>
                                        <div class="flex flex-row">
                                            <input
                                                type="number"
                                                id="elevenlabs_tts_voice_stability"
                                                required
                                                v-model="configFile.elevenlabs_tts_voice_stability"
                                                @change="settingsChanged=true"
                                                class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                                step="0.1"
                                                min="0" max="1"
                                            >
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="min-width: 200px;">
                                        <label for="elevenlabs_tts_voice_boost" class="text-sm font-bold" style="margin-right: 1rem;">Voice Boost:</label>
                                    </td>
                                    <td>
                                        <div class="flex flex-row">
                                            <input
                                                type="number"
                                                id="elevenlabs_tts_voice_boost"
                                                required
                                                v-model="configFile.elevenlabs_tts_voice_boost"
                                                @change="settingsChanged=true"
                                                class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                                step="0.1"
                                                min="0" max="1"
                                            >
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="min-width: 200px;">
                                        <label for="elevenlabs_tts_voice_id" class="text-sm font-bold" style="margin-right: 1rem;">Voice ID:</label>
                                    </td>
                                    <td>
                                        <div class="flex flex-row">
                                            <select v-model="configFile.elevenlabs_tts_voice_id" @change="settingsChanged=true">
                                                <option v-for="voice in voices" :key="voice.voice_id" :value="voice.voice_id">{{ voice.name }}</option>
                                            </select>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </Card>
                        <Card title="Fish TTS service" :is_subcard="true" class="pb-2 m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                    <td style="min-width: 200px;">
                                        <label for="fish_tts_key" class="text-sm font-bold" style="margin-right: 1rem;">Fish TTS key:</label>
                                    </td>
                                    <td>
                                        <div class="flex flex-row">
                                            <input
                                                type="text"
                                                id="fish_tts_key"
                                                required
                                                v-model="configFile.fish_tts_key"
                                                @change="settingsChanged=true"
                                                class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            >
                                        </div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="min-width: 200px;">
                                        <label for="fish_tts_voice" class="text-sm font-bold" style="margin-right: 1rem;">Fish TTS voice:</label>
                                    </td>
                                    <td>
                                        <div class="flex flex-row">
                                            <input
                                                type="text"
                                                id="fish_tts_voice"
                                                required
                                                v-model="configFile.fish_tts_voice"
                                                @change="settingsChanged=true"
                                                class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            >
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </Card>                        
                    </Card>
                
                    <Card title="TTI services" :is_shrunk="true" :is_subcard="true" class="pb-2  m-2">
                        <Card title="Stable diffusion service" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="enable_sd_service" class="text-sm font-bold" style="margin-right: 1rem;">Enable sd service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="enable_sd_service"
                                    required
                                    v-model="configFile.enable_sd_service"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                <td>
                                    <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary" @click="this.$store.state.messageBox.showMessage('Activates Stable diffusion service. The service will be automatically loaded at startup alowing you to use the stable diffusion endpoint to generate images')">
                                        <i data-feather="help-circle" class="w-5 h-5 "></i>
                                    </div>
                                </td>                            
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="install_sd_service" class="text-sm font-bold" style="margin-right: 1rem;">Install SD service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallSDService">install sd service</button>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="upgradeSDService">upgrade sd service</button>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="startSDService">start sd service</button>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="showSD">show sd ui</button>
                                    <a class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" href="https://github.com/ParisNeo/stable-diffusion-webui/blob/master/LICENSE.txt" target="_blank">automatic1111's sd licence</a>
                                    </div>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallSDService">install sd service</button>
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="sd_base_url" class="text-sm font-bold" style="margin-right: 1rem;">sd base url:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="sd_base_url"
                                    required
                                    v-model="configFile.sd_base_url"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
                            </table>                                
                        </Card>
                        <Card title="Diffusers service" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="install_diffusers_service" class="text-sm font-bold" style="margin-right: 1rem;">Install Diffusers service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallDiffusersService">install diffusers service</button>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="upgradeDiffusersService">upgrade diffusers service</button>
                                    <a class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" href="https://github.com/huggingface/diffusers?tab=Apache-2.0-1-ov-file#readme" target="_blank">Diffusers licence</a>
                                    </div>
                                </td>
                                </tr>
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="diffusers_model" class="text-sm font-bold" style="margin-right: 1rem;">Diffusers model:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="diffusers_model"
                                    required
                                    v-model="configFile.diffusers_model"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                <td>
                                </td>
                                </tr>
                            </table>                                
                        </Card>                        
                        <Card title="Diffusers client service" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="diffusers_client_base_url" class="text-sm font-bold" style="margin-right: 1rem;">Diffusers client base url:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="diffusers_client_base_url"
                                    required
                                    v-model="configFile.diffusers_client_base_url"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                <td>
                                </td>
                                </tr>
                            </table>                                
                        </Card>                        
                        <Card title="Midjourney" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="midjourney_key" class="text-sm font-bold" style="margin-right: 1rem;">midjourney key:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="midjourney_key"
                                    required
                                    v-model="configFile.midjourney_key"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="midjourney_timeout" class="text-sm font-bold" style="margin-right: 1rem;">request timeout(s):</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="number"
                                    min=10
                                    max=2048
                                    id="midjourney_timeout"
                                    required
                                    v-model="configFile.midjourney_timeout"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="midjourney_retries" class="text-sm font-bold" style="margin-right: 1rem;">number of retries:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="number"
                                    min=0
                                    max=2048
                                    id="midjourney_retries"
                                    required
                                    v-model="configFile.midjourney_retries"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
                            </table>                                
                        </Card>
                        <Card title="Dall-E" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="dall_e_key" class="text-sm font-bold" style="margin-right: 1rem;">dall e key:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="dall_e_key"
                                    required
                                    v-model="configFile.dall_e_key"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="dall_e_generation_engine" class="text-sm font-bold" style="margin-right: 1rem;">dall e generation engine:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <select v-model="configFile.dall_e_generation_engine" @change="settingsChanged=true">
                                        <option>
                                            dall-e-2
                                        </option>
                                        <option>
                                            dall-e-3
                                        </option>
                                        </select>
                                    </div>
                                </td>
                                </tr> 
                            </table>                                
                        </Card>

                        <Card title="ComfyUI service" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="enable_comfyui_service" class="text-sm font-bold" style="margin-right: 1rem;">Enable comfyui service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="enable_comfyui_service"
                                    required
                                    v-model="configFile.enable_comfyui_service"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                <td>
                                    <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary" @click="this.$store.state.messageBox.showMessage('Activates Stable diffusion service. The service will be automatically loaded at startup alowing you to use the stable diffusion endpoint to generate images')">
                                        <i data-feather="help-circle" class="w-5 h-5 "></i>
                                    </div>
                                </td>                            
                                </tr>
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="comfyui_model" class="text-sm font-bold" style="margin-right: 1rem;">Available models (only if local):</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <select
                                    id="comfyui_model"
                                    required
                                    v-model="configFile.comfyui_model"
                                    @change="settingsChanged=true"
                                    class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                        <option v-for="(comfyui_model, index) in comfyui_models" :key="comfyui_model" :value="comfyui_model">
                                            {{ comfyui_model }}
                                        </option>                                
                                    </select>
                                    </div>
                                </td>
                                </tr>                                                                     
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="comfyui_model" class="text-sm font-bold" style="margin-right: 1rem;">Enable comfyui model:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="comfyui_model"
                                    required
                                    v-model="configFile.comfyui_model"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                <td>
                                    <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary" @click="this.$store.state.messageBox.showMessage('Activates Stable diffusion service. The service will be automatically loaded at startup alowing you to use the stable diffusion endpoint to generate images')">
                                        <i data-feather="help-circle" class="w-5 h-5 "></i>
                                    </div>
                                </td>                            
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallComfyUIService">install comfyui service</button>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="upgradeComfyUIService">upgrade comfyui service</button>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="startComfyUIService">start comfyui service</button>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="showComfyui">show comfyui</button>
                                    <a class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" href="https://github.com/ParisNeo/ComfyUI/blob/master/LICENSE" target="_blank">comfyui licence</a>
                                    
                                    </div>
                                </td>
                                </tr>                                                                    
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="comfyui_base_url" class="text-sm font-bold" style="margin-right: 1rem;">comfyui base url:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="comfyui_base_url"
                                    required
                                    v-model="configFile.comfyui_base_url"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
                            </table>                                
                        </Card>                    


                    </Card>
                    <Card title="TTT services" :is_shrunk="true" :is_subcard="true" class="pb-2  m-2">
                        <Card title="Ollama service" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="enable_ollama_service" class="text-sm font-bold" style="margin-right: 1rem;">Enable ollama service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="enable_ollama_service"
                                    required
                                    v-model="configFile.enable_ollama_service"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                <td>
                                    <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary" @click="this.$store.state.messageBox.showMessage('Activates ollama service. The service will be automatically loaded at startup alowing you to use the ollama binding.\nIf you are using windows, this uses wsl which requires you to have it installed or at least activated.\nIf You are using windows, this will install wsl so you need to activate it.\n<a href=\'https://techcommunity.microsoft.com/t5/windows-11/how-to-install-the-linux-windows-subsystem-in-windows-11/m-p/2701207\' target=\'_blank\'>Here is how you can do that</a>')">
                                        <i data-feather="help-circle" class="w-5 h-5 "></i>
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="ollama_base_url" class="text-sm font-bold" style="margin-right: 1rem;">Install Ollama service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallOLLAMAService">install ollama service</button>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="startollamaService">start ollama service</button>
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="ollama_base_url" class="text-sm font-bold" style="margin-right: 1rem;">ollama base url:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="ollama_base_url"
                                    required
                                    v-model="configFile.ollama_base_url"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
                            </table>                                
                        </Card>
                        <Card title="vLLM service" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="enable_vllm_service" class="text-sm font-bold" style="margin-right: 1rem;">Enable vLLM service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="enable_vllm_service"
                                    required
                                    v-model="configFile.enable_vllm_service"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                <td>
                                    <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary" @click="this.$store.state.messageBox.showMessage('Activates vllm service. The service will be automatically loaded at startup alowing you to use the elf binding.\nIf you are using windows, this uses wsl which requires you to have it installed or at least activated.\nIf You are using windows, this will install wsl so you need to activate it.\n<a href=\'https://techcommunity.microsoft.com/t5/windows-11/how-to-install-the-linux-windows-subsystem-in-windows-11/m-p/2701207\' target=\'_blank\'>Here is how you can do that</a>')">
                                        <i data-feather="help-circle" class="w-5 h-5 "></i>
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="vllm_url" class="text-sm font-bold" style="margin-right: 1rem;">Install vLLM service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallvLLMService">install vLLM service</button>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="startvLLMService">start vllm service</button>
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="vllm_url" class="text-sm font-bold" style="margin-right: 1rem;">vllm base url:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="vllm_url"
                                    required
                                    v-model="configFile.vllm_url"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr>
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="vllm_gpu_memory_utilization" class="text-sm font-bold" style="margin-right: 1rem;">gpu memory utilization:</label>
                                </td>
                                <td>
                                    <div class="flex flex-col align-bottom ">
                                    <div class="relative">
                                        <p class="absolute left-0 mt-6">
                                            <label for="vllm_gpu_memory_utilization" class=" text-sm font-medium">
                                                vllm gpu memory utilization:
                                            </label>
                                        </p>
                                        <p class="absolute right-0">

                                            <input type="text" id="temp-val" v-model="configFile.vllm_gpu_memory_utilization"
                                                @change="settingsChanged=true"
                                                class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                        </p>

                                    </div>

                                    <input id="vllm_gpu_memory_utilization"
                                        @change="settingsChanged=true"
                                        type="range" v-model="configFile.vllm_gpu_memory_utilization" min="0.10" max="1" step="0.01"
                                        class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                </div> 
                                </td>
                                </tr>
                                
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="vllm_max_num_seqs" class="text-sm font-bold" style="margin-right: 1rem;">vllm max num seqs:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="number"
                                    id="vllm_max_num_seqs"
                                    min=64
                                    max=2048
                                    required
                                    v-model="configFile.vllm_max_num_seqs"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr>                            
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="vllm_max_model_len" class="text-sm font-bold" style="margin-right: 1rem;">max model len:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="number"
                                    id="vllm_max_model_len"
                                    min=2048
                                    max=1000000
                                    required
                                    v-model="configFile.vllm_max_model_len"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr>                            
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="vllm_model_path" class="text-sm font-bold" style="margin-right: 1rem;">vllm model path:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="vllm_model_path"
                                    required
                                    v-model="configFile.vllm_model_path"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr>                            
                                
                            </table>                                
                        </Card>                    
                        <Card title="Petals service" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="enable_petals_service" class="text-sm font-bold" style="margin-right: 1rem;">Enable petals service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="enable_petals_service"
                                    required
                                    v-model="configFile.enable_petals_service"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                <td>
                                    <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary" @click="this.$store.state.messageBox.showMessage('Activates Petals service. The service will be automatically loaded at startup alowing you to use the petals endpoint to generate text in a distributed network.\nIf You are using windows, this will install wsl so you need to activate it.\n<a href=\'https://techcommunity.microsoft.com/t5/windows-11/how-to-install-the-linux-windows-subsystem-in-windows-11/m-p/2701207\' target=\'_blank\'>Here is how you can do that</a>')">
                                        <i data-feather="help-circle" class="w-5 h-5 "></i>
                                    </div>
                                </td>                            

                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="petals_base_url" class="text-sm font-bold" style="margin-right: 1rem;">Install Petals service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallPetalsService">install petals service</button>
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="petals_base_url" class="text-sm font-bold" style="margin-right: 1rem;">petals base url:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="petals_base_url"
                                    required
                                    v-model="configFile.petals_base_url"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
                            </table>                                
                        </Card>                        
                    </Card>
                    <Card title="TTV settings" :is_subcard="true" class="pb-2  m-2">
                        <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 max-w-2xl mx-auto">
                            <div class="flex flex-col md:flex-row items-start md:items-center space-y-4 md:space-y-0 md:space-x-6">
                                <div class="w-full md:w-1/3">
                                    <label 
                                        for="lumalabs_key" 
                                        class="block text-sm font-semibold text-gray-700 dark:text-gray-200"
                                    >
                                        Lumalabs Key
                                    </label>
                                </div>
                                <div class="w-full md:w-2/3">
                                    <div class="relative">
                                        <input
                                            type="text"
                                            id="lumalabs_key"
                                            required
                                            v-model="configFile.lumalabs_key"
                                            @change="settingsChanged=true"
                                            class="w-full px-4 py-2.5 rounded-lg border border-gray-300 dark:border-gray-600 
                                                bg-gray-50 dark:bg-gray-700 
                                                text-gray-900 dark:text-white 
                                                focus:ring-2 focus:ring-blue-500 focus:border-transparent
                                                transition duration-150 ease-in-out"
                                            placeholder="Enter your Lumalabs API key"
                                        >
                                        <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                                            <svg class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor">
                                                <path d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" />
                                            </svg>
                                        </div>
                                    </div>
                                    <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                                        Your API key will be securely stored
                                    </p>
                                </div>
                            </div>
                        </div>
                        
                    </Card>
                    <Card title="Misc" :is_shrunk="true" :is_subcard="true" class="pb-2  m-2">
                        <Card title="Elastic search Service (under construction)" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="elastic_search_service" class="text-sm font-bold" style="margin-right: 1rem;">Enable elastic search service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="elastic_search_service"
                                    required
                                    v-model="configFile.elastic_search_service"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="install_elastic_search_service" class="text-sm font-bold" style="margin-right: 1rem;">Reinstall Elastic Search service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallElasticSearchService">install ElasticSearch service</button>
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="elastic_search_url" class="text-sm font-bold" style="margin-right: 1rem;">elastic search base url:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="elastic_search_url"
                                    required
                                    v-model="configFile.elastic_search_url"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
            
                            </table>

                        </Card>                    

                    </Card>


                </div>
            </div>


            <!-- BINDING ZOO -->
            <div
                class="flex flex-col mb-2  rounded-lg panels-color hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="bzc_collapsed = !bzc_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <div v-show="bzc_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!bzc_collapsed" ><i data-feather='chevron-down'></i></div>

                        <p class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Binding zoo</p>
                        <div v-if="!configFile.binding_name" class="text-base text-red-600 flex gap-3 items-center mr-2">
                            <i data-feather="alert-triangle" class="flex-shrink-0"></i>
                            No binding selected!
                        </div>

                        <div v-if="configFile.binding_name" class="mr-2">|</div>

                        <div v-if="configFile.binding_name"
                            class=" text-base font-semibold cursor-pointer select-none items-center">

                            <div class="flex gap-1 items-center">
                                <img :src="imgBinding" class="w-8 h-8 rounded-full object-fill text-blue-700">
                                <p class="font-bold font-large text-lg line-clamp-1">
                                    <!-- {{ configFile.binding_name }} -->
                                    {{ binding_name }}
                                </p>
                            </div>
                        </div>
                    </button>
                </div>
                <div :class="{ 'hidden': bzc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">

                    <div v-if="bindingsZoo&&bindingsZoo.length > 0" class="mb-2">
                        <label for="binding" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Bindings: ({{ bindingsZoo.length }})
                        </label>
                        <div class="overflow-y-auto no-scrollbar p-2 pb-0 grid lg:grid-cols-3 md:grid-cols-2 gap-4"
                            :class="bzl_collapsed ? '' : 'max-h-96'">
                            <TransitionGroup name="list">
                                <BindingEntry ref="bindingZoo" v-for="(binding, index) in bindingsZoo"
                                    :key="'index-' + index + '-' + binding.folder" :binding="binding"
                                    :on-selected="onBindingSelected" :on-reinstall="onReinstallBinding"
                                    :on-unInstall="onUnInstallBinding"
                                    :on-install="onInstallBinding" :on-settings="onSettingsBinding"
                                    :on-reload-binding="onReloadBinding"
                                    :selected="binding.folder === configFile.binding_name">
                                </BindingEntry>
                            </TransitionGroup>
                        </div>
                    </div>


                    <!-- EXPAND / COLLAPSE BUTTON -->
                    <button v-if="bzl_collapsed"
                        class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                        title="Collapse" type="button" @click="bzl_collapsed = !bzl_collapsed">
                        <i data-feather="chevron-up"></i>
                    </button>
                    <button v-else
                        class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                        title="Expand" type="button" @click="bzl_collapsed = !bzl_collapsed">
                        <i data-feather="chevron-down"></i>
                    </button>
                </div>

            </div>

            <!-- MODELS ZOO -->
            <div
                class="flex flex-col mb-2  rounded-lg panels-color hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="modelsZooToggleCollapse()"
                        class="text-2xl hover:text-primary  p-2 -m-2 w-full text-left flex items-center">
                        <div v-show="mzc_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!mzc_collapsed" ><i data-feather='chevron-down'></i></div>

                        <p class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Models zoo</p>
                        <!-- SPINNER -->
                        <div class="flex flex-row items-center">
                            <div v-if="!configFile.binding_name"
                                class="text-base text-red-600 flex gap-3 items-center mr-2">
                                <i data-feather="alert-triangle" class="flex-shrink-0"></i>
                                Select binding first!
                            </div>

                            <div v-if="!configFile.model_name && configFile.binding_name"
                                class="text-base text-red-600 flex gap-3 items-center mr-2">
                                <i data-feather="alert-triangle" class="flex-shrink-0"></i>
                                No model selected!
                            </div>

                            <div v-if="configFile.model_name" class="mr-2">|</div>

                            <div v-if="configFile.model_name"
                                class="text-base font-semibold cursor-pointer select-none items-center">
                                <div class="flex gap-1 items-center">
                                    <img :src="imgModel" class="w-8 h-8 rounded-lg object-fill">
                                    <p class="font-bold font-large text-lg line-clamp-1">
                                        {{ configFile.model_name }}
                                    </p>
                                </div>
                            </div>

                        </div>
                    </button>
                </div>


                <div :class="{ 'hidden': mzc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <!-- SEARCH BAR -->
                    <div class="mx-2 mb-4">


                            <div class="relative">
                                <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                                    <div v-if="searchModelInProgress">
                                        <!-- SPINNER -->
                                        <div role="status">
                                            <svg aria-hidden="true"
                                                class="inline w-4 h-4 mr-2 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600"
                                                viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                <path
                                                    d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                                                    fill="currentColor" />
                                                <path
                                                    d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                                                    fill="currentFill" />
                                            </svg>
                                            <span class="sr-only">Loading...</span>
                                        </div>
                                    </div>
                                    <div v-if="!searchModelInProgress">
                                        <!-- SEARCH -->
                                        <svg aria-hidden="true" class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none"
                                            stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                                        </svg>
                                    </div>

                                </div>
                                <input type="search"
                                    class="block w-full p-4 pl-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                    placeholder="Search models..." required 
                                    v-model="searchModel"
                                    @keyup.enter="searchModel_func">
                                <button v-if="searchModel" @click.stop="searchModel = ''" type="button"
                                    class="text-white absolute right-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                                    Clear search</button>

                                <!-- @input="filterPersonalities()" -->

                            </div>

                    </div>
                    <div>
                        <input v-model="show_only_installed_models" class="m-2 p-2" type="checkbox" ref="only_installed">
                        <label for="only_installed">Show only installed models</label>
                    </div>
                    <div>
                        <!-- Pass the radio options as a prop -->
                        <RadioOptions :radioOptions="sortOptions" @radio-selected="handleRadioSelected" />
                    </div>
                    <a href="https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard" target="_blank" class="mb-4 font-bold underline text-blue-500 pb-4">Hugging face Leaderboard</a>
                    <!-- SPINNER -->
                    <div v-if="is_loading_zoo" role="status" class="text-center w-full display: flex;align-items: center;">
                            <svg aria-hidden="true" class="text-center w-full display: flex;align-items: center; h-20   animate-spin  fill-secondary" viewBox="0 0 100 101"
                                fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                                    fill="currentColor" />
                                <path
                                    d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                                    fill="currentFill" />
                            </svg>
                            <p class="heartbeat-text">Loading models Zoo</p>
                    </div>                    
                        <div v-if="models_zoo && models_zoo.length > 0" class="mb-2">
                            <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                Models: ({{ models_zoo.length }})
                            </label>

                            <div class="overflow-y-auto p-2 pb-0 grid lg:grid-cols-3 md:grid-cols-2 gap-4 overflow-y-scroll w-full dark:bg-bg-dark scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary"
                                :class="mzl_collapsed ? '' : 'max-h-96'">
                                <TransitionGroup name="list">
                                    <model-entry  ref="modelZoo" v-for="(model, index) in rendered_models_zoo"
                                        :key="'index-' + index + '-' + model.name" 
                                        :model="model"
                                        :is-installed="model.isInstalled" :on-install="onInstall"
                                        :on-uninstall="onUninstall" :on-selected="onModelSelected"
                                        :selected="model.name === configFile.model_name"
                                        :model_type="model.model_type" :on-copy="onCopy" :on-copy-link="onCopyLink"
                                        :on-cancel-install="onCancelInstall" />
                                    <button ref="load_more_models" class="relative items-start p-4 hover:bg-primary-light rounded-lg mb-2 shadow-lg border-2 select-none" @click="load_more_models">Load more models</button>
                                </TransitionGroup>
                            </div>
                        </div>                    
                    <!-- EXPAND / COLLAPSE BUTTON -->
                    <button v-if="mzl_collapsed"
                        class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                        title="Collapse" type="button" @click="open_mzl">
                        <i data-feather="chevron-up"></i>
                    </button>
                    <button v-else
                        class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                        title="Expand" type="button" @click="open_mzl">
                        <i data-feather="chevron-down"></i>
                    </button>
                    <div class="mb-2">
                    <div class="p-2  ">
                        <div>
                            <div class="mb-3">
                                <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Create a reference from local file path:</label>
                                <input type="text" v-model="reference_path"
                                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                    placeholder="Enter Path ..." required>
                            </div>

                            <button type="button" @click.stop="onCreateReference()"
                                class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Add reference</button>
                        </div>

                        <div v-if="!modelDownlaodInProgress">
                            <div class="mb-3">
                                <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">Download
                                    from web:</label>
                                <input type="text" v-model="addModel.url"
                                    class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                    placeholder="Enter URL ..." required>
                            </div>

                            <button type="button" @click.stop="onInstallAddModel()"
                                class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Download</button>
                        </div>
                        <div v-if="modelDownlaodInProgress"
                            class="relative flex flex-col items-center justify-center flex-grow h-full">
                            <div role="status" class=" justify-center ">
                                <!-- SPINNER -->

                            </div>
                            <div class="relative flex flex-row flex-grow items-center w-full h-full bottom-0">
                                <!-- PROGRESS BAR -->
                                <div class="w-full p-2">


                                    <div class="flex justify-between mb-1">
                                        <span
                                            class="flex flex-row items-center gap-2 text-base font-medium text-blue-700 dark:text-white">
                                            Downloading
                                            <svg aria-hidden="true"
                                                class="w-4 h-4 mr-2 text-gray-200 animate-spin dark:text-gray-600 fill-secondary"
                                                viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                <path
                                                    d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                                                    fill="currentColor" />
                                                <path
                                                    d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                                                    fill="currentFill" />
                                            </svg>
                                            <span class="sr-only">Loading...</span>
                                        </span>

                                        <span class="text-sm font-medium text-blue-700 dark:text-white">{{
                                            Math.floor(addModel.progress) }}%</span>
                                    </div>
                                    <div class="mx-1 opacity-80 line-clamp-1" :title="addModel.url">
                                        {{ addModel.url }}

                                    </div>
                                    <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                                        <div class="bg-blue-600 h-2.5 rounded-full"
                                            :style="{ width: addModel.progress + '%' }">
                                        </div>
                                    </div>
                                    <div class="flex justify-between mb-1">
                                        <span class="text-base font-medium text-blue-700 dark:text-white">Download
                                            speed: {{ speed_computed }}/s</span>
                                        <span class="text-sm font-medium text-blue-700 dark:text-white">{{
                                            downloaded_size_computed }}/{{ total_size_computed }}</span>
                                    </div>
                                </div>
                            </div>
                            <div class="flex flex-grow">
                                <!-- CANCEL BUTTON -->

                                <div class="flex  flex-row flex-grow gap-3">
                                    <div class="p-2 text-center grow">
                                        <!-- <button @click.stop="hide(true)" type="button"
                            class="mr-2 text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm  sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                            {{ ConfirmButtonText }}
                        </button> -->
                                        <button @click.stop="onCancelInstall" type="button" title="Cancel download"
                                            class="text-gray-500 bg-white hover:bg-gray-100 focus:ring-4 focus:outline-none focus:ring-gray-200 rounded-lg border border-gray-200 text-sm font-medium px-5 py-2.5 hover:text-gray-900 focus:z-10 dark:bg-gray-700 dark:text-gray-300 dark:border-gray-500 dark:hover:text-white dark:hover:bg-gray-600 dark:focus:ring-gray-600">
                                            Cancel
                                        </button>
                                    </div>

                                </div>
                            </div>
                        </div>

                    </div>
                </div>

                </div>
            </div>
            <!-- ADD MODELS -->
            <!-- PERSONALITY ZOO -->
            <div
                class="flex flex-col mb-2  rounded-lg panels-color hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3 items-center">
                    <button @click.stop="pzc_collapsed = !pzc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 text-left w-full  flex items-center">
                        <div v-show="pzc_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!pzc_collapsed" ><i data-feather='chevron-down'></i></div>
                        <p class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Personalities zoo</p>


                        <div v-if="configFile.personalities" class="mr-2">|</div>
                        <!-- LIST OF MOUNTED PERSONALITIES -->
                        <div class="mr-2 font-bold font-large text-lg line-clamp-1">
                            {{ active_pesonality }}
                        </div>
                        <div v-if="configFile.personalities" class="mr-2">|</div>
                        <div v-if="configFile.personalities"
                            class=" text-base font-semibold cursor-pointer select-none items-center flex flex-row">
                            <!-- LIST -->
                            <div class="flex -space-x-4 items-center " v-if="mountedPersArr.length > 0">
                                <!-- ITEM -->
                                <div class="relative  hover:-translate-y-2 duration-300 hover:z-10 shrink-0 "
                                    v-for="(item, index) in mountedPersArr" :key="index + '-' + item.name"
                                    ref="mountedPersonalities">
                                    <div class="group items-center flex flex-row">
                                        <button @click.stop="onPersonalitySelected(item)">
                                            <img :src="bUrl + item.avatar" @error="personalityImgPlacehodler"
                                                class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 group-hover:border-secondary "
                                                :class="configFile.active_personality_id == configFile.personalities.indexOf(item.full_path) ? 'border-secondary' : 'border-transparent z-0'"
                                                :title="item.name">
                                        </button>
                                        <button @click.stop="unmountPersonality (item)">
                                            <span
                                                class="hidden group-hover:block -top-2 -right-1 absolute active:scale-90 bg-bg-light dark:bg-bg-dark rounded-full border-2  border-transparent"
                                                title="Unmount personality">
                                                <!-- UNMOUNT BUTTON -->
                                                <svg aria-hidden="true" class="w-4 h-4 text-red-600 hover:text-red-500 "
                                                    fill="currentColor" viewBox="0 0 20 20"
                                                    xmlns="http://www.w3.org/2000/svg">
                                                    <path fill-rule="evenodd"
                                                        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                                        clip-rule="evenodd"></path>
                                                </svg>
                                            </span>
                                        </button>
                                    </div>
                                </div>
                            </div>

                        </div>
                        <button 
                                @click.stop="unmountAll()" 
                                class="bg-bg-light hover:border-green-200 ml-5 dark:bg-bg-dark rounded-full border-2 border-transparent"
                                title="Unmount All"
                                >
                                <!-- UNMOUNT BUTTON -->
                                <svg aria-hidden="true" class="w-4 h-4 text-red-600 hover:text-red-500 "
                                    fill="currentColor" viewBox="0 0 20 20"
                                    xmlns="http://www.w3.org/2000/svg">
                                    <path fill-rule="evenodd"
                                        d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                                        clip-rule="evenodd"></path>
                                </svg>
                        </button>
                    </button>
                </div>
                <div :class="{ 'hidden': pzc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <!-- SEARCH BAR -->
                    <div class="mx-2 mb-4">
                            <label for="personality-search"
                                class="mb-2 text-sm font-medium text-gray-900 sr-only dark:text-white">Search</label>
                            <div class="relative">
                                <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                                    <div v-if="searchPersonalityInProgress">
                                        <!-- SPINNER -->
                                        <div role="status">
                                            <svg aria-hidden="true"
                                                class="inline w-4 h-4 mr-2 text-gray-200 animate-spin dark:text-gray-600 fill-blue-600"
                                                viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                                                <path
                                                    d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z"
                                                    fill="currentColor" />
                                                <path
                                                    d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z"
                                                    fill="currentFill" />
                                            </svg>
                                            <span class="sr-only">Loading...</span>
                                        </div>
                                    </div>
                                    <div v-if="!searchPersonalityInProgress">
                                        <!-- SEARCH -->
                                        <svg aria-hidden="true" class="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none"
                                            stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                                                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
                                        </svg>
                                    </div>

                                </div>
                                <input type="search" id="personality-search"
                                    class="block w-full p-4 pl-10 text-sm text-gray-900 border border-gray-300 rounded-lg bg-gray-50 focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500"
                                    placeholder="Search personality..." required v-model="searchPersonality"
                                    @keyup.stop="searchPersonality_func">
                                <button v-if="searchPersonality" @click.stop="searchPersonality = ''" type="button"
                                    class="text-white absolute right-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                                    Clear search</button>

                                <!-- @input="filterPersonalities()" -->

                            </div>

                    </div>
                    <div class="mx-2 mb-4" v-if="!searchPersonality">
                        <label for="persCat" class="block  mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Personalities Category: ({{ persCatgArr.length }})
                        </label>
                        <select id="persCat" @change="update_personality_category($event.target.value, refresh)"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                            <option v-for="(item, index) in persCatgArr" :key="index"
                                :selected="item == this.configFile.personality_category">{{
                                    item
                                }}

                            </option>

                        </select>
                    </div>
                    <div>
                        <div v-if="personalitiesFiltered.length > 0" class="mb-2">
                            <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                {{ searchPersonality ? 'Search results' : 'Personalities' }}: ({{
                                    personalitiesFiltered.length
                                }})
                            </label>
                            <div class="overflow-y-auto no-scrollbar p-2 pb-0 grid lg:grid-cols-3 md:grid-cols-2 gap-4"
                                :class="pzl_collapsed ? '' : 'max-h-96'">
                                <TransitionGroup name="bounce">
                                    <personality-entry ref="personalitiesZoo" v-for="(pers, index) in personalitiesFiltered"
                                        :key="'index-' + index + '-' + pers.name" :personality="pers"
                                        :select_language="true"
                                        :full_path="pers.full_path"
                                        :selected="configFile.active_personality_id == configFile.personalities.findIndex(item => item === pers.full_path || item === pers.full_path+':'+pers.language)"
                                        :on-selected="onPersonalitySelected" 
                                        :on-mount="mountPersonality" 
                                        :on-un-mount="unmountPersonality"  
                                        :on-remount="remountPersonality"
                                        :on-edit="editPersonality"
                                        :on-copy-to-custom="copyToCustom"
                                        :on-reinstall="onPersonalityReinstall"
                                        :on-settings="onSettingsPersonality"
                                        :on-copy-personality-name="onCopyPersonalityName"
                                        :on-copy-to_custom="onCopyToCustom"
                                        :on-open-folder="handleOpenFolder"
                                        />
                                </TransitionGroup>
                            </div>
                        </div>
                    </div>

                    <!-- EXPAND / COLLAPSE BUTTON -->
                    <button v-if="pzl_collapsed"
                        class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                        title="Collapse" type="button" @click="pzl_collapsed = !pzl_collapsed">
                        <i data-feather="chevron-up"></i>
                    </button>
                    <button v-else
                        class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                        title="Expand" type="button" @click="pzl_collapsed = !pzl_collapsed">
                        <i data-feather="chevron-down"></i>
                    </button>
                </div>

            </div>

            <!-- MODEL CONFIGURATION -->
            <div
                class="flex flex-col mb-2 p-3 rounded-lg panels-color hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row">
                    <button @click.stop="mc_collapsed = !mc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 w-full text-left flex items-center">
                        <div v-show="mc_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!mc_collapsed" ><i data-feather='chevron-down'></i></div>
                        <p class="text-lg font-semibold cursor-pointer select-none">
                            Model Configuration</p>
                    </button>
                </div>
                <div :class="{ 'hidden': mc_collapsed }" class="flex flex-col mb-2 p-2">
                    <div class="m-2">

                        <div class="flex flex-row gap-2 items-center">

                            <input id="override-model-parameters" type="checkbox"
                                class="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500 dark:focus:ring-blue-600 dark:ring-offset-gray-700 dark:focus:ring-offset-gray-700 focus:ring-2 dark:bg-gray-600 dark:border-gray-500"
                                @click.stop v-model="configFile.override_personality_model_parameters"
                                @change="update_setting('override_personality_model_parameters', configFile.override_personality_model_parameters)">
                            <label for="override-model-parameters" class="block text-sm font-medium ">
                                Override personality model parameters
                            </label>

                        </div>

                    </div>
                    <!-- DISABLE PARAMETER SELECTION -->
                    <div :class="!configFile.override_personality_model_parameters ? 'pointer-events-none opacity-30' : ''">


                        <div class="m-2">
                            <label for="seed" class="block mb-2 text-sm font-medium ">
                                Seed:
                            </label>
                            <input type="text" id="seed" v-model="configFile.seed"
                                class="bg-gray-50 border border-gray-300 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                        </div>
                        <div class="m-2">
                            <div class="flex flex-col align-bottom ">
                                <div class="relative">
                                    <p class="absolute left-0 mt-6">
                                        <label for="temperature" class=" text-sm font-medium">
                                            Temperature:
                                        </label>
                                    </p>
                                    <p class="absolute right-0">

                                        <input type="text" id="temp-val" v-model="configFile.temperature"
                                            @change="settingsChanged=true"
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="temperature"
                                    @change="settingsChanged=true"
                                    type="range" v-model="configFile.temperature" min="0" max="5" step="0.1"
                                    class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </div>
                        </div>
                        <div class="m-2">
                            <div class="flex flex-col align-bottom ">
                                <div class="relative">
                                    <p class="absolute left-0 mt-6">
                                        <label for="predict" class=" text-sm font-medium">
                                            N Predict:
                                        </label>
                                    </p>
                                    <p class="absolute right-0">

                                        <input type="text" id="predict-val" v-model="configFile.n_predict"
                                            @change="settingsChanged=true"
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="predict" 
                                    type="range"
                                    @change="settingsChanged=true"
                                    v-model="configFile.n_predict" min="0" max="2048" step="32"
                                    class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </div>
                        </div>
                        <div class="m-2">
                            <div class="flex flex-col align-bottom ">
                                <div class="relative">
                                    <p class="absolute left-0 mt-6">
                                        <label for="top_k" class=" text-sm font-medium">
                                            Top-K:
                                        </label>
                                    </p>
                                    <p class="absolute right-0">

                                        <input type="text" id="top_k-val" v-model="configFile.top_k"
                                            @change="settingsChanged=true"
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="top_k"
                                    type="range"
                                    @change="settingsChanged=true"
                                    v-model="configFile.top_k" min="0" max="100" step="1"
                                    class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </div>
                        </div>
                        <div class="m-2">
                            <div class="flex flex-col align-bottom ">
                                <div class="relative">
                                    <p class="absolute left-0 mt-6">
                                        <label for="top_p" class=" text-sm font-medium">
                                            Top-P:
                                        </label>
                                    </p>
                                    <p class="absolute right-0">

                                        <input type="text" id="top_p-val" v-model="configFile.top_p"
                                            @change="settingsChanged=true"
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="top_p" 
                                    type="range"
                                    v-model="configFile.top_p" min="0" max="1" step="0.01"
                                    @change="settingsChanged=true"
                                    class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </div>
                        </div>
                        <div class="m-2">
                            <div class="flex flex-col align-bottom ">
                                <div class="relative">
                                    <p class="absolute left-0 mt-6">
                                        <label for="repeat_penalty" class=" text-sm font-medium">
                                            Repeat penalty:
                                        </label>
                                    </p>
                                    <p class="absolute right-0">

                                        <input type="text" id="repeat_penalty-val" v-model="configFile.repeat_penalty"
                                            @change="settingsChanged=true"                                        
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="repeat_penalty"
                                    @change="settingsChanged=true"                                
                                    type="range" v-model="configFile.repeat_penalty" min="0" max="2" step="0.01"
                                    class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </div>
                        </div>
                        <div class="m-2">
                            <div class="flex flex-col align-bottom ">
                                <div class="relative">
                                    <p class="absolute left-0 mt-6">
                                        <label for="repeat_last_n" class=" text-sm font-medium">
                                            Repeat last N:
                                        </label>
                                    </p>
                                    <p class="absolute right-0">

                                        <input type="text" id="repeat_last_n-val" v-model="configFile.repeat_last_n"
                                            @change="settingsChanged=true"                                        
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="repeat_last_n"
                                    type="range" v-model="configFile.repeat_last_n" min="0" max="100" step="1"
                                    @change="settingsChanged=true"                                    
                                    class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </div>
                        </div>
                    </div>

                </div>
            </div>
        </div>
    </div>
    <AddModelDialog ref="addmodeldialog" />
    <ChoiceDialog  class="z-20"
      :show="variantSelectionDialogVisible"
      :choices="variant_choices"
      @choice-selected="onVariantChoiceSelected"
      @close-dialog="oncloseVariantChoiceDialog"
      @choice-validated="onvalidateVariantChoice"
    />
</template>
<style scoped>
.input-field {
    @apply w-full px-3 py-2 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:text-white transition-colors duration-200;
}
.heartbeat-text {
  font-size: 24px;
  animation: pulsate 1.5s infinite;
  /* You can adjust the animation duration and other properties as needed */
}

@keyframes pulsate {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.1);
    opacity: 0.7;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

/* THESE ARE FOR TransitionGroup components */
.list-move,
/* apply transition to moving elements */
.list-enter-active,
.list-leave-active {
    transition: all 0.5s ease;
}

.list-enter-from {
    transform: translatey(-30px);
}

.list-leave-to {
    opacity: 0;
    transform: translatey(30px);
}

/* ensure leaving items are taken out of layout flow so that moving
   animations can be calculated correctly. */
.list-leave-active {
    position: absolute;
}

.bounce-enter-active {
    animation: bounce-in 0.5s;
}

.bounce-leave-active {
    animation: bounce-in 0.5s reverse;
}

@keyframes bounce-in {
    0% {
        transform: scale(0);
    }

    50% {
        transform: scale(1.25);
    }

    100% {
        transform: scale(1);
    }
}

.bg-primary-light {
    background-color: aqua
}

.hover:bg-primary-light:hover {
    background-color: aquamarine
}

.font-bold {
    font-weight: bold;
}
</style>

<script>
import filesize from '../plugins/filesize'
import axios from "axios";
import feather from 'feather-icons'
import { nextTick } from 'vue'
import ModelEntry from '@/components/ModelEntry.vue';
import PersonalityViewer from '@/components/PersonalityViewer.vue';
import PersonalityEntry from "@/components/PersonalityEntry.vue";
import BindingEntry from "../components/BindingEntry.vue";
import socket from '@/services/websocket.js'
import defaultModelImgPlaceholder from "../assets/default_model.png"

import defaultPersonalityImgPlaceholder from "../assets/logo.png"
import defaultImgPlaceholder from "../assets/default_model.png"

import AddModelDialog from "@/components/AddModelDialog.vue";

import ChoiceDialog from "@/components/ChoiceDialog.vue";
import Card from "@/components/Card.vue"
import RadioOptions from '../components/RadioOptions.vue';

import storeLogo from '@/assets/logo.png'


import SVGGPU from '@/assets/gpu.svg';

import StringListManager from '@/components/StringListManager.vue';
import DictManager from '@/components/DictManager.vue';

const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
axios.defaults.baseURL = import.meta.env.VITE_LOLLMS_API_BASEURL
export default {
    components: {
        AddModelDialog,
        ModelEntry,
        // eslint-disable-next-line vue/no-unused-components
        PersonalityViewer,
        PersonalityEntry,
        BindingEntry,
        ChoiceDialog,
        Card,
        StringListManager,
        DictManager,
        RadioOptions,
    },
    data() {

        return {
            posts_headers : {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            isUploading: false,
            defaultModelImgPlaceholder:defaultModelImgPlaceholder,
            snd_input_devices: [],
            snd_input_devices_indexes: [],
            snd_output_devices: [],
            snd_output_devices_indexes: [],
            voices: [],
            voice_languages:{
                            "Arabic": "ar",
                            "Brazilian Portuguese": "pt",
                            "Chinese": "zh-cn",
                            "Czech": "cs",
                            "Dutch": "nl",
                            "English": "en",
                            "French": "fr",
                            "German": "de",
                            "Italian": "it",
                            "Polish": "pl",
                            "Russian": "ru",
                            "Spanish": "es",
                            "Turkish": "tr",
                            "Japanese": "ja",
                            "Korean": "ko",
                            "Hungarian": "hu",
                            "Hindi": "hi"
                        },
            
            storeLogo:storeLogo,
            binding_changed:false,
            SVGGPU:SVGGPU,
            models_zoo:[],
            models_zoo_initialLoadCount: 10, // Number of entries to load initially
            models_zoo_loadMoreCount: 5, // Number of entries to load each time
            models_zoo_loadedEntries: [], // Array to store the loaded entries
            models_zoo_scrollThreshold: 200, // Distance from the bottom of the page to trigger lazy loading
            // Sort options
            sortOptions: [
                { label: 'Sort by Date', value: 0 },
                { label: 'Sort by Rank', value: 1 },
                { label: 'Sort by Name', value: 2 },
                { label: 'Sort by Maker', value: 3 },
                { label: 'Sort by Quantizer', value: 4 },
            ],
            // Comfyui models
            comfyui_models:[],
            show_only_installed_models:false,
            // Local model reference path
            reference_path:"",
            audioVoices:[],      
            // update
            has_updates:false,
            // Variant selection
            variant_choices:[],
            variantSelectionDialogVisible:false,
            currenModelToInstall:null,
            // Loading text
            loading_text:"",
            // Current personality category
            personality_category:null,
            // install custom model
            addModelDialogVisibility: false,
            modelPath: '',
            // Zoo stuff
            personalitiesFiltered: [],
            modelsFiltered: [],
            // Accordeon stuff 
            collapsedArr: [],
            all_collapsed: true,
            data_conf_collapsed: true,
            internet_conf_collapsed: true,// internet 
            servers_conf_collapsed: true, // Servers configuration
            mainconf_collapsed: true, // Main configuration 
            smartrouterconf_collapsed: true, // Smart router configuration
            bec_collapsed: true,
            sort_type : 0, // 0: by date, 1: by rank, 2: by name, 3: by maker, 4: by quantizer
            is_loading_zoo:false, // Is loading models zoo
            mzc_collapsed: true, // models zoo
            mzdc_collapsed: true, // models zoo download
            pzc_collapsed: true, // personalities zoo
            bzc_collapsed: true, // binding zoo
            pc_collapsed: true,
            mc_collapsed: true,
            sc_collapsed: true, // system status
            // Zoo accordeoon
            mzl_collapsed: false,
            pzl_collapsed: false,
            ezl_collapsed: false,
            bzl_collapsed: false,
            // Settings stuff
            extCatgArr: [],
            persCatgArr: [],
            persArr: [],
            showConfirmation: false,
            showToast: false,
            isLoading: false,
            settingsChanged: false,
            isModelSelected: false,
            isMounted: false, // Needed to wait for $refs to be rendered
            bUrl: bUrl, // for personality images
            searchPersonality: "",
            searchModel: "",
            searchPersonalityTimer: {},
            searchPersonalityTimerInterval: 1500, // timeout in ms
            searchModelTimerInterval: 1500, // timeout in ms
            searchPersonalityInProgress: false,
            searchModelInProgress: false,
            addModel: {},
            modelDownlaodInProgress: false,
            uploadData: [],

        }
    },
    async created() {
        try{
        this.$store.state.loading_infos = "Getting Hardware usage"
        await this.refreshHardwareUsage(this.$store);
        }
        catch (ex){
        console.log("Error cought:", ex)
        }

        socket.on('loading_text',this.on_loading_text);
        this.updateHasUpdates();
        //await socket.on('install_progress', this.progressListener);
    }, 
        methods: {
            triggerFileInput() {
                this.$refs.fileInput.click()
            },
            async handleFileUpload(event) {
                const files = event.target.files
                if (!files.length) return

                this.isUploading = true
                const formData = new FormData()
                
                // Add database name
                formData.append('database_name', this.databaseName)
                
                // Add all files
                Array.from(files).forEach(file => {
                    formData.append('files', file)
                })

                try {
                    const response = await axios.post('/upload_files_2_rag_db', formData, {
                    headers: {
                        'Content-Type': 'multipart/form-data'
                    },
                    onUploadProgress: (progressEvent) => {
                        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
                        this.$emit('upload-progress', percentCompleted)
                    }
                    })
                    
                    this.$emit('upload-success', response.data)
                } catch (error) {
                    console.error('Upload failed:', error)
                    this.$emit('upload-error', error)
                } finally {
                    this.isUploading = false
                    event.target.value = ''
                }
            },    
            updateRagDatabase(index, value, field) {
                if (field) {
                    // For mounted, keep it as boolean, for others just set the value
                    if (field === 'mounted') {
                        this.configFile.datalakes[index][field] = Boolean(value);
                    } else {
                        this.configFile.datalakes[index][field] = value;
                    }
                    
                    this.settingsChanged = true;
                }
            },
            getServedDatabaseAlias(index) {
                return this.configFile.rag_local_services[index].alias;
            },
            getServedDatabaseType(index) {
                return this.configFile.rag_local_services[index].type;
            },
            getServedDatabaseUrl(index) {
                return this.configFile.rag_local_services[index].url;
            },
            getServedDatabaseStatus(index) {
                return this.configFile.rag_local_services[index].start_at_startup || false;
            },
            getServedDatabaseKey(index) {
                return this.configFile.rag_local_services[index].key || "";
            },
            getDataLakeAlias(index) {
                return this.configFile.datalakes[index].alias;
            },
            getDataLakeType(index) {
                return this.configFile.datalakes[index].type;
            },
            getDataLakeUrl(index) {
                return this.configFile.datalakes[index].url;
            },
            getDataLakePath(index) {
                return this.configFile.datalakes[index].path;
            },
            getDataLakeKey(index) {
                return this.configFile.datalakes[index].key || "";
            },
            getDataLakeStatus(index) {
                return this.configFile.datalakes[index].mounted || false;
            },

            updateAlias(index, value) {
                this.configFile.datalakes[index].alias = value;
                this.settingsChanged = true;
            },

            updateDatabaseType(index, value) {
                this.configFile.datalakes[index].type = value;
                this.settingsChanged = true;
            },

            updateDataLakeUrl(index, value) {
                this.configFile.datalakes[index].url = value;
                this.settingsChanged = true;
            },

            
            updateDataLakePath(index, value) {
                this.configFile.datalakes[index].path = value;
                this.settingsChanged = true;
            },

            updateDatabaseKey(index, value) {
                this.configFile.datalakes[index].key = value;
                this.settingsChanged = true;
            },

            updateMounted(index, value) {
                this.configFile.datalakes[index].mounted = value;
                this.settingsChanged = true;
            },
            updateStartAtStartup(index, value) {
                this.configFile.datalakes[index].start_at_startup = value;
                this.settingsChanged = true;
            },
            addDatabaseService(){
                if (!this.configFile.rag_local_services) {
                    this.configFile.rag_local_services = [];
                }
                
                // Add new entry as an object with default values
                this.configFile.rag_local_services.push({
                    alias: "datalake",
                    type: "lightrag",
                    url: "http://localhost:9621/",
                    path: "",
                    input_path: "",
                    working_path: "",
                    key: "",
                    start_at_startup: false
                });
                
                this.settingsChanged = true;

            },
            addDataLake() {
                if (!this.configFile.datalakes) {
                    this.configFile.datalakes = [];
                }
                
                // Add new entry as an object with default values
                this.configFile.datalakes.push({
                    alias: "datalake",
                    type: "lightrag",
                    url: "http://localhost:9621/",
                    path: "",
                    key: "",
                    mounted: false
                });
                
                this.settingsChanged = true;
            },
            removeDataLake(index) {
                console.log("Removing remote database")
                this.configFile.datalakes.splice(index, 1);
                console.log(this.configFile.datalakes)

                this.settingsChanged = true;
            },        
            
            removeServedDataBase(index) {
                console.log("Removing remote database")
                this.configFile.rag_local_services.splice(index, 1);
                console.log(this.configFile.rag_local_services)

                this.settingsChanged = true;
            },        
            fetchElevenLabsVoices() {
                fetch('https://api.elevenlabs.io/v1/voices')
                    .then(response => response.json())
                    .then(data => {
                        this.voices = data.voices;
                    })
                    .catch(error => console.error('Error fetching voices:', error));
            },         
            async refreshHardwareUsage(store) {
                await store.dispatch('refreshDiskUsage');
                await store.dispatch('refreshRamUsage');
                await store.dispatch('refreshVramUsage');
            },            
            addDataSource() {
                // Add new database entry with default values
                this.$store.state.config.datalakes.push({
                    alias: '',          // Empty name initially
                    is_local: true,     // this is a local database
                    path: '',          // Empty path initially
                    mounted: false,    // Not mounted by default
                    key: ''           // No key for local databases
                });
                
                this.settingsChanged = true;
            },

            removeDataSource(index) {
            this.$store.state.config.datalakes.splice(index, 1);
            this.settingsChanged = true;
            },
            async vectorize_folder(index){
                await axios.post('/vectorize_folder', {client_id:this.$store.state.client_id, rag_database:this.$store.state.config.datalakes[index]}, this.posts_headers)
            },
            async lightrag_select_input_folder(index) {
                try {
                    socket.on("lightrag_input_folder_added", (infos) => {
                        console.log("lightrag_input_folder_added")
                        console.log(infos)
                        if (infos) {
                            // Update with new dictionary structure
                            console.log(this.$store.state.config.rag_local_services)
                            console.log(index)
                            this.$store.state.config.rag_local_services[index]["input_path"] = infos["path"] 
                            this.settingsChanged = true;
                        } else {
                            this.$store.state.toast.showToast("Failed to select a folder", 4, false)
                        }
                    });

                    await axios.post('/select_lightrag_input_folder', 
                        { client_id: this.$store.state.client_id }, 
                        this.posts_headers
                    )
                } catch {
                    this.$store.state.toast.showToast("Failed to select a folder", 4, false)
                }
            },
            async lightrag_select_output_folder(index) {
                try {
                    socket.on("lightrag_output_folder_added", (infos) => {
                        console.log("lightrag_output_folder_added")
                        console.log(infos)
                        if (infos) {
                            // Update with new dictionary structure
                            console.log(this.$store.state.config.rag_local_services)
                            console.log(index)
                            this.$store.state.config.rag_local_services[index]["working_path"] = infos["path"] 
                            this.settingsChanged = true;
                        } else {
                            this.$store.state.toast.showToast("Failed to select a folder", 4, false)
                        }
                    });

                    await axios.post('/select_lightrag_output_folder', 
                        { client_id: this.$store.state.client_id }, 
                        this.posts_headers
                    )
                } catch {
                    this.$store.state.toast.showToast("Failed to select a folder", 4, false)
                }
            },
            
            async lollms_vectordb_select_folder(index) {
                try {
                    socket.on("lollmsvectordb_datalake_added", (infos) => {
                        console.log("lollmsvectordb_datalake_added")
                        console.log(infos)
                        if (infos) {
                            // Update with new dictionary structure
                            console.log(this.$store.state.config.datalakes)
                            console.log(index)
                            this.$store.state.config.datalakes[index] = {
                                alias: infos["datalake_name"],
                                type: "lollmsvectordb",
                                path: infos["path"],
                                mounted: false,
                                key: ''
                            };
                            this.settingsChanged = true;
                        } else {
                            this.$store.state.toast.showToast("Failed to select a folder", 4, false)
                        }
                    });

                    await axios.post('/select_lollmsvectordb_input_folder', 
                        { client_id: this.$store.state.client_id }, 
                        this.posts_headers
                    )
                } catch {
                    this.$store.state.toast.showToast("Failed to select a folder", 4, false)
                }
            },

        handleTemplateSelection(event) {
            console.log("handleTemplateSelection")
            const selectedOption = event.target.value;
            console.log("handleTemplateSelection: ",selectedOption)
            if (selectedOption === 'lollms') {
                console.log("Using lollms template")
                this.configFile.start_header_id_template = "!@>"
                this.configFile.system_message_template = "system"
                this.configFile.end_header_id_template = ": "
                this.configFile.separator_template = "\n"
                this.configFile.start_user_header_id_template = "!@>"
                this.configFile.end_user_header_id_template = ": "
                this.configFile.end_user_message_id_template = ""
                this.configFile.start_ai_header_id_template = "!@>"
                this.configFile.end_ai_header_id_template = ": "
                this.configFile.end_ai_message_id_template = ""
                this.settingsChanged=true
            } else if (selectedOption === 'lollms_simplified') {
                console.log("Using lollms template")
                this.configFile.start_header_id_template = "@>"
                this.configFile.system_message_template = "system"
                this.configFile.end_header_id_template = ": "
                this.configFile.separator_template = "\n"
                this.configFile.start_user_header_id_template = "@>"
                this.configFile.end_user_header_id_template = ": "
                this.configFile.end_user_message_id_template = ""
                this.configFile.start_ai_header_id_template = "@>"
                this.configFile.end_ai_header_id_template = ": "
                this.configFile.end_ai_message_id_template = ""
                this.settingsChanged=true
            } else if (selectedOption === 'bare') {
                console.log("Using lollms template")
                this.configFile.start_header_id_template = ""
                this.configFile.system_message_template = "system"
                this.configFile.end_header_id_template = ": "
                this.configFile.separator_template = "\n"
                this.configFile.start_user_header_id_template = ""
                this.configFile.end_user_header_id_template = ": "
                this.configFile.end_user_message_id_template = ""
                this.configFile.start_ai_header_id_template = ""
                this.configFile.end_ai_header_id_template = ": "
                this.configFile.end_ai_message_id_template = ""
                this.settingsChanged=true
            } else if (selectedOption === 'llama3') {
                console.log("Using llama3 template")
                this.configFile.start_header_id_template = "<|start_header_id|>"
                this.configFile.system_message_template = "system"
                this.configFile.end_header_id_template = "<|end_header_id|>"
                this.configFile.separator_template = "<|eot_id|>"
                this.configFile.start_user_header_id_template = "<|start_header_id|>"
                this.configFile.end_user_header_id_template = "<|end_header_id|>"
                this.configFile.end_user_message_id_template = ""
                this.configFile.start_ai_header_id_template = "<|start_header_id|>"
                this.configFile.end_ai_header_id_template = "<|end_header_id|>"
                this.configFile.end_ai_message_id_template = ""
                this.settingsChanged=true
            } else if (selectedOption === 'mistral') {
                console.log("Using mistral template")
                this.configFile.start_header_id_template = "[INST]"
                this.configFile.system_message_template = " Using this information"
                this.configFile.end_header_id_template = ": "
                this.configFile.separator_template = "\n"
                this.configFile.start_user_header_id_template = "[INST]"
                this.configFile.end_user_header_id_template = ": "
                this.configFile.end_user_message_id_template = "[/INST]"
                this.configFile.start_ai_header_id_template = "[INST]"
                this.configFile.end_ai_header_id_template = ": "
                this.configFile.end_ai_message_id_template = "[/INST]"
                this.settingsChanged=true
            } else if (selectedOption === 'deepseek') {
                console.log("Using deepseek template")
                this.configFile.start_header_id_template = ""
                this.configFile.system_message_template = " Using this information"
                this.configFile.end_header_id_template = ": "
                this.configFile.separator_template = "\n"
                this.configFile.start_user_header_id_template = ""
                this.configFile.end_user_header_id_template = ": "
                this.configFile.end_user_message_id_template = ""
                this.configFile.start_ai_header_id_template = ""
                this.configFile.end_ai_header_id_template = ": "
                this.configFile.end_ai_message_id_template = ""
                this.settingsChanged=true
            }
        },
        install_model(){

        },
        reinstallDiffusersService(){
            axios.post('/install_diffusers', {client_id:this.$store.state.client_id}, this.posts_headers)
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },

        upgradeDiffusersService(){
            axios.post('install_diffusers', {client_id:this.$store.state.client_id}, this.posts_headers)
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        reinstallXTTSService(){
            axios.post('install_xtts', {client_id:this.$store.state.client_id}, this.posts_headers)
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        reinstallWhisperService(){
            axios.post('install_whisper', {client_id:this.$store.state.client_id}, this.posts_headers)
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        reinstallSDService(){
            axios.post('/install_sd', {client_id:this.$store.state.client_id}, this.posts_headers)
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        upgradeSDService(){
            axios.post('upgrade_sd', {client_id:this.$store.state.client_id}, this.posts_headers)
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        startSDService(){
            axios.post('start_sd', {client_id:this.$store.state.client_id}, this.posts_headers)
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        showSD(){
            axios.post('show_sd', {client_id:this.$store.state.client_id}, this.posts_headers)
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        reinstallComfyUIService(){
            axios.post('install_comfyui', {client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        upgradeComfyUIService(){
            axios.post('upgrade_comfyui', {client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        startComfyUIService(){
            axios.post('start_comfyui', {client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },        
        showComfyui(){
            axios.post('show_comfyui', {client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });
        },
        reinstallvLLMService(){
            axios.post('install_vllm', {client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        startvLLMService(){
            axios.post('start_vllm', {client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        startollamaService(){
            axios.post('start_ollama', {client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        reinstallPetalsService(){
            axios.post('install_petals', {client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        reinstallOLLAMAService(){
        axios.post('install_ollama', {client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        reinstallElasticSearchService(){
            axios.post('install_vllm', {client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },

        getSeviceVoices() {
        axios.get('list_voices')
            .then(response => {
            this.voices = response.data["voices"];
            })
            .catch(error => {
            console.error(error);
            });
        },
        load_more_models(){
            if(this.models_zoo_initialLoadCount+10<this.models_zoo.length){
                this.models_zoo_initialLoadCount+=10
            }
            else{
                this.models_zoo_initialLoadCount=this.models_zoo.length
            }
        },
        async modelsZooToggleCollapse(){
            this.mzc_collapsed = !this.mzc_collapsed
            nextTick(() => {
                feather.replace()
            })
            if (this.binding_changed && !this.mzc_collapsed && (this.modelsZoo==undefined || this.modelsZoo.length==0)){
                console.log("Refreshing models")
                await this.$store.dispatch('refreshConfig');
                this.models_zoo = []
                this.refreshModelsZoo();
                this.binding_changed = false;
            }
        }, 
        async selectSortOption(index){
            this.$store.state.sort_type=index
            this.updateModelsZoo();   
            console.log(`Selected sorting:${index}`)
            console.log(`models:${this.models_zoo}`)
        },
        handleRadioSelected(index){
            this.isLoading = true;
            this.selectSortOption(index).then(()=>{
                this.isLoading = false;
            })
        },
        filter_installed(models){
            console.log("filtering")
            return models.filter(element => element.isInstalled === true);
        },
        getVoices() {
        // Fetch available voices from the SpeechSynthesis API
        if ('speechSynthesis' in window) {
            console.log("voice synthesis")
            this.audioVoices = speechSynthesis.getVoices();
            console.log("Voices:"+this.audioVoices)
            if (!this.audio_out_voice && this.audioVoices.length > 0) {
                this.audio_out_voice = this.audioVoices[0].name;
            }
            speechSynthesis.onvoiceschanged = () => {
            // Set a default voice if needed
            };
        }
        },
        async updateHasUpdates() {
            let res = await this.api_get_req("check_update");
            this.has_updates = res["update_availability"];
            console.log("has_updates", this.has_updates);
        },
        onVariantChoiceSelected(choice){
            this.selected_variant = choice     
        },
        oncloseVariantChoiceDialog(){
        this.variantSelectionDialogVisible=false;
        },
        onvalidateVariantChoice(choice){
            this.variantSelectionDialogVisible=false;
            this.currenModelToInstall.installing=true;
            let model_object = this.currenModelToInstall;
            if (model_object.linkNotValid) {
                model_object.installing = false
                this.$store.state.toast.showToast("Link is not valid, file does not exist", 4, false)
                return
            }
            let path = 'https://huggingface.co/'+model_object.model.quantizer+'/'+model_object.model.name+'/resolve/main/'+this.selected_variant.name;
            this.showProgress = true;
            this.progress = 0;
            this.addModel = { 
                model_name: this.selected_variant.name, 
                binding_folder: this.configFile.binding_name, 
                model_url: path 
            }
            console.log("installing...", this.addModel);

            // Use an arrow function for progressListener
            const progressListener = (response) => {
                console.log("received something");
                if (response.status && response.progress <= 100) {
                    this.addModel = response
                    console.log(`Progress`, response);
                    model_object.progress = response.progress
                    model_object.speed = response.speed
                    model_object.total_size = response.total_size
                    model_object.downloaded_size = response.downloaded_size
                    model_object.start_time = response.start_time
                    model_object.installing = true
                    if (model_object.progress == 100) {
                        const index = this.models_zoo.findIndex((model) => model.name === model_object.model.name);
                        this.models_zoo[index].isInstalled = true;
                        this.showProgress = false;
                        model_object.installing = false

                        console.log("Received succeeded")
                        socket.off('install_progress', progressListener);
                        console.log("Installed successfully")
                        // Update the isInstalled property of the corresponding model

                        this.$store.state.toast.showToast("Model:\n" + model_object.model.name + "\ninstalled!", 4, true)
                        this.$store.dispatch('refreshDiskUsage');
                    }
                } else {
                    socket.off('install_progress', progressListener);
                    console.log("Install failed")
                    // Installation failed or encountered an error
                    model_object.installing = false;

                    this.showProgress = false;
                    console.error('Installation failed:', response.error);
                    this.$store.state.toast.showToast("Model:\n" + model_object.model.name + "\nfailed to install!", 4, false)
                    this.$store.dispatch('refreshDiskUsage');
                }
                console.log("Here")
            };

            socket.on('install_progress', progressListener);


            socket.emit('install_model', { path: path, name: model_object.model.name, variant_name:this.selected_variant.name, type:model_object.model.type });
            console.log("Started installation, please wait");               
        },
        resetLogo(){
            this.configFile.app_custom_logo='';
            this.settingsChanged=true
        },
        resetAvatar(){
            this.configFile.user_avatar='';
            this.settingsChanged=true
        },
        removeLogo() {
            axios.post('/remove_logo')
                .then(() => {
                    this.configFile.app_custom_logo = null;
                    this.$store.state.config.app_custom_logo = null;
                    this.settingsChanged = true;
                    this.$store.state.toast.showToast("Logo removed successfully!", 4, true);
                })
                .catch(error => {
                    console.error('Error removing logo:', error);
                    this.$store.state.toast.showToast("Error removing logo!", 4, false);
                });
        },
        uploadLogo(event){
            const file = event.target.files[0]; // Get the selected file
            const formData = new FormData(); // Create a FormData object
            formData.append('logo', file); // Add the file to the form data with the key 'avatar'
            console.log("Uploading logo")
            // Make an API request to upload the avatar
            axios.post('/upload_logo', formData)
                .then(response => {
                    console.log("Logo uploaded successfully")
                    
                    this.$store.state.toast.showToast("Avatar uploaded successfully!", 4, true)
                    // Assuming the server responds with the file name after successful upload
                    const fileName = response.data.fileName;
                    console.log("response",response);
                    this.app_custom_logo = fileName; // Update the user_avatar value with the file name
                    this.$store.state.config.app_custom_logo=fileName;
                    this.settingsChanged = true
                })
                .catch(error => {
                console.error('Error uploading avatar:', error);
                });            
        },
        uploadAvatar(event){
            const file = event.target.files[0]; // Get the selected file
            const formData = new FormData(); // Create a FormData object
            formData.append('avatar', file); // Add the file to the form data with the key 'avatar'
            console.log("Uploading avatar")
            // Make an API request to upload the avatar
            axios.post('/upload_avatar', formData)
                .then(response => {
                    console.log("Avatar uploaded successfully")
                    
                    this.$store.state.toast.showToast("Avatar uploaded successfully!", 4, true)
                    // Assuming the server responds with the file name after successful upload
                    const fileName = response.data.fileName;
                    console.log("response",response);
                    this.user_avatar = fileName; // Update the user_avatar value with the file name
                    this.$store.state.config.user_avatar=fileName;
                    this.settingsChanged = true
                })
                .catch(error => {
                    console.error('Error uploading avatar:', error);
                });            
        },
        async update_software() {
            console.log("Posting")
            const res =  await this.api_post_req('update_software')
            console.log("Posting done")
            if(res.status){
                this.$store.state.toast.showToast("Success!", 4, true)
            }
            else{
                this.$store.state.toast.showToast("Failure!", 4, false)
            }
            
        },
        async restart_software() {
            console.log("Posting")
            const res =  await this.api_post_req('restart_program')
            console.log("Posting done")
            if(res.status){
                this.$store.state.toast.showToast("Success!", 4, true)
            }
            else{
                this.$store.state.toast.showToast("Failure!", 4, false)
            }
        },        
        on_loading_text(text){
            
            console.log("Loading text",text)
            this.loading_text = text

        },
        async load_everything() {
            this.isLoading = true
            nextTick(() => {
                feather.replace()
            })
            while (this.isReady === false) {
                await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for 100ms
            }  
            
            this.refresh();

            console.log("Ready")
            if (this.configFile.model_name) {
                this.isModelSelected = true
            }
            this.persCatgArr = await this.api_get_req("list_personalities_categories")
            this.persArr = await this.api_get_req("list_personalities?category="+this.configFile.personality_category)

            console.log("category")

            this.personality_category = this.configFile.personality_category
            this.personalitiesFiltered = this.$store.state.personalities.filter((item) => item.category === this.configFile.personality_category)
            // this.personalitiesFiltered.sort()
            //mountedPersArr
            this.modelsFiltered = []
           
            
            this.updateModelsZoo();

            this.isLoading = false
            this.isMounted = true
            console.log("READY Stuff")

        },
        async open_mzl(){
            this.mzl_collapsed = !this.mzl_collapsed; 
            console.log("Fetching models")
            //this.fetchModels();
        },        
        async getVramUsage() {
            const resp = await this.api_get_req("vram_usage")
        },
        async progressListener(response) {
            // does not work Still freezes UI
            console.log("received something");

            // Find model


            // 'model_name' : model_name,
            // 'binding_folder' : binding_folder,
            // 'model_url' : model_url


            if (response.status === 'progress') {

                // FInd model
                if (this.$refs.modelZoo) {
                    const index = this.$refs.modelZoo.findIndex(item => item.model.name == response.model_name && this.configFile.binding_name == response.binding_folder)
                    const modelEntry = this.models_zoo[index]

                    if (modelEntry) {
                        // Model found
                        console.log('model entry', modelEntry)
                        modelEntry.installing = true
                        modelEntry.progress = response.progress
                        console.log(`Progress = ${response.progress}`);
                        if (response.progress >= 100) {
                            modelEntry.installing = false
                            modelEntry.isInstalled = true
                        }
                        else{
                            modelEntry.installing = true
                            modelEntry.isInstalled = true
                        }

                    }
                }
            } else if (response.status === 'succeeded') {
                console.log("Received succeeded")
                // FInd model
                if (this.$refs.modelZoo) {
                    const index = this.$refs.modelZoo.findIndex(item => item.model.name == response.model_name && this.configFile.binding_name == response.binding_folder)
                    const modelEntry = this.models_zoo[index]
                    if (response.progress >= 100) {
                            modelEntry.installing = false
                            modelEntry.isInstalled = true
                    }
                }
                console.log("Installed successfully")

                if (this.$refs.modelZoo) {
                    const index = this.$refs.modelZoo.findIndex(item => item.model.name == response.model_name && this.configFile.binding_name == response.binding_folder)
                    const modelEntry = this.models_zoo[index]

                    if (modelEntry) {
                        // Model found

                        modelEntry.installing = false
                        modelEntry.isInstalled = true

                    }
                }


                this.$store.state.toast.showToast("Model:\n" + model_object.name + "\ninstalled!", 4, true)
                this.$store.dispatch('refreshDiskUsage');
            } else if (response.status === 'failed') {

                console.log("Install failed")
                // Installation failed or encountered an error
                if (this.$refs.modelZoo) {
                    const index = this.$refs.modelZoo.findIndex(item => item.model.name == response.model_name && this.configFile.binding_name == response.binding_folder)
                    const modelEntry = this.models_zoo[index]

                    if (modelEntry) {
                        // Model found

                        modelEntry.installing = false
                        modelEntry.isInstalled = false

                    }
                    console.error('Installation failed:', response.error);
                    this.$store.state.toast.showToast("Model:\n" + model_object.name + "\nfailed to install!", 4, false)
                    this.$store.dispatch('refreshDiskUsage');
                }
            }
        },
        showAddModelDialog() {
            this.$refs.addmodeldialog.showDialog("").then(() => {
                console.log(this.$refs.addmodeldialog.model_path);

                // Make a POST request to the "install model" endpoint
                const path = this.$refs.addmodeldialog.model_path;

                // Emit an event to the Socket.IO server
                socket.emit("install_model", { path: path, type: this.models_zoo[0].type }, (response) => {
                    // Handle the response from the server
                    console.log("Model installation successful:", response);
                });
                console.log(this.$refs.addmodeldialog.model_path)
            })

        },
        closeAddModelDialog() {
            this.addModelDialogVisibility = false;
        },
        collapseAll(val) {
            this.servers_conf_collapsed = val
            this.mainconf_collapsed = val
            this.bec_collapsed = val
            this.mzc_collapsed = val
            this.pzc_collapsed = val
            this.bzc_collapsed = val
            this.pc_collapsed = val
            this.mc_collapsed = val
            this.sc_collapsed = val
            this.mzdc_collapsed = val

        },
        fetchPersonalities(){
            this.api_get_req("list_personalities_categories").then(response => {
                this.persCatgArr = response
                this.persCatgArr.sort()
            })

            this.api_get_req("list_personalities").then(response => {
                this.persArr = response
                this.persArr.sort()
                console.log(`Listed personalities:\n${response}`)
            })
        },
        fetchHardwareInfos(){
            this.$store.dispatch('refreshDiskUsage');
            this.$store.dispatch('refreshRamUsage');
        },
        
        async onPersonalitySelected(pers) {
            console.log('on pers', pers)
            // eslint-disable-next-line no-unused-vars
            if (this.isLoading) {
                this.$store.state.toast.showToast("Loading... please wait", 4, false)
            }
            this.isLoading = true
            console.log('selecting ', pers)
            if (pers) {

                if (pers.selected) {
                    this.$store.state.toast.showToast("Personality already selected", 4, true)
                    this.isLoading = false
                    return
                }


                //this.settingsChanged = true
                let pth = pers.language==null?pers.full_path:pers.full_path+":"+pers.language
                console.log("pth",pth)
                if (pers.isMounted && this.configFile.personalities.includes(pth)) {

                    const res = await this.select_personality(pers)
                    console.log('pers is mounted', res)
                    if (res && res.status && res.active_personality_id > -1) {
                        this.$store.state.toast.showToast("Selected personality:\n" + pers.name, 4, true)

                    } else {
                        this.$store.state.toast.showToast("Error on select personality:\n" + pers.name, 4, false)
                    }
                    this.isLoading = false

                } else {
                    console.log('mounting pers')
                    this.mountPersonality(pers)

                }


                nextTick(() => {
                    feather.replace()

                })

            }

        },
   
        onModelSelected(model_object) {
            // eslint-disable-next-line no-unused-vars
            if (this.isLoading) {
                this.$store.state.toast.showToast("Loading... please wait", 4, false)
                return
            }
            if (model_object) {
                if (model_object.isInstalled) {
                    
                    this.update_model(model_object.model.name).then((res)=>{
                        console.log("update_model",res)
                        this.configFile.model_name = model_object.model.name
                        if(res.status){
                            this.$store.state.toast.showToast("Selected model:\n" + model_object.name, 4, true)
                            nextTick(() => {
                                feather.replace()
                                this.is_loading_zoo = false
                            })
                            this.updateModelsZoo()
                            this.api_get_req("get_model_status").then((res)=>{
                                this.$store.commit('setIsModelOk', res);
                            })
                        }else{
                            this.$store.state.toast.showToast("Couldn't select model:\n" + model_object.name, 4, false)
                            nextTick(() => {
                                feather.replace()
                            })
                        }
                        this.settingsChanged = true
                        this.isModelSelected = true
                    });

                } else {
                    this.$store.state.toast.showToast("Model:\n" + model_object.model.name + "\nis not installed", 4, false)
                }

                nextTick(() => {
                    feather.replace()

                })
            }

        },
        onCopy(modelEntry) {
            let content
            if (!modelEntry.model.isCustomModel) {
                content = `Model name: ${modelEntry.name}\nFile size: ${modelEntry.fileSize}\nDownload: ${'https://huggingface.co/'+modelEntry.quantizer+'/'+modelEntry.name}\nLicense: ${modelEntry.license}\nOwner: ${modelEntry.quantizer}\nWebsite: ${'https://huggingface.co/'+modelEntry.quantizer}\nDescription: ${modelEntry.description}`
            } else {
                content = `Model name: ${modelEntry.name}\nFile size: ${modelEntry.fileSize}\nManually downloaded model `
            }

            this.$store.state.toast.showToast("Copied model info to clipboard!", 4, true)
            navigator.clipboard.writeText(content.trim());
        },
        onCopyLink(modelEntry) {
            this.$store.state.toast.showToast("Copied link to clipboard!", 4, true)
            navigator.clipboard.writeText(modelEntry.model.name);
        },
        onCopyPersonalityName(personality) {
            this.$store.state.toast.showToast("Copied name to clipboard!", 4, true)
            navigator.clipboard.writeText(personality.name);
        },
        async onCopyToCustom(pers) {
            await axios.post("/copy_to_custom_personas",{client_id:this.$store.state.client_id, category: pers.personality.category, name: pers.personality.name})
        },
        async handleOpenFolder(pers){
            await axios.post("/open_personality_folder",{client_id:this.$store.state.client_id, personality_folder: pers.personality.category/pers.personality.folder})
        },
        onCancelInstall() {

            const modelEntry = this.addModel
            console.log('cancel install', modelEntry)
            // const keys = Object.keys(this.addModel)
            // if (keys.includes('url')) {
            //     return
            // }
            this.modelDownlaodInProgress = false
            this.addModel = {}
            socket.emit('cancel_install', { model_name: modelEntry.model_name, binding_folder: modelEntry.binding_folder, model_url: modelEntry.model_url, patreon: modelEntry.patreon?modelEntry.patreon:"None"});
            this.$store.state.toast.showToast("Model installation aborted", 4, false)
        },

        // Model installation

        onInstall(model_object) {
            this.variant_choices = model_object.model.variants;
            this.currenModelToInstall = model_object;
            console.log("variant_choices")
            console.log(this.variant_choices)
            console.log(model_object)
            this.variantSelectionDialogVisible=true;
        },
        onCreateReference() {
            axios.post("/add_reference_to_local_model",{"path": this.reference_path}).then((resp)=>{
                if(resp.status){
                    this.$store.state.toast.showToast("Reference created", 4, true)
                    this.is_loading_zoo = true;
                    this.refreshModelsZoo().then(()=>{this.updateModelsZoo(); this.is_loading_zoofalse;})
                }
                else{
                    this.$store.state.toast.showToast("Couldn't create reference", 4, false)
                }
            }) 
        },
        onInstallAddModel() {



            if (!this.addModel.url) {

                this.$store.state.toast.showToast("Link is empty", 4, false)
                return
            }
            let path = this.addModel.url;

            this.addModel.progress = 0;
            console.log("installing...");
            console.log("value ", this.addModel.url);
            this.modelDownlaodInProgress = true
            // Use an arrow function for progressListener
            const progressListener = (response) => {
                console.log("received something");
                if (response.status && response.progress <= 100) {
                    console.log(`Progress`, response);
                    this.addModel = response
                    this.addModel.url = path
                    if (this.addModel.progress == 100) {

                        this.modelDownlaodInProgress = false

                        console.log("Received succeeded")
                        socket.off('install_progress', progressListener);
                        console.log("Installed successfully")
                        // Update the isInstalled property of the corresponding model
                        this.addModel = {}
                        this.$store.state.toast.showToast("Model:\n" + this.addModel.model_name + "\ninstalled!", 4, true)
                        this.$store.dispatch('refreshDiskUsage');
                    }
                } else {
                    socket.off('install_progress', progressListener);
                    console.log("Install failed")
                    // Installation failed or encountered an error
                    this.modelDownlaodInProgress = false;
                    console.error('Installation failed:', response.error);
                    this.$store.state.toast.showToast("Model:\n" + this.addModel.model_name + "\nfailed to install!", 4, false)
                    this.$store.dispatch('refreshDiskUsage');
                }
            };

            socket.on('install_progress', progressListener);

            socket.emit('install_model', { path: path, type: this.models_zoo[0].type });
            console.log("Started installation, please wait");
        },
        uploadLocalModel() {


            if (this.uploadData.length == 0) {

                this.$store.state.toast.showToast("No files to upload", 4, false)
                return
            }
            let path = this.addModel.url;

            this.addModel.progress = 0;
            console.log("installing...");
            console.log("value ", this.addModel.url);
            this.modelDownlaodInProgress = true
            // Use an arrow function for progressListener
            const progressListener = (response) => {
                console.log("received something");
                if (response.status && response.progress <= 100) {
                    console.log(`Progress`, response);
                    this.addModel = response
                    this.addModel.url = path
                    // this.addModel.progress = response.progress
                    // this.addModel.speed = response.speed
                    // this.addModel.total_size = response.total_size
                    // this.addModel.downloaded_size = response.downloaded_size
                    // this.addModel.start_time = response.start_time
                    if (this.addModel.progress == 100) {

                        this.modelDownlaodInProgress = false

                        console.log("Received succeeded")
                        socket.off('progress', progressListener);
                        console.log("Installed successfully")
                        // Update the isInstalled property of the corresponding model
                        this.addModel = {}
                        this.$store.state.toast.showToast("Model:\n" + this.addModel.model_name + "\ninstalled!", 4, true)
                        this.$store.dispatch('refreshDiskUsage');
                    }
                } else {
                    socket.off('progress', progressListener);
                    console.log("Install failed")
                    // Installation failed or encountered an error
                    this.modelDownlaodInProgress = false;


                    console.error('Installation failed:', response.error);
                    this.$store.state.toast.showToast("Model:\n" + this.addModel.model_name + "\nfailed to install!", 4, false)
                    this.$store.dispatch('refreshDiskUsage');
                }
            };

            socket.on('progress', progressListener);


            // socket.emit('send_file', { file: this.uploadData });
            console.log("Started installation, please wait");


        },
        setFileList(event) {
            this.uploadData = event.target.files
            console.log('set file list', this.uploadData)

        },
        onUninstall(model_object) {

            this.$store.state.yesNoDialog.askQuestion("Are you sure you want to delete this model?\n [" + model_object.name + "]", 'Yes', 'Cancel').then(yesRes => {
                if (yesRes) {
                    console.log("uninstalling model...")
                    const progressListener = (response) => {
                        console.log("uninstalling res", response)
                        if (response.status) {
                            console.log("uninstalling success", response)

                            // Installation completed
                            model_object.uninstalling = false;
                            socket.off('install_progress', progressListener);
                            this.showProgress = false;
                            this.is_loading_zoo = true;
                            this.refreshModelsZoo().then(()=>{this.updateModelsZoo(); this.is_loading_zoo = false;})
                            
                            this.modelsFiltered = this.models_zoo
                            this.$store.state.toast.showToast("Model:\n" + model_object.model.name + "\nwas uninstalled!", 4, true)
                            this.$store.dispatch('refreshDiskUsage');
                        } else {
                            console.log("uninstalling failed", response)
                            // Installation failed or encountered an error
                            model_object.uninstalling = false;
                            this.showProgress = false;
                            socket.off('uninstall_progress', progressListener);
                            // eslint-disable-next-line no-undef
                            console.error('Uninstallation failed:', response.error);
                            this.$store.state.toast.showToast("Model:\n" + model_object.model.name + "\nfailed to uninstall!", 4, false)
                            this.$store.dispatch('refreshDiskUsage');
                        }
                    };

                    socket.on('uninstall_progress', progressListener);
                    if(this.selected_variant!=undefined){
                        socket.emit('uninstall_model', { path: 'https://huggingface.co/'+model_object.model.quantizer+'/'+model_object.model.name+'/resolve/main/'+this.selected_variant.name, type: model_object.model.type });
                    }
                    else{
                        socket.emit('uninstall_model', { path: 'https://huggingface.co/'+model_object.model.quantizer+'/'+model_object.model.name, type: model_object.model.type });
                    }

                }

            })
        },
        onBindingSelected(binding_object) {
            console.log("Binding selected")
            if (!binding_object.binding.installed) {
                this.$store.state.toast.showToast("Binding is not installed:\n" + binding_object.binding.name, 4, false)
                return
            }
            this.mzc_collapsed=true;
            if (this.configFile.binding_name != binding_object.binding.folder) {
                this.update_binding(binding_object.binding.folder)
                this.binding_changed = true;
            }
            this.api_get_req("get_model_status").then((res)=>{
                this.$store.commit('setIsModelOk', res);
            })
        },
        onInstallBinding(binding_object) {

            if (this.configFile.binding_name != binding_object.binding.folder) {

                // disabled for now
                // if (binding_object.binding.folder === 'backend_template' || binding_object.binding.folder === 'binding_template') {
                //     this.$store.state.toast.showToast("Cannot select template", 4, false)

                //     return
                // }
                this.isLoading = true

                if (binding_object.disclaimer){
                    this.$store.state.yesNoDialog.askQuestion(binding_object.disclaimer, 'Proceed', 'Cancel')
                }
                axios.post('/install_binding', {client_id:this.$store.state.client_id, name: binding_object.binding.folder }).then((res) => {

                if (res) {
                    this.isLoading = false
                    console.log('install_binding', res)
                    if (res.data.status) {
                        this.$store.state.toast.showToast("Binding installed successfully!", 4, true)
                        this.$store.state.messageBox.showMessage("It is advised to reboot the application after installing a binding.\nPage will refresh in 5s.")
                        setTimeout(()=>{window.location.href = "/"},5000) ;
                    } else {
                        this.$store.state.toast.showToast("Could not reinstall binding", 4, false)
                    }
                    this.isLoading = false

                    return res.data;
                }
                this.isLoading = false
                })
                // eslint-disable-next-line no-unused-vars

                .catch(error => {
                    this.isLoading = false
                    this.$store.state.toast.showToast("Could not reinstall binding\n" + error.message, 4, false)
                    return { 'status': false }
                });                //console.log('lol',binding_object)
            }
            else{
                this.update_binding(binding_object.binding.folder);                
            }
        },
        onUnInstallBinding(binding_object){
            this.isLoading = true
            axios.post('/unInstall_binding', {client_id:this.$store.state.client_id, name: binding_object.binding.folder }).then((res) => {
                
                if (res) {
                    this.isLoading = false
                    console.log('unInstall_binding', res)
                    if (res.data.status) {
                        const index = this.bindingsZoo.findIndex(item => item.folder == binding_object.binding.folder)
                        const item = this.bindingsZoo[index]
                        if (item) {
                            item.installed = true
                        }
                        else{
                            item.installed = false
                        }

                        this.settingsChanged = true

                        this.binding_changed = true;
                        this.$store.state.toast.showToast("Binding uninstalled successfully!", 4, true)
                    } else {
                        this.$store.state.toast.showToast("Could not uninstall binding", 4, false)
                    }
                    return res.data;
                }
                this.isLoading = false
                binding_object.isInstalled=False

            })
                // eslint-disable-next-line no-unused-vars

                .catch(error => {
                    this.isLoading = false
                    this.$store.state.toast.showToast("Could not uninstall binding\n" + error.message, 4, false)
                    return { 'status': false }
                });            
        },
        onReinstallBinding(binding_object) {
            this.isLoading = true
            axios.post('/reinstall_binding', {client_id:this.$store.state.client_id, name: binding_object.binding.folder }).then((res) => {

                if (res) {
                    this.isLoading = false
                    console.log('reinstall_binding', res)
                    if (res.data.status) {
                        this.$store.state.toast.showToast("Binding reinstalled successfully!", 4, true)
                        this.$store.state.messageBox.showMessage("It is advised to reboot the application after installing a binding")

                    } else {
                        this.$store.state.toast.showToast("Could not reinstall binding", 4, false)
                    }
                    return res.data;
                }
                this.isLoading = false
            })
                // eslint-disable-next-line no-unused-vars

                .catch(error => {
                    this.isLoading = false
                    this.$store.state.toast.showToast("Could not reinstall binding\n" + error.message, 4, false)
                    return { 'status': false }
                });
        },
        onSettingsBinding(bindingEntry) {
            try {
                this.isLoading = true
                axios.get('/get_active_binding_settings').then(res => {
                    console.log(res)
                    this.isLoading = false
                    if (res) {

                        console.log('binding setting', res)

                        if (res.data && Object.keys(res.data).length > 0) {

                            // open form

                            this.$store.state.universalForm.showForm(res.data, "Binding settings - " + bindingEntry.binding.name, "Save changes", "Cancel").then(res => {
                                // send new data
                                try {
                                    axios.post('/set_active_binding_settings',
                                        {client_id:this.$store.state.client_id, "settings":res}, {headers: this.posts_headers}).then(response => {
                                            if (response && response.data) {
                                                console.log('binding set with new settings', response.data)
                                                this.$store.state.toast.showToast("Binding settings updated successfully!", 4, true)
                                                axios.post('/update_binding_settings', {client_id:this.$store.state.client_id}).then((res) => {
                                                    this.$store.state.toast.showToast("Binding settings committed successfully!", 4, true)
                                                    window.location.href = "/";
                                                })
                                            } else {
                                                this.$store.state.toast.showToast("Did not get binding settings responses.\n" + response, 4, false)
                                                this.isLoading = false
                                            }
                                        })
                                } catch (error) {
                                    this.$store.state.toast.showToast("Did not get binding settings responses.\n Endpoint error: " + error.message, 4, false)
                                    this.isLoading = false
                                }



                            })
                        } else {
                            this.$store.state.toast.showToast("Binding has no settings", 4, false)
                            this.isLoading = false
                        }

                    }
                })

            } catch (error) {
                this.isLoading = false
                this.$store.state.toast.showToast("Could not open binding settings. Endpoint error: " + error.message, 4, false)
            }
        },
        onReloadBinding(binding_object){
            console.log("Reloading binding")
            this.isLoading = true
            axios.post('/reload_binding', { name: binding_object.binding.folder }, {headers: this.posts_headers}).then((res) => {

                if (res) {
                    this.isLoading = false
                    console.log('reload_binding', res)
                    if (res.data.status) {
                        this.$store.state.toast.showToast("Binding reloaded successfully!", 4, true)
                    } else {
                        this.$store.state.toast.showToast("Could not reload binding", 4, false)
                    }
                    return res.data;
                }
                this.isLoading = false
            })
                // eslint-disable-next-line no-unused-vars

                .catch(error => {
                    this.isLoading = false
                    this.$store.state.toast.showToast("Could not reload binding\n" + error.message, 4, false)
                    return { 'status': false }
                });
        },
        onSettingsPersonality(persEntry) {
            try {
                this.isLoading = true
                axios.get('/get_active_personality_settings').then(res => {
                    this.isLoading = false
                    if (res) {

                        console.log('pers sett', res)
                        if (res.data && Object.keys(res.data).length > 0) {

                            this.$store.state.universalForm.showForm(res.data, "Personality settings - " + persEntry.personality.name, "Save changes", "Cancel").then(res => {

                                // send new data
                                try {
                                    axios.post('/set_active_personality_settings',
                                        res).then(response => {

                                            if (response && response.data) {
                                                console.log('personality set with new settings', response.data)
                                                this.$store.state.toast.showToast("Personality settings updated successfully!", 4, true)

                                            } else {
                                                this.$store.state.toast.showToast("Did not get Personality settings responses.\n" + response, 4, false)
                                                this.isLoading = false
                                            }


                                        })
                                } catch (error) {
                                    this.$store.state.toast.showToast("Did not get Personality settings responses.\n Endpoint error: " + error.message, 4, false)
                                    this.isLoading = false
                                }

                            })
                        } else {
                            this.$store.state.toast.showToast("Personality has no settings", 4, false)
                            this.isLoading = false
                        }

                    }
                })

            } catch (error) {
                this.isLoading = false
                this.$store.state.toast.showToast("Could not open personality settings. Endpoint error: " + error.message, 4, false)
            }

        },
        // messagebox ok stuff
        onMessageBoxOk() {
            console.log("OK button clicked");
        },

        update_personality_category(cat, next){
            this.personality_category = cat
            next()
        },
        // Refresh stuff
        refresh() {
            console.log("Refreshing")
            this.$store.dispatch('refreshConfig').then(() => {
                console.log(this.personality_category)

                this.api_get_req("list_personalities_categories").then((cats)=>{
                    console.log("cats",cats)
                    this.persCatgArr = cats
                    this.personalitiesFiltered = this.$store.state.personalities.filter((item) => item.category === this.personality_category)
                    this.personalitiesFiltered.sort()

                })

            });            

            

        },
        // Accordeon stuff
        toggleAccordion() {
            this.showAccordion = !this.showAccordion;
        },
        async update_setting(setting_name_val, setting_value_val, next) {
            this.isLoading = true
            const obj = {
                client_id: this.$store.state.client_id,
                setting_name: setting_name_val,
                setting_value: setting_value_val
            }

            console.log("Updating setting", setting_name_val, ":", setting_value_val)
            let res = await axios.post('/update_setting', obj, {headers: this.posts_headers})

            if (res) {
                this.isLoading = false
                console.log('update_setting', res)
                if(res['status']){
                    this.$store.state.toast.showToast("Setting updated successfully.\n", 4, true)
                }
                else{
                    this.$store.state.toast.showToast("Setting update failed.\nPlease view the console for more details.", 4, false)
                }
                if (next !== undefined) {
                    next(res)
                }
                return res.data;
            }
            this.isLoading = false

        },
        async refreshModelsZoo() {
            this.models_zoo = []
            console.log("refreshing models")
            this.is_loading_zoo = true;
            await this.$store.dispatch('refreshModelsZoo');
            console.log("ModelsZoo refreshed")
            await this.$store.dispatch('refreshModels');
            console.log("Models refreshed")
            this.updateModelsZoo()
            console.log("Models updated")
            this.is_loading_zoo = false;
        },
        async updateModelsZoo(){
            let models_zoo = this.$store.state.modelsZoo
            if(models_zoo.length==0)
                return
            
            /*
            let index = models_zoo.findIndex(item => item.name == this.configFile.model_name)
            if (index>0){
                this.imgModel = models_zoo[index].icon
            }
            else{
                this.imgModel = defaultModelImgPlaceholder
            }*/

            console.log(`REFRESHING models using sorting ${this.sort_type}`)
            if(models_zoo.length>1){
            if(this.sort_type==0){ //  Sort by date
                models_zoo.sort((a, b) => {
                const dateA = new Date(a.last_commit_time);
                const dateB = new Date(b.last_commit_time);
                
                // Compare the date objects to sort by last_commit_time
                return dateB - dateA;
                });
                console.log("Sorted")
            } else if(this.sort_type==1){ //  Sort by rank
                models_zoo.sort((a, b) => {
                // Compare the date objects to sort by last_commit_time
                return b.rank - a.rank;
                });
            
            } else if(this.sort_type==2){ //  Sort by name
                models_zoo.sort((a, b) => a.name.localeCompare(b.name))
            } else if(this.sort_type==3){ //  Sort by name
                models_zoo.sort((a, b) => a.name.localeCompare(b.name))
            }
            // models_zoo.sort((a, b) => a.name.localeCompare(b.name))
            console.log("Sorted")  
            }
            else{
            console.log("No sorting needed");
            }
            models_zoo.forEach(model => {
                if (model.name == this.$store.state.config["model_name"]) {
                    model.selected = true;
                }
                else{
                model.selected = false; 
                }
            }); 

            console.log("Selected models") 

            // Returns array of model filenames which are = to name of models zoo entry
            for (let i = 0; i < this.$store.state.modelsArr.length; i++) {
                const customModel = this.$store.state.modelsArr[i]
                let index = models_zoo.findIndex(x => x.name == customModel)
                if(index==-1){
                    // The customModel is not directly in the model zoo, so check its variants
                    for (let j = 0; j < models_zoo.length; j++) {
                        let v = models_zoo[j]["variants"]
                        if(v!=undefined){
                            index = v.findIndex(x => x.name == customModel);
                            if(index!=-1){
                                index=j
                                console.log(`Found ${customModel} at index ${index}`)
                                break;
                            }  
                        }
                    }
                }
                
                if (index == -1) {
                    let newModelEntry = {}
                    newModelEntry.name = customModel
                    newModelEntry.icon = this.imgBinding
                    newModelEntry.isCustomModel = true
                    newModelEntry.isInstalled = true
                    models_zoo.push(newModelEntry)
                }
                else{
                    models_zoo[index].isInstalled=true;
                }
            }
            console.log("Determined models")
            models_zoo.sort((a, b) => {
                if (a.isInstalled && !b.isInstalled) {
                    return -1; // a is installed, b is not installed, so a comes first
                } else if (!a.isInstalled && b.isInstalled) {
                    return 1; // b is installed, a is not installed, so b comes first
                } else {
                    return 0; // both models are either installed or not installed, maintain their original order
                }
            });
            console.log("Done")
            this.models_zoo = this.$store.state.modelsZoo;

        },
        
        update_binding(value) {
            // eslint-disable-next-line no-unused-vars
            this.isLoading = true
            this.$store.state.modelsZoo=[]
            this.configFile.model_name = null
            this.$store.state.config.model_name = null
            console.log("updating binding_name")
            this.update_setting('binding_name', value, async (res) => {
                console.log("updated binding_name")
                await this.$store.dispatch('refreshConfig');
                this.models_zoo = []
                this.mzc_collapsed = true;
                const index = this.bindingsZoo.findIndex(item => item.folder == value)
                const item = this.bindingsZoo[index]
                if (item) {
                    item.installed = true
                }
                else{
                    item.installed = false
                }

                this.settingsChanged = true
                this.isLoading = false
                nextTick(() => {
                    feather.replace()

                })


                console.log("updating model")
                // If binding changes then reset model
                this.update_model(null).then(()=>{
                    
                });


                nextTick(() => {
                    feather.replace()

                })
            })
            nextTick(() => {
                feather.replace()

            })


        },
        async update_model(value) {
            if (!value) this.isModelSelected = false
            // eslint-disable-next-line no-unused-vars
            this.isLoading = true
            let res = await this.update_setting('model_name', value)
            this.isLoading = false
            nextTick(() => {
                feather.replace()
            })

            return res
        },
        async cancelConfiguration() {
            await this.$store.dispatch('refreshConfig');
            this.settingsChanged=false
        },
        applyConfiguration() {
            this.isLoading = true;
            axios.post('/apply_settings', {"client_id":this.$store.state.client_id, "config":this.configFile}, {headers: this.posts_headers}).then((res) => {
                this.isLoading = false;
                //console.log('apply-res',res)
                if (res.data.status) {

                    this.$store.state.toast.showToast("Configuration changed successfully.", 4, true)
                    this.settingsChanged = false
                    //this.save_configuration()
                } else {

                    this.$store.state.toast.showToast("Configuration change failed.", 4, false)

                }
                nextTick(() => {
                    feather.replace()

                })
            })
        },
        save_configuration() {
            this.showConfirmation = false
            axios.post('/save_settings', {}, {headers: this.posts_headers})
                .then((res) => {
                    if (res) {
                        if (res.status) {
                            // this.$store.state.messageBox.showMessage("Settings saved!")
                        }
                        else
                            this.$store.state.messageBox.showMessage("Error: Couldn't save settings!")
                        return res.data;
                    }
                })
                .catch(error => {
                    console.log(error.message, 'save_configuration')
                    this.$store.state.messageBox.showMessage("Couldn't save settings!")
                    return { 'status': false }
                });

        },
        reset_configuration() {
            this.$store.state.yesNoDialog.askQuestion("Are you sure?\nThis will delete all your configurations and get back to default configuration.").then(response => {
                if (response) {
                    // User clicked Yes
                    axios.post('/reset_settings', {}, {headers: this.posts_headers})
                        .then((res) => {
                            if (res) {
                                if (res.status)
                                    this.$store.state.messageBox.showMessage("Settings have been reset correctly")
                                else
                                    this.$store.state.messageBox.showMessage("Couldn't reset settings!")
                                return res.data;
                            }
                        })
                        .catch(error => {
                            console.log(error.message, 'reset_configuration')
                            this.$store.state.messageBox.showMessage("Couldn't reset settings!")
                            return { 'status': false }
                        });
                    // Perform delete operation
                } else {
                    // User clicked No
                    // Do nothing
                }
            });
        },

        async api_get_req(endpoint) {
            try {
                const res = await axios.get("/" + endpoint);

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'api_get_req - settings')
                return
            }


        },
        async api_post_req(endpoint) {
            try {
                const res = await axios.post("/" + endpoint, {client_id: this.$store.state.client_id});

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'api_post_req - settings')
                return
            }


        },
        closeToast() {
            this.showToast = false
        },
        async getPersonalitiesArr() {
            this.isLoading = true
            this.$store.state.personalities = []
            const dictionary = await this.api_get_req("get_all_personalities")
            const config = this.$store.state.config
            console.log("recovering all_personalities")
            // console.log(dictionary)
            const catkeys = Object.keys(dictionary); // returns categories folder names
            for (let j = 0; j < catkeys.length; j++) {
                const catkey = catkeys[j];
                const personalitiesArray = dictionary[catkey];
                const modPersArr = personalitiesArray.map((item) => {

                    const isMounted = config.personalities.includes(catkey + '/' + item.folder)
                    // if (isMounted) {
                    //     console.log(item)
                    // }
                    let newItem = {}
                    newItem = item
                    newItem.category = catkey // add new props to items
                    newItem.language = "" // add new props to items
                    newItem.full_path = catkey + '/' + item.folder // add new props to items
                    newItem.isMounted = isMounted // add new props to items
                    return newItem
                })


                if (this.$store.state.personalities.length == 0) {
                    this.$store.state.personalities = modPersArr
                } else {
                    this.$store.state.personalities = this.$store.state.personalities.concat(modPersArr)
                }
            }

            this.$store.state.personalities.sort((a, b) => a.name.localeCompare(b.name))
            this.personalitiesFiltered = this.$store.state.personalities.filter((item) => item.category === this.configFile.personality_category)
            this.personalitiesFiltered.sort()
            console.log('per filtered', this.personalitiesFiltered)
            this.isLoading = false

        },
        async filterPersonalities() {
            if (!this.searchPersonality) {
                this.personalitiesFiltered = this.$store.state.personalities.filter((item) => item.category === this.configFile.personality_category )
                this.personalitiesFiltered.sort()
                this.searchPersonalityInProgress = false
                return
            }
            const searchTerm = this.searchPersonality.toLowerCase()
            const seachedPersonalities = this.$store.state.personalities.filter((item) => {

                if (item.name && item.name.toLowerCase().includes(searchTerm) || item.description && item.description.toLowerCase().includes(searchTerm) || item.full_path && item.full_path.toLowerCase().includes(searchTerm)) {
                    return item
                }

            })



            if (seachedPersonalities.length > 0) {
                this.personalitiesFiltered = seachedPersonalities.sort()
            } else {
                this.personalitiesFiltered = this.$store.state.personalities.filter((item) => item.category === this.configFile.personality_category)
                this.personalitiesFiltered.sort()
            }
            this.searchPersonalityInProgress = false

        },
        async filterModels() {
            const searchTerm = this.searchModel.toLowerCase()
            this.is_loading_zoo = true;
            console.log("filtering models")
            console.log(this.models_zoo)
            const seachedModels = this.models_zoo.filter((item) => {

                if (item.name && item.name.toLowerCase().includes(searchTerm) || item.description && item.description.toLowerCase().includes(searchTerm) || item.category && item.category.toLowerCase().includes(searchTerm)) {
                    return item
                }

            })
            this.is_loading_zoo=false; 



            if (seachedModels.length > 0) {
                this.modelsFiltered = seachedModels
            } else {
                this.modelsFiltered = []
            }
            this.searchModelInProgress = false

        },
        computedFileSize(size) {
            return filesize(size)
        },
        async mount_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - mount_personality' } }

            try {
                const obj = {
                    client_id: this.$store.state.client_id,
                    language: pers.language?pers.language:"",
                    category: pers.category?pers.category:"",
                    folder: pers.folder?pers.folder:"",
                }
                const res = await axios.post('/mount_personality', obj, {headers: this.posts_headers});

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'mount_personality - settings')
                return
            }

        },
        async unmount_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - unmount_personality' } }

            const obj = {
                client_id: this.$store.state.client_id,
                language: pers.language,
                category: pers.category,
                folder: pers.folder
            }


            try {
                const res = await axios.post('/unmount_personality', obj, {headers: this.posts_headers});

                if (res) {
                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'unmount_personality - settings')
                return
            }

        },
        
        async select_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - select_personality' } }
            let pth = pers.language==null?pers.full_path:pers.full_path+":"+pers.language
            console.log("pth",pth)
            const id = this.configFile.personalities.findIndex(item => item === pth)

            const obj = {
                client_id: this.$store.state.client_id,
                id: id
            }


            try {
                const res = await axios.post('/select_personality', obj, {headers: this.posts_headers});

                if (res) {

                    this.$store.dispatch('refreshConfig').then(() => {
                        this.$store.dispatch('refreshPersonalitiesZoo').then(() => {
                        this.$store.dispatch('refreshMountedPersonalities');                
                        });
                    });
                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'select_personality - settings')
                return
            }

        },
        async mountPersonality(pers) {
            this.isLoading = true
            console.log('mount pers', pers)

            if(pers.personality.disclaimer!=""){
                this.$store.state.messageBox.showMessage(pers.personality.disclaimer)
            }

            if (!pers) { return }

            if (this.configFile.personalities.includes(pers.personality.full_path)) {
                this.isLoading = false
                this.$store.state.toast.showToast("Personality already mounted", 4, false)

                return
            }

            const res = await this.mount_personality(pers.personality)
            console.log('mount_personality res', res)

            if (res && res.status && res.active_personality_id > -1 && res.personalities.includes(pers.personality.full_path)) {
                this.configFile.personalities = res.personalities
                this.$store.state.toast.showToast("Personality mounted", 4, true)
                pers.isMounted = true

                const res2 = await this.select_personality(pers.personality)
                if (res2.status) {
                    this.$store.state.toast.showToast("Selected personality:\n" + pers.personality.name, 4, true)

                }
                this.$store.dispatch('refreshMountedPersonalities');
            } else {
                pers.isMounted = false
                this.$store.state.toast.showToast("Could not mount personality\nError: " + res.error + "\nResponse:\n" + res, 4, false)
            }
            this.isLoading = false

        },
        async unmountAll(){
            await axios.post('/unmount_all_personalities', {client_id: this.$store.state.client_id,}, {headers: this.posts_headers});
            this.$store.dispatch('refreshMountedPersonalities');
            this.$store.dispatch('refreshConfig');
            this.$store.state.toast.showToast("All personas unmounted", 4, true)
        },
        async unmountPersonality(pers) {
            this.isLoading = true
            if (!pers) { return }

            const res = await this.unmount_personality(pers.personality || pers)


            if (res.status) {
                this.configFile.personalities = res.personalities
                this.$store.state.toast.showToast("Personality unmounted", 4, true)
                const persId = this.$store.state.personalities.findIndex(item => item.full_path == pers.full_path)
                const persFilteredId = this.personalitiesFiltered.findIndex(item => item.full_path == pers.full_path)
                const persIdZoo = this.$refs.personalitiesZoo.findIndex(item => item.full_path == pers.full_path)
                console.log('ppp', this.$store.state.personalities[persId])

                this.$store.state.personalities[persId].isMounted = false

                if (persFilteredId > -1) {
                    this.personalitiesFiltered[persFilteredId].isMounted = false

                }

                if (persIdZoo > -1) {
                    this.$refs.personalitiesZoo[persIdZoo].isMounted = false

                }


                //pers.isMounted = false
                this.$store.dispatch('refreshMountedPersonalities');
                // Select some other personality
                const lastPers = this.mountedPersArr[this.mountedPersArr.length - 1]

                console.log(lastPers, this.mountedPersArr.length)
                // const res2 = await this.select_personality(lastPers.personality)
                const res2 = await this.select_personality(pers.personality)
                if (res2.status) {
                    this.$store.state.toast.showToast("Selected personality:\n" + lastPers.name, 4, true)

                }


            } else {
                this.$store.state.toast.showToast("Could not unmount personality\nError: " + res.error, 4, false)
            }

            this.isLoading = false
        },
        editPersonality(pers) {
            pers=pers.personality;
            // Make a POST request to the '/get_personality_config' endpoint using Axios
            axios.post('/get_personality_config', {
                client_id:this.$store.state.client_id,
                category: pers.category,
                name: pers.folder,
            })
            .then(response => {
            const data = response.data;
            console.log("Done")
            if (data.status) {
                // Update the currentPersonConfig with the received data
                this.$store.state.currentPersonConfig = data.config;
                this.$store.state.showPersonalityEditor = true;
                this.$store.state.personality_editor.showPanel()
                this.$store.state.selectedPersonality = pers
            } else {
                // Handle the error
                console.error(data.error);
            }
            })
            .catch(error => {
            // Handle the error
            console.error(error);
            });
        },
        copyToCustom(pers) {
            pers=pers.personality;
            // Make a POST request to the '/get_personality_config' endpoint using Axios
            axios.post('/copy_to_custom_personas', {
                category: pers.category,
                name: pers.folder,
            })
            .then(response => {
                if (response.status){
                    this.$store.state.messageBox.showMessage(
                        "Personality copied to the custom personalities folder:\n"+
                        "Now it's up to you to modify it, enhance it, and maybe even share it.\n"+
                        "Feel free to add your name as an author, but please remember to keep the original creator's name as well.\n"+
                        "You have the freedom to give, sell, or keep the personas you create for yourself.\n"+
                        "The possibilities are endless, they are now yours to mold and customize as you see fit."
                    
                    )

                    this.$store.dispatch('refreshPersonalitiesZoo')
                }
                else{
                    this.$store.state.toast.showToast("Personality couldn't be copied to the custom personalities folder:\nVerify that the personality is not already copied there.", 4, false)
                }
            })
            .catch(error => {
            // Handle the error
                this.$store.state.toast.showToast("Personality couldn't be copied to the custom personalities folder:\n", 4, false)
                console.error(error);
            });
        },
        async remountPersonality(pers){
            await this.unmountPersonality(pers);
            await this.mountPersonality(pers);
        },

        onPersonalityReinstall(persItem){
            console.log('on reinstall ', persItem)
            this.isLoading = true
            console.log("Personality path:",persItem.personality.path)
            axios.post('/reinstall_personality', { client_id:this.$store.state.client_id, name: persItem.personality.path }, {headers: this.posts_headers}).then((res) => {

                if (res) {
                    this.isLoading = false
                    console.log('reinstall_personality', res)
                    if (res.data.status) {
                        this.$store.state.toast.showToast("Personality reinstalled successfully!", 4, true)
                    } else {
                        this.$store.state.toast.showToast("Could not reinstall personality", 4, false)
                    }
                    return res.data;
                }
                this.isLoading = false
            })
                // eslint-disable-next-line no-unused-vars

                .catch(error => {
                    this.isLoading = false
                    this.$store.state.toast.showToast("Could not reinstall personality\n" + error.message, 4, false)
                    return { 'status': false }
                });
        },
        personalityImgPlacehodler(event) {
            event.target.src = defaultPersonalityImgPlaceholder
        },
        searchPersonality_func() {
            
            clearTimeout(this.searchPersonalityTimer)
            if (this.searchPersonality) {
                this.searchPersonalityInProgress = true
                setTimeout(this.filterPersonalities, this.searchPersonalityTimerInterval)
            }
        },
        searchModel_func() {
            this.filterModels()
        }


    }, async mounted() {
        console.log("Getting voices")
        this.getVoices();
        console.log("Constructing")
        this.load_everything()
        this.getSeviceVoices()
        try{
            console.log("Loading input devices list")
            const response = await axios.get("/get_snd_input_devices")
            this.snd_input_devices = response.data["device_names"]
            this.snd_input_devices_indexes = response.data["device_indexes"]
        }
        catch{
            console.log("Couldin't list input devices")
        }
        try{
            console.log("Loading output devices list")
            const response = await axios.get("/get_snd_output_devices")
            this.snd_output_devices = response.data["device_names"]
            this.snd_output_devices_indexes = response.data["device_indexes"]
        }
        catch{
            console.log("Couldin't list output devices")
        }
        
        try{
            console.log("Getting comfyui models")
            if(this.configFile.activate_lollms_tti_server && this.configFile.active_tti_service=="comfyui"){
                const res = await axios.get("/list_comfyui_models")
                if(res.data.status){
                    this.comfyui_models= res.data.models
                }

            }

        }
        catch{
            console.log("Couldin't list output devices")
        }
        this.fetchElevenLabsVoices();
    },
    activated() {
        //this.load_everything()
    },
    computed: { 
        full_template:{
            get(){
                return (this.configFile.start_header_id_template+this.configFile.system_message_template+this.configFile.end_header_id_template+" system message"+this.configFile.separator_template+this.configFile.start_user_header_id_template+"user name"+this.configFile.end_user_header_id_template+" User prompt"+this.configFile.separator_template+this.configFile.end_user_message_id_template+this.configFile.separator_template+this.configFile.start_ai_header_id_template+"ai personality"+this.configFile.end_ai_header_id_template+"ai response"+this.configFile.end_ai_message_id_template).replace("\n","<br>")
            }
        },
        rendered_models_zoo:{
            get(){
                if (this.searchModel){
                    if(this.show_only_installed_models){
                        return this.modelsFiltered.filter(element => element.isInstalled === true) 
                    }else{
                        return this.modelsFiltered.slice(0, Math.min(this.models_zoo.length,this.models_zoo_initialLoadCount))
                    }
                }
                console.log("this.models_zoo")
                console.log(this.models_zoo)
                console.log(this.models_zoo_initialLoadCount)
                if(this.show_only_installed_models){
                    return this.models_zoo.filter(element => element.isInstalled === true) 
                }
                else{
                    return this.models_zoo.slice(0, Math.min(this.models_zoo.length,this.models_zoo_initialLoadCount));
                }
            }
        },
        imgBinding: {
            get(){

                if (!this.isMounted) {
                    return defaultImgPlaceholder
                }
                try {
                    return this.$refs.bindingZoo[this.$refs.bindingZoo.findIndex(item => item.binding.folder == this.configFile.binding_name)].$refs.imgElement.src
                }
                catch (error) {
                    return defaultImgPlaceholder
                }
            }
        },
        imgModel:{
            get() {
                try{
                    let idx = this.$store.state.modelsZoo.findIndex(item => item.name == this.$store.state.selectedModel)
                    if(idx>=0){
                        console.log(`model avatar : ${this.$store.state.modelsZoo[idx].icon}`)
                        return this.$store.state.modelsZoo[idx].icon
                    }
                    else{
                        return  defaultModelImgPlaceholder            
                    }
                }
                catch{
                    console.log("error")
                }
                if (!this.isMounted) {
                    return defaultImgPlaceholder
                }
                try {
                    return this.$refs.bindingZoo[this.$refs.bindingZoo.findIndex(item => item.binding.folder == this.configFile.binding_name)].$refs.imgElement.src
                }
                catch (error) {
                    return defaultImgPlaceholder
                }                
            },
        },
        isReady:{
            
            get() {
                return this.$store.state.ready;
            },
        },
        audio_out_voice:{
            get() {
                return this.$store.state.config.audio_out_voice;
            },
            set(value) {
                this.$store.state.config.audio_out_voice = value;
            },
        },
        openaiWhisperModels(){
            return [
                "whisper-1"
            ]
        },
        whisperModels(){
            return [
            'tiny.en', 'tiny', 'base.en', 'base', 'small.en', 'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large-v3', 'large'
            ]
        },
        audioLanguages() {
        // Replace this with your own list of language codes and names
        // Example data structure: [{ code: 'en-US', name: 'English (US)' }, ...]
        return [
            { code: 'en-US', name: 'English (US)' },
            { code: 'en-GB', name: 'English (UK)' },
            { code: 'es-ES', name: 'Spanish (Spain)' },
            { code: 'es-MX', name: 'Spanish (Mexico)' },
            { code: 'fr-FR', name: 'French (France)' },
            { code: 'fr-CA', name: 'French (Canada)' },
            { code: 'de-DE', name: 'German (Germany)' },
            { code: 'it-IT', name: 'Italian (Italy)' },
            { code: 'pt-BR', name: 'Portuguese (Brazil)' },
            { code: 'pt-PT', name: 'Portuguese (Portugal)' },
            { code: 'ru-RU', name: 'Russian (Russia)' },
            { code: 'zh-CN', name: 'Chinese (China)' },
            { code: 'ja-JP', name: 'Japanese (Japan)' },
            { code: 'ar-SA', name: 'Arabic (Saudi Arabia)' },
            { code: 'tr-TR', name: 'Turkish (Turkey)' },
            { code: 'ms-MY', name: 'Malay (Malaysia)' },
            { code: 'ko-KR', name: 'Korean (South Korea)' },
            { code: 'nl-NL', name: 'Dutch (Netherlands)' },
            { code: 'sv-SE', name: 'Swedish (Sweden)' },
            { code: 'da-DK', name: 'Danish (Denmark)' },
            { code: 'fi-FI', name: 'Finnish (Finland)' },
            { code: 'no-NO', name: 'Norwegian (Norway)' },
            { code: 'pl-PL', name: 'Polish (Poland)' },
            { code: 'el-GR', name: 'Greek (Greece)' },
            { code: 'hu-HU', name: 'Hungarian (Hungary)' },
            { code: 'cs-CZ', name: 'Czech (Czech Republic)' },
            { code: 'th-TH', name: 'Thai (Thailand)' },
            { code: 'hi-IN', name: 'Hindi (India)' },
            { code: 'he-IL', name: 'Hebrew (Israel)' },
            { code: 'id-ID', name: 'Indonesian (Indonesia)' },
            { code: 'vi-VN', name: 'Vietnamese (Vietnam)' },
            { code: 'uk-UA', name: 'Ukrainian (Ukraine)' },
            { code: 'ro-RO', name: 'Romanian (Romania)' },
            { code: 'bg-BG', name: 'Bulgarian (Bulgaria)' },
            { code: 'hr-HR', name: 'Croatian (Croatia)' },
            { code: 'sr-RS', name: 'Serbian (Serbia)' },
            { code: 'sk-SK', name: 'Slovak (Slovakia)' },
            { code: 'sl-SI', name: 'Slovenian (Slovenia)' },
            { code: 'et-EE', name: 'Estonian (Estonia)' },
            { code: 'lv-LV', name: 'Latvian (Latvia)' },
            { code: 'lt-LT', name: 'Lithuanian (Lithuania)' },
            { code: 'ka-GE', name: 'Georgian (Georgia)' },
            { code: 'hy-AM', name: 'Armenian (Armenia)' },
            { code: 'az-AZ', name: 'Azerbaijani (Azerbaijan)' },
            { code: 'kk-KZ', name: 'Kazakh (Kazakhstan)' },
            { code: 'uz-UZ', name: 'Uzbek (Uzbekistan)' },
            { code: 'kkj-CM', name: 'Kako (Cameroon)' },
            { code: 'my-MM', name: 'Burmese (Myanmar)' },
            { code: 'ne-NP', name: 'Nepali (Nepal)' },
            { code: 'si-LK', name: 'Sinhala (Sri Lanka)' },
            // Add more language entries as needed
        ];
        },        
        configFile: {
            get() {
                return this.$store.state.config;
            },
            set(value) {
                this.$store.commit('setConfig', value);
            },
        },
        userName: {
                get() {
                    return this.$store.state.config.user_name;
                },
                set(value) {
                    // You should not set the value directly here; use the updateSetting method instead
                    this.$store.state.config.user_name = value
                },
            },
        user_avatar:{
                get() {
                    return this.$store.state.config.user_avatar!=''?"/user_infos/"+this.$store.state.config.user_avatar:storeLogo;
                },
                set(value) {
                    // You should not set the value directly here; use the updateSetting method instead
                    this.$store.state.config.user_avatar = value
                },
            },
            
        hardware_mode:{
            get() {
                return this.$store.state.config.hardware_mode;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                this.$store.state.config.hardware_mode = value
            },

        },
        auto_update:{
            get() {
                return this.$store.state.config.auto_update;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                this.$store.state.config.auto_update = value
            },

        },
        auto_speak:{
            get() {
                return this.$store.state.config.auto_speak;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                this.$store.state.config.auto_speak = value
            },
        },
        auto_read:{
            get() {
                return this.$store.state.config.auto_read;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                this.$store.state.config.auto_read = value
            },
        },
        xtts_current_language:{
            get() {
                return this.$store.state.config.xtts_current_language;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                console.log("Current xtts voice set to ",value)
                this.$store.state.config.xtts_current_language = value
            },
        },
        xtts_current_voice:{
            get() {
                if (this.$store.state.config.xtts_current_voice===null || this.$store.state.config.xtts_current_voice===undefined){
                    console.log("current voice", this.$store.state.config.xtts_current_voice)
                    return "main_voice";
                }
                return this.$store.state.config.xtts_current_voice;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                if(value=="main_voice" || value===undefined){
                    console.log("Current voice set to None")
                    this.$store.state.config.xtts_current_voice = null
                }
                else{
                    console.log("Current voice set to ",value)
                    this.$store.state.config.xtts_current_voice = value
                }
            },
        },

        audio_pitch:{
            get() {
                return this.$store.state.config.audio_pitch;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                this.$store.state.config.audio_pitch = value
            },
        },
        audio_in_language:{
            get() {
                return this.$store.state.config.audio_in_language;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                this.$store.state.config.audio_in_language = value
            },
        },
        
        use_user_name_in_discussions: {
            get() {
                return this.$store.state.config.use_user_name_in_discussions;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                this.$store.state.config.use_user_name_in_discussions = value
            },
        },
        discussion_db_name: {
            get() {
                return this.$store.state.config.discussion_db_name;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                this.$store.state.config.discussion_db_name = value
            },
        },
            
        personalities:{
            get() {
                return this.$store.state.personalities;
            },
            set(value) {
                this.$store.commit('setPersonalities', value);
            }
        },
        mountedPersArr:{
            get() {
                return this.$store.state.mountedPersArr;
            },
            set(value) {
                this.$store.commit('setMountedPers', value);
            }
        },
        bindingsZoo: {
            get() {
                return this.$store.state.bindingsZoo;
            },
            set(value) {
                this.$store.commit('setbindingsZoo', value);
            }
        },
        modelsArr: {
            get() {
                return this.$store.state.modelsArr;
            },
            set(value) {
                this.$store.commit('setModelsArr', value);
            }
        },
        models: {
            get() {
                return this.models_zoo;
            },
            set(value) {
                this.$store.commit('setModelsZoo', value);
            }
        },
        installed_models: {
            get() {
                return this.models_zoo;
            },
            set(value) {
                this.$store.commit('setModelsZoo', value);
            }
        },
        diskUsage: {
            get() {
                return this.$store.state.diskUsage;
            },
            set(value) {
                this.$store.commit('setDiskUsage', value);
            }            
        },
        ramUsage: {
            get() {
                return this.$store.state.ramUsage;
            },
            set(value) {
                this.$store.commit('setRamUsage', value);
            }            
        },
        vramUsage: {
            get() {
                return this.$store.state.vramUsage;
            },
            set(value) {
                this.$store.commit('setVramUsage', value);
            }            
        },

        disk_available_space() {
            return this.computedFileSize(this.diskUsage.available_space)
        },
        disk_binding_models_usage() {
            console.log(`this.diskUsage : ${this.diskUsage}`)
            return this.computedFileSize(this.diskUsage.binding_models_usage)
        },
        disk_percent_usage() {
            return this.diskUsage.percent_usage

        },
        disk_total_space() {
            return this.computedFileSize(this.diskUsage.total_space)
        },
        ram_available_space() {
            return this.computedFileSize(this.ramUsage.available_space)
        },
        ram_usage() {
            return this.computedFileSize(this.ramUsage.ram_usage)
        },
        ram_percent_usage() {
            return this.ramUsage.percent_usage

        },
        ram_total_space() {
            return this.computedFileSize(this.ramUsage.total_space)
        },
        // vram_available_space() {
        //     return this.computedFileSize(this.vramUsage.gpu_0_total_vram - this.vramUsage.gpu_0_used_vram)
        // },
        // vram_usage() {
        //     return this.computedFileSize(this.vramUsage.gpu_0_used_vram)
        // },
        // vram_percent_usage() {
        //     const percentage = (this.vramUsage.gpu_0_used_vram / this.vramUsage.gpu_0_total_vram) * 100
        //     return percentage.toFixed(2)

        // },
        // vram_total_space() {
        //     return this.computedFileSize(this.vramUsage.gpu_0_total_vram)
        // },
        model_name() {
            if (!this.isMounted) {
                return
            }
            return this.configFile.model_name
        },
        binding_name() {
            if (!this.isMounted) {
                return null
            }
            const index = this.bindingsZoo.findIndex(item => item.folder === this.configFile.binding_name)
            if (index > -1) {
                return this.bindingsZoo[index].name

            } else {
                return null
            }
        },
        active_pesonality() {
            if (!this.isMounted) {
                return null
            }
            const index = this.$store.state.personalities.findIndex(item => item.full_path === this.configFile.personalities[this.configFile.active_personality_id])
            if (index > -1) {
                return this.$store.state.personalities[index].name
            } else {
                return null

            }
        },
        speed_computed() {
            return filesize(this.addModel.speed)
        },
        total_size_computed() {
            return filesize(this.addModel.total_size)
        },
        downloaded_size_computed() {
            return filesize(this.addModel.downloaded_size)
        },


    },
    watch: {
        bec_collapsed() {
            nextTick(() => {
                feather.replace()

            })
        },
        pc_collapsed() {
            nextTick(() => {
                feather.replace()

            })
        },
        mc_collapsed() {
            nextTick(() => {
                feather.replace()

            })
        },
        sc_collapsed() {
            nextTick(() => {
                feather.replace()

            })
        },
        showConfirmation() {
            nextTick(() => {
                feather.replace()

            })
        },
        mzl_collapsed() {

            nextTick(() => {
                feather.replace()

            })
        },
        pzl_collapsed() {

            nextTick(() => {
                feather.replace()

            })
        },
        ezl_collapsed() {
        nextTick(() => {
            feather.replace()
        })
        },
        bzl_collapsed() {

            nextTick(() => {
                feather.replace()

            })
        },
        all_collapsed(val) {

            this.collapseAll(val)
            nextTick(() => {
                feather.replace()

            })
        },
        settingsChanged(val) {

            this.$store.state.settingsChanged = val
            nextTick(() => {
                feather.replace()

            })
        },
        isLoading() {
            nextTick(() => {
                feather.replace()

            })
        },
        searchPersonality(val) {
            if (val == "") {
                this.filterPersonalities()
            }
        },
        mzdc_collapsed() {
            nextTick(() => {
                feather.replace()

            })
        }



    },
    async beforeRouteLeave(to) {
        // console.log('did settings?',this.settingsChanged)
        await this.$router.isReady()
        // if (this.settingsChanged) {
        //     const res = await this.$store.state.yesNoDialog.askQuestion("Did You forget to apply changes?\nYou need to apply changes before you leave, or else.", 'Apply configuration', 'Cancel')
        //     if (res) {
        //         this.applyConfiguration()

        //     }
        //     return false
        // }


    },
}
</script>
