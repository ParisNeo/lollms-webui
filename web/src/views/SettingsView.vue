<template>
    <div class="container overflow-y-scroll flex flex-col no-scrollbar shadow-lg p-10 pt-0 ">
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


                <!-- <div v-if="!isModelSelected" class="text-red-600 flex gap-3 items-center">
                    <i data-feather="alert-triangle"></i>
                    No model selected!
                </div> -->
                <div class="flex gap-3 items-center">
                    <div v-if="settingsChanged" class="flex gap-3 items-center">
                        Apply changes:
                        <button v-if="!isLoading" class="text-2xl hover:text-secondary duration-75 active:scale-90"
                            title="Apply changes" type="button" @click.stop="applyConfiguration()">
                            <i data-feather="check"></i>
                        </button>
                    </div>

                    <!-- SPINNER -->
                    <div v-if="isLoading" role="status">
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

        <div :class="isLoading ? 'pointer-events-none opacity-30' : ''">
            <!-- DISK AND RAM USAGE -->
            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="sc_collapsed = !sc_collapsed"
                        class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1 flex flex-row items-center ">
                        <i data-feather="chevron-right" class="mr-2  flex-shrink-0"></i>

                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            System status</h3>
                        <div class="mr-2">|</div>

                        <div class=" text-base font-semibold cursor-pointer select-none items-center">

                            <div class="flex gap-2 items-center ">
                                <svg class="flex-shrink-0" xmlns="http://www.w3.org/2000/svg" width="24" height="24"
                                    viewBox="0 0 24 24">
                                    <path fill="currentColor"
                                        d="M17 17H7V7h10m4 4V9h-2V7a2 2 0 0 0-2-2h-2V3h-2v2h-2V3H9v2H7c-1.11 0-2 .89-2 2v2H3v2h2v2H3v2h2v2a2 2 0 0 0 2 2h2v2h2v-2h2v2h2v-2h2a2 2 0 0 0 2-2v-2h2v-2h-2v-2m-6 2h-2v-2h2m2-2H9v6h6V9Z" />
                                </svg>
                                <h3 class="font-bold font-large text-lg">
                                    <div>{{ ram_usage }} / {{ ram_total_space }}</div>
                                </h3>
                                <i data-feather="hard-drive" class="w-5 h-5 mx-1 flex-shrink-0"></i>
                                <h3 class="font-bold font-large text-lg">
                                    <div> {{ disk_binding_models_usage }} / {{ disk_total_space }}</div>
                                </h3>
                            </div>
                        </div>
                    </button>
                </div>
                <div :class="{ 'hidden': sc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">

                    <div class="mb-2">

                        <label for="disk"
                            class=" flex items-center gap-1 ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24">
                                <path fill="currentColor"
                                    d="M17 17H7V7h10m4 4V9h-2V7a2 2 0 0 0-2-2h-2V3h-2v2h-2V3H9v2H7c-1.11 0-2 .89-2 2v2H3v2h2v2H3v2h2v2a2 2 0 0 0 2 2h2v2h2v-2h2v2h2v-2h2a2 2 0 0 0 2-2v-2h2v-2h-2v-2m-6 2h-2v-2h2m2-2H9v6h6V9Z" />
                            </svg>
                            Ram usage:
                        </label>
                        <div class="flex flex-col mx-2">
                            <div><b>Avaliable space:&nbsp;</b>{{ ram_available_space }}</div>
                            <div><b>Ram usage:&nbsp;</b> {{ ram_usage }} / {{ ram_total_space }}</div>
                        </div>
                        <div class="p-2 ">
                            <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                                <div class="bg-blue-600 h-2.5 rounded-full" :style="'width: ' + ram_percent_usage + '%;'">
                                </div>
                            </div>

                        </div>
                    </div>
                    <div class="mb-2">
                        <label for="disk"
                            class="flex items-center gap-1 ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            <i data-feather="hard-drive" class="w-5 h-5"></i>
                            Disk usage:
                        </label>
                        <div class="flex flex-col mx-2">
                            <div><b>Avaliable space:&nbsp;</b>{{ disk_available_space }}</div>
                            <div><b>Disk usage:&nbsp;</b> {{ disk_binding_models_usage }} / {{ disk_total_space }}</div>
                        </div>
                        <div class="p-2 ">
                            <div class="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
                                <div class="bg-blue-600 h-2.5 rounded-full" :style="'width: ' + disk_percent_usage + '%;'">
                                </div>
                            </div>

                        </div>
                    </div>



                </div>

            </div>
            <!-- BINDING ZOO -->
            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="bzc_collapsed = !bzc_collapsed"
                        class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1 flex flex-row items-center">
                        <i data-feather="chevron-right" class="mr-2 flex-shrink-0"></i>

                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Binding zoo</h3>
                        <div v-if="configFile.binding_name" class="mr-2">|</div>

                        <div v-if="configFile.binding_name"
                            class=" text-base font-semibold cursor-pointer select-none items-center">

                            <div class="flex gap-1 items-center">
                                <img :src="imgBinding" class="w-8 h-8 rounded-full object-fill text-blue-700">
                                <h3 class="font-bold font-large text-lg line-clamp-1">
                                    {{ configFile.binding_name }}
                                </h3>
                            </div>
                        </div>
                    </button>
                </div>
                <div :class="{ 'hidden': bzc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">

                    <div v-if="bindings.length > 0" class="mb-2">
                        <label for="binding" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Bindings: ({{ bindings.length }})
                        </label>
                        <div class="overflow-y-auto no-scrollbar p-2 pb-0 grid lg:grid-cols-3 md:grid-cols-2 gap-4"
                            :class="bzl_collapsed ? '' : 'max-h-96'">
                            <TransitionGroup name="list">
                                <BindingEntry ref="bindingZoo" v-for="(binding, index) in bindings"
                                    :key="'index-' + index + '-' + binding.folder" :binding="binding"
                                    :on-selected="onSelectedBinding" :selected="binding.folder === configFile.binding_name">
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
                    <button @click.stop="mzc_collapsed = !mzc_collapsed"
                        class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1 flex items-center">
                        <i :data-feather="mzc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2 flex-shrink-0"></i>
                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Models zoo</h3>
                        <div class="flex flex-row items-center">
                            <div v-if="!isModelSelected" class="text-base text-red-600 flex gap-3 items-center mr-2">
                                <i data-feather="alert-triangle" class="flex-shrink-0"></i>
                                No model selected!
                            </div>

                            <div v-if="configFile.model_name" class="mr-2">|</div>

                            <div v-if="configFile.model_name"
                                class=" text-base font-semibold cursor-pointer select-none items-center">

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

                    <div v-if="models.length > 0" class="mb-2">
                        <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Models: ({{ models.length }})
                        </label>

                        <div class="overflow-y-auto no-scrollbar p-2 pb-0 " :class="mzl_collapsed ? '' : 'max-h-96'">
                            <TransitionGroup name="list">
                                <model-entry ref="modelZoo" v-for="(model, index) in models"
                                    :key="'index-' + index + '-' + model.title" :title="model.title" :icon="model.icon"
                                    :path="model.path" :owner="model.owner" :owner_link="model.owner_link"
                                    :license="model.license" :description="model.description"
                                    :is-installed="model.isInstalled" :on-install="onInstall" :on-uninstall="onUninstall"
                                    :on-selected="onSelected" :selected="model.title === configFile.model_name"
                                    :model="model" :model_type="model.model_type" :on-copy="onCopy" />
                            </TransitionGroup>
                        </div>
                    </div>
                    <!-- EXPAND / COLLAPSE BUTTON -->
                    <button v-if="mzl_collapsed"
                        class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                        title="Collapse" type="button" @click="mzl_collapsed = !mzl_collapsed">
                        <i data-feather="chevron-up"></i>
                    </button>
                    <button v-else
                        class="text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                        title="Expand" type="button" @click="mzl_collapsed = !mzl_collapsed">
                        <i data-feather="chevron-down"></i>
                    </button>
                </div>

            </div>

            <!-- PERSONALITY ZOO -->
            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">


                <div class="flex flex-row p-3">
                    <button @click.stop="pzc_collapsed = !pzc_collapsed"
                        class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1 flex items-center">
                        <i :data-feather="pzc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2 flex-shrink-0"></i>
                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Personalities zoo</h3>
                        <div v-if="configFile.personalities" class="mr-2">|</div>

                        <div v-if="configFile.personalities"
                            class=" text-base font-semibold cursor-pointer select-none items-center">

                            <div class="flex gap-1 items-center">
                                <img :src="imgPersonality" class="w-8 h-8 rounded-full object-fill text-red-700">
                                <h3 class="font-bold font-large text-lg line-clamp-1">
                                    {{ this.configFile.personality_folder }}
                                </h3>
                            </div>

                        </div>
                    </button>
                </div>
                <div :class="{ 'hidden': pzc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <div class="mx-2 mb-4">
                        <label for="persLang" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Personalities Languages: ({{ persLangArr.length }})
                        </label>
                        <select id="persLang" @change="update_setting('personality_language', $event.target.value, refresh)"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                            <option v-for="item in persLangArr" :selected="item === this.configFile.personality_language">{{
                                item
                            }}

                            </option>

                        </select>
                    </div>
                    <div class="mx-2 mb-4">
                        <label for="persCat" class="block  mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Personalities Category: ({{ persCatgArr.length }})
                        </label>
                        <select id="persCat" @change="update_setting('personality_category', $event.target.value, refresh)"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                            <option v-for="item in persCatgArr" :selected="item === this.configFile.personality_category">{{
                                item
                            }}

                            </option>

                        </select>
                    </div>

                    <!-- <div class="mx-2 mb-4">
                        <label for="persona" class="block mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Personality:
                        </label>
                        <select id="persona" @change="update_setting('personality', $event.target.value, refresh)"
                            class="bg-gray-50 border border-gray-300 text-gray-900 text-sm rounded-lg focus:ring-blue-500 focus:border-blue-500 block w-full p-2.5 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white dark:focus:ring-blue-500 dark:focus:border-blue-500">

                            <option v-for="item in persArr" :selected="item === configFile.personality">{{ item }}</option>

                        </select>
                    </div> -->

                    <div v-if="personalitiesFiltered.length > 0" class="mb-2">
                        <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Personalities: ({{ personalitiesFiltered.length }})
                        </label>
                        <div class="overflow-y-auto no-scrollbar p-2 pb-0 grid lg:grid-cols-3 md:grid-cols-2 gap-4"
                            :class="pzl_collapsed ? '' : 'max-h-96'">
                            <TransitionGroup name="bounce">
                                <personality-entry ref="personalitiesZoo" v-for="(pers, index) in personalitiesFiltered"
                                    :key="'index-' + index + '-' + pers.name" :personality="pers"
                                    :selected="pers.folder === this.configFile.personality_folder && pers.category === this.configFile.personality_category && pers.language === this.configFile.personality_language"
                                    :on-selected="onPersonalitySelected" />
                            </TransitionGroup>
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
                class="flex flex-col mb-2 p-3 rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row">
                    <button @click.stop="mc_collapsed = !mc_collapsed"
                        class="text-2xl hover:text-primary duration-75 p-2 -m-2 w-full text-left active:translate-y-1 flex items-center">
                        <i :data-feather="mc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2"></i>
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
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="temperature" @change="update_setting('temperature', $event.target.value)"
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
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="predict" @change="update_setting('n_predict', $event.target.value)" type="range"
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
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="top_k" @change="update_setting('top_k', $event.target.value)" type="range"
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
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="top_p" @change="update_setting('top_p', $event.target.value)" type="range"
                                    v-model="configFile.top_p" min="0" max="1" step="0.01"
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
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="repeat_penalty" @change="update_setting('repeat_penalty', $event.target.value)"
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
                                            class="mt-2 w-16 text-right p-2 border border-gray-300 rounded-lg bg-gray-50 sm:text-xs focus:ring-blue-500 focus:border-blue-500 dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-blue-500 dark:focus:border-blue-500">
                                    </p>

                                </div>

                                <input id="repeat_last_n" @change="update_setting('repeat_last_n', $event.target.value)"
                                    type="range" v-model="configFile.repeat_last_n" min="0" max="100" step="1"
                                    class="flex-none h-2 mt-14 mb-2 w-full bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700  focus:ring-blue-500 focus:border-blue-500  dark:border-gray-600 dark:placeholder-gray-400  dark:focus:ring-blue-500 dark:focus:border-blue-500">
                            </div>
                        </div>
                    </div>
                    <!-- sdasdas -->
                </div>
            </div>
        </div>

    </div>

    <YesNoDialog ref="yesNoDialog" />
    <MessageBox ref="messageBox" />
    <Toast ref="toast" />
</template>
<style scoped>
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
</style>
<script>
import filesize from '../plugins/filesize'
import axios from "axios";
import feather from 'feather-icons'
import { nextTick, TransitionGroup } from 'vue'
import MessageBox from "@/components/MessageBox.vue";
import YesNoDialog from "@/components/YesNoDialog.vue";
import Toast from '../components/Toast.vue'
import ModelEntry from '@/components/ModelEntry.vue';
import PersonalityViewer from '@/components/PersonalityViewer.vue';
import PersonalityEntry from "../components/PersonalityEntry.vue";
import BindingEntry from "../components/BindingEntry.vue";
import socket from '@/services/websocket.js'
import defaultModelImgPlaceholder from "../assets/default_model.png"
import defaultPersonalityImgPlaceholder from "../assets/logo.svg"

axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
    components: {
        MessageBox,
        YesNoDialog,
        ModelEntry,
        // eslint-disable-next-line vue/no-unused-components
        PersonalityViewer,
        Toast,
        PersonalityEntry,
        BindingEntry,
    },
    data() {

        return {
            // Zoo stuff
            models: [],
            personalities: [],
            personalitiesFiltered: [],
            bindings: [],
            // Accordeon stuff 
            collapsedArr: [],
            all_collapsed: true,
            bec_collapsed: true,
            mzc_collapsed: true, // models zoo
            pzc_collapsed: true, // personalities zoo
            bzc_collapsed: true, // binding zoo
            pc_collapsed: true,
            mc_collapsed: true,
            sc_collapsed: true, // system status
            // Zoo accordeoon
            mzl_collapsed: false,
            pzl_collapsed: false,
            bzl_collapsed: false,
            // Settings stuff
            bindingsArr: [],
            modelsArr: [], // not used anymore but still have references in some methods
            persLangArr: [],
            persCatgArr: [],
            persArr: [],
            langArr: [],
            configFile: {},
            showConfirmation: false,
            showToast: false,
            isLoading: false,
            settingsChanged: false,
            isModelSelected: false,
            diskUsage: {},
            ramUsage: {},
            isMounted: false // Needed to wait for $refs to be rendered


        }
    },
    created() {

    }, methods: {
        collapseAll(val) {
            this.bec_collapsed = val
            this.mzc_collapsed = val
            this.pzc_collapsed = val
            this.bzc_collapsed = val
            this.pc_collapsed = val
            this.mc_collapsed = val
            this.sc_collapsed = val

        },
        fetchModels() {

            axios.get('/get_available_models')
                .then(response => {

                    this.models = response.data;
                    this.fetchCustomModels()
                })
                .catch(error => {
                    console.log(error.message, 'fetchModels');
                });
        },
        fetchCustomModels() {

            axios.get('/list_models')
                .then(response => {
                    // Returns array of model filenames which are = to title of models zoo entry
                    for (let i = 0; i < response.data.length; i++) {
                        const customModel = response.data[i]
                        const index = this.models.findIndex(x => x.title == customModel)

                        if (index == -1) {
                            let newModelEntry = {}
                            newModelEntry.title = customModel
                            newModelEntry.path = customModel
                            newModelEntry.isCustomModel = true
                            newModelEntry.isInstalled = true
                            this.models.push(newModelEntry)
                        }
                    }


                })
                .catch(error => {
                    console.log(error.message, 'fetchCustomModels');
                });
        },
        onPersonalitySelected(pers) {

            // eslint-disable-next-line no-unused-vars
            if (this.isLoading) {
                this.$refs.toast.showToast("Loading... please wait", 4, false)
            }
            if (pers.personality) {
                if (this.configFile.personality_folder != pers.personality.folder) {


                    this.settingsChanged = true
                    const res = this.update_setting('personality_folder', pers.personality.folder, () => {
                        this.$refs.toast.showToast("Selected personality:\n" + pers.personality.name, 4, true)
                        this.configFile.personalities[configFile.active_personality_id] = pers.personality.language + "/" + pers.personality.category + "/" + pers.personality.name
                    })
                }
                nextTick(() => {
                    feather.replace()

                })
            }

        },
        onSelected(model_object) {

            // eslint-disable-next-line no-unused-vars
            if (this.isLoading) {
                this.$refs.toast.showToast("Loading... please wait", 4, false)
            }
            if (model_object) {
                if (model_object.isInstalled) {

                    if (this.configFile.model_name != model_object.title) {
                        this.update_model(model_object.title)
                        this.configFile.model_name = model_object.title
                        this.$refs.toast.showToast("Selected model:\n" + model_object.title, 4, true)
                        this.settingsChanged = true
                        this.isModelSelected = true
                    }

                } else {
                    this.$refs.toast.showToast("Model:\n" + model_object.title + "\nis not installed", 4, false)
                }

                nextTick(() => {
                    feather.replace()

                })
            }

        },
        onCopy(modelEntry) {
            let content
            if (!modelEntry.model.isCustomModel) {
                content = `Model name: ${modelEntry.title}\nFile size: ${modelEntry.fileSize}\nDownload: ${modelEntry.path}\nLicense: ${modelEntry.license}\nOwner: ${modelEntry.owner}\nWebsite: ${modelEntry.owner_link}\nDescription: ${modelEntry.description}`
            } else {
                content = `Model name: ${modelEntry.title}\nFile size: ${modelEntry.fileSize}\nManually downloaded model `
            }

            this.$refs.toast.showToast("Copied model info to clipboard!", 4, true)
            navigator.clipboard.writeText(content.trim());
        },

        // Model installation

        onInstall(model_object) {
            if (model_object.linkNotValid) {
                model_object.installing = false
                this.$refs.toast.showToast("Link is not valid, file does not exist", 4, false)
                return
            }
            let path = model_object.path;
            this.showProgress = true;
            this.progress = 0;
            console.log("installing...");

            // Use an arrow function for progressListener
            const progressListener = (response) => {
                console.log("received something");
                if (response.status === 'progress') {
                    console.log(`Progress = ${response.progress}`);
                    model_object.progress = response.progress
                    model_object.installing = true
                    if (model_object.progress == 100) {
                        const index = this.models.findIndex((model) => model.path === path);
                        this.models[index].isInstalled = true;
                        this.showProgress = false;
                        model_object.installing = false
                    }
                } else if (response.status === 'succeeded') {
                    console.log("Received succeeded")
                    socket.off('install_progress', progressListener);
                    console.log("Installed successfully")
                    // Update the isInstalled property of the corresponding model
                    const index = this.models.findIndex((model) => model.path === path);
                    this.models[index].isInstalled = true;
                    this.showProgress = false;
                    model_object.installing = false
                    this.$refs.toast.showToast("Model:\n" + model_object.title + "\ninstalled!", 4, true)
                    this.api_get_req("disk_usage").then(response => {
                        this.diskUsage = response
                    })
                } else if (response.status === 'failed') {
                    socket.off('install_progress', progressListener);
                    console.log("Install failed")
                    // Installation failed or encountered an error
                    model_object.installing = false;
                    v
                    this.showProgress = false;
                    console.error('Installation failed:', response.error);
                    this.$refs.toast.showToast("Model:\n" + model_object.title + "\nfailed to install!", 4, false)
                    this.api_get_req("disk_usage").then(response => {
                        this.diskUsage = response
                    })
                }
            };

            socket.on('install_progress', progressListener);


            socket.emit('install_model', { path: path });
            console.log("Started installation, please wait");
        },
        onUninstall(model_object) {
            console.log("uninstalling model...")
            const progressListener = (response) => {
                if (response.status === 'progress') {
                    this.progress = response.progress;
                } else if (response.status === 'succeeded') {
                    // Installation completed
                    model_object.uninstalling = false;
                    socket.off('install_progress', progressListener);
                    this.showProgress = false;
                    const index = this.models.findIndex((model) => model.path === model_object.path);
                    this.models[index].isInstalled = false;
                    if (model_object.model.isCustomModel) {
                        this.models = this.models.filter((model) => model.title !== model_object.title)
                    }
                    this.$refs.toast.showToast("Model:\n" + model_object.title + "\nwas uninstalled!", 4, true)
                    this.api_get_req("disk_usage").then(response => {
                        this.diskUsage = response
                    })
                } else if (response.status === 'failed') {
                    // Installation failed or encountered an error
                    model_object.uninstalling = false;
                    this.showProgress = false;
                    socket.off('install_progress', progressListener);
                    // eslint-disable-next-line no-undef
                    console.error('Uninstallation failed:', message.error);
                    this.$refs.toast.showToast("Model:\n" + model_object.title + "\nfailed to uninstall!", 4, false)
                    this.api_get_req("disk_usage").then(response => {
                        this.diskUsage = response
                    })
                }
            };

            socket.on('install_progress', progressListener);

            socket.emit('uninstall_model', { path: model_object.path });
        },
        onSelectedBinding(binding_object) {

            if (this.configFile.binding_name != binding_object.binding.folder) {

                // disabled for now
                // if (binding_object.binding.folder === 'backend_template' || binding_object.binding.folder === 'binding_template') {
                //     this.$refs.toast.showToast("Cannot select template", 4, false)

                //     return
                // }
                this.update_binding(binding_object.binding.folder)
                //console.log('lol',binding_object)
            }
        },
        // messagebox ok stuff
        onMessageBoxOk() {
            console.log("OK button clicked");
        },
        // Refresh stuff
        refresh() {


            // No need to refresh all lists because they never change during using application. 
            // On settings change only config file chnages.
            //
            //this.api_get_req("list_bindings").then(response => { this.bindingsArr = response })
            this.api_get_req("list_models").then(response => { this.modelsArr = response })
            //this.api_get_req("list_personalities_languages").then(response => { this.persLangArr = response })
            this.api_get_req("list_personalities_categories").then(response => { this.persCatgArr = response })
            this.api_get_req("list_personalities").then(response => { this.persArr = response })
            //this.api_get_req("list_languages").then(response => { this.langArr = response })
            this.api_get_req("get_config").then(response => {
                console.log("Received config")
                this.configFile = response

                this.models.forEach(model => {

                    if (model.title == response["model_name"]) {
                        model.selected = true;

                    }
                    else {
                        model.selected = false;
                    }
                });
            })
            this.api_get_req("get_current_personality_path_infos").then(response => {
                this.configFile.personality_language = response["personality_language"]
                this.configFile.personality_category = response["personality_category"]
                this.configFile.personality_folder = response["personality_name"]
                console.log("received infos")
            });
            this.api_get_req("disk_usage").then(response => {
                this.diskUsage = response
            })
            this.api_get_req("ram_usage").then(response => {
                this.ramUsage = response
            })
            //console.log('ram',this.ramUsage)
            this.getPersonalitiesArr()
            this.fetchModels();
        },
        // Accordeon stuff
        toggleAccordion() {
            this.showAccordion = !this.showAccordion;
        },
        update_setting(setting_name_val, setting_value_val, next) {
            const obj = {
                setting_name: setting_name_val,
                setting_value: setting_value_val
            }

            axios.post('/update_setting', obj).then((res) => {

                if (res) {

                    if (next !== undefined) {

                        next(res)
                    }
                    return res.data;
                }
            })
                // eslint-disable-next-line no-unused-vars
                .catch(error => { return { 'status': false } });
        },
        update_binding(value) {

            // eslint-disable-next-line no-unused-vars
            this.isLoading = true

            this.update_setting('binding_name', value, (res) => {
                

                this.$refs.toast.showToast("Binding changed.", 4, true)
                this.settingsChanged = true
                this.isLoading = false

                // If binding changes then reset model
                this.update_model(null)
                this.configFile.model_name = null

                this.refresh();
                nextTick(() => {
                    feather.replace()

                })
            })

        },
        update_model(value) {
            if (!value) this.isModelSelected = false
            // eslint-disable-next-line no-unused-vars
            this.isLoading = true
            this.update_setting('model_name', value, (res) => {

                //this.fetchModels();
                this.isLoading = false
            })
        },
        applyConfiguration() {
            // if (!this.configFile.model_name) {

            //     this.$refs.toast.showToast("Configuration changed failed.\nPlease select model first", 4, false)
            //     nextTick(() => {
            //         feather.replace()
            //     })
            //     return
            // }
            this.isLoading = true;
            axios.post('/apply_settings').then((res) => {
                this.isLoading = false;

                if (res.data.status === "succeeded") {

                    this.$refs.toast.showToast("Configuration changed successfully.", 4, true)
                    this.settingsChanged = false
                    this.save_configuration()
                } else {

                    this.$refs.toast.showToast("Configuration change failed.", 4, false)

                }
                nextTick(() => {
                    feather.replace()

                })
            })
        },
        save_configuration() {
            this.showConfirmation = false
            axios.post('/save_settings', {})
                .then((res) => {
                    if (res) {
                        if (res.status) {
                            // this.$refs.messageBox.showMessage("Settings saved!")
                        }
                        else
                            this.$refs.messageBox.showMessage("Error: Couldn't save settings!")
                        return res.data;
                    }
                })
                .catch(error => {
                    console.log(error.message, 'save_configuration')
                    this.$refs.messageBox.showMessage("Couldn't save settings!")
                    return { 'status': false }
                });

        },
        reset_configuration() {
            this.$refs.yesNoDialog.askQuestion("Are you sure?\nThis will delete all your configurations and get back to default configuration.").then(response => {
                if (response) {
                    // User clicked Yes
                    axios.post('/reset_settings', {})
                        .then((res) => {
                            if (res) {
                                if (res.status)
                                    this.$refs.messageBox.showMessage("Settings have been reset correctly")
                                else
                                    this.$refs.messageBox.showMessage("Couldn't reset settings!")
                                return res.data;
                            }
                        })
                        .catch(error => {
                            console.log(error.message, 'reset_configuration')
                            this.$refs.messageBox.showMessage("Couldn't reset settings!")
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
        closeToast() {
            this.showToast = false
        },
        async getPersonalitiesArr() {
            this.isLoading = true
            this.personalities = []
            const dictionary = await this.api_get_req("get_all_personalities")
            // console.log("all_personalities")
            // console.log(dictionary)
            const langkeys = Object.keys(dictionary); // returns languages folder names
            for (let i = 0; i < langkeys.length; i++) {
                const langkey = langkeys[i];
                const catdictionary = dictionary[langkey];
                const catkeys = Object.keys(catdictionary); // returns categories

                for (let j = 0; j < catkeys.length; j++) {
                    const catkey = catkeys[j];
                    const personalitiesArray = catdictionary[catkey];
                    const modPersArr = personalitiesArray.map((item) => {
                        let newItem = {}
                        newItem = item
                        newItem.category = catkey // add new props to items
                        newItem.language = langkey // add new props to items
                        return newItem
                    })


                    if (this.personalities.length == 0) {
                        this.personalities = modPersArr
                    } else {
                        this.personalities = this.personalities.concat(modPersArr)
                    }
                }

            }
            // console.log(this.configFile)
            // console.log(this.configFile.personality_category)
            // console.log(this.configFile.personality_language)
            // console.log("Personalities")
            // console.log(this.personalities)
            this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.configFile.personality_category && item.language === this.configFile.personality_language)
            //console.log(`Personalities filtered ${this.personalitiesFiltered}`)
            this.isLoading = false

        },
        computedFileSize(size) {
            return filesize(size)
        },


    }, async mounted() {
        this.isLoading = true
        nextTick(() => {
            feather.replace()

        })
        this.configFile = await this.api_get_req("get_config")
        let personality_path_infos = await this.api_get_req("get_current_personality_path_infos")
        this.configFile.personality_language = personality_path_infos["personality_language"]
        this.configFile.personality_category = personality_path_infos["personality_category"]
        this.configFile.personality_folder = personality_path_infos["personality_name"]


        if (this.configFile.model_name) {
            this.isModelSelected = true
        }

        this.fetchModels();
        this.bindingsArr = await this.api_get_req("list_bindings")
        this.modelsArr = await this.api_get_req("list_models")
        this.persLangArr = await this.api_get_req("list_personalities_languages")
        this.persCatgArr = await this.api_get_req("list_personalities_categories")
        this.persArr = await this.api_get_req("list_personalities")
        this.langArr = await this.api_get_req("list_languages")
        await this.getPersonalitiesArr()
        this.bindings = await this.api_get_req("list_bindings")
        this.isLoading = false
        this.diskUsage = await this.api_get_req("disk_usage")
        this.ramUsage = await this.api_get_req("ram_usage")
        console.log('ran', this.ramUsage)
        this.isMounted = true

    },
    computed: {
        disk_available_space() {
            return this.computedFileSize(this.diskUsage.available_space)
        },
        disk_binding_models_usage() {
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
        imgBinding() {
            if (!this.isMounted) {
                return
            }
            try {
                return this.$refs.bindingZoo[this.$refs.bindingZoo.findIndex(item => item.binding.folder == this.configFile.binding_name)].$refs.imgElement.src
            }
            catch (error) {
                return defaultImgPlaceholder
            }
        },
        imgModel() {
            if (!this.isMounted) {
                return
            }
            // console.log("Config file")
            // console.log(this.configFile)
            try {
                return this.$refs.modelZoo[this.$refs.modelZoo.findIndex(item => item.title == this.configFile.model_name)].$refs.imgElement.src
            }
            catch (error) {
                return defaultModelImgPlaceholder
            }
        },
        imgPersonality() {
            if (!this.isMounted) {
                return
            }
            try {
                return this.$refs.personalitiesZoo[this.$refs.personalitiesZoo.findIndex(item => item.personality.folder == this.configFile.personality_folder)].$refs.imgElement.src
            }
            catch (error) {
                return defaultPersonalityImgPlaceholder
            }
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
        settingsChanged() {
            nextTick(() => {
                feather.replace()

            })
        },
        isLoading() {
            nextTick(() => {
                feather.replace()

            })
        },

    }
}
</script>

