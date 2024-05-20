<template>
    <div class="container overflow-y-scroll flex flex-row shadow-lg p-10 pt-0 overflow-y-scroll w-full dark:bg-bg-dark scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
        <!-- CONTROL PANEL -->
        <div
            class="sticky top-0 z-10 flex flex-row mb-2 p-3 gap-3 w-full rounded-b-lg bg-bg-light-tone dark:bg-bg-dark-tone  shadow-lg">
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
            <div v-if="!showConfirmation" class="flex gap-3 flex-1 items-center ">
                <button title="Save configuration" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    @click="showConfirmation = true">
                    <i data-feather="save"></i>
                </button>
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
                    <button
                    title="Upgrade program "
                    class="text-2xl hover:text-secondary duration-75 active:scale-90"
                    @click="api_post_req('update_software').then((res)=>{if(res.status){this.$store.state.toast.showToast('Success!', 4, true)}else{this.$store.state.toast.showToast('Success!', 4, true)}})"
                    >
                    <i data-feather="arrow-up-circle"></i>
                    
                    <div  v-if="has_updates" >
                        <i data-feather="alert-circle"></i>
                    </div>
                    </button>
                <div class="flex gap-3 items-center">
                    <div v-if="settingsChanged" class="flex gap-3 items-center">
                        <p class="text-red-600 font-bold">Apply changes:</p>
                        <button v-if="!isLoading" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                            title="Apply changes" type="button" @click.stop="applyConfiguration()">
                            <i data-feather="check"></i>
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
            <div class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="sc_collapsed = !sc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 w-full text-left flex flex-row items-center ">
                        <div v-show="sc_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!sc_collapsed" ><i data-feather='chevron-down'></i></div>


                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            System status</h3>
                        <div class="mr-2">|</div>

                        <div class=" text-base font-semibold cursor-pointer select-none items-center">

                            <div class="flex gap-2 items-center ">
                                <div>
                                    <div v-if="vramUsage&&vramUsage.gpus && vramUsage.gpus.length == 1">
                                        <div class="flex gap-2 items-center " v-for="item in vramUsage.gpus" :key="item">
                                            <!-- GPU IMAGE  -->
                                            <img :src="SVGGPU"  width="25" height="25">

                                            <h3 class="font-bold font-large text-lg">
                                                <div>{{ computedFileSize(item.used_vram) }} / {{ computedFileSize(item.total_vram) }} ({{ item.percentage }}%)
                                                </div>
                                            </h3>
                                        </div>
                                    </div>
                                    <div v-if="vramUsage&& vramUsage.gpus && vramUsage.gpus.length >1">
                                        <div class="flex gap-2 items-center ">

                                            <!-- GPU IMAGE  -->
                                            <img :src="SVGGPU"  width="25" height="25">
                                            <h3 class="font-bold font-large text-lg">
                                                <div> {{ vramUsage.gpus.length }}x
                                                </div>
                                            </h3>

                                        </div>
                                    </div>
                                </div>
                                <i data-feather="cpu" title="CPU Ram" class="w-5 h-5 mx-1 flex-shrink-0"></i>
                                <h3 class="font-bold font-large text-lg">
                                    <div>{{ ram_usage }} / {{ ram_total_space }} ({{ ram_percent_usage }}%)</div>
                                </h3>
                                <i data-feather="hard-drive" title="Hard drive" class="w-5 h-5 mx-1 flex-shrink-0"></i>
                                <h3 class="font-bold font-large text-lg">
                                    <div> {{ disk_binding_models_usage }} / {{ disk_total_space }} ({{ disk_percent_usage
                                    }}%)</div>
                                </h3>
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
            <!-- MAIN CONFIGS -->
            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="minconf_collapsed = !minconf_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <div v-show="minconf_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!minconf_collapsed" ><i data-feather='chevron-down'></i></div>

                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Main configurations</h3>
                    </button>
                </div>
                <div :class="{ 'hidden': minconf_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <div class="flex flex-col mb-2 px-3 pb-2">
                                <Card title="General" :is_subcard="true" class="pb-2 m-2">
                                    <table class="expand-to-fit bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="app_custom_logo" class="text-sm font-bold" style="margin-right: 1rem;">Application logo:</label>
                                        </td>
                                        <td>
                                            <label for="logo-upload">
                                                <img :src="configFile.app_custom_logo!=null && configFile.app_custom_logo!=''? '/user_infos/'+configFile.app_custom_logo:storeLogo" class="w-50 h-50 rounded-full" style="max-width: 50px; max-height: 50px; cursor: pointer;">
                                            </label>
                                            <input type="file" id="logo-upload" style="display: none" @change="uploadLogo">
                                        </td>
                                        <td style="width: 10%;">
                                            <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Discard title changes"
                                                type="button" @click.stop="resetLogo()">
                                                <i data-feather="x"></i>
                                            </button>
                                        </td>
                                        
                                        </tr>

                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="hardware_mode" class="text-sm font-bold" style="margin-right: 1rem;">Hardware mode:</label>
                                        </td>
                                        <td class="text-center items-center">
                                            <div class="flex flex-row">
                                            <select
                                                id="hardware_mode"
                                                required
                                                v-model="configFile.hardware_mode"
                                                @change="settingsChanged=true"
                                                class="m-2 h-50 w-50 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                                <option value="cpu">CPU</option>
                                                <option value="cpu-noavx">CPU (No AVX)</option>
                                                <option value="nvidia-tensorcores">NVIDIA (Tensor Cores)</option>
                                                <option value="nvidia">NVIDIA</option>
                                                <option value="amd-noavx">AMD (No AVX)</option>
                                                <option value="amd">AMD</option>
                                                <option value="apple-intel">Apple Intel</option>
                                                <option value="apple-silicon">Apple Silicon</option>
                                            </select>
                                            </div>
                                        </td>
                                        </tr>                                        
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="discussion_db_name" class="text-sm font-bold" style="margin-right: 1rem;">Database path:</label>
                                        </td>
                                        <td style="width: 100%;">
                                            <input
                                            type="text"
                                            id="discussion_db_name"
                                            required
                                            v-model="configFile.discussion_db_name"
                                            @change="settingsChanged=true"
                                            class="w-full w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                            >
                                        </td>
                                        </tr>      
                                        
                                        
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="copy_to_clipboard_add_all_details" class="text-sm font-bold" style="margin-right: 1rem;">Add details to messages copied to clipboard:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                                <input
                                            type="checkbox"
                                            id="copy_to_clipboard_add_all_details"
                                            required
                                            v-model="configFile.copy_to_clipboard_add_all_details"
                                            @change="settingsChanged=true"
                                            class="m-2 h-50 w-50 py-1 border border-gray-300 rounded  dark:bg-gray-600 "
                                            >
                                            </div>
                                        </td>
                                        </tr>
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="auto_show_browser" class="text-sm font-bold" style="margin-right: 1rem;">Auto show browser:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                                <input
                                            type="checkbox"
                                            id="auto_show_browser"
                                            required
                                            v-model="configFile.auto_show_browser"
                                            @change="settingsChanged=true"
                                            class="m-2 h-50 w-50 py-1 border border-gray-300 rounded  dark:bg-gray-600 "
                                            >
                                            </div>
                                        </td>
                                        </tr>
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="activate_debug" class="text-sm font-bold" style="margin-right: 1rem;">Activate debug mode:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                                <input
                                            type="checkbox"
                                            id="activate_debug"
                                            required
                                            v-model="configFile.debug"
                                            @change="settingsChanged=true"
                                            class="m-2 h-50 w-50 py-1 border border-gray-300 rounded  dark:bg-gray-600 "
                                            >
                                            </div>
                                        </td>
                                        </tr>
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="debug_log_file_path" class="text-sm font-bold" style="margin-right: 1rem;">Debug file path:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                                <input
                                            type="text"
                                            id="debug_log_file_path"
                                            required
                                            v-model="configFile.debug_log_file_path"
                                            @change="settingsChanged=true"
                                            class="m-2 h-50 w-50 py-1 border border-gray-300 rounded  dark:bg-gray-600 "
                                            >
                                            </div>
                                        </td>
                                        </tr>
                                        <tr>
                                            
                                            <td style="min-width: 200px;">
                                                <label for="show_news_panel" class="text-sm font-bold" style="margin-right: 1rem;">Show news panel:</label>
                                            </td>
                                            <td>
                                                <div class="flex flex-row">
                                                    <input
                                                    type="checkbox"
                                                    id="show_news_panel"
                                                    required
                                                    v-model="configFile.show_news_panel"
                                                    @change="settingsChanged=true"
                                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                                    >
                                                </div>
                                            </td>
                                            </tr>
                                        <tr>
                                            
                                        <td style="min-width: 200px;">
                                            <label for="auto_save" class="text-sm font-bold" style="margin-right: 1rem;">Auto save:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                                <input
                                                type="checkbox"
                                                id="auto_save"
                                                required
                                                v-model="configFile.auto_save"
                                                @change="settingsChanged=true"
                                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                                >
                                            </div>
                                        </td>
                                        </tr>
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="auto_update" class="text-sm font-bold" style="margin-right: 1rem;">Auto update:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="checkbox"
                                            id="auto_update"
                                            required
                                            v-model="configFile.auto_update"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="auto_update" class="text-sm font-bold" style="margin-right: 1rem;">Auto title:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="checkbox"
                                            id="auto_title"
                                            required
                                            v-model="configFile.auto_title"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>                                        
                                    </table>
                                </Card>
                                <Card  title="User" :is_subcard="true" class="pb-2  m-2">
                                    <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="user_name" class="text-sm font-bold" style="margin-right: 1rem;">User name:</label>
                                        </td>
                                        <td style="width: 100%;">
                                            <input
                                            type="text"
                                            id="user_name"
                                            required
                                            v-model="configFile.user_name"
                                            @change="settingsChanged=true"
                                            class="w-full w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                        </td>
                                        </tr>
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="user_description" class="text-sm font-bold" style="margin-right: 1rem;">User description:</label>
                                        </td>
                                        <td style="width: 100%;">
                                            <textarea
                                            id="user_description"
                                            required
                                            v-model="configFile.user_description"
                                            @change="settingsChanged=true"
                                            class="min-h-[500px] w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            ></textarea>
                                        </td>


                                        </tr>
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="use_user_informations_in_discussion" class="text-sm font-bold" style="margin-right: 1rem;">Use user description in discussion:</label>
                                        </td>
                                        <td style="width: 100%;">
                                            <input
                                            type="checkbox"
                                            id="use_user_informations_in_discussion"
                                            required
                                            v-model="configFile.use_user_informations_in_discussion"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                        </td>
                                        </tr>
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="use_model_name_in_discussions" class="text-sm font-bold" style="margin-right: 1rem;">Use model name in discussion:</label>
                                        </td>
                                        <td style="width: 100%;">
                                            <input
                                            type="checkbox"
                                            id="use_model_name_in_discussions"
                                            required
                                            v-model="configFile.use_model_name_in_discussions"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                        </td>
                                        </tr>
                                        
                                        
                                        <!-- Row 3 -->
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="user_avatar" class="text-sm font-bold" style="margin-right: 1rem;">User avatar:</label>
                                        </td>
                                        <td>
                                            <label for="avatar-upload">
                                                <img :src="configFile.user_avatar!=null && configFile.user_avatar!=''?'/user_infos/'+configFile.user_avatar: storeLogo" class="w-50 h-50 rounded-full" style="max-width: 50px; max-height: 50px; cursor: pointer;">
                                            </label>
                                            <input type="file" id="avatar-upload" style="display: none" @change="uploadAvatar">
                                        </td>
                                        <td style="width: 10%;">
                                            <button class="text-2xl hover:text-red-600 duration-75 active:scale-90 " title="Discard title changes"
                                                type="button" @click.stop="resetAvatar()">
                                                <i data-feather="x"></i>
                                            </button>
                                        </td>

                                        </tr>
                                        <!-- Row 4 -->
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="use_user_name_in_discussions" class="text-sm font-bold" style="margin-right: 1rem;">Use User Name in discussions:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="checkbox"
                                            id="use_user_name_in_discussions"
                                            required
                                            v-model="configFile.use_user_name_in_discussions"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>  
                                        <tr>
                                            <td style="min-width: 200px;">
                                                <label for="max_n_predict" class="text-sm font-bold" style="margin-right: 1rem;">Maximum number of output tokens space (forces the model to have more space to speak):</label>
                                            </td>
                                            <td style="width: 100%;">
                                                <input
                                                type="number"
                                                id="max_n_predict"
                                                required
                                                v-model="configFile.max_n_predict"
                                                @change="settingsChanged=true"
                                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                                >
                                            </td>
                                        </tr>                                        
                                        <tr>
                                            <td style="min-width: 200px;">
                                                <label for="max_n_predict" class="text-sm font-bold" style="margin-right: 1rem;">Minimum number of output tokens space (forces the model to have more space to speak):</label>
                                            </td>
                                            <td style="width: 100%;">
                                                <input
                                                type="number"
                                                id="max_n_predict"
                                                required
                                                v-model="configFile.max_n_predict"
                                                @change="settingsChanged=true"
                                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                                >
                                            </td>
                                        </tr>                                        
                                    </table>
                                </Card>  
                                <Card  title="Security settings" :is_subcard="true" class="pb-2  m-2">
                                    <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="turn_on_code_execution" class="text-sm font-bold" style="margin-right: 1rem;">turn on code execution:</label>
                                        </td>
                                        <td style="width: 100%;">
                                            <input
                                            type="checkbox"
                                            id="turn_on_code_execution"
                                            required
                                            v-model="configFile.turn_on_code_execution"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                        </td>
                                        </tr>
                                        
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="turn_on_code_validation" class="text-sm font-bold" style="margin-right: 1rem;">turn on code validation (very recommended for security reasons):</label>
                                        </td>

                                        <td style="width: 100%;">
                                            <input
                                            type="checkbox"
                                            id="turn_on_code_validation"
                                            required
                                            v-model="configFile.turn_on_code_validation"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                        </td>
                                        </tr>                                        
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="turn_on_setting_update_validation" class="text-sm font-bold" style="margin-right: 1rem;">turn on apply settings validation (very recommended for security reasons):</label>
                                        </td>

                                        <td style="width: 100%;">
                                            <input
                                            type="checkbox"
                                            id="turn_on_setting_update_validation"
                                            required
                                            v-model="configFile.turn_on_setting_update_validation"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                        </td>
                                        </tr>                                           
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="turn_on_open_file_validation" class="text-sm font-bold" style="margin-right: 1rem;">turn on open file/folder validation:</label>
                                        </td>
                                        <td style="width: 100%;">
                                            <input
                                            type="checkbox"
                                            id="turn_on_open_file_validation"
                                            required
                                            v-model="configFile.turn_on_open_file_validation"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                        </td>
                                        </tr>  
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="turn_on_send_file_validation" class="text-sm font-bold" style="margin-right: 1rem;">turn on send file validation:</label>
                                        </td>
                                        <td style="width: 100%;">
                                            <input
                                            type="checkbox"
                                            id="turn_on_send_file_validation"
                                            required
                                            v-model="configFile.turn_on_send_file_validation"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                        </td>
                                        </tr>                                                                                
                                    </table>
                                </Card>         
                                <Card title="Knowledge database" :is_subcard="true" class="pb-2  m-2">
                                    <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="activate_skills_lib" class="text-sm font-bold" style="margin-right: 1rem;">Activate Skills library:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="checkbox"
                                            id="activate_skills_lib"
                                            required
                                            v-model="configFile.activate_skills_lib"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="discussion_db_name" class="text-sm font-bold" style="margin-right: 1rem;">Skills library database name:</label>
                                        </td>
                                        <td style="width: 100%;">
                                            <input
                                            type="text"
                                            id="skills_lib_database_name"
                                            required
                                            v-model="configFile.skills_lib_database_name"
                                            @change="settingsChanged=true"
                                            class="w-full w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                            >
                                        </td>
                                        </tr>      
                                    </table>
                                </Card>         
                                <Card title="Internet search" :is_subcard="true" class="pb-2  m-2">
                                    <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="activate_internet_search" class="text-sm font-bold" style="margin-right: 1rem;">Activate internet search:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="checkbox"
                                            id="fun_mode"
                                            required
                                            v-model="configFile.activate_internet_search"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>                                        
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="internet_quick_search" class="text-sm font-bold" style="margin-right: 1rem;">Activate quick search:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="checkbox"
                                            id="internet_quick_search"
                                            required
                                            v-model="configFile.internet_quick_search"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>                                        
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="internet_activate_search_decision" class="text-sm font-bold" style="margin-right: 1rem;">Activate search decision:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="checkbox"
                                            id="internet_activate_search_decision"
                                            required
                                            v-model="configFile.internet_activate_search_decision"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>                                        
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="internet_vectorization_chunk_size" class="text-sm font-bold" style="margin-right: 1rem;">Internet vectorization chunk size:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-col">
                                                <input id="internet_vectorization_chunk_size" v-model="configFile.internet_vectorization_chunk_size"
                                                @change="settingsChanged=true"
                                                type="range" min="0" max="64000" step="1"
                                                class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">

                                                <input v-model="configFile.internet_vectorization_chunk_size"
                                                type="number"
                                                @change="settingsChanged=true"
                                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                                >
                                            </div>
                                        </td>
                                        </tr>              
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="internet_vectorization_overlap_size" class="text-sm font-bold" style="margin-right: 1rem;">Internet vectorization overlap size:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-col">
                                                <input id="internet_vectorization_overlap_size" v-model="configFile.internet_vectorization_overlap_size"
                                                @change="settingsChanged=true"
                                                type="range" min="0" max="1000" step="1"
                                                class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">

                                                <input v-model="configFile.internet_vectorization_overlap_size"
                                                type="number"
                                                @change="settingsChanged=true"
                                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                                >
                                            </div>
                                        </td>
                                        </tr>                                                                                
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="internet_vectorization_nb_chunks" class="text-sm font-bold" style="margin-right: 1rem;">Internet vectorization number of chunks:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-col">
                                                <input id="internet_vectorization_nb_chunks" v-model="configFile.internet_vectorization_nb_chunks"
                                                @change="settingsChanged=true"
                                                type="range" min="0" max="100" step="1"
                                                class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">

                                                <input v-model="configFile.internet_vectorization_nb_chunks"
                                                type="number"
                                                @change="settingsChanged=true"
                                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                                >
                                            </div>
                                        </td>
                                        </tr>         
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="internet_nb_search_pages" class="text-sm font-bold" style="margin-right: 1rem;">Internet number of search pages:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-col">
                                                <input id="internet_nb_search_pages" v-model="configFile.internet_nb_search_pages"
                                                @change="settingsChanged=true"
                                                type="range" min="1" max="100" step="1"
                                                class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">

                                                <input v-model="configFile.internet_nb_search_pages"
                                                type="number"
                                                @change="settingsChanged=true"
                                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                                >
                                            </div>
                                        </td>
                                        </tr>                                                                            
                                    </table>
                                </Card>
                                <Card title="Latex" :is_subcard="true" class="pb-2  m-2">
                                    <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="pdf_latex_path" class="text-sm font-bold" style="margin-right: 1rem;">PDF LaTeX path:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="text"
                                            id="pdf_latex_path"
                                            required
                                            v-model="configFile.pdf_latex_path"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>                                        
                                    </table>
                                </Card>
                                <Card title="Boost" :is_subcard="true" class="pb-2  m-2">
                                    <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="positive_boost" class="text-sm font-bold" style="margin-right: 1rem;">Positive Boost:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="text"
                                            id="positive_boost"
                                            required
                                            v-model="configFile.positive_boost"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>                                        
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="negative_boost" class="text-sm font-bold" style="margin-right: 1rem;">Negative Boost:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="text"
                                            id="negative_boost"
                                            required
                                            v-model="configFile.negative_boost"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>   
                                        <tr>
                                        <td style="min-width: 200px;">
                                            <label for="fun_mode" class="text-sm font-bold" style="margin-right: 1rem;">Fun mode:</label>
                                        </td>
                                        <td>
                                            <div class="flex flex-row">
                                            <input
                                            type="checkbox"
                                            id="fun_mode"
                                            required
                                            v-model="configFile.fun_mode"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                            >
                                            </div>
                                        </td>
                                        </tr>                                                                                                                     
                                    </table>
                                </Card>
                    </div>
                </div>
            </div>

            <!-- Data settings-->

            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="data_conf_collapsed = !data_conf_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <div v-show="data_conf_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!data_conf_collapsed" ><i data-feather='chevron-down'></i></div>

                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Data management settings</h3>
                    </button>
                </div>
                <div :class="{ 'hidden': data_conf_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                
                    <Card title="Data Vectorization" :is_subcard="true" class="pb-2  m-2">
                        <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                                        
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_save_db" class="text-sm font-bold" style="margin-right: 1rem;">Save vectorized database:</label>
                            </td>
                            <td>
                                <div class="flex flex-row">
                                <input
                                type="checkbox"
                                id="data_vectorization_save_db"
                                required
                                v-model="configFile.data_vectorization_save_db"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                </div>
                            </td>
                            </tr>                                  
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_visualize_on_vectorization" class="text-sm font-bold" style="margin-right: 1rem;">show vectorized data:</label>
                            </td>
                            <td>
                                <div class="flex flex-row">
                                <input
                                type="checkbox"
                                id="data_vectorization_visualize_on_vectorization"
                                required
                                v-model="configFile.data_vectorization_visualize_on_vectorization"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                </div>
                            </td>
                            </tr>                                                                                                                         
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_build_keys_words" class="text-sm font-bold" style="margin-right: 1rem;">Reformulate prompt before querying database (advised):</label>
                            </td>
                            <td>
                                <div class="flex flex-row">
                                <input
                                type="checkbox"
                                id="data_vectorization_build_keys_words"
                                required
                                v-model="configFile.data_vectorization_build_keys_words"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                </div>
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_force_first_chunk" class="text-sm font-bold" style="margin-right: 1rem;">Force adding the first chunk of the file to the context:</label>
                            </td>
                            <td>
                                <div class="flex flex-row">
                                <input
                                type="checkbox"
                                id="data_vectorization_force_first_chunk"
                                required
                                v-model="configFile.data_vectorization_force_first_chunk"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                </div>
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_put_chunk_informations_into_context" class="text-sm font-bold" style="margin-right: 1rem;">Put Chunk Information Into Context:</label>
                            </td>
                            <td>
                                <div class="flex flex-row">
                                <input
                                type="checkbox"
                                id="data_vectorization_put_chunk_informations_into_context"
                                required
                                v-model="configFile.data_vectorization_put_chunk_informations_into_context"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                </div>
                            </td>
                            </tr>
                            
                                                       
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_method" class="text-sm font-bold" style="margin-right: 1rem;">Data vectorization method:</label>
                            </td>
                            <td>
                                <select
                                id="data_vectorization_method"
                                required
                                v-model="configFile.data_vectorization_method"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                    <option value="tfidf_vectorizer">tfidf Vectorizer</option>
                                    <option value="bm25_vectorizer">bm25 Vectorizer</option>
                                    <option value="model_embedding">Model Embedding</option>
                                    <option value="sentense_transformer">Sentense Transformer</option>
                                </select>
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_sentense_transformer_model" class="text-sm font-bold" style="margin-right: 1rem;">Data vectorization model (for Sentense Transformer):</label>
                            </td>
                            <td style="width: 100%;">
                                <input
                                type="text"
                                id="data_vectorization_sentense_transformer_model"
                                required
                                v-model="configFile.data_vectorization_sentense_transformer_model"
                                @change="settingsChanged=true"
                                class="w-full w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                >
                            </td>
                            </tr>      
                            
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_visualization_method" class="text-sm font-bold" style="margin-right: 1rem;">Data visualization method:</label>
                            </td>
                            <td>
                                <select
                                id="data_visualization_method"
                                required
                                v-model="configFile.data_visualization_method"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                    <option value="PCA">PCA</option>
                                    <option value="TSNE">TSNE</option>
                                </select>
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_save_db" class="text-sm font-bold" style="margin-right: 1rem;">Save the new files to the database (The database wil always grow and continue to be the same over many sessions):</label>
                            </td>
                            <td>
                                <div class="flex flex-row">
                                <input
                                type="checkbox"
                                id="data_vectorization_save_db"
                                required
                                v-model="configFile.data_vectorization_save_db"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                </div>
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_chunk_size" class="text-sm font-bold" style="margin-right: 1rem;">Data vectorization chunk size(tokens):</label>
                            </td>
                            <td>
                                <input id="data_vectorization_chunk_size" v-model="configFile.data_vectorization_chunk_size"
                                @change="settingsChanged=true"
                                type="range" min="0" max="64000" step="1"
                                class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">

                                <input v-model="configFile.data_vectorization_chunk_size"
                                type="number"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                            </td>
                            </tr>                                          
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_overlap_size" class="text-sm font-bold" style="margin-right: 1rem;">Data vectorization overlap size(tokens):</label>
                            </td>
                            <td>
                                <input id="data_vectorization_overlap_size" v-model="configFile.data_vectorization_overlap_size"
                                @change="settingsChanged=true"
                                type="range" min="0" max="64000" step="1"
                                class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <input v-model="configFile.data_vectorization_overlap_size"
                                type="number"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                            </td>
                            </tr>                                          
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="data_vectorization_overlap_size" class="text-sm font-bold" style="margin-right: 1rem;">Number of chunks to use for each message:</label>
                            </td>
                            <td>
                                <input id="data_vectorization_nb_chunks" v-model="configFile.data_vectorization_nb_chunks"
                                @change="settingsChanged=true"
                                type="range" min="0" max="1000" step="1"
                                class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <input v-model="configFile.data_vectorization_nb_chunks"
                                type="number"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                            </td>
                            </tr>                                           
                                                                            
                        </table>
                    </Card>
                
                
                
                </div>
            </div>


            <!-- Servers CONFIGS -->
            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="servers_conf_collapsed = !servers_conf_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <div v-show="servers_conf_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!servers_conf_collapsed" ><i data-feather='chevron-down'></i></div>

                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Services Zoo</h3>
                    </button>
                </div>


                                
                <div :class="{ 'hidden': servers_conf_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <Card title="Default services selection" :is_subcard="true" class="pb-2  m-2">
                        <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="active_tts_service" class="text-sm font-bold" style="margin-right: 1rem;" title="Default Text to speach engine">Active TTS Service:</label>
                            </td>
                            <td style="width: 100%;">
                                <select
                                id="active_tts_service"
                                required
                                v-model="configFile.active_tts_service"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                    <option value="None">None</option>
                                    <option value="browser">Use Browser TTS (doesn't work in realtime mode)</option>
                                    <option value="xtts">XTTS</option>
                                    <option value="openai_tts">Open AI TTS</option>
                                </select>
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="active_stt_service" class="text-sm font-bold" style="margin-right: 1rem;" title="Default Speach to Text engine">Active STT Service:</label>
                            </td>
                            <td style="width: 100%;">
                                <select
                                id="active_stt_service"
                                required
                                v-model="configFile.active_stt_service"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                    <option value="None">None</option>
                                    <option value="whisper">Whisper</option>
                                    <option value="openai_whisper">Open AI Whisper</option>
                                </select>
                            </td>
                            </tr>
                            <tr></tr>                            
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="active_tti_service" class="text-sm font-bold" style="margin-right: 1rem;" title="Default Text to image engine">Active TTI Service:</label>
                            </td>
                            <td style="width: 100%;">
                                <select
                                id="active_tti_service"
                                required
                                v-model="configFile.active_tti_service"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                    <option value="None">None</option>
                                    <option value="autosd">AUTO1111's SD</option>
                                    <option value="dall-e">Open AI DALL-E</option>
                                    <option value="midjourney">Midjourney</option>
                                    <option value="comfyui">Comfyui</option>
                                    <option value="fooocus">Fooocus</option>
                                </select>
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="active_ttm_service" class="text-sm font-bold" style="margin-right: 1rem;" title="Default Text to Music engine">Active TTM Service:</label>
                            </td>
                            <td style="width: 100%;">
                                <select
                                id="active_ttm_service"
                                required
                                v-model="configFile.active_ttm_service"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                    <option value="None">None</option>
                                    <option value="musicgen">Music Gen</option>
                                </select>
                            </td>
                            </tr>

                        </table>                    
                    </Card>
                    <Card title="Audio devices settings" :is_subcard="true" class="pb-2  m-2">
                        <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="stt_input_device" class="text-sm font-bold" style="margin-right: 1rem;" title="Input device">Audio Input device:</label>
                            </td>
                            <td style="width: 100%;">
                                <select
                                id="stt_input_device"
                                required
                                v-model="configFile.stt_input_device"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                    <option v-for="snd_input_device in snd_input_devices" :key="snd_input_device" :value="snd_input_device">
                                        {{ snd_input_device }}
                                    </option>                                
                                </select>
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="tts_output_device" class="text-sm font-bold" style="margin-right: 1rem;" title="Input device">Audio Output device:</label>
                            </td>
                            <td style="width: 100%;">
                                <select
                                id="tts_output_device"
                                required
                                v-model="configFile.tts_output_device"
                                @change="settingsChanged=true"
                                class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                >
                                    <option v-for="tts_output_device in tts_output_devices" :key="tts_output_device" :value="tts_output_device">
                                        {{ tts_output_device }}
                                    </option>                                
                                </select>
                            </td>
                            </tr>

                        </table>                    
                    </Card>
                    <Card title="Lollms service" :is_shrunk="true" :is_subcard="true" class="pb-2  m-2">
                        <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="host" class="text-sm font-bold" style="margin-right: 1rem;">Host:</label>
                            </td>
                            <td style="width: 100%;">
                                <input
                                type="text"
                                id="host"
                                required
                                v-model="configFile.host"
                                @change="settingsChanged=true"
                                class="w-full w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                >
                            </td>
                            </tr>                                        
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="lollms_access_keys" class="text-sm font-bold" style="margin-right: 1rem;">Access keys (coma separated, if empty, anyone can use the server without authentication):</label>
                            </td>
                            <td style="width: 100%;">
                                <input
                                type="text"
                                id="lollms_access_keys"
                                required
                                v-model="configFile.lollms_access_keys"
                                @change="settingsChanged=true"
                                class="w-full w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                >
                            </td>
                            </tr>                                        
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="discussion_db_name" class="text-sm font-bold" style="margin-right: 1rem;">Port:</label>
                            </td>
                            <td style="width: 100%;">
                                <input
                                type="number"
                                step="1"
                                id="port"
                                required
                                v-model="configFile.port"
                                @change="settingsChanged=true"
                                class="w-full w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                >
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="discussion_db_name" class="text-sm font-bold" style="margin-right: 1rem;">Activate headless server mode (deactivates all code exectuion to protect the PC from attacks):</label>
                            </td>
                            <td style="width: 100%;">
                                <input
                                type="checkbox"
                                id="headless_server_mode"
                                required
                                v-model="configFile.headless_server_mode"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                >
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="activate_lollms_server" class="text-sm font-bold" style="margin-right: 1rem;">Activate lollms server:</label>
                            </td>
                            <td style="width: 100%;">
                                <input
                                type="checkbox"
                                id="activate_lollms_server"
                                required
                                v-model="configFile.activate_lollms_server"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                >
                            </td>
                            </tr>      
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="activate_ollama_emulator" class="text-sm font-bold" style="margin-right: 1rem;">Activate ollama server emulator:</label>
                            </td>
                            <td style="width: 100%;">
                                <input
                                type="checkbox"
                                id="activate_ollama_emulator"
                                required
                                v-model="configFile.activate_ollama_emulator"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                >
                            </td>
                            </tr>
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="activate_openai_emulator" class="text-sm font-bold" style="margin-right: 1rem;">Activate openai server emulator:</label>
                            </td>
                            <td style="width: 100%;">
                                <input
                                type="checkbox"
                                id="activate_openai_emulator"
                                required
                                v-model="configFile.activate_openai_emulator"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                >
                            </td>
                            </tr>                                  
                            <tr>
                            <td style="min-width: 200px;">
                                <label for="activate_mistralai_emulator" class="text-sm font-bold" style="margin-right: 1rem;">Activate mistral ai server emulator:</label>
                            </td>
                            <td style="width: 100%;">
                                <input
                                type="checkbox"
                                id="activate_mistralai_emulator"
                                required
                                v-model="configFile.activate_mistralai_emulator"
                                @change="settingsChanged=true"
                                class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600  dark:bg-gray-600"
                                >
                            </td>
                            </tr>   
                        </table>               
                    </Card>                    
                    <Card title="TTS services" :is_shrunk="true" :is_subcard="true" class="pb-2  m-2">
                        <Card title="Browser Audio" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="activate_audio_infos" class="text-sm font-bold" style="margin-right: 1rem;">Activate audio infos:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="activate_audio_infos"
                                    required
                                    v-model="configFile.activate_audio_infos"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr>

                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="audio_auto_send_input" class="text-sm font-bold" style="margin-right: 1rem;">Send audio input automatically:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="audio_auto_send_input"
                                    required
                                    v-model="configFile.audio_auto_send_input"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr>
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
                                    <label for="audio_silenceTimer" class="text-sm font-bold" style="margin-right: 1rem;">audio in silence timer (ms):</label>
                                </td>
                                <td>
                                    <input id="audio_silenceTimer" v-model="configFile.audio_silenceTimer"
                                    @change="settingsChanged=true"
                                    type="range" min="0" max="10000" step="1"
                                    class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    <input v-model="configFile.audio_silenceTimer"
                                    @change="settingsChanged=true"
                                    class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                </td>
                                </tr>                                        
                                
                                <tr>
                                    <td style="min-width: 200px;">
                                    <label for="audio_in_language" class="text-sm font-bold" style="margin-right: 1rem;">Input Audio Language:</label>
                                    </td>
                                    <td>
                                    <!-- Select element for choosing the input audio language -->
                                    <select
                                        id="audio_in_language"
                                        v-model="configFile.audio_in_language"
                                        @change="settingsChanged=true"
                                        class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                        <!-- Options with language codes and corresponding language names -->
                                        <option v-for="language in audioLanguages" :key="language.code" :value="language.code">
                                        {{ language.name }}
                                        </option>
                                    </select>
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
                                    <label for="xtts_enable" class="text-sm font-bold" style="margin-right: 1rem;">Enable voice service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="xtts_enable"
                                    required
                                    v-model="configFile.xtts_enable"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="install_xtts_service" class="text-sm font-bold" style="margin-right: 1rem;">xTTS service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallAudioService">install xtts service</button>
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="startAudioService">start xtts service</button>
                                    <a class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" :href="this.$store.state.config.xtts_base_url+'/docs'" target="_blank">show xtts service entries</a>
                                    <a class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" href="https://github.com/ParisNeo/xtts-api-server/blob/main/LICENSE" target="_blank">licence</a>
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_base_url" class="text-sm font-bold" style="margin-right: 1rem;">xtts base url:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="text"
                                    id="xtts_base_url"
                                    required
                                    v-model="configFile.xtts_base_url"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                </tr> 
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_current_language" class="text-sm font-bold" style="margin-right: 1rem;">Current language:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <select v-model="xtts_current_language" @change="settingsChanged=true" :disabled="!xtts_enable">
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
                                        <select v-model="xtts_current_voice" @change="settingsChanged=true" :disabled="!xtts_enable">
                                        <option v-for="voice in voices" :key="voice" :value="voice">
                                            {{ voice }}
                                        </option>
                                        </select>
                                    </div>
                                </td>
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_use_deepspeed" class="text-sm font-bold" style="margin-right: 1rem;">Enable deepspeed:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="checkbox"
                                            id="xtts_use_deepspeed"
                                            required
                                            v-model="configFile.xtts_use_deepspeed"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            :disabled="!xtts_enable"
                                        >
                                    </div>
                                </td>
                                </tr>
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_use_streaming_mode" class="text-sm font-bold" style="margin-right: 1rem;">Enable streaming mode:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                        <input
                                            type="checkbox"
                                            id="xtts_use_streaming_mode"
                                            required
                                            v-model="configFile.xtts_use_streaming_mode"
                                            @change="settingsChanged=true"
                                            class="mt-1 px-2 py-1 border border-gray-300 rounded dark:bg-gray-600"
                                            :disabled="!xtts_enable"
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
                                            :disabled="!xtts_enable"
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
                    <Card title="STT services" :is_shrunk="true" :is_subcard="true" class="pb-2  m-2">
                        <Card title="Whisper audio transcription" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="whisper_activate" class="text-sm font-bold" style="margin-right: 1rem;">Activate Whisper at startup:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="whisper_activate"
                                    required
                                    v-model="configFile.whisper_activate"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>                                        </tr>
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="whisper_model" class="text-sm font-bold" style="margin-right: 1rem;">Whisper model:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <select
                                        id="whisper_model"
                                        v-model="configFile.whisper_model"
                                        @change="settingsChanged=true"
                                        class="w-full mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                        <!-- Options with language codes and corresponding language names -->
                                        <option v-for="whispermodel in whisperModels" :key="whispermodel" :value="whispermodel">
                                        {{ whispermodel }}
                                        </option>
                                    </select>
                                    </div>
                                </td>
                                </tr>                                        

                            </table>
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
                    <Card title="Misc" :is_shrunk="true" :is_subcard="true" class="pb-2  m-2">
                        <Card title="Motion Ctrl service" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="enable_sd_service" class="text-sm font-bold" style="margin-right: 1rem;">Enable Motion Ctrl service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <input
                                    type="checkbox"
                                    id="enable_motion_ctrl_service"
                                    required
                                    v-model="configFile.enable_motion_ctrl_service"
                                    @change="settingsChanged=true"
                                    class="mt-1 px-2 py-1 border border-gray-300 rounded  dark:bg-gray-600"
                                    >
                                    </div>
                                </td>
                                <td>
                                    <div class="hover:text-secondary duration-75 active:scale-90 peer-checked:text-primary" @click="this.$store.state.messageBox.showMessage('Activates Motion ctrl service. The service will be automatically loaded at startup alowing you to use the motoin control endpoint to generate videos')">
                                        <i data-feather="help-circle" class="w-5 h-5 "></i>
                                    </div>
                                </td>                            
                                </tr>                                        
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="install_sd_service" class="text-sm font-bold" style="margin-right: 1rem;">Install Motion Ctrl service:</label>
                                </td>
                                <td>
                                    <div class="flex flex-row">
                                    <button class="hover:text-primary bg-green-200 rounded-lg p-4 m-4 w-full text-center items-center" @click="reinstallMotionCtrlService">install Motion Ctrl service</button>
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

                        <Card title="Elastic search Service (under construction)" :is_subcard="true" class="pb-2  m-2">
                            <table class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                <tr>
                                <td style="min-width: 200px;">
                                    <label for="xtts_enable" class="text-sm font-bold" style="margin-right: 1rem;">Enable elastic search service:</label>
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
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="bzc_collapsed = !bzc_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <div v-show="bzc_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!bzc_collapsed" ><i data-feather='chevron-down'></i></div>

                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Binding zoo</h3>
                        <div v-if="!configFile.binding_name" class="text-base text-red-600 flex gap-3 items-center mr-2">
                            <i data-feather="alert-triangle" class="flex-shrink-0"></i>
                            No binding selected!
                        </div>

                        <div v-if="configFile.binding_name" class="mr-2">|</div>

                        <div v-if="configFile.binding_name"
                            class=" text-base font-semibold cursor-pointer select-none items-center">

                            <div class="flex gap-1 items-center">
                                <img :src="imgBinding" class="w-8 h-8 rounded-full object-fill text-blue-700">
                                <h3 class="font-bold font-large text-lg line-clamp-1">
                                    <!-- {{ configFile.binding_name }} -->
                                    {{ binding_name }}
                                </h3>
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
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="modelsZooToggleCollapse()"
                        class="text-2xl hover:text-primary  p-2 -m-2 w-full text-left flex items-center">
                        <div v-show="mzc_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!mzc_collapsed" ><i data-feather='chevron-down'></i></div>

                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Models zoo</h3>
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
                                    <h3 class="font-bold font-large text-lg line-clamp-1">
                                        {{ configFile.model_name }}
                                    </h3>
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
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3 items-center">
                    <button @click.stop="pzc_collapsed = !pzc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 text-left w-full  flex items-center">
                        <div v-show="pzc_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!pzc_collapsed" ><i data-feather='chevron-down'></i></div>
                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Personalities zoo</h3>


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
            <!-- EXTENSIONS ZOO -->
            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3 items-center">
                    <button @click.stop="ezc_collapsed = !ezc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 text-left w-full  flex items-center">
                    <div v-show="ezc_collapsed" ><i data-feather='chevron-right'></i></div>
                    <div v-show="!ezc_collapsed" ><i data-feather='chevron-down'></i></div>
                    <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                        Extensions zoo</h3>
                    <div v-if="configFile.extensions" class="mr-2">|</div>
                    <div v-if="configFile.extensions"
                        class=" text-base font-semibold cursor-pointer select-none items-center flex flex-row">
                            <!-- LIST -->
                            <div class="flex -space-x-4 items-center " v-if="mountedExtensions.length > 0">
                                <!-- ITEM -->
                                <div class="relative  hover:-translate-y-2 duration-300 hover:z-10 shrink-0 "
                                    v-for="(item, index) in mountedExtensions" :key="index + '-' + item.name"
                                    ref="mountedExtensions">
                                    <div class="group items-center flex flex-row">
                                        <button>
                                            <img :src="bUrl + item.avatar" @error="extensionImgPlacehodler"
                                                class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 group-hover:border-secondary "
                                                :class="'border-transparent z-0'"
                                                :title="item.name">
                                        </button>
                                        <button @click.stop="unmountExtension (item)">
                                            <span
                                                class="hidden group-hover:block top-0 left-7 absolute active:scale-90 bg-bg-light dark:bg-bg-dark rounded-full border-2  border-transparent"
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
                    </button>
                </div>
                <div :class="{ 'hidden': ezc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <!-- SEARCH BAR -->
                    <div class="mx-2 mb-4">
                            <label for="personality-search"
                                class="mb-2 text-sm font-medium text-gray-900 sr-only dark:text-white">Search</label>
                            <div class="relative">
                                <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                                    <div v-if="searchExtensionInProgress">
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
                                    <div v-if="!searchExtensionInProgress">
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
                                    placeholder="Search extension..." required v-model="searchExtension"
                                    @keyup.stop="searchExtension_func">
                                <button v-if="searchExtension" @click.stop="searchExtension = ''" type="button"
                                    class="text-white absolute right-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                                    Clear search</button>

                                <!-- @input="filterPersonalities()" -->

                            </div>

                    </div>
                    <div class="mx-2 mb-4" v-if="!searchExtension">
                        <label for="extCat" class="block  mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Extensions Category: ({{ extCatgArr.length }})
                        </label>
                        <select id="extCat" @change="update_extension_category($event.target.value, refresh)"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                            <option v-for="(item, index) in extCatgArr" :key="index"
                                :selected="item == this.extension_category">{{
                                    item
                                }}

                            </option>

                        </select>
                    </div>
                    <div>
                        <div v-if="extensionsFiltered.length > 0" class="mb-2">
                            <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                {{ searchExtension ? 'Search results' : 'Personalities' }}: ({{
                                    extensionsFiltered.length
                                }})
                            </label>
                            <div class="overflow-y-auto no-scrollbar p-2 pb-0 grid lg:grid-cols-3 md:grid-cols-2 gap-4"
                                :class="ezl_collapsed ? '' : 'max-h-96'">
                                    <ExtensionEntry ref="extensionsZoo" v-for="(ext, index) in extensionsFiltered"
                                        :key="'index-' + index + '-' + ext.name" 
                                        :extension="ext"
                                        :select_language="true"
                                        :full_path="ext.full_path"
                                        :on-mount="mountExtension" 
                                        :on-un-mount="unmountExtension"  
                                        :on-remount="remountExtension"
                                        :on-reinstall="onExtensionReinstall"
                                        :on-settings="onSettingsExtension" />
                            </div>
                        </div>
                    </div>

                    <!-- EXPAND / COLLAPSE BUTTON -->
                    <button v-if="ezc_collapsed"
                        class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                        title="Collapse" type="button" @click="ezl_collapsed = !ezl_collapsed">
                        <i data-feather="chevron-up"></i>
                    </button>
                    <button v-else
                        class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                        title="Expand" type="button" @click="ezl_collapsed = !ezl_collapsed">
                        <i data-feather="chevron-down"></i>
                    </button>
                </div>

            </div>
            <!-- EXTENSIONS ZOO -->
            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3 items-center">
                    <button @click.stop="mep_collapsed = !mep_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 text-left w-full  flex items-center">
                    <div v-show="mep_collapsed" ><i data-feather='chevron-right'></i></div>
                    <div v-show="!mep_collapsed" ><i data-feather='chevron-down'></i></div>
                    <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                        Mounted Extensions Priority</h3>
                    </button>
                </div>
                <div :class="{ 'hidden': mep_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                </div>
            </div>
            <!-- MODEL CONFIGURATION -->
            <div
                class="flex flex-col mb-2 p-3 rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row">
                    <button @click.stop="mc_collapsed = !mc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 w-full text-left flex items-center">
                        <div v-show="mc_collapsed" ><i data-feather='chevron-right'></i></div>
                        <div v-show="!mc_collapsed" ><i data-feather='chevron-down'></i></div>
                        <h3 class="text-lg font-semibold cursor-pointer select-none">
                            Model Configuration</h3>
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
import { nextTick, TransitionGroup } from 'vue'
import ModelEntry from '@/components/ModelEntry.vue';
import PersonalityViewer from '@/components/PersonalityViewer.vue';
import PersonalityEntry from "@/components/PersonalityEntry.vue";
import BindingEntry from "../components/BindingEntry.vue";
import socket from '@/services/websocket.js'
import defaultModelImgPlaceholder from "../assets/default_model.png"

import defaultPersonalityImgPlaceholder from "../assets/logo.png"
import defaultExtensionImgPlaceholder from "../assets/extension.png"
import defaultImgPlaceholder from "../assets/default_model.png"

import AddModelDialog from "@/components/AddModelDialog.vue";

import ChoiceDialog from "@/components/ChoiceDialog.vue";
import Card from "@/components/Card.vue"
import RadioOptions from '../components/RadioOptions.vue';
import ExtensionEntry from "@/components/ExtensionEntry.vue"

import storeLogo from '@/assets/logo.png'


import {refreshHardwareUsage} from "../main"
import SVGGPU from '@/assets/gpu.svg';


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
        RadioOptions,
        ExtensionEntry
    },
    data() {

        return {
            posts_headers : {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            defaultModelImgPlaceholder:defaultModelImgPlaceholder,
            snd_input_devices: [],
            snd_output_devices: [],
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
            extension_category:"bound_extensions",
            personality_category:null,
            // install custom model
            addModelDialogVisibility: false,
            modelPath: '',
            // Zoo stuff
            personalitiesFiltered: [],
            modelsFiltered: [],
            extensionsFiltered: [],
            // Accordeon stuff 
            collapsedArr: [],
            all_collapsed: true,
            data_conf_collapsed: true,
            servers_conf_collapsed: true, // Servers configuration
            minconf_collapsed: true, // Main configuration 
            bec_collapsed: true,
            sort_type : 0, // 0: by date, 1: by rank, 2: by name, 3: by maker, 4: by quantizer
            is_loading_zoo:false, // Is loading models zoo
            mzc_collapsed: true, // models zoo
            mzdc_collapsed: true, // models zoo download
            pzc_collapsed: true, // personalities zoo
            ezc_collapsed: true, // extension zoo
            mep_collapsed: true, // mounted extensions priority
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
            searchExtension: "",
            searchModel: "",
            searchPersonalityTimer: {},
            searchPersonalityTimerInterval: 1500, // timeout in ms
            searchModelTimerInterval: 1500, // timeout in ms
            searchPersonalityInProgress: false,
            searchExtensionInProgress: false,
            searchModelInProgress: false,
            addModel: {},
            modelDownlaodInProgress: false,
            uploadData: [],

        }
    },
    async created() {
        socket.on('loading_text',this.on_loading_text);
        this.updateHasUpdates();
        //await socket.on('install_progress', this.progressListener);
        //refreshHardwareUsage()
    }, 
    methods: {
        install_model(){

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
            axios.get('install_comfyui')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        upgradeComfyUIService(){
            axios.get('upgrade_comfyui')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        startComfyUIService(){
            axios.get('start_comfyui')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },        
        showComfyui(){
            axios.get('show_comfyui')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });
        },
        reinstallMotionCtrlService(){
            axios.get('install_motion_ctrl')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });
        },
        reinstallvLLMService(){
            axios.get('install_vllm')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        startvLLMService(){
            axios.get('start_vllm')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        startollamaService(){
            axios.get('start_ollama')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        reinstallPetalsService(){
            axios.get('install_petals')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        reinstallOLLAMAService(){
        axios.get('install_ollama')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });

        },
        reinstallAudioService(){
            axios.post('install_xtts',{client_id:this.$store.state.client_id})
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });
        },
        startAudioService(){
            axios.get('start_xtts')
            .then(response => {

            })
            .catch(error => {
            console.error(error);
            });
        },
        reinstallElasticSearchService(){
            axios.get('install_vllm')
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

            try{
                this.extCatgArr = await this.api_get_req("list_extensions_categories")
                this.extension_category = this.extCatgArr[0]
                console.log(this.extCatgArr)
            }
            catch{
                console.log("Couldn't list catergories")
                this.extCatgArr = []
            }
            try{
                console.log("Loading extension category content")
                this.extArr = await this.api_get_req("list_extensions?category="+this.extension_category)
                console.log(this.extArr)
            }
            catch{
                console.log("Couldn't list extensions")
                this.extCatgArr = []
            }


            
            //await this.getPersonalitiesArr()
            this.personality_category = this.configFile.personality_category
            this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.configFile.personality_category)
            // this.personalitiesFiltered.sort()
            //mountedPersArr
            this.modelsFiltered = []
            this.extension_category = this.configFile.extension_category
            this.extensionsFiltered = this.$store.state.extensionsZoo.filter((item) => item.category === this.configFile.extension_category )
           
            
            this.updateModelsZoo();

            this.isLoading = false
            this.isMounted = true
            this.extension_category = this.configFile.extension_category
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
            this.minconf_collapsed = val
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
        fetchExtensions(){
            this.api_get_req("list_extensions_categories").then(response => {
                this.extCatgArr = response
                this.extCatgArr.sort()
            })

            this.api_get_req("list_extensions").then(response => {
                this.extArr = response
                this.extArr.sort()
                console.log(`Listed extensions:\n${response}`)
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
        async handleOpenFolder(pers){
            await axios.post("/open_personality_folder",{client_id:this.$store.state.client_id, personality_folder: pers.personality.folder})
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
                    if(self.selected_variant!=undefined){
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
                axios.post('/install_binding', { name: binding_object.binding.folder }).then((res) => {

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
            axios.post('/unInstall_binding', { name: binding_object.binding.folder }).then((res) => {
                
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
            axios.post('/reinstall_binding', { name: binding_object.binding.folder }).then((res) => {

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
        onSettingsExtension(extensionEntry){
            try {
                this.isLoading = true
                axios.get('/get_extension_settings',{name:extensionEntry.name}).then(res => {
                    this.isLoading = false
                    if (res) {

                        console.log('ext sett', res)
                        if (res.data && Object.keys(res.data).length > 0) {

                            this.$store.state.universalForm.showForm(res.data, "Extension settings - " + extensionEntry.extension.name, "Save changes", "Cancel").then(res => {

                                // send new data
                                try {
                                    axios.post('/set_extension_settings', {"name":extensionEntry.name,"config":res}).then(response => {

                                            if (response && response.data) {
                                                console.log('extension set with new settings', response.data)
                                                this.$store.state.toast.showToast("Extension settings updated successfully!", 4, true)

                                            } else {
                                                this.$store.state.toast.showToast("Did not get Extension settings responses.\n" + response, 4, false)
                                                this.isLoading = false
                                            }


                                        })
                                } catch (error) {
                                    this.$store.state.toast.showToast("Did not get Extension settings responses.\n Endpoint error: " + error.message, 4, false)
                                    this.isLoading = false
                                }

                            })
                        } else {
                            this.$store.state.toast.showToast("Extension has no settings", 4, false)
                            this.isLoading = false
                        }

                    }
                })

            } catch (error) {
                this.isLoading = false
                this.$store.state.toast.showToast("Could not open personality settings. Endpoint error: " + error.message, 4, false)
            }

        },
        onSettingsBinding(bindingEntry) {
            try {
                this.isLoading = true
                axios.get('/get_active_binding_settings').then(res => {
                    console.log(res)
                    this.isLoading = false
                    if (res) {

                        console.log('binding sett', res)

                        if (res.data && Object.keys(res.data).length > 0) {

                            // open form

                            this.$store.state.universalForm.showForm(res.data, "Binding settings - " + bindingEntry.binding.name, "Save changes", "Cancel").then(res => {
                                // send new data
                                try {
                                    axios.post('/set_active_binding_settings',
                                        res, {headers: this.posts_headers}).then(response => {
                                            if (response && response.data) {
                                                console.log('binding set with new settings', response.data)
                                                this.$store.state.toast.showToast("Binding settings updated successfully!", 4, true)
                                                axios.get('/update_binding_settings').then((res) => {
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
        update_extension_category(cat, next){
            this.extension_category = cat
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
                    this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.personality_category)
                    this.personalitiesFiltered.sort()

                })

                this.api_get_req("list_extensions_categories").then((cats)=>{
                    console.log("cats",cats)
                    this.extCatgArr = cats
                    console.log("this.$store.state.extensionsZoo",this.$store.state.extensionsZoo)
                    console.log("this.extension_category", this.extension_category)
                    this.extensionsFiltered = this.$store.state.extensionsZoo.filter((item) => item.category === this.extension_category)
                    this.extensionsFiltered.sort()
                    console.log("this.extensionsFiltered", this.extensionsFiltered)

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
            this.personalities = []
            const dictionary = await this.api_get_req("get_all_personalities")
            const config = this.$store.state.config
            //console.log('asdas',config)
            // console.log("all_personalities")
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


                if (this.personalities.length == 0) {
                    this.personalities = modPersArr
                } else {
                    this.personalities = this.personalities.concat(modPersArr)
                }
            }

            this.personalities.sort((a, b) => a.name.localeCompare(b.name))
            this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.configFile.personality_category)
            this.personalitiesFiltered.sort()
            console.log('per filtered', this.personalitiesFiltered)
            this.isLoading = false

        },
        async getExtensionsArr() {
            this.isLoading = true
            this.extensions = []
            const dictionary = await this.api_get_req("get_all_extensions")
            const config = this.$store.state.config
            //console.log('asdas',config)
            // console.log("all_extensions")
            // console.log(dictionary)
            const catkeys = Object.keys(dictionary); // returns categories folder names
            for (let j = 0; j < catkeys.length; j++) {
                const catkey = catkeys[j];
                const extensionsArray = dictionary[catkey];
                const modPersArr = extensionsArray.map((item) => {

                    const isMounted = config.extensions.includes(catkey + '/' + item.folder)
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


                if (this.extensions.length == 0) {
                    this.extensions = modPersArr
                } else {
                    this.extensions = this.extensions.concat(modPersArr)
                }
            }

            this.extensions.sort((a, b) => a.name.localeCompare(b.name))
            this.extensions = this.extensions.filter((item) => item.category === this.configFile.personality_category)
            this.extensions.sort()
            console.log('per filtered', this.extensionsFiltered)
            this.isLoading = false

        },        
        async filterPersonalities() {
            if (!this.searchPersonality) {
                this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.configFile.personality_category )
                this.personalitiesFiltered.sort()
                this.searchPersonalityInProgress = false
                return
            }
            const searchTerm = this.searchPersonality.toLowerCase()
            const seachedPersonalities = this.personalities.filter((item) => {

                if (item.name && item.name.toLowerCase().includes(searchTerm) || item.description && item.description.toLowerCase().includes(searchTerm) || item.full_path && item.full_path.toLowerCase().includes(searchTerm)) {
                    return item
                }

            })



            if (seachedPersonalities.length > 0) {
                this.personalitiesFiltered = seachedPersonalities.sort()
            } else {
                this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.configFile.personality_category)
                this.personalitiesFiltered.sort()
            }
            this.searchPersonalityInProgress = false

        },
        async filterExtensions() {
            if (!this.searchExtension) {
                this.personalitiesFiltered = this.extensions.filter((item) => item.category === this.extension_category )
                this.personalitiesFiltered.sort()
                this.searchExtensionInProgress = false
                return
            }
            const searchTerm = this.searchExtension.toLowerCase()
            const seachedPersonalities = this.personalities.filter((item) => {

                if (item.name && item.name.toLowerCase().includes(searchTerm) || item.description && item.description.toLowerCase().includes(searchTerm) || item.full_path && item.full_path.toLowerCase().includes(searchTerm)) {
                    return item
                }

            })



            if (seachedPersonalities.length > 0) {
                this.personalitiesFiltered = seachedPersonalities.sort()
            } else {
                this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.configFile.personality_category)
                this.personalitiesFiltered.sort()
            }
            this.searchExtensionInProgress = false

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
        async mount_extension(ext) {
            if (!ext) { return { 'status': false, 'error': 'no extension - mount_extension' } }

            try {
                const obj = {
                    client_id: this.$store.state.client_id,
                    category: ext.category,
                    folder: ext.folder,
                }
                const res = await axios.post('/mount_extension', obj, {headers: this.posts_headers});

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'mount_extension - settings')
                return
            }

        },
        async unmount_extension(ext) {
            if (!ext) { return { 'status': false, 'error': 'no extension - unmount_extension' } }

            const obj = {
                client_id: this.$store.state.client_id,
                language: ext.language,
                category: ext.category,
                folder: ext.folder
            }


            try {
                const res = await axios.post('/unmount_extension', obj, {headers: this.posts_headers});

                if (res) {
                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'unmount_extension - settings')
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
                const persId = this.personalities.findIndex(item => item.full_path == pers.full_path)
                const persFilteredId = this.personalitiesFiltered.findIndex(item => item.full_path == pers.full_path)
                const persIdZoo = this.$refs.personalitiesZoo.findIndex(item => item.full_path == pers.full_path)
                console.log('ppp', this.personalities[persId])

                this.personalities[persId].isMounted = false

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

        async mountExtension(ext) {
            this.isLoading = true
            console.log('mount ext', ext)
            if (!ext) { return }

            if (this.configFile.personalities.includes(ext.extension.full_path)) {
                this.isLoading = false
                this.$store.state.toast.showToast("Extension already mounted", 4, false)

                return
            }

            const res = await this.mount_extension(ext.extension)
            console.log('mount_extension res', res)

            if (res && res.status && res.extensions.includes(ext.extension.full_path)) {
                this.configFile.extensions = res.extensions
                this.$store.state.toast.showToast("Extension mounted", 4, true)
                ext.isMounted = true
                this.$store.dispatch('refreshMountedExtensions');
            } else {
                ext.isMounted = false
                this.$store.state.toast.showToast("Could not mount extension\nError: " + res.error + "\nResponse:\n" + res, 4, false)
            }
            this.isLoading = false

        },
        async unmountExtension(ext) {
            this.isLoading = true
            if (!ext) { return }

            const res = await this.p_unmount_extension(ext.extension || ext)


            if (res.status) {
                this.configFile.extensions = res.extensions
                this.$store.state.toast.showToast("Extension unmounted", 4, true)
                const extId = this.extensions.findIndex(item => item.full_path == ext.full_path)
                const persFilteredId = this.extensionsFiltered.findIndex(item => item.full_path == ext.full_path)
                const extIdZoo = this.$refs.extensionsZoo.findIndex(item => item.full_path == ext.full_path)
                console.log('ext', this.extensions[extId])

                this.extensions[extId].isMounted = false

                if (persFilteredId > -1) {
                    this.extensionsFiltered[persFilteredId].isMounted = false

                }

                if (extIdZoo > -1) {
                    this.$refs.extensionsZoo[extIdZoo].isMounted = false

                }


                //ext.isMounted = false
                this.$store.dispatch('refreshMountedPersonalities');
                // Select some other personality
                const lastPers = this.mountedExtensions[this.mountedExtensions.length - 1]

                console.log(lastPers, this.mountedExtensions.length)


            } else {
                this.$store.state.toast.showToast("Could not unmount extension\nError: " + res.error, 4, false)
            }

            this.isLoading = false
        },
        async remountExtension(ext){
            await this.unmountExtension(ext);
            await this.mountExtension(ext);
        },
        onExtensionReinstall(extItem){
            console.log('on reinstall ', extItem)
            this.isLoading = true
            console.log(extItem)
            axios.post('/reinstall_extension', { name: extItem.extension.full_path }).then((res) => {

                if (res) {
                    this.isLoading = false
                    console.log('reinstall_extension', res)
                    if (res.data.status) {
                        this.$store.state.toast.showToast("Extension reinstalled successfully!", 4, true)
                    } else {
                        this.$store.state.toast.showToast("Could not reinstall extension", 4, false)
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
        extensionImgPlacehodler(event){
            event.target.src = defaultExtensionImgPlaceholder
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
        this.snd_input_devices = await axios.get("/get_snd_input_devices")
        this.snd_output_devices = await axios.get("/get_snd_output_devices")

    },
    activated() {
        //this.load_everything()
    },
    computed: { 
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
                "base",
                "base.en",
                "base.fr",
                "base.es",
                "small",
                "small.en",
                "small.fr",
                "small.es",
                "medium",
                "medium.en",
                "medium.fr",
                "medium.es",
                "large",
                "large.en",
                "large.fr",
                "large.es",
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
        xtts_enable:{
            get() {
                return this.$store.state.config.xtts_enable;
            },
            set(value) {
                // You should not set the value directly here; use the updateSetting method instead
                this.$store.state.config.xtts_enable = value
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
        mountedExtensions:{
            get() {
                console.log("this.$store.state.mountedExtensions:",this.$store.state.mountedExtensions)
                return this.$store.state.mountedExtensions;
            },
            set(value) {
                this.$store.commit('setActiveExtensions', value);
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
                return
            }
            const index = this.bindingsZoo.findIndex(item => item.folder === this.configFile.binding_name)
            if (index > -1) {
                return this.bindingsZoo[index].name

            } else {
                return
            }
        },
        active_pesonality() {
            if (!this.isMounted) {
                return
            }
            const index = this.personalities.findIndex(item => item.full_path === this.configFile.personalities[this.configFile.active_personality_id])
            if (index > -1) {
                return this.personalities[index].name
            } else {
                return

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
        xtts_enable(newValue) {
            if (!newValue) {
              this.configFile.auto_read = false;
            }
        },
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
        if (this.settingsChanged) {
            const res = await this.$store.state.yesNoDialog.askQuestion("Did You forget to apply changes?\nYou need to apply changes before you leave, or else.", 'Apply configuration', 'Cancel')
            if (res) {
                this.applyConfiguration()

            }
            return false
        }


    },
}
</script>

