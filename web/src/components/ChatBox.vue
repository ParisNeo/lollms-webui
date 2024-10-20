<template>

            <div class="absolute bottom-0 left-0 w-fit min-w-96  w-full justify-center text-center">
                <div v-if="filesList.length > 0 || showPersonalities" class="items-center gap-2 panels-color shadow-sm hover:shadow-none dark:border-gray-800  w-fit">
                    <!-- EXPAND / COLLAPSE BUTTON -->
                    <div class="flex">
                        <button 
                            class="mx-1 w-full text-2xl hover:text-secondary duration-75 flex justify-center  hover:bg-bg-light-tone hover:dark:bg-bg-dark-tone rounded-lg "
                            :title="showfilesList ? 'Hide file list' : 'Show file list'" type="button"
                            @click.stop=" showfilesList = !showfilesList">
                            <i data-feather="list"></i>
                        </button>
                    </div>                 
                    <!-- FILES     -->
                    <div v-if="filesList.length > 0 && showfilesList ==true">
                        <div class="flex flex-col max-h-64  ">
                            <TransitionGroup name="list" tag="div"
                                class="flex flex-col flex-grow overflow-y-auto scrollbar-thin scrollbar-track-bg-light scrollbar-thumb-bg-light-tone hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark dark:scrollbar-thumb-bg-dark-tone dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
                                <div v-for="(file, index) in filesList" :key="index + '-' + file.name">
                                    <div class="  m-1" :title="file.name">

                                        <div
                                            class="flex flex-row items-center gap-1 text-left p-2 text-sm font-medium items-center gap-2 rounded-lg border bg-gray-100 p-1.5 shadow-sm hover:shadow-none dark:border-gray-800 dark:bg-gray-700 hover:bg-primary dark:hover:bg-primary">
                                            <div v-if="!isFileSentList[index]" filesList role="status">
                                                <svg aria-hidden="true" class="w-6 h-6   animate-spin  fill-secondary"
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
                                            <div>
                                                <i data-feather="file" class="w-5 h-5"></i>

                                            </div>


                                            <div class="line-clamp-1 w-3/5" :class="isFileSentList[index]?'text-green-500':'text-red-200'">
                                                {{ file.name }}
                                            </div>
                                            <div class="grow">

                                            </div>

                                            <div class="flex flex-row items-center">
                                                <p class="whitespace-nowrap">
                                                    {{ computedFileSize(file.size) }}

                                                </p>
                                                <button type="button" title="Remove item"
                                                    class="flex items-center p-0.5 text-sm rounded-sm hover:text-red-600 active:scale-75"
                                                    @click="removeItem(file)">
                                                    <i data-feather="x" class="w-5 h-5 "></i>

                                                </button>

                                            </div>


                                        </div>


                                    </div>
                                </div>
                            </TransitionGroup>

                        </div>
                    </div>
                    <div v-if="filesList.length > 0" class="flex mx-1 w-500">
                        <!-- ADDITIONAL INFO PANEL -->
                        <div class="whitespace-nowrap flex flex-row gap-2">
                            <p class="font-bold ">
                                Total size:
                            </p>

                            {{ totalSize }}

                            ({{ filesList.length }})


                        </div>
                        <div class="grow">

                        </div>
                        <button type="button" title="Clear all"
                            class="flex items-center p-0.5 text-sm rounded-sm hover:text-red-600 active:scale-75"
                            @click="clear_files">
                            <i data-feather="trash" class="w-5 h-5 "></i>
                        </button>
                        <button type="button" title="Download database"
                            class="flex items-center p-0.5 text-sm rounded-sm hover:text-red-600 active:scale-75"
                            @click="download_files">
                            <i data-feather="download-cloud" class="w-5 h-5 "></i>
                        </button>                        
                    </div>
                    <div v-if="showPersonalities" class="mx-1">
                        <MountedPersonalitiesList ref="mountedPersList" 
                            :onShowPersList="onShowPersListFun"
                            :on-mounted="onMountFun"
                            :on-un-mounted="onUnmountFun"
                            :on-remounted="onRemountFun"
                            :on-talk="handleOnTalk"
                            :discussionPersonalities="allDiscussionPersonalities" />
                    </div>
                </div>

                <!-- CHAT BOX -->
                <div v-if="selecting_model||selecting_binding" title="Selecting model" class="flex flex-row flex-grow justify-end panels-color">
                    <!-- SPINNER -->
                    <div role="status">
                        <img :src="loader_v0" class="w-50 h-50">
                        <span class="sr-only">Selecting model...</span>
                    </div>
                </div>
                <div class="flex w-fit relative grow w-full">
                    <div class="relative text-light-text-panel dark:text-dark-text-panel grow flex h-12.5 cursor-pointer select-none items-center gap-2 chatbox-color p-1 shadow-sm hover:shadow-none dark:border-gray-800" tabindex="0">
                        <div v-if="loading" title="Waiting for reply">
                            <img :src="loader_v0">
                            <!-- SPINNER -->
                            <div role="status">
                                <span class="sr-only">Loading...</span>
                            </div>
                        </div>

                        <ChatBarButton 
                            @click="toggleLeftPanel" 
                            :class="{ 'text-red-500': leftPanelCollapsed }" 
                            title="Toggle View Mode"
                        >
                            <div v-show="leftPanelCollapsed">
                                <!-- Chevron Right SVG -->
                                <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="24"
                                height="24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                >
                                <polyline points="9 18 15 12 9 6"></polyline>
                                </svg>
                            </div>
                            <div v-show="!leftPanelCollapsed">
                                <!-- Chevron Left SVG -->
                                <svg
                                xmlns="http://www.w3.org/2000/svg"
                                width="24"
                                height="24"
                                fill="none"
                                stroke="currentColor"
                                stroke-width="2"
                                stroke-linecap="round"
                                stroke-linejoin="round"
                                >
                                <polyline points="15 18 9 12 15 6"></polyline>
                                </svg>
                            </div>
                        </ChatBarButton>                             
                        <div class="w-fit group relative" v-if="!loading" >
                            <div class= "hide top-50 hide opacity-0 group-hover:bottom-0 opacity-0 .group-hover:block fixed w-[1000px] group absolute  group-hover:opacity-100 transform group-hover:translate-y-[-50px] group-hover:translate-x-[0px] transition-all duration-300">
                                <div class="w-fit flex-wrap flex bg-white bg-opacity-50 backdrop-blur-md rounded p-4">
                                <div class="w-fit h-fit inset-0 opacity-100"
                                    v-for="(item, index) in installedBindings" :key="index + '-' + item.name"
                                    ref="installedBindings"
                                    @mouseover="showBindingHoveredIn(index)" @mouseleave="showBindingHoveredOut()"
                                    >
                                    <div v-if="index!=binding_name" class="items-center flex flex-row relative z-20  hover:-translate-y-8 duration-300"
                                    :class="bindingHoveredIndex === index?'scale-150':''"
                                    >
                                        <div class="relative">
                                            <button @click.prevent="setBinding(item)" class="w-10 h-10 relative">
                                                <img :src="item.icon?item.icon:modelImgPlaceholder" @error="modelImgPlaceholder"
                                                class="z-50 w-10 h-10 rounded-full object-fill text-red-700 border-2 border-gray-500 active:scale-90"
                                                :class="bindingHoveredIndex === index?'scale-150  ':'' + item.name==binding_name ? 'border-secondary' : 'border-transparent z-0'"
                                                :title="item.name">
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                </div>
                            </div>
                            <div class="group items-center flex flex-row">
                                <button @click.prevent="showModelConfig()" class="w-8 h-8">
                                    <img :src="currentBindingIcon"
                                        class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:border-secondary hover:scale-110 hover:-translate-y-1 duration-200"
                                        :title="currentBinding?currentBinding.name:'unknown'">
                                </button>
                            </div>

                        </div>                                    
                        
                        <div class="w-fit group relative" v-if="!loading">
                            <div class="hide top-50 hide opacity-0 group-hover:bottom-0 opacity-0 .group-hover:block fixed w-[1000px] group absolute group-hover:opacity-100 transform group-hover:translate-y-[-50px] group-hover:translate-x-[0px] transition-all duration-300">
                                <div class="w-fit flex-wrap flex bg-white bg-opacity-50 backdrop-blur-md rounded p-4">
                                    <div class="w-fit h-fit"
                                        v-for="(item, index) in installedModels" :key="index + '-' + item.name"
                                        ref="installedModels"
                                        @mouseover="showModelHoveredIn(index)" 
                                        @mouseleave="showModelHoveredOut()"
                                    >
                                        <div v-if="index!=model_name" class="items-center flex flex-row relative z-20 hover:-translate-y-8 duration-300"
                                            :class="modelHoveredIndex === index ? 'scale-150' : ''"
                                        >
                                            <div class="relative flex items-center">
                                                <!-- Parent container for both buttons -->
                                                <div class="relative group">
                                                    <button @click.prevent="setModel(item)" class="w-10 h-10 relative">
                                                        <img :src="item.icon ? item.icon : modelImgPlaceholder" @error="personalityImgPlacehodler"
                                                            class="z-50 w-10 h-10 rounded-full object-fill text-red-700 border-2 border-gray-500 active:scale-90"
                                                            :class="modelHoveredIndex === index ? 'scale-150' : '' + item.name == model_name ? 'border-secondary' : 'border-transparent z-0'"
                                                            :title="item.name">
                                                    </button>
                                                    <!-- New copy button with SVG icon that appears on hover -->
                                                    <button v-if="modelHoveredIndex === index" @click.prevent="copyModelNameFrom(item.name)"
                                                        class="absolute -top-2 -right-2 bg-blue-500 text-white p-1 rounded-full hover:bg-blue-700 transition duration-300">
                                                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" viewBox="0 0 20 20" fill="currentColor">
                                                            <path d="M8 3a1 1 0 011-1h2a1 1 0 110 2H9a1 1 0 01-1-1z" />
                                                            <path d="M6 3a2 2 0 00-2 2v11a2 2 0 002 2h8a2 2 0 002-2V5a2 2 0 00-2-2 3 3 0 01-3 3H9a3 3 0 01-3-3z" />
                                                        </svg>
                                                    </button>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="group items-center flex flex-row">
                                <button @click.prevent="copyModelName()" class="w-8 h-8">
                                    <img :src="currentModelIcon"
                                        class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:border-secondary hover:scale-110 hover:-translate-y-1 duration-400"
                                        :title="currentModel ? currentModel.name : 'unknown'">
                                </button>
                            </div>
                        </div>
                        <!-- Personalities menu positioned above the dock -->
                        <div class="relative" @mouseleave="hidePersonalitiesMenu"  v-if="!loading">
                            <div class="relative inline-block">
                                <!-- Personalities menu positioned above the button -->
                                <div v-show="isPersonalitiesMenuVisible" class="absolute z-10 bottom-full left-1/2 transform -translate-x-1/2 w-60 bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none transition-all duration-300 ease-out mb-2">
                                    <div class="p-2 grid grid-cols-4 gap-4 max-h-60 overflow-y-auto custom-scrollbar">
                                        <div v-for="(item, index) in mountedPersonalities" :key="index" class="relative group/item">                             
                                            <button @click.prevent="onPersonalitySelected(item)" :title="item.name" class="w-10 h-10 rounded-full overflow-hidden transition-transform duration-200 transform group-hover/item:scale-110 focus:outline-none">
                                                <img :src="bUrl + item.avatar" @error="personalityImgPlacehodler" :alt="item.name" class="w-full h-full object-cover" :class="{'border-2 border-secondary': $store.state.active_personality_id == $store.state.personalities.indexOf(item.full_path)}">
                                            </button>
                                            
                                            <div class="absolute -bottom-4 left-0 w-full flex items-center justify-center opacity-0 group-hover/item:opacity-100 transition-opacity duration-200 bg-white rounded-md shadow-md p-1">
                                                <button @click.prevent="unmountPersonality(item)" class="p-1 bg-red-500 rounded-full text-white hover:bg-red-600 focus:outline-none" title="Unmount">
                                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                                                </button>
                                                <button @click.prevent="remount_personality(item)" class="p-1 bg-blue-500 rounded-full text-white hover:bg-blue-600 focus:outline-none ml-1" title="Remount">
                                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
                                                </button>
                                                <button @click.prevent="handleOnTalk(item)" class="p-1 bg-green-500 rounded-full text-white hover:bg-green-600 focus:outline-none ml-1" title="Talk">
                                                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"></path></svg>
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                <div @mouseenter="showPersonalitiesMenu">
                                <MountedPersonalities ref="mountedPers" :onShowPersList="onShowPersListFun" :onReady="onPersonalitiesReadyFun"/>
                                </div>
                            </div>
                        </div>                              
                        <div class="w-fit">
                            <PersonalitiesCommands
                                v-if="personalities_ready && this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id].commands!=''" 
                                :commandsList="this.$store.state.mountedPersArr[this.$store.state.config.active_personality_id].commands"
                                :sendCommand="sendCMDEvent"
                                :on-show-toast-message="onShowToastMessage"
                                ref="personalityCMD"
                            ></PersonalitiesCommands>
                        </div>   
                        <div class="w-fit">
                            <PersonalitiesCommands
                                v-if="isDataSourceNamesValid"
                                :icon="'feather:book'"
                                :commandsList="dataSourceNames"
                                :sendCommand="mountDB"
                                :on-show-toast-message="onShowToastMessage"
                                ref="databasesList"
                            ></PersonalitiesCommands>                                    
                        </div>      
                        <div class="relative grow">
                            <form>
                                <textarea
                                    id="chat"
                                    rows="1"
                                    v-model="message"
                                    @paste="handlePaste"
                                    @keydown.enter.exact="submitOnEnter($event)"
                                    class="w-full p-3 text-sm text-gray-900 dark:text-white bg-gray-100 dark:bg-gray-700 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                                    placeholder="Send message..."
                                ></textarea>
                            </form>
                            </div>

                            <div class="flex items-center space-x-3">
                            <ChatBarButton
                                v-if="loading"
                                @click="stopGenerating"
                                class="bg-red-500 dark:bg-red-600 hover:bg-red-600 dark:hover:bg-red-700"
                            >
                                <template #icon>
                                <svg class="animate-spin h-5 w-5" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                </template>
                                <span>Stop</span>
                            </ChatBarButton>

                            <ChatBarButton v-else @click="submit" title="Send">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8"/>
                                </svg>
                                </template>
                            </ChatBarButton>

                            <ChatBarButton @click="submitWithInternetSearch" title="Send with internet search">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9"/>
                                </svg>
                                </template>
                            </ChatBarButton>
                            <ChatBarButton 
                                @click="startSpeechRecognition" 
                                :class="{ 'text-red-500': isListeningToVoice }" 
                                title="Voice input"
                            >
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"/>
                                </svg>
                                </template>
                            </ChatBarButton>

                            <ChatBarButton 
                                v-if="$store.state.config.active_tts_service != 'None' && $store.state.config.active_tts_service != null && this.$store.state.config.active_stt_service!='None' && this.$store.state.config.active_stt_service!=null"
                                @click="is_rt ? stopRTCom : startRTCom"
                                :class="is_rt ? 'bg-red-500 dark:bg-red-600' : 'bg-green-500 dark:bg-green-600'"
                                title="Real-time audio mode"
                            >
                                <template #icon>
                                    🪶
                                </template>
                            </ChatBarButton>

                            <ChatBarButton @click="add_file" title="Send file">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z"/>
                                </svg>
                                </template>
                            </ChatBarButton>

                            <ChatBarButton @click="takePicture" title="Take picture">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"/>
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"/>
                                </svg>
                                </template>
                            </ChatBarButton>

                            <ChatBarButton @click="addWebLink" title="Add web link">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"/>
                                </svg>
                                </template>
                            </ChatBarButton>

                            <ChatBarButton @click="makeAnEmptyUserMessage" title="New user message" class="text-gray-600 dark:text-gray-300">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/>
                                </svg>
                                </template>
                            </ChatBarButton>

                            <ChatBarButton @click="makeAnEmptyAIMessage" title="New AI message" class="text-red-400 dark:text-red-300">
                                <template #icon>
                                <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                                </svg>
                                </template>
                            </ChatBarButton>
                            
                            <ChatBarButton 
                                @click="toggleRightPanel" 
                                :class="{ 'text-red-500': !rightPanelCollapsed }" 
                                title="Toggle View Mode"
                            >
                                <template #icon>
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                                    <circle cx="12" cy="5" r="2"></circle>
                                    <path d="M12 7v4"></path>
                                    <line x1="8" y1="16" x2="8" y2="16"></line>
                                    <line x1="16" y1="16" x2="16" y2="16"></line>
                                    </svg>                                        </template>
                            </ChatBarButton>   

                            </div>
                            
                            <input type="file" ref="fileDialog" @change="addFiles" multiple style="display: none" />
                    </div> 
                    <div class="ml-auto gap-2"> 
                        
                    </div>
                </div>
            </div>
        
    <UniversalForm ref="universalForm" class="z-20" />
</template>
<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(155, 155, 155, 0.5) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(155, 155, 155, 0.5);
  border-radius: 20px;
  border: transparent;
}
.chat-bar {
  transition: all 0.3s ease;
}

.chat-bar:hover {
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
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
</style>
<!-- <script setup>
import MountedPersonalitiesComponent from './MountedPersonalitiesComponent.vue'

</script> -->
<script>
import { nextTick, ref, TransitionGroup } from 'vue'
import axios from "axios";
import feather from 'feather-icons'
import filesize from '../plugins/filesize'
import MountedPersonalities from '@/components/MountedPersonalities.vue'
import MountedPersonalitiesList from '@/components/MountedPersonalitiesList.vue'
import PersonalitiesCommands from '@/components/PersonalitiesCommands.vue';
import ChatBarButton from '@/components/ChatBarButton.vue'
import socket from '@/services/websocket.js'
import UniversalForm from '@/components/UniversalForm.vue';
import modelImgPlaceholder from "../assets/default_model.png"
import sendGlobe from "../assets/send_globe.svg"
import loader_v0 from "../assets/loader_v0.svg"
import InteractiveMenu from './InteractiveMenu.vue';

console.log("modelImgPlaceholder:",modelImgPlaceholder)
const bUrl = import.meta.env.VITE_LOLLMS_API_BASEURL
export default {
    name: 'ChatBox',
    emits: ["messageSentEvent", "sendCMDEvent", "stopGenerating", "loaded", "createEmptyUserMessage", "createEmptyAIMessage", "personalitySelected","addWebLink"],
    props: {
        onTalk: Function,
        discussionList: Array,
        loading: {
            default:false
        },
        onShowToastMessage: Function

    },
    components: {        
        UniversalForm,
        MountedPersonalities,
        MountedPersonalitiesList,
        PersonalitiesCommands,
        ChatBarButton
    },
    setup() {



    },
    data() {
        return {
            isPersonalitiesMenuVisible: false,
            is_rt:false,
            bindingHoveredIndex:null,
            modelHoveredIndex:null,
            personalityHoveredIndex:null,
            loader_v0:loader_v0,
            sendGlobe:sendGlobe,
            modelImgPlaceholder:modelImgPlaceholder,
            bUrl:bUrl,
            message: "",
            selecting_binding:false,
            selecting_model:false,
            selectedModel:'',
            isListeningToVoice:false,
            filesList: [],
            isFileSentList: [],
            totalSize: 0,
            showfilesList: true,
            showPersonalities: false,
            personalities_ready: false,
            models_menu_icon:"",
            posts_headers : {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            }
        }
    },
    computed: {
        leftPanelCollapsed(){
            return this.$store.state.leftPanelCollapsed;
        },
        rightPanelCollapsed(){
            return this.$store.state.rightPanelCollapsed;
        },
        isCompactMode() {
            return this.$store.state.view_mode === 'compact';
        },
        isDataSourceNamesValid() {
            console.log('dataSourceNames:', this.dataSourceNames);
            console.log('Type of dataSourceNames:', typeof this.dataSourceNames);
            return Array.isArray(this.dataSourceNames) && this.dataSourceNames.length > 0;
        },        
        dataSourceNames() {
            console.log("dataSourceNames", this.$store.state.config.rag_databases);
            // Extract the names from the rag_databases array and transform them into the desired format
            const formattedDataSources = this.$store.state.config.rag_databases.map(dataSource => {
                console.log("entry", dataSource);
                const parts = dataSource.split('::');
                console.log("extracted", parts[0]);

                const isMounted = dataSource.endsWith('mounted');
                const icon = isMounted ? 'feather:check' : '';

                console.log("icon decision", icon);

                return {
                    name: parts[0], 
                    value: parts[0] || 'default_value', 
                    icon: icon, 
                    help: 'mounts the database'
                };
            });
            console.log("formatted data sources", formattedDataSources);
            return formattedDataSources;
        },    
        currentBindingIcon(){
            return this.currentBinding.icon || this.modelImgPlaceholder;
        },
        currentBinding(){
            return this.$store.state.currentBinding || {};
        },
        currentModel() {
            return this.$store.state.currentModel || {};
        },
        currentModelIcon() {
            return this.currentModel.icon || this.modelImgPlaceholder;
        },
        installedBindings() {
            return this.$store.state.installedBindings;
        },
        installedModels() {
            return this.$store.state.installedModels;
        },
        mountedPersonalities() {
            return this.$store.state.mountedPersArr;
        },
        binding_name(){
            return this.$store.state.config.binding_name    
        },
        model_name(){
            return this.$store.state.config.model_name    
        },
        personality_name(){
            return this.$store.state.config.active_personality_id
        },
        config() {
            return this.$store.state.config;
        },
        mountedPers(){
            return this.$store.state.mountedPers;
        },
        allDiscussionPersonalities() {
            if (this.discussionList.length > 0) {

                let persArray = []
                for (let i = 0; i < this.discussionList.length; i++) {
                    if (!persArray.includes(this.discussionList[i].personality) && !this.discussionList[i].personality == "") {
                        persArray.push(this.discussionList[i].personality)
                    };
                }

                console.log('conputer pers', persArray)
                console.log('dis conputer pers', this.discussionList)
                return persArray
            }
            return null;
        }
    },
    methods: { 
        showPersonalitiesMenu() {
        this.isPersonalitiesMenuVisible = true
        },
        hidePersonalitiesMenu() {
        this.isPersonalitiesMenuVisible = false
        },
        toggleLeftPanel(){
            console.log(this.leftPanelCollapsed)
            this.$store.commit('setLeftPanelCollapsed', ! this.leftPanelCollapsed); // Assuming you have a mutation to set the view mode
        },
        async toggleRightPanel(){
            console.log(this.rightPanelCollapsed)
            this.$store.commit('setRightPanelCollapsed', !this.rightPanelCollapsed); // Assuming you have a mutation to set the view mode
            if(this.rightPanelCollapsed){
                this.$store.commit('setleftPanelCollapsed', true); // Assuming you have a mutation to set the view mode
                this.$nextTick(() => {
                this.extractHtml()
                });

            }
            console.log(this.rightPanelCollapsed)
        }, 

        handlePaste(event) {
            const items = (event.clipboardData || event.originalEvent.clipboardData).items;
            let filesToUpload = [];
            for (let item of items) {
                if (item.type.indexOf("image") !== -1) {
                    const blob = item.getAsFile();
                    // Generate a unique identifier for the file
                    const uniqueId = Date.now() + '_' + Math.random().toString(36).substr(2, 9);
                    const newFileName = `image_${uniqueId}.png`;
                    console.log("newFileName",newFileName)
                    // Create a new file with the unique name
                    const newFile = new File([blob], newFileName, {type: blob.type});

                    this.addFiles([newFile]); // Assuming addFiles accepts an array of files
                }
                else if (item.kind === 'file') {
                    const file = item.getAsFile();
                    filesToUpload.push(file);
                }
            }
            if (filesToUpload.length > 0) {
                this.addFiles(filesToUpload);
            }
        },
        toggleSwitch() {
            this.$store.state.config.activate_internet_search = !this.$store.state.config.activate_internet_search;
            this.isLoading = true;
            axios.post('/apply_settings', {"config":this.$store.state.config}).then((res) => {
                this.isLoading = false;
                //console.log('apply-res',res)
                if (res.data.status) {
                    if(this.$store.state.config.activate_internet_search){
                        this.$store.state.toast.showToast("Websearch activated.", 4, true)
                    }
                    else{
                        this.$store.state.toast.showToast("Websearch deactivated.", 4, true)
                    }
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
        copyModelName(){
            navigator.clipboard.writeText(this.binding_name + "::" + this.model_name);
            this.$store.state.toast.showToast("Model name copyed to clipboard: "+this.binding_name + "::" + this.model_name, 4, true)
        },
        copyModelNameFrom(model){
            navigator.clipboard.writeText(this.binding_name + "::" + model);
            this.$store.state.toast.showToast("Model name copyed to clipboard: "+this.binding_name + "::" + this.model_name, 4, true)
        },
        showModelConfig(){
            try {
                this.isLoading = true
                axios.get('/get_active_binding_settings').then(res => {
                    this.isLoading = false
                    if (res) {

                        console.log('binding sett', res)

                        if (res.data && Object.keys(res.data).length > 0) {

                            // open form

                            this.$refs.universalForm.showForm(res.data, "Binding settings ", "Save changes", "Cancel").then(res => {
                                // send new data
                                try {
                                    axios.post('/set_active_binding_settings',
                                    {client_id:this.$store.state.client_id, "settings":res}).then(response => {

                                            if (response && response.data) {
                                                console.log('binding set with new settings', response.data)
                                                this.$store.state.toast.showToast("Binding settings updated successfully!", 4, true)

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
        async remount_personality(pers) {
            console.log("Remounting personality ", pers)
            if (!pers) { return { 'status': false, 'error': 'no personality - mount_personality' } }
            try {
                console.log("before")
                const obj = {
                    client_id: this.$store.state.client_id,
                    category: pers.category,
                    folder: pers.folder,
                    language: pers.language
                }
                console.log("after")
                const res = await axios.post('/remount_personality', obj);
                console.log("Remounting personality executed:",res)
                

                if (res) {
                    console.log("Remounting personality res")
                    this.$store.state.toast.showToast("Personality remounted", 4, true)

                    return res.data

                }
                else{
                    console.log("failed remount_personality")
                }
            } catch (error) {
                console.log(error.message, 'remount_personality - settings')
                return
            }

        },      
        async unmountPersonality(pers) {
            console.log("Unmounting personality:",pers)
            if (!pers) { return }

            const res = await this.unmount_personality(pers.personality || pers)

            console.log(res)
            if (res.status) {
                this.$store.state.config.personalities = res.personalities
                this.$store.state.toast.showToast("Personality unmounted", 4, true)

                //pers.isMounted = false
                this.$store.dispatch('refreshMountedPersonalities');
                // Select some other personality
                const lastPers = this.$store.state.mountedPersArr[this.$store.state.mountedPersArr.length - 1]

                console.log(lastPers, this.$store.state.mountedPersArr.length)
                // const res2 = await this.select_personality(lastPers.personality)
                const res2 = await this.select_personality(pers.personality)
                if (res2.status) {
                    this.$store.state.toast.showToast("Selected personality:\n" + lastPers.name, 4, true)
                }


            } else {
                this.$store.state.toast.showToast("Could not unmount personality\nError: " + res.error, 4, false)
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
                const res = await axios.post('/unmount_personality', obj);

                if (res) {
                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'unmount_personality - settings')
                return
            }

        },
        async showBindingHoveredIn(index){
            this.bindingHoveredIndex = index
        },
        async showBindingHoveredOut(){
            this.bindingHoveredIndex = null
        },

        async showModelHoveredIn(index){
            this.modelHoveredIndex = index
        },
        async showModelHoveredOut(){
            this.modelHoveredIndex = null
        },
        async showPersonalityHoveredIn(index){
            this.personalityHoveredIndex = index
        },
        async showPersonalityHoveredOut(){
            this.personalityHoveredIndex = null
        },
        async onPersonalitySelected(pers) {
            // eslint-disable-next-line no-unused-vars
            if (pers) {

                if (pers.selected) {
                    this.$store.state.toast.showToast("Personality already selected", 4, true)
                    return
                }


                //this.settingsChanged = true
                const pers_path = pers.language===null?pers.full_path:pers.full_path+':'+pers.language
                console.log("pers_path",pers_path)
                console.log("this.$store.state.config.personalities",this.$store.state.config.personalities)
                if (this.$store.state.config.personalities.includes(pers_path)) {

                    const res = await this.select_personality(pers)
                    await this.$store.dispatch('refreshConfig');    
                    await this.$store.dispatch('refreshBindings');
                    await this.$store.dispatch('refreshModelsZoo');
                    await this.$store.dispatch('refreshModels');
                    await this.$store.dispatch('refreshMountedPersonalities');
                    await this.$store.dispatch('refreshConfig');    
                    await this.$store.dispatch('fetchLanguages');
                    await this.$store.dispatch('fetchLanguage');
                    await this.$store.dispatch('fetchisRTOn');
                    
                    console.log('pers is mounted', res)

                    if (res && res.status && res.active_personality_id > -1) {
                        this.$store.state.toast.showToast("Selected personality:\n" + pers.name, 4, true)

                    } else {
                        this.$store.state.toast.showToast("Error on select personality:\n" + pers.name, 4, false)
                    }

                } else {
                    console.log('mounting pers')
                }

                this.$emit('personalitySelected')
            

                nextTick(() => {
                    feather.replace()

                })

            }

        },    
        async select_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - select_personality' } }
            const pers_path = pers.language===null?pers.full_path:pers.full_path+':'+pers.language
            console.log("Selecting personality ",pers_path)
            const id = this.$store.state.config.personalities.findIndex(item => item === pers_path)

            const obj = {
                client_id:this.$store.state.client_id,
                id: id
            }


            try {
                const res = await axios.post('/select_personality', obj);

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
        emitloaded(){
            this.$emit('loaded')
        },
        showModels(event){
            // Prevent the default button behavior
            event.preventDefault();

            // Programmatically trigger the click event on the select element
            const selectElement = this.$refs.modelsSelectionList;
            console.log(selectElement)

            const event_ = new MouseEvent("click");

            selectElement.dispatchEvent(event_);
        }, 
        setBinding(selectedBinding){
            console.log("Setting binding to "+selectedBinding.name);
            this.selecting_binding=true
            this.selectedBinding = selectedBinding
            this.$store.state.messageBox.showBlockingMessage("Loading binding")

            axios.post("/update_setting", {    
                        client_id: this.$store.state.client_id,
                        setting_name: "binding_name",
                        setting_value: selectedBinding.name
                    }).then(async (response) => {
                this.$store.state.messageBox.hideMessage()
                console.log("UPDATED");
                console.log(response);
                await this.$store.dispatch('refreshConfig');    
                await this.$store.dispatch('refreshBindings');
                await this.$store.dispatch('refreshModelsZoo');
                await this.$store.dispatch('refreshModels');
                
                this.$store.state.toast.showToast(`Binding changed to ${this.currentBinding.name}`,4,true)
                this.selecting_binding=false
                }).catch(err=>{
                this.$store.state.messageBox.hideMessage()
                this.$store.state.toast.showToast(`Error ${err}`,4,true)
                this.selecting_binding=false
                });            
        },
        setModel(selectedModel){
            console.log("Setting model to "+selectedModel.name);
            this.selecting_model=true
            this.selectedModel = selectedModel
            this.$store.state.messageBox.showBlockingMessage("Loading model")
            axios.post("/update_setting", {     
                        client_id: this.$store.state.client_id,           
                        setting_name: "model_name",
                        setting_value: selectedModel.name
                    }).then(async (response) => {
                this.$store.state.messageBox.hideMessage()
                console.log("UPDATED");
                console.log(response);
                await this.$store.dispatch('refreshConfig');    
                await this.$store.dispatch('refreshModels');
                this.$store.state.toast.showToast(`Model changed to ${this.currentModel.name}`,4,true)
                this.selecting_model=false
                }).catch(err=>{
                this.$store.state.messageBox.hideMessage()
                this.$store.state.toast.showToast(`Error ${err}`,4,true)
                this.selecting_model=false
                });
        
        },
        download_files(){
            axios.get('/download_files')
        },
        remove_file(file){
            axios.get('/remove_discussion_file',{client_id:this.$store.state.client_id, name: file}).then(res=>{
                console.log(res)
            })
        },
        clear_files(){
            axios.post('/clear_discussion_files_list', {"client_id":this.$store.state.client_id}).then(res=>{
                console.log(res)
                if(res.data.state){
                    this.$store.state.toast.showToast("File removed successfully",4,true);
                    this.filesList.length = 0;
                    this.isFileSentList.length = 0;
                    this.totalSize = 0;
                }
                else{
                    this.$store.state.toast.showToast("Files couldn't be removed",4,false);
                }
            })

        },
        send_file(file, next) {
            console.log("Send file triggered")
            const fileReader = new FileReader();
            const chunkSize = 24 * 1024; // Chunk size in bytes (e.g., 1MB)
            let offset = 0;
            let chunkIndex = 0;
            fileReader.onloadend = () => {
                if (fileReader.error) {
                console.error('Error reading file:', fileReader.error);
                return;
                }
                const chunk = fileReader.result;
                const isLastChunk = offset + chunk.byteLength >= file.size;
                socket.emit('send_file_chunk', {
                filename: file.name,
                chunk: chunk,
                offset: offset,
                isLastChunk: isLastChunk,
                chunkIndex: chunkIndex
                });
                offset += chunk.byteLength;
                chunkIndex++;
                if (!isLastChunk) {
                    readNextChunk();
                } else {
                    console.log('File sent successfully');
                    this.isFileSentList[this.filesList.length-1]=true;
                    console.log(this.isFileSentList)
                    this.$store.state.toast.showToast("File uploaded successfully",4,true);
                    next();
                }
            };
            function readNextChunk() {
                const blob = file.slice(offset, offset + chunkSize);
                fileReader.readAsArrayBuffer(blob);
            }
            console.log('Uploading file');
            readNextChunk();
        },    
        makeAnEmptyUserMessage() {
            this.$emit('createEmptyUserMessage',this.message)
            this.message=""
        },
        makeAnEmptyAIMessage() {
            this.$emit('createEmptyAIMessage')
        },
        startRTCom(){
            this.is_rt = true
            console.log("is_rt:",this.is_rt)
            socket.emit('start_bidirectional_audio_stream');
            nextTick(() => {
                feather.replace()
            })
        },
        stopRTCom(){
            this.is_rt = false
            console.log("is_rt:",this.is_rt)
            socket.emit('stop_bidirectional_audio_stream');
            nextTick(() => {
                feather.replace()
            }
            )
        },
        startSpeechRecognition() {
            if ('SpeechRecognition' in window || 'webkitSpeechRecognition' in window) {
                this.recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
                this.recognition.lang = this.$store.state.config.audio_in_language; // Set the language, adjust as needed
                this.recognition.interimResults = true; // Enable interim results to get real-time updates

                this.recognition.onstart = () => {
                this.isListeningToVoice = true;
                this.silenceTimer = setTimeout(() => {
                    this.recognition.stop();
                }, this.silenceTimeout); // Set the silence timeout to stop recognition
                };

                this.recognition.onresult = (event) => {
                let result = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    result += event.results[i][0].transcript;
                }
                this.message = result; // Update the textarea with the real-time recognized words
                clearTimeout(this.silenceTimer); // Clear the silence timeout on every recognized result
                this.silenceTimer = setTimeout(() => {
                    this.recognition.stop();
                }, this.silenceTimeout); // Set a new silence timeout after every recognized result
                };

                this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isListeningToVoice = false;
                clearTimeout(this.silenceTimer); // Clear the silence timeout on error
                };

                this.recognition.onend = () => {
                console.log('Speech recognition ended.');
                this.isListeningToVoice = false;
                clearTimeout(this.silenceTimer); // Clear the silence timeout when recognition ends normally
                this.submit(); // Call the function to handle form submission or action once speech recognition ends
                };

                this.recognition.start();
            } else {
                console.error('Speech recognition is not supported in this browser.');
            }
        },

        onPersonalitiesReadyFun(){
            this.personalities_ready = true;
        },
        onShowPersListFun(comp) {
            this.showPersonalities = !this.showPersonalities

        },
        handleOnTalk(pers){
            console.log("talking")
            this.showPersonalities=false
            this.$store.state.toast.showToast(`Personality ${pers.name} is Talking`, 4, true)
            this.onTalk(pers)
        },
                            
        onMountFun(comp) {
            console.log('Mounting personality')
            this.$refs.mountedPers.constructor()
        },     
        onUnmountFun(comp) {
            console.log('Unmounting personality')
            this.$refs.mountedPers.constructor()
            
        },
        onRemount(comp){
            console.log('Remounting chat')
            this.$refs.mountedPers.constructor()
        },
        computedFileSize(size) {
            nextTick(() => {
                feather.replace()
            })
            return filesize(size)
        },

        removeItem(file) {
            console.log("Removing ",file.name)
            axios.post('/remove_discussion_file',{
                                        client_id:this.$store.state.client_id, 
                                        name:file.name
                                    },
                                    {headers: this.posts_headers}
                                ).then(()=>{
                    this.filesList = this.filesList.filter((item) => item != file)
                })            

            console.log(this.filesList)
        },
        sendMessageEvent(msg, type="no_internet") {
            this.$emit('messageSentEvent', msg, type)

        },
        sendCMDEvent(cmd){
            this.$emit('sendCMDEvent', cmd)
        },
        async mountDB(cmd){
            await axios.post('/toggle_mount_rag_database', {"client_id":this.$store.state.client_id,"database_name":cmd})
            await this.$store.dispatch('refreshConfig');
            console.log("Refreshed")

        },
        addWebLink(){
            console.log("Emitting addWebLink")
            this.$emit('addWebLink')
        },
        add_file(){
            // Create a new hidden input element
            const input = document.createElement('input');
            input.type = 'file';
            input.style.display = 'none';
            input.multiple = true;

            // Append the input to the body
            document.body.appendChild(input);

            // Listen for the change event
            input.addEventListener('change', () => {
                // Call the add file function
                console.log("Calling Add file...")
                this.addFiles(input.files);

                // Remove the input element from the DOM
                document.body.removeChild(input);
            });            
            // Trigger the file dialog
            input.click();
       },
        takePicture(){
            socket.emit('take_picture')
            socket.on('picture_taken',()=>{
                axios.post('/get_discussion_files_list', {"client_id":this.$store.state.client_id}).then(res=>{
                    this.filesList = res.data.files;
                    this.isFileSentList= res.data.files.map(file => {
                        return true;
                    });
                    console.log(`Files recovered: ${this.filesList}`)
                })
            });
        },
        submitOnEnter(event) {
            if(!this.loading){
                if (event.which === 13) {
                    event.preventDefault(); // Prevents the addition of a new line in the text field

                    if (!event.repeat) {

                        this.sendMessageEvent(this.message)
                        this.message = "" // Clear input field
                    }

                }
            }
        },
        submit() {
            if (this.message) {
                this.sendMessageEvent(this.message)
                this.message = ""
            }

        },
        submitWithInternetSearch(){
            if (this.message) {
                this.sendMessageEvent(this.message, "internet")
                this.message = ""
            }

        },
        stopGenerating() {
            this.$emit('stopGenerating')
        },
        addFiles(files) {
            console.log("Adding files");
            const newFiles = [...files];
            let index = 0;
            const sendNextFile = () => {
                if (index >= newFiles.length) {
                console.log(`Files_list: ${this.filesList}`);
                return;
                }
                const file = newFiles[index];
                this.filesList.push(file);
                this.isFileSentList.push(false);
                this.send_file(file, () => {
                index++;
                sendNextFile();
                }
                );
            };
            sendNextFile();
        }
    },
    watch: {
        installedModels: {
            immediate: true,
            handler(newVal) {
                this.$nextTick(() => {
                this.installedModels = newVal;
                });
            },
        },   
        model_name: {
            immediate: true,
            handler(newVal) {
                this.$nextTick(() => {
                this.model_name = newVal;
                });
            },
        },                
        showfilesList() {
            nextTick(() => {
                feather.replace()
            })
        },
        loading(newval, oldval) {
            nextTick(() => {
                feather.replace()
            })
        },
        filesList: {
            // Calculate total size
            handler(val, oldVal) {
                let total = 0
                if (val.length > 0) {
                    for (let i = 0; i < val.length; i++) {
                        total = total + parseInt(val[i].size)
                    }
                }
                this.totalSize = filesize(total, true)
                console.log("filesList changed")

            },
            deep: true
        },
        discussionList(val) {

            console.log('discussion arr', val)
        }

    },
    mounted() {
        this.emitloaded();
        nextTick(() => {
            feather.replace()
        })
        console.log("Chatbar mounted")
        socket.on('rtcom_status_changed', (data)=>{
                this.$store.dispatch('fetchisRTOn');
                console.log("rtcom_status_changed: ",data.status)
                console.log("active_tts_service: ",this.$store.state.config.active_tts_service)
                console.log("is_rt_on: ",this.$store.state.is_rt_on)
                //this.is_rt = this.$store.state.is_rt_on
            });
        this.$store.dispatch('fetchisRTOn');
    },
    
    activated() {
        nextTick(() => {
            feather.replace()
        })
    }
}
</script>
