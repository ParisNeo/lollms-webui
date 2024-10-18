<template>
    <transition name="fade-and-fly">
        <div v-if="!isReady" class="fixed top-0 left-0 w-screen h-screen flex items-center justify-center bg-gradient-to-br from-blue-400 to-purple-100 dark:from-blue-900 dark:to-purple-900 overflow-hidden">
        <!-- Falling strawberries -->
        <div class="absolute inset-0 pointer-events-none overflow-hidden">
            <div v-for="n in 50" :key="n" class="absolute animate-fall animate-giggle"
                :style="{
                left: `${Math.random() * 100}%`,
                top: `-20px`,
                animationDuration: `${3 + Math.random() * 7}s`,
                animationDelay: `${Math.random() * 5}s`
                }">
            🌟
            </div>
        </div>

        <div class="flex flex-col items-center text-center max-w-4xl w-full px-4 relative z-10">
            <div class="mb-8 w-full">
                <div class="text-6xl md:text-7xl font-bold text-amber-500 mb-2"
                    style="text-shadow: 2px 2px 0px white, -2px -2px 0px white, 2px -2px 0px white, -2px 2px 0px white;">
                    L🌟LLMS
                </div>

            <p class="text-2xl text-gray-600 dark:text-gray-300 italic">
                One tool to rule them all
            </p>
            <p class="text-xl text-gray-500 dark:text-gray-400 mb-6">
                by ParisNeo
            </p>
            <p class="bottom-0 text-2xl text-gray-600 dark:text-gray-300 italic">
                {{ version_info }}
            </p>

            <div class="w-full h-24 relative overflow-hidden bg-gradient-to-r from-blue-200 to-purple-200 dark:from-blue-800 dark:to-purple-800 rounded-full shadow-lg flex items-center justify-center">
                <p style="font-size: 48px; line-height: 1;">🌟</p>
            </div>

            </div>
            
            <div class="w-full max-w-2xl">
            <div role="status" class="w-full">
                <p class="text-xl text-gray-700 dark:text-gray-300">
                {{ loading_infos }}...
                </p>
                <p class="text-2xl font-bold text-blue-600 dark:text-blue-400 mt-2">
                {{ Math.round(loading_progress) }}%
                </p>
            </div>
            </div>
        </div>
    </div>
    </transition>
    <transition name="slide-right">
    <div  v-if="showLeftPanel"
        class="relative flex flex-col no-scrollbar shadow-lg min-w-[15rem] max-w-[15rem]"
        >
            <RouterLink :to="{ name: 'discussions' }" class="flex items-center space-x-2"> <!-- Added space-x-2 -->
                <div class="logo-container"> <!-- Removed mr-1 -->
                <img class="w-12 h-12 rounded-full object-cover logo-image" 
                    :src="$store.state.config == null ? storeLogo : $store.state.config.app_custom_logo != '' ? '/user_infos/' + $store.state.config.app_custom_logo : storeLogo" 
                    alt="Logo" title="LoLLMS WebUI">
                </div>
                <div class="flex flex-col justify-center">
                <div class="text-6xl md:text-2xl font-bold text-amber-500 mb-2"
                    style="text-shadow: 2px 2px 0px white, -2px -2px 0px white, 2px -2px 0px white, -2px 2px 0px white;">
                    L🌟LLMS
                </div>
                <p class="text-gray-400 text-sm">One tool to rule them all</p>
                </div>
            </RouterLink>

            <div class="toolbar discussion">
                <!-- Toolbar container -->
                <div class="toolbar-container">                    
                    <!-- "+" button -->
                    <button 
                        class="toolbar-button" 
                        title="Create new discussion" 
                        @click="createNewDiscussion"
                    >
                        <i data-feather="plus"></i>
                    </button>

                    <!-- Menu container -->
                    <div class="menu-container">
                    <!-- Menu toggle button -->
                    <button 
                    class="toolbar-button" 
                    title="Toggle menu" 
                    @click="toggleMenu"
                    >
                    <i data-feather="menu"></i>
                    </button>

                    <!-- Expandable menu -->
                    <div v-if="isMenuVisible" class="expandable-menu discussion z-50 p-4 bg-white dark:bg-bg-dark rounded-lg shadow-lg">
                        <!-- Edit discussion list -->
                        <button class="text-3xl hover:text-secondary dark:hover:text-secondary-light duration-150 active:scale-95" title="Edit discussion list" type="button" @click="isCheckbox = !isCheckbox" :class="isCheckbox ? 'text-secondary dark:text-secondary-light' : 'text-gray-700 dark:text-gray-300'">
                        <i data-feather="check-square"></i>
                        </button>

                        <!-- Reset database -->
                        <button class="text-3xl hover:text-red-500 dark:hover:text-red-400 duration-150 active:scale-95" title="Reset database, remove all discussions" @click.stop="">
                        <i data-feather="trash-2"></i>
                        </button>

                        <!-- Export database -->
                        <button class="text-3xl hover:text-secondary dark:hover:text-secondary-light duration-150 active:scale-95" title="Export database" type="button" @click.stop="database_selectorDialogVisible=true">
                        <i data-feather="database"></i>
                        </button>

                        <!-- Import discussions -->
                        <input type="file" ref="fileDialog" class="hidden" @change="importDiscussions" />
                        <button class="text-3xl hover:text-secondary dark:hover:text-secondary-light duration-150 active:scale-95 rotate-90" title="Import discussions" type="button" @click.stop="$refs.fileDialog.click()">
                        <i data-feather="log-in"></i>
                        </button>

                        <!-- Import discussion bundle -->
                        <input type="file" ref="bundleLoadingDialog" class="hidden" @change="importDiscussionsBundle" />
                        <button v-if="!showSaveConfirmation" title="Import discussion bundle" @click.stop="$refs.bundleLoadingDialog.click()" class="text-3xl hover:text-secondary dark:hover:text-secondary-light duration-150 active:scale-95">
                        <i data-feather="folder"></i>
                        </button>

                        <!-- Filter discussions -->
                        <button class="text-3xl hover:text-secondary dark:hover:text-secondary-light duration-150 active:scale-95" title="Filter discussions" type="button" @click="isSearch = !isSearch" :class="isSearch ? 'text-secondary dark:text-secondary-light' : 'text-gray-700 dark:text-gray-300'">
                        <i data-feather="search"></i>
                        </button>

                        <!-- Add to skills database -->
                        <button v-if="!loading" type="button" @click.stop="addDiscussion2SkillsLibrary" title="Add this discussion content to skills database" class="text-3xl hover:text-secondary dark:hover:text-secondary-light duration-150 active:scale-95">
                        <i data-feather="hard-drive"></i>
                        </button>

                        <!-- Toggle skills database -->
                        <button v-if="!loading && $store.state.config.activate_skills_lib" type="button" @click.stop="toggleSkillsLib" title="Skills database is activated" class="text-3xl hover:text-secondary dark:hover:text-secondary-light duration-150 active:scale-95">
                        <i data-feather="check-circle"></i>
                        </button>
                        <button v-if="!loading && !$store.state.config.activate_skills_lib" type="button" @click.stop="toggleSkillsLib" title="Skills database is deactivated" class="text-3xl hover:text-secondary dark:hover:text-secondary-light duration-150 active:scale-95">
                        <i data-feather="x-octagon"></i>
                        </button>

                        <!-- Show skills database -->
                        <button v-if="!loading" type="button" @click.stop="showSkillsLib" title="Show Skills database" class="text-3xl hover:text-secondary dark:hover:text-secondary-light duration-150 active:scale-95">
                        <i data-feather="book"></i>
                        </button>

                        <!-- Loading spinner -->
                        <div v-if="loading" title="Loading.." class="flex justify-center mt-4">
                            <div role="status">
                            <svg aria-hidden="true" class="w-8 h-8 animate-spin fill-secondary dark:fill-secondary-light" viewBox="0 0 100 101" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M100 50.5908C100 78.2051 77.6142 100.591 50 100.591C22.3858 100.591 0 78.2051 0 50.5908C0 22.9766 22.3858 0.59082 50 0.59082C77.6142 0.59082 100 22.9766 100 50.5908ZM9.08144 50.5908C9.08144 73.1895 27.4013 91.5094 50 91.5094C72.5987 91.5094 90.9186 73.1895 90.9186 50.5908C90.9186 27.9921 72.5987 9.67226 50 9.67226C27.4013 9.67226 9.08144 27.9921 9.08144 50.5908Z" fill="currentColor" />
                                <path d="M93.9676 39.0409C96.393 38.4038 97.8624 35.9116 97.0079 33.5539C95.2932 28.8227 92.871 24.3692 89.8167 20.348C85.8452 15.1192 80.8826 10.7238 75.2124 7.41289C69.5422 4.10194 63.2754 1.94025 56.7698 1.05124C51.7666 0.367541 46.6976 0.446843 41.7345 1.27873C39.2613 1.69328 37.813 4.19778 38.4501 6.62326C39.0873 9.04874 41.5694 10.4717 44.0505 10.1071C47.8511 9.54855 51.7191 9.52689 55.5402 10.0491C60.8642 10.7766 65.9928 12.5457 70.6331 15.2552C75.2735 17.9648 79.3347 21.5619 82.5849 25.841C84.9175 28.9121 86.7997 32.2913 88.1811 35.8758C89.083 38.2158 91.5421 39.6781 93.9676 39.0409Z" fill="currentFill" />
                            </svg>
                            <span class="sr-only">Loading...</span>
                            </div>
                        </div>

                        <!-- Save confirmation -->
                        <div v-if="showSaveConfirmation" class="flex justify-center mt-4 space-x-4">
                            <button class="text-3xl hover:text-red-500 dark:hover:text-red-400 duration-150 active:scale-95" title="Cancel" type="button" @click.stop="showSaveConfirmation = false">
                            <i data-feather="x"></i>
                            </button>
                            <button class="text-3xl hover:text-green-500 dark:hover:text-green-400 duration-150 active:scale-95" title="Confirm save changes" type="button" @click.stop="save_configuration()">
                            <i data-feather="check"></i>
                            </button>
                        </div>

                        <!-- Import options -->
                        <div v-if="isOpen" class="flex flex-col space-y-2 mt-4">
                            <button @click="importDiscussions" class="text-sm hover:text-secondary dark:hover:text-secondary-light">LOLLMS</button> 
                            <button @click="importChatGPT" class="text-sm hover:text-secondary dark:hover:text-secondary-light">ChatGPT</button>
                        </div>
                    </div>
                    <button @click="toggleInfosMenu" title="Infos">
                        <svg xmlns="http://www.w3.org/2000/svg" width="25" height="25" viewBox="0 0 25 25">
                        <!-- Circle background -->
                        <circle cx="12.5" cy="12.5" r="11.25" fill="#3498db"/>
                        
                        <!-- "i" stem -->
                        <rect x="11.25" y="10" width="2.5" height="8.75" fill="white"/>
                        
                        <!-- "i" dot -->
                        <circle cx="12.5" cy="6.25" r="1.25" fill="white"/>
                        </svg>
                    </button>
                    <!-- Menu Content -->
                    <nav v-if="isinfosMenuVisible" class="expandable-menu discussion z-50 p-4 bg-white dark:bg-bg-dark rounded-lg shadow-lg ">
                        <div class="container flex flex-col lg:flex-row items-center gap-2 p-4">
                        <!-- SYSTEM STATUS -->
                        <div class="flex gap-3 flex-1 items-center justify-end">
                            <div v-if="isModelOK" title="Model is ok" class="text-green-500 dark:text-green-400 cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M9 12L11 14L15 10" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            </div>
                            <div v-else title="Model is not ok" class="text-red-500 dark:text-red-400 cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-8 h-8" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M21 12C21 16.9706 16.9706 21 12 21C7.02944 21 3 16.9706 3 12C3 7.02944 7.02944 3 12 3C16.9706 3 21 7.02944 21 12Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M15 9L9 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                                <path d="M9 9L15 15" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                            </div>
                            <div v-if="!isGenerating" title="Text is not being generated. Ready to generate" class="text-green-500 dark:text-green-400 cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 21v-4m0 0V5a2 2 0 012-2h6.5l1 1H21l-3 6 3 6h-8.5l-1-1H5a2 2 0 00-2 2zm9-13.5V9"></path>
                            </svg>
                            </div>
                            <div v-else title="Generation in progress..." class="text-yellow-500 dark:text-yellow-400 cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-6 h-6 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                            </svg>
                            </div>
                            <div v-if="isConnected" title="Connection status: Connected" class="text-green-500 dark:text-green-400 cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path>
                            </svg>
                            </div>
                            <div v-else title="Connection status: Not connected" class="text-red-500 dark:text-red-400 cursor-pointer transition-transform hover:scale-110">
                            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18.364 18.364A9 9 0 005.636 5.636m12.728 12.728A9 9 0 015.636 5.636m12.728 12.728L5.636 5.636"></path>
                            </svg>
                            </div>
                        </div>
                        <div class="flex items-center space-x-4">
                            <ActionButton @click="restartProgram" icon="power" title="restart program" />
                            <ActionButton @click="refreshPage" icon="refresh-ccw" title="refresh page" />
                            <ActionButton href="/docs" icon="file-text" title="Fast API doc" />
                        </div>

                        <!-- SOCIALS -->
                        <SocialIcon href="https://github.com/ParisNeo/lollms-webui" icon="github" />
                        <SocialIcon href="https://www.youtube.com/channel/UCJzrg0cyQV2Z30SQ1v2FdSQ" icon="youtube" />
                        <SocialIcon href="https://x.com/ParisNeo_AI" icon="x" />
                        <SocialIcon href="https://discord.com/channels/1092918764925882418" icon="discord" />
                
                        <div class="relative group" title="Lollms News">
                            <div @click="showNews()" class="text-2xl w-8 h-8 cursor-pointer transition-colors duration-300 text-gray-600 hover:text-primary dark:text-gray-300 dark:hover:text-primary">
                            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-full h-full">
                                <path d="M19 20H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h10a2 2 0 0 1 2 2v1m2 13a2 2 0 0 1-2-2V7m2 13a2 2 0 0 0 2-2V9a2 2 0 0 0-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path>
                            </svg>
                            </div>
                            <span class="absolute hidden group-hover:block bg-gray-800 text-white text-xs rounded py-1 px-2 top-full left-1/2 transform -translate-x-1/2 mt-2 whitespace-nowrap">
                            Lollms News
                            </span>
                        </div>

                            <div 
                                v-if="is_fun_mode" 
                                title="Fun mode is on, press to turn off" 
                                class="w-8 h-8 cursor-pointer text-green-500 dark:text-green-400 hover:text-green-600 dark:hover:text-green-300 transition-colors duration-300"
                                @click="fun_mode_off()"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-full h-full animate-bounce">
                                <circle cx="12" cy="12" r="10"></circle>
                                <path d="M8 14s1.5 2 4 2 4-2 4-2"></path>
                                <line x1="9" y1="9" x2="9.01" y2="9"></line>
                                <line x1="15" y1="9" x2="15.01" y2="9"></line>
                                </svg>
                            </div>
                            <div 
                                v-else 
                                title="Fun mode is off, press to turn on" 
                                class="w-8 h-8 cursor-pointer text-gray-500 dark:text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors duration-300"
                                @click="fun_mode_on()"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="w-full h-full">
                                <circle cx="12" cy="12" r="10"></circle>
                                <line x1="8" y1="15" x2="16" y2="15"></line>
                                <line x1="9" y1="9" x2="9.01" y2="9"></line>
                                <line x1="15" y1="9" x2="15.01" y2="9"></line>
                                </svg>
                            </div>
                            <span class="absolute hidden group-hover:block bg-gray-800 text-white text-xs rounded py-1 px-2 top-full left-1/2 transform -translate-x-1/2 mb-2 whitespace-nowrap">
                                {{ is_fun_mode ? 'Turn off fun mode' : 'Turn on fun mode' }}
                            </span>
                        <div class="language-selector relative">
                            <button @click="toggleLanguageMenu" class="bg-transparent text-black dark:text-white py-1 px-1 rounded font-bold uppercase transition-colors duration-300 hover:bg-blue-500">
                            {{ $store.state.language.slice(0, 2) }}
                            </button>
                            <div v-if="isLanguageMenuVisible" ref="languageMenu" class="container language-menu absolute left-0 mt-1 bg-white dark:bg-bg-dark-tone rounded shadow-lg z-10 overflow-y-auto scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary" style="position: absolute; top: 100%; width: 200px; max-height: 300px; overflow-y: auto;">
                            <ul style="list-style-type: none; padding-left: 0; margin-left: 0;">
                                <li v-for="language in languages" :key="language" class="relative flex items-center" style="padding-left: 0; margin-left: 0;">
                                <button @click="deleteLanguage(language)" class="mr-2 text-red-500 hover:text-white hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 rounded-full">✕</button>
                                <div @click="selectLanguage(language)" :class="{'cursor-pointer hover:bg-blue-500 hover:text-white py-2 px-4 block whitespace-no-wrap': true, 'bg-blue-500 text-white': language === $store.state.language, 'flex-grow': true}">
                                    {{ language }}
                                </div>
                                </li>
                                <li class="cursor-pointer hover:text-white py-0 px-0 block whitespace-no-wrap">
                                <input type="text" v-model="customLanguage" @keyup.enter.prevent="addCustomLanguage" placeholder="Enter language..." class="bg-transparent border border-gray-300 rounded py-0 px-0 mx-0 my-1 w-full">
                                </li>
                            </ul>
                            </div>
                        </div>
                        <div class="sun text-2xl w-6 hover:text-primary duration-150 cursor-pointer" title="Switch to Light theme" @click="themeSwitch()">
                            <i data-feather="sun"></i>
                        </div>
                        <div class="moon text-2xl w-6 hover:text-primary duration-150 cursor-pointer" title="Switch to Dark theme" @click="themeSwitch()">
                            <i data-feather="moon"></i>
                        </div>
                        </div>
                    </nav>                        
                </div>
            </div>
        </div>
        <!-- Search bar -->
        <div v-if="isSearch" class="w-full p-4 bg-bg-light dark:bg-bg-dark">
            <div class="relative">
            <div class="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
                <div class="scale-75">
                <i data-feather="search"></i>
                </div>
            </div>
            <div class="absolute inset-y-0 right-0 flex items-center pr-3">
                <div class="hover:text-secondary duration-75 active:scale-90" :class="filterTitle ? 'visible' : 'invisible'" title="Clear" @click="filterTitle = ''">
                <i data-feather="x"></i>
                </div>
            </div>
            <input type="search" id="default-search" class="block w-full p-2 pl-10 pr-10 text-sm border border-gray-300 rounded-lg bg-bg-light focus:ring-secondary focus:border-secondary dark:bg-bg-dark dark:border-gray-600 dark:placeholder-gray-400 dark:focus:ring-secondary dark:focus:border-secondary" placeholder="Search..." title="Filter discussions by title" v-model="filterTitle" @input="filterDiscussions()" />
            </div>
        </div>

        <!-- Checkbox operations -->
        <div v-if="isCheckbox" class="w-full p-4 bg-bg-light dark:bg-bg-dark">
            <div class="flex flex-col space-y-2">
                <p v-if="selectedDiscussions.length > 0">Selected: {{ selectedDiscussions.length }}</p>
                <div v-if="selectedDiscussions.length > 0" class="flex space-x-2">
                    <button v-if="!showConfirmation" class="text-2xl hover:text-red-600 duration-75 active:scale-90" title="Remove selected" type="button" @click.stop="showConfirmation = true">
                    <i data-feather="trash"></i>
                    </button>
                    <div v-if="showConfirmation" class="flex space-x-2">
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Confirm removal" type="button" @click.stop="deleteDiscussionMulti">
                        <i data-feather="check"></i>
                    </button>
                    <button class="text-2xl hover:text-red-600 duration-75 active:scale-90" title="Cancel removal" type="button" @click.stop="showConfirmation = false">
                        <i data-feather="x"></i>
                    </button>
                    </div>
                </div>
                <div class="flex space-x-2">
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90 rotate-90" title="Export selected to a json file" type="button" @click.stop="exportDiscussionsAsJson">
                    <i data-feather="codepen"></i>
                    </button>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90 rotate-90" title="Export selected to a markdown file" type="button" @click.stop="exportDiscussions">
                    <i data-feather="folder"></i>
                    </button>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90 rotate-90" title="Export selected to a markdown file" type="button" @click.stop="exportDiscussionsAsMarkdown">
                    <i data-feather="bookmark"></i>
                    </button>
                    <button class="text-2xl hover:text-secondary duration-75 active:scale-90" title="Select All" type="button" @click.stop="selectAllDiscussions">
                    <i data-feather="list"></i>
                    </button>
                </div>
            </div>
        </div>
        <!-- LEFT SIDE PANEL -->
        <div id="leftPanel" class="flex flex-col flex-grow overflow-y-scroll overflow-x-hidden custom-scrollbar "
            @dragover.stop.prevent="setDropZoneDiscussion()">

            <div class="relative flex flex-row flex-grow mb-10 z-0  w-full">
                <!-- DISCUSSION LIST -->
                <div class="mx-0 flex flex-col flex-grow  w-full " :class="isDragOverDiscussion ? 'pointer-events-none' : ''">
                    <div id="dis-list" :class="filterInProgress ? 'opacity-20 pointer-events-none' : ''"
                        class="flex flex-col flex-grow w-full pb-80">
                        <TransitionGroup v-if="list.length > 0" name="list">
                            <Discussion v-for="(item, index) in list" :key="item.id" :id="item.id" :title="item.title"
                                :selected="currentDiscussion.id == item.id" :loading="item.loading" :isCheckbox="isCheckbox"
                                :checkBoxValue="item.checkBoxValue" 
                                @select="selectDiscussion(item)"
                                @delete="deleteDiscussion(item.id)" 
                                @openFolder="openFolder"
                                @editTitle="editTitle" 
                                @makeTitle="makeTitle"
                                @checked="checkUncheckDiscussion" />
                        </TransitionGroup>
                        <div v-if="list.length < 1"
                            class="gap-2 py-2 my-2 hover:shadow-md hover:bg-primary-light dark:hover:bg-primary rounded-md p-2 duration-75 group cursor-pointer">
                            <p class="px-3">No discussions are found</p>
                        </div>
                        <div
                            class="sticky bottom-0 bg-gradient-to-t pointer-events-none from-bg-light-tone dark:from-bg-dark-tone flex flex-grow">
                            <!-- FADING DISCUSSION LIST END ELEMENT -->
                        </div>
                    </div>
                </div>
            </div>
        </div>
        <div class="flex flex-row panels-color">
            <div class="h-15 w-full  py-4 cursor-pointer text-light-text-panel dark:text-dark-text-panel hover:text-secondary" @click="showDatabaseSelector">
                <p class="text-center font-large font-bold text-l drop-shadow-md align-middle">{{ formatted_database_name.replace("_"," ") }}</p>
            </div>
        </div>
    </div>
    </transition>
        <div v-if="isReady" class="relative flex flex-col flex-grow" >
            <div id="messages-list"
                class="w-full z-0 flex flex-col  flex-grow  overflow-y-auto scrollbar"
                :class="isDragOverChat ? 'pointer-events-none' : ''">

                <!-- CHAT AREA -->
                <div class="container pt-4 pb-50 mb-50 w-full">
                    <TransitionGroup v-if="discussionArr.length > 0" name="list">
                        <Message v-for="(msg, index) in discussionArr" 
                            :key="msg.id" :message="msg"  :id="'msg-' + msg.id" :ref="'msg-' + msg.id"
                            :host="host"
                            
                            @copy="copyToClipBoard" @delete="deleteMessage" @rankUp="rankUpMessage"
                            @rankDown="rankDownMessage" @updateMessage="updateMessage" @resendMessage="resendMessage" @continueMessage="continueMessage"
                            :avatar="getAvatar(msg.sender)" />
                        
                        <!-- REMOVED FOR NOW, NEED MORE TESTING -->
                        <!-- @click="scrollToElementInContainer($event.target, 'messages-list')"  -->
                        <div  v-if="discussionArr.length < 2 && personality.prompts_list.length > 0"  class="w-full rounded-lg m-2 shadow-lg hover:border-primary dark:hover:border-primary hover:border-solid hover:border-2 border-2 border-transparent even:bg-bg-light-discussion-odd dark:even:bg-bg-dark-discussion-odd flex flex-col overflow-hidden p-4 pb-2 h-[600px]">
                            <h2 class="text-2xl font-bold mb-4">Prompt examples</h2>
                            <div v-if="discussionArr.length < 2 && personality.prompts_list.length > 0" 
                                class="overflow-y-auto flex-grow pr-2 custom-scrollbar">
                                <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4 p-2">
                                <div 
                                    v-for="(prompt, index) in personality.prompts_list" 
                                    :key="index" 
                                    @click="selectPrompt(prompt)"
                                    class="bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg p-4 cursor-pointer hover:shadow-lg transition-all duration-300 ease-in-out transform hover:scale-105 flex flex-col justify-between h-[220px] overflow-hidden group"
                                >
                                    <div 
                                    :title="prompt" 
                                    class="text-base text-gray-700 dark:text-gray-300 overflow-hidden relative h-full"
                                    >
                                    <div class="absolute inset-0 overflow-hidden">
                                        {{ prompt }}
                                    </div>
                                    <div class="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-white dark:to-gray-800 group-hover:opacity-0 transition-opacity duration-300"></div>
                                    </div>
                                    <div class="mt-2 text-sm text-gray-500 dark:text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                                    Click to select
                                    </div>
                                </div>
                                </div>
                            </div>
                        </div>


                    </TransitionGroup>
                    <WelcomeComponent v-if="!currentDiscussion.id" />
                    <div><br><br><br><br><br><br><br></div>
                </div>

                <div
                    class="absolute w-full bottom-0 bg-transparent p-10 pt-16 bg-gradient-to-t from-bg-light dark:from-bg-dark from-5% via-bg-light dark:via-bg-dark via-10% to-transparent to-100%">
                </div>
            </div>
            <div class="flex flex-row items-center justify-center h-10" v-if="currentDiscussion.id">
                <ChatBox ref="chatBox" 
                    :loading="isGenerating" 
                    :discussionList="discussionArr" 
                    :on-show-toast-message="showToastMessage"
                    :on-talk="talk"

                    @personalitySelected="recoverFiles"
                    @messageSentEvent="sendMsg" 
                    @sendCMDEvent="sendCmd"
                    @addWebLink="add_webpage"
                    @createEmptyUserMessage="createEmptyUserMessage"
                    @createEmptyAIMessage="createEmptyAIMessage"
                    @stopGenerating="stopGenerating" 
                    @loaded="recoverFiles"
                    >
                </ChatBox>
            </div>        
        </div>
    <transition name="slide-left">
    <div  v-if="showRightPanel"
        class="relative flex flex-col no-scrollbar shadow-lg w-1/2 bg-bg-light-tone dark:bg-bg-dark-tone h-full"
        >
        <!-- RIGHT SIDE PANEL -->
         <!--  <div v-html="lastMessageHtml"></div> --> 
        <div ref="isolatedContent" class="h-full"></div>
    </div>
    </transition>
    <ChoiceDialog reference="database_selector" class="z-20"
      :show="database_selectorDialogVisible"
      :choices="databases"
      :can-remove=true      
      @choice-removed="ondatabase_selectorDialogRemoved"
      @choice-selected="ondatabase_selectorDialogSelected"
      @close-dialog="onclosedatabase_selectorDialog"
      @choice-validated="onvalidatedatabase_selectorChoice"
    />      
    <div v-show="progress_visibility" role="status" class="fixed m-0 p-2 left-2 bottom-2  min-w-[24rem] max-w-[24rem] h-20 flex flex-col justify-center items-center pb-4 bg-blue-500 rounded-lg shadow-lg z-50 background-a">
        <ProgressBar ref="progress" :progress="progress_value" class="w-full h-4"></ProgressBar>
        <p class="text-2xl animate-pulse mt-2 text-light-text-panel dark:text-dark-text-panel">{{ loading_infos }} ...</p>
    </div>
    <InputBox prompt-text="Enter the url to the page to use as discussion support" @ok="addWebpage" ref="web_url_input_box"></InputBox>   
    <SkillsLibraryViewer ref="skills_lib" ></SkillsLibraryViewer>
    <Toast ref="toast" />
    <MessageBox ref="messageBox" />
    <div v-show="progress_visibility" role="status" class="fixed m-0 p-2 left-2 bottom-2 min-w-[24rem] max-w-[24rem] h-20 flex flex-col justify-center items-center pb-4 bg-blue-500 rounded-lg shadow-lg z-50 background-a">
    <ProgressBar ref="progress" :progress="progress_value" class="w-full h-4"></ProgressBar>
    <p class="text-2xl animate-pulse mt-2 text-white">{{ loading_infos }} ...</p>
    </div>     
    <UniversalForm ref="universalForm" class="z-20" />
    <YesNoDialog ref="yesNoDialog" class="z-20" />
    <PersonalityEditor ref="personality_editor" :config="currentPersonConfig" :personality="selectedPersonality"></PersonalityEditor>
    <div id="app">
    <PopupViewer ref="news"/>
    </div>    
</template>


<style scoped>
@keyframes giggle {
    0%, 100% {
        transform: translateX(0) rotate(0deg) scale(1);
    }
    25% {
        transform: translateX(-5px) rotate(-10deg) scale(1.05);
    }
    50% {
        transform: translateX(5px) rotate(10deg) scale(0.95);
    }
    75% {
        transform: translateX(-5px) rotate(-10deg) scale(1.05);
    }
}

.animate-giggle {
    animation: giggle 1.5s infinite ease-in-out;
}

.custom-scrollbar {
scrollbar-width: thin;
scrollbar-color: rgba(155, 155, 155, 0.5) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
width: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
background-color: rgba(155, 155, 155, 0.5);
border-radius: 20px;
border: transparent;
}
@keyframes custom-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(59, 130, 246, 0.5); }
    50% { box-shadow: 0 0 0 15px rgba(59, 130, 246, 0); }
  }
.animate-pulse {
animation: custom-pulse 2s infinite;
}

.slide-right-enter-active {
  transition: transform 0.3s ease;
}

.slide-right-leave-active {
  transition: transform 0.3s ease;
}

.slide-right-enter,
.slide-right-leave-to {
  transform: translateX(-100%);
}

.slide-left-enter-active {
  transition: transform 0.3s ease;
}

.slide-left-leave-active {
  transition: transform 0.3s ease;
}

.slide-left-enter,
.slide-left-leave-to {
  transform: translateX(100%);
}

.fade-and-fly-enter-active {
  animation: fade-and-fly-enter 0.5s ease;
}

.fade-and-fly-leave-active {
  animation: fade-and-fly-leave 0.5s ease;
}

@keyframes fade-and-fly-enter {
  0% {
    opacity: 0;
    transform: translateY(20px) scale(0.8);
  }
  100% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes fade-and-fly-leave {
  0% {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
  100% {
    opacity: 0;
    transform: translateY(-20px) scale(1.2);
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
@keyframes float {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}
.animate-float {
  animation: float linear infinite;
}

@keyframes star-move {
  0% { transform: translate(0, 0) rotate(0deg); }
  50% { transform: translate(20px, 20px) rotate(180deg); }
  100% { transform: translate(0, 0) rotate(360deg); }
}

.animate-star {
  animation: star-move linear infinite;
}

@keyframes fall {
  from {
    transform: translateY(-20px) rotate(0deg);
    opacity: 1;
  }
  to {
    transform: translateY(calc(100vh + 20px)) rotate(360deg);
    opacity: 0;
  }
}

.animate-fall {
  animation: fall linear infinite;
}

@keyframes glow {
  0%, 100% { 
    text-shadow: 0 0 5px rgba(66, 153, 225, 0.5), 0 0 10px rgba(66, 153, 225, 0.5);
  }
  50% { 
    text-shadow: 0 0 20px rgba(66, 153, 225, 0.8), 0 0 30px rgba(66, 153, 225, 0.8);
  }
}

.animate-glow {
  animation: glow 2s ease-in-out infinite;
}

@media (prefers-color-scheme: dark) {
  @keyframes glow {
    0%, 100% { 
      text-shadow: 0 0 5px rgba(147, 197, 253, 0.5), 0 0 10px rgba(147, 197, 253, 0.5);
    }
    50% { 
      text-shadow: 0 0 20px rgba(147, 197, 253, 0.8), 0 0 30px rgba(147, 197, 253, 0.8);
    }
  }
}

@media (prefers-color-scheme: dark) {
  @keyframes glow {
    0%, 100% { 
      text-shadow: 0 0 5px rgba(147, 197, 253, 0.5), 0 0 10px rgba(147, 197, 253, 0.5);
    }
    50% { 
      text-shadow: 0 0 20px rgba(147, 197, 253, 0.8), 0 0 30px rgba(147, 197, 253, 0.8);
    }
  }
}


@keyframes roll {
  0% {
    transform: translateX(-50%) rotate(0deg);
  }
  100% {
    transform: translateX(50%) rotate(360deg);
  }
}

.animate-roll {
  animation: roll 4s linear infinite;
}


.toolbar {
@apply relative w-full;
}

.toolbar-container {
@apply flex items-center h-10; /* h-10 is equivalent to 40px */
}

.toolbar-button {
@apply bg-transparent border-none cursor-pointer p-2 transition-colors duration-300;
}

.toolbar-button:hover {
@apply text-blue-500; /* Assuming #007bff is close to Tailwind's blue-500 */
}

.menu-container {
  position: relative;
}
.expandable-menu {
  @apply absolute top-full left-2.5 border border-gray-300 rounded flex-col shadow-md;
}


.menu-container:hover .expandable-menu,
.menu-visible {
  display: flex;
}

.menu-item {
  background: none;
  border: none;
  cursor: pointer;
  padding: 8px;
  color: #333;
  transition: background-color 0.3s;
}

.menu-item:hover {
  background-color: #f0f0f0;
}


.dot {
width: 10px;
height: 10px;
border-radius: 50%;
}

.dot-green {
background-color: green;
}

.dot-red {
background-color: red;
}

.animate-pulse {
animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
0%, 100% {
    opacity: 1;
}
50% {
    opacity: .7;
}
}
.logo-container {
position: relative;
width: 48px;
height: 48px;
}

.logo-image {
width: 100%;
height: 100%;
border-radius: 50%;
object-fit: cover;
}
@keyframes bounce {
0%, 100% {
    transform: translateY(-25%);
    animation-timing-function: cubic-bezier(0.8, 0, 1, 1);
}
50% {
    transform: translateY(0);
    animation-timing-function: cubic-bezier(0, 0, 0.2, 1);
}
}
.animate-bounce {
animation: bounce 1s infinite;
}


@keyframes roll-and-bounce {
0%, 100% {
    transform: translateX(0) rotate(0deg);
}
45% {
    transform: translateX(100px) rotate(360deg);
}
50% {
    transform: translateX(90px) rotate(390deg);
}
55% {
    transform: translateX(100px) rotate(360deg);
}
95% {
    transform: translateX(0) rotate(0deg);
}
}

@keyframes spin {
0% {
    transform: rotate(0deg);
}
100% {
    transform: rotate(360deg);
}
}
</style>
<script>
import Toast from '@/components/Toast.vue'
import MessageBox from "@/components/MessageBox.vue";
import ProgressBar from "@/components/ProgressBar.vue";
import UniversalForm from '../components/UniversalForm.vue';
import YesNoDialog from '../components/YesNoDialog.vue';
import PersonalityEditor from "@/components/PersonalityEditor.vue"
import PopupViewer from '@/components/PopupViewer.vue';
import ActionButton from '@/components/ActionButton.vue'
import SocialIcon from '@/components/SocialIcon.vue'

import FastAPI from '@/assets/fastapi.png';
import discord from '@/assets/discord.svg';
import { RouterLink } from 'vue-router'
import { nextTick } from 'vue'
import feather from 'feather-icons'

import static_info from "../assets/static_info.svg"
import animated_info from "../assets/animated_info.svg"
import { useRouter } from 'vue-router'
import storeLogo from '@/assets/logo.png'
import fun_mode from "../assets/fun_mode.svg"
import normal_mode from "../assets/normal_mode.svg"

import axios from 'axios';
import { store } from '../main';

import SVGRedBrain from '@/assets/brain_red.svg';
import SVGOrangeBrain from '@/assets/brain_orange.svg';
import SVGGreenBrain from '@/assets/brain_green.svg';
import memory_icon from "../assets/memory_icon.svg"
import active_skills from "../assets/active.svg"
import inactive_skills from "../assets/inactive.svg"
import skillsRegistry from "../assets/registry.svg"
import robot from "../assets/robot.svg"
import { mapState } from 'vuex';
export default {
    
    setup() { },
    
    data() {
        return {
            isMenuVisible: false,
            isinfosMenuVisible: false,
            isNavMenuVisible: false,
            static_info: static_info,
            animated_info: animated_info,
            normal_mode:normal_mode,
            fun_mode:fun_mode,
            is_first_connection:true,
            discord:discord,
            FastAPI:FastAPI,
            customLanguage: '', // Holds the value of the custom language input
            selectedLanguage: '',
            isLanguageMenuVisible: false,
            rebooting_audio: new Audio("rebooting.wav"),            
            connection_lost_audio: new Audio("connection_lost.wav"),
            connection_recovered_audio: new Audio("connection_recovered.wav"),
            database_selectorDialogVisible:false,
            progress_visibility:false,
            progress_value:0,
            codeBlockStylesheet:'',
            sunIcon: document.querySelector(".sun"),
            moonIcon: document.querySelector(".moon"),
            userTheme: localStorage.getItem("theme"),
            systemTheme: window.matchMedia("prefers-color-scheme: dark").matches,

            lastMessageHtml:"",
            defaultMessageHtml: `
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Default Render Panel</title>
            <style>
                body, html {
                    margin: 0;
                    padding: 0;
                    height: 100%;
                    font-family: Arial, sans-serif;
                    background-color: #f0f0f0;
                }
                .container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    height: 100%;
                    padding: 20px;
                    box-sizing: border-box;
                }
                .message {
                    text-align: center;
                    padding: 30px;
                    background-color: white;
                    border-radius: 12px;
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    max-width: 600px;
                    width: 100%;
                }
                h1 {
                    color: #2c3e50;
                    margin-bottom: 20px;
                    font-size: 28px;
                }
                p {
                    color: #34495e;
                    margin: 0 0 15px;
                    line-height: 1.6;
                }
                .highlight {
                    color: #e74c3c;
                    font-weight: bold;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="message">
                    <h1>Welcome to the Interactive Render Panel</h1>
                    <p>This space is designed to bring your ideas to life! Currently, it's empty because no HTML has been generated yet.</p>
                    <p>To see something amazing here, try asking the AI to <span class="highlight">create a specific web component or application</span>. For example:</p>
                    <p>"Create a responsive image gallery" or "Build a simple todo list app"</p>
                    <p>Once you request a web component, the AI will generate the necessary HTML, CSS, and JavaScript, and it will be rendered right here in this panel!</p>
                </div>
            </div>
        </body>
        </html>       
            `,
            memory_icon: memory_icon,
            active_skills:active_skills,
            inactive_skills:inactive_skills,
            skillsRegistry:skillsRegistry,
            robot:robot,
            posts_headers : {
                'accept': 'application/json',
                'Content-Type': 'application/json'
            },
            host:"",
            progress_visibility_val         : true,
            progress_value                  : 0,
            msgTypes: {
                // Messaging
                MSG_TYPE_CONTENT                   : 1, // A full message (for some personality the answer is sent in bulk)
                MSG_TYPE_CONTENT_INVISIBLE_TO_AI   : 2, // A full message (for some personality the answer is sent in bulk)
                MSG_TYPE_CONTENT_INVISIBLE_TO_USER : 3, // A full message (for some personality the answer is sent in bulk)
            },
            // To be synced with the backend database types
            operationTypes: {
                // Messaging
                MSG_OPERATION_TYPE_ADD_CHUNK    : 0, // Add a chunk to the current message
                MSG_OPERATION_TYPE_SET_CONTENT  : 1, // sets the content of current message
                MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI      : 2, // sets the content of current message as invisible to ai
                MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_USER    : 3, // sets the content of current message as invisible to user
                // Informations
                MSG_OPERATION_TYPE_EXCEPTION              : 4, // An exception occured
                MSG_OPERATION_TYPE_WARNING                : 5, // A warning occured
                MSG_OPERATION_TYPE_INFO                   : 6, // An information to be shown to user

                // Steps
                MSG_OPERATION_TYPE_STEP                   : 7, // An instant step (a step that doesn't need time to be executed)
                MSG_OPERATION_TYPE_STEP_START             : 8, // A step has started (the text contains an explanation of the step done by he personality)
                MSG_OPERATION_TYPE_STEP_PROGRESS          : 9, // The progress value (the text contains a percentage and can be parsed by the reception)
                MSG_OPERATION_TYPE_STEP_END_SUCCESS       : 10, // A step has been done (the text contains an explanation of the step done by he personality)
                MSG_OPERATION_TYPE_STEP_END_FAILURE       : 11, // A step has been done (the text contains an explanation of the step done by he personality)

                //Extra
                MSG_OPERATION_TYPE_JSON_INFOS             : 12, // A JSON output that is useful for summarizing the process of generation used by personalities like chain of thoughts and tree of thooughts
                MSG_OPERATION_TYPE_REF                    : 13, // References (in form of  [text](path))
                MSG_OPERATION_TYPE_CODE                   : 14, // A javascript code to execute
                MSG_OPERATION_TYPE_UI                     : 15, // A vue.js component to show (we need to build some and parse the text to show it)

                //Commands
                MSG_OPERATION_TYPE_NEW_MESSAGE            : 16, // A new message
                MSG_OPERATION_TYPE_FINISHED_MESSAGE       : 17, // End of current message

            },
            // Sender types
            senderTypes: {
                SENDER_TYPES_USER               : 0, // Sent by user
                SENDER_TYPES_AI                 : 1, // Sent by ai
                SENDER_TYPES_SYSTEM             : 2, // Sent by athe system
            },
            list                                : [], // Discussion list
            tempList                            : [], // Copy of Discussion list (used for keeping the original list during filtering discussions/searching action)
            currentDiscussion                   : {}, // Current/selected discussion id
            discussionArr                       : [],
            loading: false,
            filterTitle: '',
            filterInProgress: false,
            isCreated: false,
            isCheckbox: false,
            isSelectAll: false,
            showSaveConfirmation: false,
            showBrainConfirmation: false,
            showConfirmation: false,
            chime: new Audio("chime_aud.wav"),
            showToast: false,
            isSearch: false,
            isDiscussionBottom: false,
            personalityAvatars: [], // object array of personality name: and avatar: props
            fileList: [],
            database_selectorDialogVisible:false,
            isDragOverDiscussion: false,
            isDragOverChat: false,
            isOpen: false,
            discussion_id: 0,
        }
    },
    methods: {        
        toggleMenu() {
            this.isMenuVisible = !this.isMenuVisible;
            if (this.isMenuVisible){
                this.isinfosMenuVisible=false;
            }
            nextTick(() => {
                feather.replace()

            })            
        },      
        toggleInfosMenu() {
            this.isinfosMenuVisible = !this.isinfosMenuVisible;
            if (this.isinfosMenuVisible){
                this.isMenuVisible=false;
            }

            nextTick(() => {
                feather.replace()
            })
        },
        adjustMenuPosition() {
            const menu = this.$refs.languageMenu;
            if(menu){
                const rect = menu.getBoundingClientRect();
                const windowWidth = window.innerWidth;

                if (rect.right > windowWidth) {
                    menu.style.left = 'auto';
                    menu.style.right = '0';
                } else {
                    menu.style.left = '0';
                    menu.style.right = 'auto';
                }
            }
        },
        addCustomLanguage() {
            if (this.customLanguage.trim() !== '') {
            this.selectLanguage(this.customLanguage);
            this.customLanguage = ''; // Reset the input field after adding
            }
        },
        async selectLanguage(language) {
            await this.$store.dispatch('changeLanguage', language);
            this.toggleLanguageMenu(); // Fermer le menu après le changement de langue
            this.language = language
        },
        async deleteLanguage(language) {
            await this.$store.dispatch('deleteLanguage', language);
            this.toggleLanguageMenu(); // Fermer le menu après le changement de langue
            this.language = language
        },
        
        toggleLanguageMenu() {
            console.log("Toggling language ",this.isLanguageMenuVisible)
            this.isLanguageMenuVisible = !this.isLanguageMenuVisible;
        },        
        restartProgram(event) {
            event.preventDefault();
            this.$store.state.api_post_req('restart_program', this.$store.state.client_id)
            this.rebooting_audio.play()
            this.$store.state.toast.showToast("Rebooting the app. Please wait...", 410, false)
            //this.$store.state.toast.showToast("Rebooting the app. Please wait...", 50, true);
            console.log("this.$store.state.api_get_req",this.$store.state.api_get_req)
            setTimeout(()=>{
                window.close();
            },2000)
        },  
        applyConfiguration() {
            this.isLoading = true;
            console.log(this.$store.state.config)
            axios.post('/apply_settings', {"client_id":this.$store.state.client_id, "config":this.$store.state.config}, {headers: this.posts_headers}).then((res) => {
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
        fun_mode_on(){
            console.log("Turning on fun mode")
            this.$store.state.config.fun_mode=true;
            this.applyConfiguration()
        },
        fun_mode_off(){
            console.log("Turning off fun mode")
            this.$store.state.config.fun_mode=false;
            this.applyConfiguration()
        },
        showNews(){
            this.$store.state.news.show()
        },
        themeCheck() {

            if (this.userTheme == "dark" || (!this.userTheme && this.systemTheme)) {
                document.documentElement.classList.add("dark");
                this.moonIcon.classList.add("display-none");

                nextTick(()=>{
                    //import('highlight.js/styles/tokyo-night-dark.css');
                    import('highlight.js/styles/stackoverflow-dark.css');

                })

                return
            }

            nextTick(()=>{
                //import('highlight.js/styles/tomorrow-night-blue.css');
                import('highlight.js/styles/stackoverflow-light.css');
            })
            this.sunIcon.classList.add("display-none")

        },
        themeSwitch() {
            
            if (document.documentElement.classList.contains("dark")) {
                document.documentElement.classList.remove("dark");
                localStorage.setItem("theme", "light")
                this.userTheme == "light"
                this.iconToggle()
             
                return

            }
            import('highlight.js/styles/tokyo-night-dark.css');
            document.documentElement.classList.add("dark");
            localStorage.setItem("theme", "dark")
            this.userTheme == "dark"
            this.iconToggle()
            // Dispatch the themeChanged event
            window.dispatchEvent(new Event('themeChanged'));
        },
        iconToggle() {
            this.sunIcon.classList.toggle("display-none");
            this.moonIcon.classList.toggle("display-none");
        },        
        refreshPage() {
            const hostnameParts = window.location.href.split('/');

            if(hostnameParts.length > 4){
                window.location.href='/'
            }
            else{
                window.location.reload(true);
            }
        },
        handleOk(inputText) {
            console.log("Input text:", inputText);
        },

        getRandomEdgePosition() {
            const edge = Math.floor(Math.random() * 4);
            switch (edge) {
                case 0: return 0; // Top edge
                case 1: return 100; // Right edge
                case 2: return Math.random() * 100; // Bottom or left edge
                case 3: return Math.random() * 100; // Bottom or left edge
            }
        },
        selectPrompt(prompt){
            this.$refs.chatBox.message = prompt;
        },
        extractHtml() {
            if (this.discussionArr.length > 0) {
                const lastMessage = this.discussionArr[this.discussionArr.length - 1].content;
                const startTag = '```html';
                const endTag = '```';
                let startIndex = lastMessage.indexOf(startTag);
                if (startIndex === -1) {
                    this.lastMessageHtml = this.defaultMessageHtml;
                    this.renderIsolatedContent();
                    return this.defaultMessageHtml;
                }
                
                startIndex += startTag.length;
                let endIndex = lastMessage.indexOf(endTag, startIndex);
                
                if (endIndex === -1) {
                    this.lastMessageHtml = lastMessage.slice(startIndex).trim();
                } else {
                    this.lastMessageHtml = lastMessage.slice(startIndex, endIndex).trim();
                }
            } else {
                this.lastMessageHtml = this.defaultMessageHtml;
            }
            this.renderIsolatedContent()
        },
        renderIsolatedContent() {
            const iframe = document.createElement('iframe');
            iframe.style.border = 'none';
            iframe.style.width = '100%';
            iframe.style.height = '100%'; // Adjust as needed
            if (this.$refs.isolatedContent){
                this.$refs.isolatedContent.innerHTML = '';
                this.$refs.isolatedContent.appendChild(iframe);
                
                const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                iframeDoc.open();
                iframeDoc.write(`
                    ${this.lastMessageHtml}
                `);
                iframeDoc.close();
            }

        },        
        async triggerRobotAction(){
            this.rightPanelCollapsed = !this.rightPanelCollapsed;
            if(!this.rightPanelCollapsed){
                this.$store.commit('setleftPanelCollapsed', false); // Assuming you have a mutation to set the view mode
                this.$nextTick(() => {
                this.extractHtml()
                });

            }
            console.log(this.rightPanelCollapsed)
        }, 
        add_webpage(){
            console.log("addWebLink received")
            this.$refs.web_url_input_box.showPanel();
        },
        addWebpage(){

            axios.post('/add_webpage', {"client_id":this.client_id, "url": this.$refs.web_url_input_box.inputText}, {headers: this.posts_headers}).then(response => {
                if (response && response.status){
                    console.log("Done")
                    this.recoverFiles()
                }
            });

        },
        show_progress(data){
            this.progress_visibility_val = true;
        },
        hide_progress(data){
            this.progress_visibility_val = false;
        },
        update_progress(data){
            console.log("Progress update")
            this.progress_value = data.value;
        },
        onSettingsBinding() {
            try {
                this.isLoading = true
                axios.get('/get_active_binding_settings').then(res => {
                    this.isLoading = false
                    if (res) {
                        if (res.data && Object.keys(res.data).length > 0) {

                            // open form
                            const bindingEntry = this.$store.state.bindingsZoo.find(item=>item.name == this.state.config.binding_name)
                            this.$store.state.universalForm.showForm(res.data, "Binding settings - " + bindingEntry.binding.name, "Save changes", "Cancel").then(res => {
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
        showDatabaseSelector() {
            this.database_selectorDialogVisible = true;
        },   
             
        async ondatabase_selectorDialogRemoved(choice){
            console.log("Deleted:",choice)
        },
        async ondatabase_selectorDialogSelected(choice){
            console.log("Selected:",choice)
        },
        onclosedatabase_selectorDialog(){this.database_selectorDialogVisible=false;},
        async onvalidatedatabase_selectorChoice(choice){
            this.database_selectorDialogVisible=false;
            const data = {
                "client_id": this.client_id,
                "name": typeof choice === 'string' ? choice : choice.name
            };
            console.log("data:")
            console.log(data)
            const res = await axios.post("/select_database", data, {headers: this.posts_headers});
            if(res.status){
                console.log("Selected database")
                this.$store.state.config = await axios.post("/get_config",{"client_id":this.client_id});
                console.log("new config loaded :",this.$store.state.config)
                let dbs = await axios.get("/list_databases")["data"];
                console.log("New list of database: ",dbs)

                this.$store.state.databases = dbs
                console.log("New list of database: ",this.$store.state.databases)
                location.reload();
            }
        
        },
        async addDiscussion2SkillsLibrary(){
            let result = await axios.post("/add_discussion_to_skills_library", {
                        client_id: this.client_id
                    }, {headers: this.posts_headers});
            if(result.status){
                console.log("done")
            }
        },
        async toggleSkillsLib(){
            this.$store.state.config.activate_skills_lib =! this.$store.state.config.activate_skills_lib;
            await this.applyConfiguration();
        },
        async showSkillsLib(){
            this.$refs.skills_lib.showSkillsLibrary()
        },
        
        async applyConfiguration() {
            this.loading = true;
            const res = await axios.post('/apply_settings', {"client_id":this.$store.state.client_id, "config":this.$store.state.config})
            this.loading = false;
            //console.log('apply-res',res)
            if (res.data.status) {
                
                this.$store.state.toast.showToast("Configuration changed successfully.", 4, true)
                //this.save_configuration()
            } else {
                this.$store.state.toast.showToast("Configuration change failed.", 4, false)
            }
            nextTick(() => {
                feather.replace()
            })
        },
        save_configuration() {
            this.showConfirmation = false
            axios.post('/save_settings', {})
                .then((res) => {
                    if (res) {
                        if (res.status) {
                            this.$store.state.toast.showToast("Settings saved!",4,true)
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
        showToastMessage(text, duration, isok){
            console.log("sending",text)
            this.$store.state.toast.showToast(text, duration, isok)
        },        
        toggleDropdown() {
            this.isOpen = !this.isOpen;
        },
        importChatGPT() {
            // handle ChatGPT import
        },  
        async api_get_req(endpoint) {
            try {
                const res = await axios.get("/" + endpoint);

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'api_get_req')
                return
            }
        },
        async list_discussions() {
            try {
                const res = await axios.get('/list_discussions')

                if (res) {

                    this.createDiscussionList(res.data)
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not list discussions", error.message)
                return []
            }
        },
        load_discussion(id, next) {
            if (id) {
                console.log("Loading discussion", id)
                this.loading = true
                this.discussionArr=[]
                this.setDiscussionLoading(id, this.loading)


                socket.on('discussion', (data)=>{
                    console.log("Discussion recovered")
                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                    if (data) {
                        // Filter out the user and bot entries
                        this.discussionArr = data.filter((item) => 
                                                                item.message_type == this.msgTypes.MSG_TYPE_CONTENT ||
                                                                item.message_type == this.msgTypes.MSG_TYPE_CONTENT_INVISIBLE_TO_AI
                                                        )
                        this.discussionArr.forEach((item) => {
                            item.status_message = "Done";
                        });                          
                        
                        console.log("this.discussionArr")
                        console.log(this.discussionArr)
                        if(next){
                            next()
                        }
                    }
                    
                    socket.off('discussion')
                    this.extractHtml()
                })

                socket.emit('load_discussion',{"id":id});

            }
        },
        recoverFiles(){
            console.log("Recovering files")
            axios.post('/get_discussion_files_list', {"client_id":this.$store.state.client_id}).then(res=>{
                this.$refs.chatBox.filesList = res.data.files;
                this.$refs.chatBox.isFileSentList= res.data.files.map(file => {
                    return true;
                });
                console.log(`Files recovered: ${this.$refs.chatBox.filesList}`)
            })
        },
        new_discussion(title) {
            try {
                this.loading = true
                socket.on('discussion_created',(data)=>{
                    socket.off('discussion_created')
                    this.list_discussions().then(()=>{
                        const index = this.list.findIndex((x) => x.id == data.id)
                        const discussionItem = this.list[index]
                        this.selectDiscussion(discussionItem)
                        this.load_discussion(data.id,()=>{
                            this.loading = false
                            this.recoverFiles();
                            nextTick(() => {
                                const selectedDisElement = document.getElementById('dis-' + data.id)
                                this.scrollToElement(selectedDisElement)
                                console.log("Scrolling tp "+selectedDisElement)
                            })
                        })
                    });
                });
                console.log("new_discussion ", title)
                socket.emit('new_discussion', {title:title});
            } catch (error) {
                console.log("Error: Could not create new discussion", error.message)
                return {}
            }
        },
        async delete_discussion(id) {
            try {
                if (id) {
                    this.loading = true
                    this.setDiscussionLoading(id, this.loading)
                    await axios.post('/delete_discussion', {
                        client_id: this.client_id,
                        id: id
                    }, {headers: this.posts_headers})
                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                }
            } catch (error) {
                console.log("Error: Could not delete discussion", error.message)
                this.loading = false
                this.setDiscussionLoading(id, this.loading)
            }
        },
        async edit_title(id, new_title) {
            try {
                if (id) {
                    this.loading = true
                    this.setDiscussionLoading(id, this.loading)
                    const res = await axios.post('/edit_title', {
                        client_id: this.client_id,
                        id: id,
                        title: new_title
                    }, {headers: this.posts_headers})
                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                    if (res.status == 200) {
                        const index = this.list.findIndex((x) => x.id == id)
                        const discussionItem = this.list[index]
                        discussionItem.title = new_title
                        this.tempList = this.list
                    }
                }
            } catch (error) {
                console.log("Error: Could not edit title", error.message)
                this.loading = false
                this.setDiscussionLoading(id, this.loading)
            }
        },
        async make_title(id) {
            try {
                if (id) {
                    this.loading = true
                    this.setDiscussionLoading(id, this.loading)
                    const res = await axios.post('/make_title', {
                        client_id: this.client_id,
                        id: id,
                    }, {headers: this.posts_headers})
                    console.log("Making title:",res)

                    this.loading = false
                    this.setDiscussionLoading(id, this.loading)
                    if (res.status == 200) {
                        const index = this.list.findIndex((x) => x.id == id)
                        const discussionItem = this.list[index]
                        discussionItem.title = res.data.title
                        
                        this.tempList = this.list
                    }
                }
            } catch (error) {
                console.log("Error: Could not edit title", error.message)
                this.loading = false
                this.setDiscussionLoading(id, this.loading)
            }
        },        
        async delete_message(id) {
            try {
                console.log(typeof id)
                console.log(typeof this.client_id)
                console.log(id)
                console.log(this.client_id)
                const res = await axios.post('/delete_message', { client_id: this.client_id, id: id }, {headers: this.posts_headers})

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could delete message", error.message)
                return {}
            }
        },

        
        async stop_gen() {
            try {
                if (this.discussionArr.length>0)
                {
                    const messageItem = this.discussionArr[this.discussionArr.length-1]            
                    messageItem.status_message = "Generation canceled"
                }
                socket.emit('cancel_generation');
                //const res = await axios.get('/stop_gen')

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not stop generating", error.message)
                return {}
            }
        },
        async message_rank_up(id) {
            try {
                const res = await axios.post('/message_rank_up', { client_id: this.client_id, id: id }, {headers: this.posts_headers})

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not rank up message", error.message)
                return {}
            }
        },
        async message_rank_down(id) {
            try {
                const res = await axios.post('/message_rank_down', { client_id: this.client_id, id: id } , {headers: this.posts_headers})

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not rank down message", error.message)
                return {}
            }
        },
        async edit_message(id, message, audio_url) {
            try {
                console.log(typeof this.client_id)
                console.log(typeof id)
                console.log(typeof message)
                console.log(typeof {audio_url:audio_url})
                const res = await axios.post('/edit_message', {
                                                            client_id: this.client_id, 
                                                            id: id, 
                                                            message: message,
                                                            metadata: [{audio_url:audio_url}]
                                                    }, {headers: this.posts_headers}
                )

                if (res) {
                    return res.data
                }
            } catch (error) {
                console.log("Error: Could not update message", error.message)
                return {}
            }
        },
        async export_multiple_discussions(discussionIdArr, export_format) {
            try {
                if (discussionIdArr.length > 0) {
                    const res = await axios.post('/export_multiple_discussions', {
                        client_id:this.$store.state.client_id,
                        discussion_ids: discussionIdArr,
                        export_format: export_format
                    }, {headers: this.posts_headers})

                    if (res) {
                        return res.data
                    }
                }

            } catch (error) {
                console.log("Error: Could not export multiple discussions", error.message)
                return {}
            }
        },
        async import_multiple_discussions(jArray_) {
            try {
                if (jArray_.length > 0) {
                    console.log('sending import', jArray_)
                    const res = await axios.post('/import_multiple_discussions', {
                        client_id: this.$store.state.client_id,
                        jArray: jArray_
                    }, {headers: this.posts_headers})

                    if (res) {
                        console.log('import response', res.data)
                        return res.data
                    }
                }

            } catch (error) {
                console.log("Error: Could not import multiple discussions", error.message)
                return
            }
        },
        filterDiscussions() {
            // Search bar in for filtering discussions by title (serch)

            if (!this.filterInProgress) {
                this.filterInProgress = true
                setTimeout(() => {
                    if (this.filterTitle) {
                        this.list = this.tempList.filter((item) => item.title && item.title.includes(this.filterTitle))

                    } else {
                        this.list = this.tempList
                    }
                    this.filterInProgress = false
                }, 100)
            }
        },
        async selectDiscussion(item) {
            if(this.isGenerating){
                this.$store.state.toast.showToast("You are currently generating a text. Please wait for text generation to finish or stop it before trying to select another discussion", 4, false)
                return;
            }

            if (item) {
                // When discussion is selected it loads the discussion array
                if (this.currentDiscussion===undefined) {
                    this.currentDiscussion = item

                    this.setPageTitle(item)

                    localStorage.setItem('selected_discussion', this.currentDiscussion.id)

                    this.load_discussion(item.id, ()=>{
                        if (this.discussionArr.length > 1) {
                        if (this.currentDiscussion.title === '' || this.currentDiscussion.title === null) {
                            this.changeTitleUsingUserMSG(this.currentDiscussion.id, this.discussionArr[1].content)
                        }
                        this.recoverFiles()
                    }
                    })

                }
                else{
                    if (this.currentDiscussion.id != item.id) {
                        console.log("item",item)
                        console.log("this.currentDiscussion",this.currentDiscussion)
                        this.currentDiscussion = item
                        console.log("this.currentDiscussion",this.currentDiscussion)

                        this.setPageTitle(item)

                        localStorage.setItem('selected_discussion', this.currentDiscussion.id)

                        this.load_discussion(item.id, ()=>{
                            if (this.discussionArr.length > 1) {
                                if (this.currentDiscussion.title === '' || this.currentDiscussion.title === null) {
                                    this.changeTitleUsingUserMSG(this.currentDiscussion.id, this.discussionArr[1].content)
                                }
                            }
                            this.recoverFiles()
                        });

                    }
                }

                nextTick(() => {


                    const discussionitem = document.getElementById('dis-' + this.currentDiscussion.id)

                    //this.scrollToElement(discussionitem)

                    this.scrollToElementInContainer(discussionitem, 'leftPanel')
                    const msgList = document.getElementById('messages-list')

                    this.scrollBottom(msgList)

                })
            }
        },

        scrollToElement(el) {

            if (el) {
                el.scrollIntoView({ behavior: 'smooth', block: 'start', inline: 'nearest' })
            } else {
                console.log("Error: scrollToElement")
            }
        },
        scrollToElementInContainer(el, containerId) {
            try{
                const topPos = el.offsetTop; //+ el.clientHeight
                const container = document.getElementById(containerId)
                // console.log(el.offsetTop , el.clientHeight, container.clientHeight)


                container.scrollTo(
                    {
                        top: topPos,
                        behavior: "smooth",
                    }
                )

            }
            catch{
                console.log("error")
            }

        },
        scrollBottom(el) {

            if (el) {
                el.scrollTo(
                    {
                        top: el.scrollHeight,
                        behavior: "smooth",
                    }
                )
            } else {
                console.log("Error: scrollBottom")
            }

        },

        scrollTop(el) {

            if (el) {
                el.scrollTo(
                    {
                        top: 0,
                        behavior: "smooth",
                    }
                )
            } else {
                console.log("Error: scrollTop")
            }

        },
        createUserMsg(msgObj) {

            let usrMessage = {
                content: msgObj.message,
                id: msgObj.id,
                rank: 0,
                sender: msgObj.user,
                created_at: msgObj.created_at,
                steps: [],
                html_js_s: [],
                status_message: "Warming up"

            }
            this.discussionArr.push(usrMessage)
            nextTick(() => {
                const msgList = document.getElementById('messages-list')

                this.scrollBottom(msgList)

            })
        },
        updateLastUserMsg(msgObj) {

            // const lastMsg = this.discussionArr[this.discussionArr.length - 1]
            // lastMsg.content = msgObj.message
            // lastMsg.id = msgObj.user_id
            // // lastMsg.parent=msgObj.parent
            // lastMsg.rank = msgObj.rank
            // lastMsg.sender = msgObj.user
            // // lastMsg.type=msgObj.type
            const index = this.discussionArr.indexOf(item => item.id = msgObj.user_id)
            const newMessage ={
                binding: msgObj.binding,
                content: msgObj.message,
                created_at: msgObj.created_at,
                type: msgObj.type,
                finished_generating_at: msgObj.finished_generating_at,
                id: msgObj.user_id,
                model: msgObj.model,
                personality: msgObj.personality,
                sender: msgObj.user,
                steps:[]
            }
            
            
            if (index !== -1) {
                this.discussionArr[index] = newMessage;
            }

        },
        async socketIOConnected() {
            console.log("socketIOConnected")
 
        },
        socketIODisconnected() {
            console.log("socketIOConnected")
            this.currentDiscussion=null
            this.$store.dispatch('refreshModels');
            this.$store.state.isConnected=false;
            return true
        },
        new_message(msgObj) {
            if(msgObj.sender_type==this.SENDER_TYPES_AI){
                this.isGenerating = true
            }
            console.log("Making a new message")
            console.log('New message', msgObj);
            
            let responseMessage = {
                sender:                 msgObj.sender,
                message_type:           msgObj.message_type,
                sender_type:            msgObj.sender_type,
                content:                msgObj.content,//"✍ please stand by ...",
                id:                     msgObj.id,
                discussion_id:          msgObj.discussion_id,
                parent_id:              msgObj.parent_id,

                binding:                msgObj.binding,
                model:                  msgObj.model,
                personality:            msgObj.personality,

                created_at:             msgObj.created_at,
                finished_generating_at: msgObj.finished_generating_at,
                rank:                   0,

                ui:                     msgObj.ui,

                steps                   : [],
                parameters              : msgObj.parameters,
                metadata                : msgObj.metadata,

                open                    : msgObj.open
            }
            
            responseMessage.status_message = "Warming up"
            console.log(responseMessage)
            this.discussionArr.push(responseMessage)
            // nextTick(() => {
            //     const msgList = document.getElementById('messages-list')

            //     this.scrollBottom(msgList)

            // })

            if (this.currentDiscussion.title === '' || this.currentDiscussion.title === null) {
                this.changeTitleUsingUserMSG(this.currentDiscussion.id, msgObj.message)
            }
            console.log("infos", msgObj)
            /*
            }
            else {
                this.$store.state.toast.showToast("It seems that no model has been loaded. Please download and install a model first, then try again.", 4, false)
                this.isGenerating = false
                this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating)
                this.chime.play()
            }*/
        },
        async talk(pers){
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            let res = await axios.get('/get_generation_status', {})
            if (res) {
                //console.log(res.data.status);
                if (!res.data.status) {
                    const id = this.$store.state.config.personalities.findIndex(item => item === pers.full_path)
                    const obj = {
                    client_id:this.$store.state.client_id,
                    id: id
                    }
                    res = await axios.post('/select_personality', obj);

                    console.log('Generating message from ',res.data.status);
                    socket.emit('generate_msg_from', { id: -1 });
                }
                else {
                    console.log("Already generating");
                }
            }
        },
        createEmptyUserMessage(message){
            socket.emit('create_empty_message', {"type":0,"message":message}); // 0 for user and 1 for AI
        },
        createEmptyAIMessage(){
            socket.emit('create_empty_message', {"type":1}); // 0 for user and 1 for AI
        },
        sendMsg(msg,type) {
            // Sends message to binding
            if (!msg) {
                this.$store.state.toast.showToast("Message contains no content!", 4, false)
                return
            }
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    //console.log(res.data.status);
                    if (!res.data.status) {
                        if(type=="internet"){
                            socket.emit('generate_msg_with_internet', { prompt: msg });
                        }
                        else{
                            socket.emit('generate_msg', { prompt: msg });
                        }

                        // Create new User message
                        // Temp data
                        let lastmsgid =0
                        if(this.discussionArr.length>0){
                            lastmsgid= Number(this.discussionArr[this.discussionArr.length - 1].id) + 1
                        }
                        
                        
                        let usrMessage = {
                            message: msg,
                            id: lastmsgid,
                            rank: 0,
                            user: this.$store.state.config.user_name,
                            created_at: new Date().toLocaleString(),


                            sender:                 this.$store.state.config.user_name,
                            message_type:           this.operationTypes.MSG_TYPE_CONTENT,
                            sender_type:            this.senderTypes.SENDER_TYPES_USER,
                            content:                msg,
                            id:                     lastmsgid,
                            discussion_id:          this.discussion_id,
                            parent_id:              lastmsgid,

                            binding:                "",
                            model:                  "",
                            personality:            "",

                            created_at:             new Date().toLocaleString(),
                            finished_generating_at: new Date().toLocaleString(),
                            rank:                   0,

                            steps:                  [],
                            parameters:             null,
                            metadata:               [],
                            ui:                     null

                        };
                        this.createUserMsg(usrMessage);

                    }
                    else {
                        console.log("Already generating");
                    }
                }
            }).catch((error) => {
                console.log("Error: Could not get generation status", error);
            });
        },
        sendCmd(cmd){
            this.isGenerating = true;
            // axios.post('/execute_personality_command', {command: cmd, parameters:[]})
            //     .then((res) => {
            //         if (res) {
            //             if (res.status) {
            //                 this.$store.state.toast.showToast("Command executed",4,true)
            //             }
            //             else
            //                 this.$store.state.messageBox.showMessage("Error: Couldn't execute command!")
            //             return res.data;
            //         }
            //     })
            //     .catch(error => {
            //         console.log(error.message, 'save_configuration')
            //         this.$store.state.messageBox.showMessage("Couldn't save settings!")
                    
            //     });
            
            socket.emit('execute_command', { command: cmd, parameters: [] });            
        },
        notify(notif){
            self.isGenerating = false
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            nextTick(() => {
                const msgList = document.getElementById('messages-list')
                this.scrollBottom(msgList)
            })
            if(notif.display_type==0){
                this.$store.state.toast.showToast(notif.content, notif.duration, notif.notification_type)
            }
            else if(notif.display_type==1){
                this.$store.state.messageBox.showMessage(notif.content)
            }
            else if(notif.display_type==2){
                this.$store.state.messageBox.hideMessage()
                this.$store.state.yesNoDialog.askQuestion(notif.content, 'Yes', 'No').then(yesRes => {
                    socket.emit("yesNoRes",{yesRes:yesRes})
                })
            }
            else if(notif.display_type==3){
                this.$store.state.messageBox.showBlockingMessage(notif.content)
            }
            else if(notif.display_type==4){
                this.$store.state.messageBox.hideMessage()
            }
            
            this.chime.play()
        },
        update_message(msgObj) {
            console.log("update_message trigged")
            console.log(msgObj)
            // Streams response message content from binding
            this.discussion_id = msgObj.discussion_id
            this.setDiscussionLoading(this.discussion_id, true);

            if (this.currentDiscussion.id == this.discussion_id) {
                console.log("discussion ok")
                //this.isGenerating = true;
                const index = this.discussionArr.findIndex((x) => x.id == msgObj.id)
                const messageItem = this.discussionArr[index]
                if (
                    messageItem && (msgObj.operation_type==this.operationTypes.MSG_OPERATION_TYPE_SET_CONTENT ||
                    msgObj.operation_type==this.operationTypes.MSG_OPERATION_TYPE_SET_CONTENT_INVISIBLE_TO_AI)
                ) {
                    console.log("Content triggered")
                    this.isGenerating = true;
                    messageItem.content = msgObj.content
                    messageItem.created_at = msgObj.created_at
                    messageItem.started_generating_at = msgObj.started_generating_at
                    messageItem.nb_tokens = msgObj.nb_tokens
                    messageItem.finished_generating_at = msgObj.finished_generating_at
                    this.extractHtml()
                }
                else if(messageItem && msgObj.operation_type==this.operationTypes.MSG_OPERATION_TYPE_ADD_CHUNK){
                    this.isGenerating = true;
                    messageItem.content += msgObj.content
                    console.log("Chunk triggered")
                    //console.log("content")
                    //console.log(messageItem.content)
                    messageItem.created_at              = msgObj.created_at
                    messageItem.started_generating_at   = msgObj.started_generating_at
                    messageItem.nb_tokens               = msgObj.nb_tokens
                    messageItem.finished_generating_at  = msgObj.finished_generating_at
                    this.extractHtml()
                } else if (msgObj.operation_type == this.operationTypes.MSG_OPERATION_TYPE_STEP || msgObj.operation_type == this.operationTypes.MSG_OPERATION_TYPE_STEP_START || msgObj.operation_type == this.operationTypes.MSG_OPERATION_TYPE_STEP_END_SUCCESS || msgObj.operation_type == this.operationTypes.MSG_OPERATION_TYPE_STEP_END_FAILURE){
                    if (Array.isArray(msgObj.steps)) {
                        messageItem.status_message = msgObj.steps[msgObj.steps.length - 1]["text"]
                        console.log("step Content: ", messageItem.status_message)
                        messageItem.steps = msgObj.steps;
                        console.log("steps: ", msgObj.steps)
                    } else {
                        console.error("Invalid steps data:", msgObj.steps);
                    }

                } else if (msgObj.operation_type == this.operationTypes.MSG_OPERATION_TYPE_JSON_INFOS) {
                    console.log("metadata triggered", msgObj.operation_type)
                    console.log("metadata", msgObj.metadata)
                    if (typeof msgObj.metadata === 'string') {
                        try {
                            messageItem.metadata = JSON.parse(msgObj.metadata);
                        } catch (error) {
                            console.error("Error parsing metadata string:", error);
                            messageItem.metadata = { raw: msgObj.metadata }; // Fallback: store as raw string in an object
                        }
                    } else if (Array.isArray(msgObj.metadata) || typeof msgObj.metadata === 'object') {
                        messageItem.metadata = msgObj.metadata; // Already an array or object, assign directly
                    } else {
                        messageItem.metadata = { value: msgObj.metadata }; // For any other type, wrap in an object
                    }
                } else if (msgObj.operation_type == this.operationTypes.MSG_OPERATION_TYPE_UI) {
                    console.log("UI triggered",msgObj.operation_type)
                    console.log("UI", msgObj.ui)
                    messageItem.ui = msgObj.ui
                } else if (msgObj.operation_type == this.operationTypes.MSG_OPERATION_TYPE_EXCEPTION) {
                    this.$store.state.toast.showToast(msgObj.content, 5, false)
                }
                // // Disables as per request
                // nextTick(() => {
                //     const msgList = document.getElementById('messages-list')
                //     this.scrollBottom(msgList)
                // })
            }
            // Force an immediate UI update
            this.$nextTick(() => {
                // UI updates are rendered here
                feather.replace()
            });

        },
        async changeTitleUsingUserMSG(id, msg) {
            // If discussion is untitled or title is null then it sets the title to first user message.

            const index = this.list.findIndex((x) => x.id == id)
            const discussionItem = this.list[index]
            if (msg) {
                discussionItem.title = msg
                this.tempList = this.list
                await this.edit_title(id, msg)
            }

        },
        async createNewDiscussion() {
            // Creates new discussion on binding,
            // gets new discussion list, selects
            // newly created discussion,
            // scrolls to the discussion
            this.new_discussion(null)
        },
        loadLastUsedDiscussion() {
            // Checks local storage for last selected discussion
            console.log("Loading last discussion")
            const id = localStorage.getItem('selected_discussion')
            console.log("Last discussion id: ",id)
            if (id) {
                const index = this.list.findIndex((x) => x.id == id)
                const discussionItem = this.list[index]
                if (discussionItem) {
                    this.selectDiscussion(discussionItem)
                }
            }
        },        
        onCopyPersonalityName(personality) {
            this.$store.state.toast.showToast("Copied name to clipboard!", 4, true)
            navigator.clipboard.writeText(personality.name);
        },
        async deleteDiscussion(id) {
            // Deletes discussion from binding and frontend

            await this.delete_discussion(id)
            if (this.currentDiscussion.id == id) {
                this.currentDiscussion = {}
                this.discussionArr = []
                this.setPageTitle()
            }
            this.list.splice(this.list.findIndex(item => item.id == id), 1)

            this.createDiscussionList(this.list)
        },
        async deleteDiscussionMulti() {
            // Delete selected discussions

            const deleteList = this.selectedDiscussions

            for (let i = 0; i < deleteList.length; i++) {
                const discussionItem = deleteList[i]
                //discussionItem.loading = true
                await this.delete_discussion(discussionItem.id)
                if (this.currentDiscussion.id == discussionItem.id) {
                    this.currentDiscussion = {}
                    this.discussionArr = []
                    this.setPageTitle()
                }
                this.list.splice(this.list.findIndex(item => item.id == discussionItem.id), 1)
            }
            this.tempList = this.list
            this.isCheckbox = false
            this.$store.state.toast.showToast("Removed (" + deleteList.length + ") items", 4, true)
            this.showConfirmation = false
            console.log("Multi delete done")
        },
        async deleteMessage(msgId) {

            await this.delete_message(msgId).then(() => {

                this.discussionArr.splice(this.discussionArr.findIndex(item => item.id == msgId), 1)

            }).catch(() => {
                this.$store.state.toast.showToast("Could not remove message", 4, false)
                console.log("Error: Could not delete message")
            })

        },
        async openFolder(id){
            const json = JSON.stringify({ 'client_id': this.$store.state.client_id, 'discussion_id': id.id })   
            console.log(json)     
            await axios.post(`/open_discussion_folder`, json, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
            })
        },
        async editTitle(newTitleObj) {

            const index = this.list.findIndex((x) => x.id == newTitleObj.id)
            const discussionItem = this.list[index]
            discussionItem.title = newTitleObj.title
            discussionItem.loading = true
            await this.edit_title(newTitleObj.id, newTitleObj.title)
            discussionItem.loading = false
        },
        async makeTitle(editTitleObj) {
            const index = this.list.findIndex((x) => x.id == editTitleObj.id)
            await this.make_title(editTitleObj.id)
        },

        checkUncheckDiscussion(event, id) {
            // If checked = true and item is not in array then add item to list
            const index = this.list.findIndex((x) => x.id == id)
            const discussionItem = this.list[index]
            discussionItem.checkBoxValue = event.target.checked
            this.tempList = this.list
        },
        selectAllDiscussions() {

            // Check if there is one discussion not selected
            this.isSelectAll = !this.tempList.filter((item) => item.checkBoxValue == false).length > 0
            // Selects or deselects all discussions
            for (let i = 0; i < this.tempList.length; i++) {
                this.tempList[i].checkBoxValue = !this.isSelectAll
            }

            this.tempList = this.list
            this.isSelectAll = !this.isSelectAll
        },
        createDiscussionList(disList) {
            // This creates a discussion list for UI with additional properties
            if (disList) {
                const newDisList = disList.map((item) => {

                    const newItem = {
                        id: item.id,
                        title: item.title,
                        selected: false,
                        loading: false,
                        checkBoxValue: false
                    }
                    return newItem

                }).sort(function (a, b) {
                    return b.id - a.id
                })

                this.list = newDisList
                this.tempList = newDisList
            }
        },
        setDiscussionLoading(id, loading) {
            try{
                const index = this.list.findIndex((x) => x.id == id)
                const discussionItem = this.list[index]
                discussionItem.loading = loading
            }
            catch{
                console.log("Error setting discussion loading")
            }
        },
        setPageTitle(item) {
            // item is either title:String or {id:Number, title:String}
            if (item) {
                if (item.id) {
                    const realTitle = item.title ? item.title === "untitled" ? "New discussion" : item.title : "New discussion"
                    document.title = 'L🌟LLMS WebUI - ' + realTitle
                } else {
                    const title = item || "Welcome"
                    document.title = 'L🌟LLMS WebUI - ' + title
                }
            } else {
                const title = item || "Welcome"
                document.title = 'L🌟LLMS WebUI - ' + title
            }

        },
        async rankUpMessage(msgId) {
            await this.message_rank_up(msgId).then((res) => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.rank = res.new_rank
            }).catch(() => {
                this.$store.state.toast.showToast("Could not rank up message", 4, false)
                console.log("Error: Could not rank up message")
            })

        },
        async rankDownMessage(msgId) {
            await this.message_rank_down(msgId).then((res) => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.rank = res.new_rank
            }).catch(() => {
                this.$store.state.toast.showToast("Could not rank down message", 4, false)

                console.log("Error: Could not rank down message")
            })

        },
        async updateMessage(msgId, msg, audio_url) {
            await this.edit_message(msgId, msg, audio_url).then(() => {

                const message = this.discussionArr[this.discussionArr.findIndex(item => item.id == msgId)]
                message.content = msg

            }).catch(() => {
                this.$store.state.toast.showToast("Could not update message", 4, false)

                console.log("Error: Could not update message")
            })

        },
        resendMessage(msgId, msg, msg_type) {
            nextTick(() => {
                feather.replace()

            })
            // Resend message
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    if (!res.data.status) {
                        socket.emit('generate_msg_from', { prompt: msg, id: msgId, msg_type: msg_type });
                    }
                    else {
                        this.$store.state.toast.showToast("The server is busy. Wait", 4, false)
                        console.log("Already generating");
                    }
                }
            }).catch((error) => {
                console.log("Error: Could not get generation status", error);
            });
        },
        continueMessage(msgId, msg) {
            nextTick(() => {
                feather.replace()

            })
            // Resend message
            this.isGenerating = true;
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating);
            axios.get('/get_generation_status', {}).then((res) => {
                if (res) {
                    if (!res.data.status) {
                        socket.emit('continue_generate_msg_from', { prompt: msg, id: msgId });


                    }
                    else {
                        console.log("Already generating");
                    }
                }
            }).catch((error) => {
                console.log("Error: Could not get generation status", error);
            });
        },
        stopGenerating() {
            this.stop_gen()
            this.isGenerating = false
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating)
            console.log("Stopped generating")
            nextTick(() => {
                const msgList = document.getElementById('messages-list')
                this.scrollBottom(msgList)
            })
        },
        finalMsgEvent(msgObj) {
            console.log("Received message close order")
            let index=0;
            // Last message contains halucination suppression so we need to update the message content too
            this.discussion_id = msgObj.discussion_id
            if (this.currentDiscussion.id == this.discussion_id) {
                index = this.discussionArr.findIndex((x) => x.id == msgObj.id)
                this.discussionArr[index].content = msgObj.content
                this.discussionArr[index].finished_generating_at = msgObj.finished_generating_at
                this.discussionArr[index].nb_tokens  = msgObj.nb_tokens
                this.discussionArr[index].binding  = msgObj.binding
                this.discussionArr[index].model  = msgObj.model
                this.discussionArr[index].personality  = msgObj.personality


                // const messageItem = this.discussionArr[index]
                // if (messageItem) {
                //     messageItem.content = msgObj.content
                // }
            }
            nextTick(() => {
                const msgList = document.getElementById('messages-list')
                this.scrollBottom(msgList)
                this.recoverFiles()
            })


            this.isGenerating = false
            this.setDiscussionLoading(this.currentDiscussion.id, this.isGenerating)
            this.chime.play()
            index = this.discussionArr.findIndex((x) => x.id == msgObj.id)
            const messageItem = this.discussionArr[index]            
            messageItem.status_message = "Done"
            console.log("final", msgObj)
            if(this.$store.state.config.auto_speak && (this.$store.state.config.xtts_enable && this.$store.state.config.xtts_use_streaming_mode)){
                index = this.discussionArr.findIndex((x) => x.id == msgObj.id)
                let message_component = this.$refs['msg-' + msgObj.id][0]
                console.log(message_component)
                message_component.speak()
            }

        },
        copyToClipBoard(messageEntry) {
            let content = ""
            if (messageEntry.message.content) {
                content = messageEntry.message.content
            }


            if(this.$store.state.config.copy_to_clipboard_add_all_details){
                let binding = ""
                if (messageEntry.message.binding) {
                    binding = `Binding: ${messageEntry.message.binding}`
                }
                let personality = ""
                if (messageEntry.message.personality) {
                    personality = `\nPersonality: ${messageEntry.message.personality}`
                }
                let time = ""
                if (messageEntry.created_at_parsed) {
                    time = `\nCreated: ${messageEntry.created_at_parsed}`
                }
                let model = ""
                if (messageEntry.message.model) {
                    model = `Model: ${messageEntry.message.model}`
                }
                let seed = ""
                if (messageEntry.message.seed) {
                    seed = `Seed: ${messageEntry.message.seed}`
                }
                let time_spent = ""
                if (messageEntry.time_spent) {
                    time_spent = `\nTime spent: ${messageEntry.time_spent}`
                }                
                let bottomRow = ''
                bottomRow = `${binding} ${model} ${seed} ${time_spent}`.trim()
                const result = `${messageEntry.message.sender}${personality}${time}\n\n${content}\n\n${bottomRow}`

                navigator.clipboard.writeText(result);
            }
            else{
                navigator.clipboard.writeText(content);
            }



            this.$store.state.toast.showToast("Copied to clipboard successfully", 4, true)

            nextTick(() => {
                feather.replace()

            })
        },
        closeToast() {
            this.showToast = false
        },
        saveJSONtoFile(jsonData, filename) {
            filename = filename || "data.json"
            const a = document.createElement("a");
            a.href = URL.createObjectURL(new Blob([JSON.stringify(jsonData, null, 2)], {
                type: "text/plain"
            }));
            a.setAttribute("download", filename);
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        },
        saveMarkdowntoFile(markdownData, filename) {
            filename = filename || "data.md"
            const a = document.createElement("a");
            a.href = URL.createObjectURL(new Blob([markdownData], {
                type: "text/plain"
            }));
            a.setAttribute("download", filename);
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
        },
        parseJsonObj(obj) {
            try {
                const ret = JSON.parse(obj)
                return ret
            } catch (error) {
                this.$store.state.toast.showToast("Could not parse JSON. \n" + error.message, 4, false)
                return null
            }

        },
        async parseJsonFile(file) {

            return new Promise((resolve, reject) => {
                const fileReader = new FileReader()
                fileReader.onload = event => resolve(this.parseJsonObj(event.target.result))
                fileReader.onerror = error => reject(error)
                fileReader.readAsText(file)
            })
        },
        
        async exportDiscussionsAsMarkdown() {
            // Export selected discussions

            const discussionIdArr = this.list.filter((item) => item.checkBoxValue == true).map((item) => {
                return item.id
            })

            if (discussionIdArr.length > 0) {
                console.log("export", discussionIdArr)
                let dateObj = new Date()

                const year = dateObj.getFullYear();
                const month = (dateObj.getMonth() + 1).toString().padStart(2, "0");
                const day = dateObj.getDate().toString().padStart(2, "0");
                const hours = dateObj.getHours().toString().padStart(2, "0");
                const minutes = dateObj.getMinutes().toString().padStart(2, "0");
                const seconds = dateObj.getSeconds().toString().padStart(2, "0");
                const formattedDate =
                    year +
                    "." +
                    month +
                    "." +
                    day +
                    "." +
                    hours +
                    "" +
                    minutes +
                    "" +
                    seconds;

                const filename = 'discussions_export_' + formattedDate + '.md'
                this.loading = true
                const res = await this.export_multiple_discussions(discussionIdArr,"markdown")

                if (res) {
                    this.saveMarkdowntoFile(res, filename)
                    this.$store.state.toast.showToast("Successfully exported", 4, true)
                    this.isCheckbox = false
                } else {
                    this.$store.state.toast.showToast("Failed to export discussions", 4, false)
                }
                this.loading = false
            }

        },
        async exportDiscussions(){

        },
        async exportDiscussionsAsJson() {
            // Export selected discussions

            const discussionIdArr = this.list.filter((item) => item.checkBoxValue == true).map((item) => {
                return item.id
            })

            if (discussionIdArr.length > 0) {
                console.log("export", discussionIdArr)
                let dateObj = new Date()

                const year = dateObj.getFullYear();
                const month = (dateObj.getMonth() + 1).toString().padStart(2, "0");
                const day = dateObj.getDate().toString().padStart(2, "0");
                const hours = dateObj.getHours().toString().padStart(2, "0");
                const minutes = dateObj.getMinutes().toString().padStart(2, "0");
                const seconds = dateObj.getSeconds().toString().padStart(2, "0");
                const formattedDate =
                    year +
                    "." +
                    month +
                    "." +
                    day +
                    "." +
                    hours +
                    "" +
                    minutes +
                    "" +
                    seconds;

                const filename = 'discussions_export_' + formattedDate + '.json'
                this.loading = true
                const res = await this.export_multiple_discussions(discussionIdArr, "json")

                if (res) {
                    this.saveJSONtoFile(res, filename)
                    this.$store.state.toast.showToast("Successfully exported", 4, true)
                    this.isCheckbox = false
                } else {
                    this.$store.state.toast.showToast("Failed to export discussions", 4, false)
                }
                this.loading = false
            }

        },
        async importDiscussionsBundle(event){

        },
        async importDiscussions(event) {
            const obj = await this.parseJsonFile(event.target.files[0])

            const res = await this.import_multiple_discussions(obj)
            if (res) {
                this.$store.state.toast.showToast("Successfully imported (" + obj.length + ")", 4, true)
                await this.list_discussions()
            } else {
                this.$store.state.toast.showToast("Failed to import discussions", 4, false)
            }



        },
        async getPersonalityAvatars() {
            while (this.$store.state.personalities === null) {
                await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for 100ms
            }  
            let personalities = this.$store.state.personalities

            this.personalityAvatars = personalities.map(item => {
                const newItem = {
                    name: item.name,
                    avatar: item.avatar
                }
                return newItem
            })
        },
        getAvatar(sender) {
            if (sender.toLowerCase().trim() == this.$store.state.config.user_name.toLowerCase().trim()){
                return "user_infos/"+this.$store.state.config.user_avatar
            }
            const index = this.personalityAvatars.findIndex((x) => x.name === sender)
            const pers = this.personalityAvatars[index]
            if (pers) {
                console.log("Avatar",pers.avatar)
                return pers.avatar
            }

            return
        },
        setFileListChat(files) {


            try {
                this.$refs.chatBox.fileList = this.$refs.chatBox.fileList.concat(files)
            } catch (error) {
                this.$store.state.toast.showToast("Failed to set filelist in chatbox\n" + error.message, 4, false)

            }


            this.isDragOverChat = false


        },
        async setFileListDiscussion(files) {

            if (files.length > 1) {
                this.$store.state.toast.showToast("Failed to import discussions. Too many files", 4, false)
                return
            }
            const obj = await this.parseJsonFile(files[0])

            const res = await this.import_multiple_discussions(obj)
            if (res) {
                this.$store.state.toast.showToast("Successfully imported (" + obj.length + ")", 4, true)
                await this.list_discussions()
            } else {
                this.$store.state.toast.showToast("Failed to import discussions", 4, false)
            }


            this.isDragOverDiscussion = false
        },
    },
    async created() {
        console.log("Created discussions view")
        const response = await axios.get('/get_versionID');
        const serverVersionId = response.data.versionId;

        socket.onopen = () => {
            console.log('WebSocket connection established.');
            if (this.currentDiscussion!=null){
                this.setPageTitle(item)
                localStorage.setItem('selected_discussion', this.currentDiscussion.id)
                this.load_discussion(item.id, ()=>{
                    if (this.discussionArr.length > 1) {
                        if (this.currentDiscussion.title === '' || this.currentDiscussion.title === null) {
                            this.changeTitleUsingUserMSG(this.currentDiscussion.id, this.discussionArr[1].content)
                        }
                    }
                });
            }
        };

        if (this.versionId !== serverVersionId) {
            // Update the store value
            this.$store.commit('updateVersionId', serverVersionId);
            
            // Force a page refresh
            window.location.reload(true);
        }
        this.$nextTick(() => {
            feather.replace();
        });           

        console.log("Connected to socket io")
        
        try{
        this.$store.state.loading_infos = "Getting version"
        this.$store.state.loading_progress = 30
        await this.$store.dispatch('getVersion');
        }
        catch (ex){
        console.log("Error cought:", ex)
        }


        try{
        this.$store.state.loading_infos = "Loading Configuration"
        while(socket.id===undefined){
            await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for 100ms
        }
        this.$store.state.client_id = socket.id
        console.log(this.$store.state.client_id)
        await this.$store.dispatch('refreshConfig');
        console.log("Config ready")
        }
        catch (ex){
        console.log("Error cought:", ex)
        }
        try{
        this.$store.state.loading_infos = "Loading Database"
        this.$store.state.loading_progress = 20
        await this.$store.dispatch('refreshDatabase');
        }
        catch (ex){
        console.log("Error cought:", ex)
        }

        try{
        this.$store.state.loading_infos = "Getting Bindings list"
        this.$store.state.loading_progress = 40
        await this.$store.dispatch('refreshBindings');
        }
        catch (ex){
        console.log("Error cought:", ex)
        }
    
        try{
        this.$store.state.loading_infos = "Getting personalities zoo"
        this.$store.state.loading_progress = 70
        await this.$store.dispatch('refreshPersonalitiesZoo')
        }
        catch (ex){
        console.log("Error cought:", ex)
        }
        try{
        this.$store.state.loading_infos = "Getting mounted personalities"
        this.$store.state.loading_progress = 80
        await this.$store.dispatch('refreshMountedPersonalities');
        }
        catch (ex){
        console.log("Error cought:", ex)
        }

        try{
        this.$store.state.loading_infos = "Getting models zoo"
        this.$store.state.loading_progress = 90
        await this.$store.dispatch('refreshModelsZoo');
        }
        catch (ex){
        console.log("Error cought:", ex)
        }
        try{
        this.$store.state.loading_infos = "Getting active models"
        this.$store.state.loading_progress = 100
        await this.$store.dispatch('refreshModels');
        await this.$store.dispatch('refreshModelStatus');
        }
        catch (ex){
        console.log("Error cought:", ex)
        }
    
        try{
        await this.$store.dispatch('fetchLanguages');
        await this.$store.dispatch('fetchLanguage');
        }
        catch (ex){
        console.log("Error cought:", ex)
        }
        try{
        await this.$store.dispatch('fetchisRTOn');
        }
        catch (ex){
        console.log("Error cought:", ex)
        }

        this.$store.state.isConnected=true;
        this.$store.state.client_id = socket.id
        console.log("Ready")
        // Constructor
        this.setPageTitle()
        await this.list_discussions()
        this.loadLastUsedDiscussion()

        this.isCreated = true
        this.$store.state.ready = true;    

        socket.on('connected',this.socketIOConnected)
        socket.on('disconnected',this.socketIODisconnected)
        console.log("Added events")

        // socket responses
        socket.on('show_progress', this.show_progress)
        socket.on('hide_progress', this.hide_progress)
        socket.on('update_progress', this.update_progress)
        
        socket.on('notification', this.notify)
        socket.on('new_message', this.new_message)
        socket.on('update_message', this.update_message)
        socket.on('close_message', this.finalMsgEvent)

        socket.on('disucssion_renamed',(event)=>{
            console.log('Received new title', event.discussion_id, event.title);
            const index = this.list.findIndex((x) => x.id == event.discussion_id)
            const discussionItem = this.list[index]
            discussionItem.title = event.title
            /*
            {
            'status': True,
            'discussion_id':d.id,
            'title':title
            }*/
        })
        socket.onclose = (event) => {
            console.log('WebSocket connection closed:', event.code, event.reason);
            this.socketIODisconnected();
        };
        socket.on("connect_error", (error) => {
            if (error.message === "ERR_CONNECTION_REFUSED") {
            console.error("Connection refused. The server is not available.");
            // Handle the ERR_CONNECTION_REFUSED error here
            } else {
            console.error("Connection error:", error);
            // Handle other connection errors here
            }
            this.$store.state.isConnected = false
        });        
        socket.onerror = (event) => {
            console.log('WebSocket connection error:', event.code, event.reason);
            this.socketIODisconnected();
            socket.disconnect();
        };
    },
    
    beforeUnmount() {
        window.removeEventListener('resize', this.adjustMenuPosition);
    },
    async mounted() {
        this.$store.state.toast = this.$refs.toast
        this.$store.state.news = this.$refs.news
        this.$store.state.messageBox = this.$refs.messageBox
        this.$store.state.universalForm = this.$refs.universalForm
        this.$store.state.yesNoDialog = this.$refs.yesNoDialog
        this.$store.state.personality_editor = this.$refs.personality_editor

        
        this.sunIcon = document.querySelector(".sun");
        this.moonIcon = document.querySelector(".moon");
        this.userTheme = localStorage.getItem("theme");
        this.systemTheme = window.matchMedia("prefers-color-scheme: dark").matches;
        this.themeCheck()

        nextTick(() => {
            feather.replace()
        })

        window.addEventListener('resize', this.adjustMenuPosition);

        // let serverAddress = "http://localhost:9600/";
        // try {
        //     const response = await fetch('/get_server_address'); // Replace with the actual endpoint on your Flask server
        //     serverAddress = await response.text();
        //     if(serverAddress.includes('<')){
        //         console.log(`Server address not found`)
        //         serverAddress = "http://localhost:9600/"//process.env.VITE_LOLLMS_API
                
        //     }
        //     console.log(`Server address: ${serverAddress}`)
        // } catch (error) {
        //     console.error('Error fetching server address:', error);
            // Handle error if necessary
        //     serverAddress = "http://localhost:9600/"
        // }
        // this.host = `${serverAddress}`; // Construct the full server address dynamically
        // axios.defaults.baseURL = serverAddress
        //console.log('chatbox mnt',this.$refs)
        socket.on('refresh_files',()=>{
            this.recoverFiles()
        })
        this.$nextTick(() => {
            feather.replace();
        });
    },
    async activated() {
        //console.log('settings changed acc', this.$store.state.settingsChanged)
        // await this.getPersonalityAvatars()
        while (this.isReady === false) {
                await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for 100ms
            }  
        await this.getPersonalityAvatars()
        console.log("Avatars found:",this.personalityAvatars)
        if (this.isCreated) {
           // this.loadLastUsedDiscussion()
            nextTick(() => {

                const msgList = document.getElementById('messages-list')

                this.scrollBottom(msgList)

            })
        }
        if (this.$store.state.config.show_news_panel)
            this.$store.state.news.show()
    },
    components: {
        Discussion,
        Message,
        ChatBox,
        WelcomeComponent,
        ChoiceDialog,
        ProgressBar,
        InputBox,
        SkillsLibraryViewer,
        Toast,
        MessageBox,
        ProgressBar,
        UniversalForm,
        YesNoDialog,
        
        PersonalityEditor,
        PopupViewer,
        ActionButton,
        SocialIcon

    },
    watch: {  
        '$store.state.config.fun_mode': function(newVal, oldVal) {
            console.log(`Fun mode changed from ${oldVal} to ${newVal}! 🎉`);
        },        
        '$store.state.isConnected': function(newVal, oldVal) {
            if (!this.isConnected){
                this.$store.state.messageBox.showBlockingMessage("Server suddenly disconnected. Please reboot the server to recover the connection")
                this.is_first_connection = false
                console.log("this.is_first_connection set to false")
                console.log(this.is_first_connection)
                if(this.$store.state.config.activate_audio_infos)
                    this.connection_lost_audio.play()
            }
            else{
                console.log("this.is_first_connection")
                console.log(this.is_first_connection)
                if(!this.is_first_connection){
                    this.$store.state.messageBox.hideMessage()
                    this.$store.state.messageBox.showMessage("Server connected.")
                    if(this.$store.state.config.activate_audio_infos)
                        this.connection_recovered_audio.play()
                }
            }
            nextTick(() => {
                feather.replace()
            })
        },

        messages: {
        handler: 'extractHtml',
        deep: true
        },
        progress_visibility_val(newVal) {
            console.log("progress_visibility changed to "+ newVal)
        },
        filterTitle(newVal) {
            if (newVal == '') {
                this.filterInProgress = true
                this.list = this.tempList
                this.filterInProgress = false
            }
        },
        isCheckbox(newval) {
            nextTick(() => {
                feather.replace()
            })
            if (!newval) {
                this.isSelectAll = false
            }
        },
        socketConnected(newval) {
            console.log("Websocket connected (watch)", newval)
        },
        showConfirmation() {
            nextTick(() => {
                feather.replace()

            })
        },
        isSearch() {
            nextTick(() => {
                feather.replace()

            })
        },
        
    },
    computed: { 
        isFullMode() {
          return this.$store.state.view_mode === 'full'; // Accessing the mode directly
        },      
        storeLogo(){
            if (this.$store.state.config){
                return storeLogo
            }
            return this.$store.state.config.app_custom_logo!=''?'/user_infos/'+this.$store.state.config.app_custom_logo:storeLogo
        },        
        languages: {
            get(){
                console.log("searching languages", this.$store.state.languages)
                return this.$store.state.languages
            }
        },
        language: {
            get(){
                console.log("searching language", this.$store.state.language)
                return this.$store.state.language
            }
        },
        currentPersonConfig (){
            try{
                return this.$store.state.currentPersonConfig
            }
            catch{
                console.log("Error finding current personality configuration")
                return undefined
            }
        },        
        selectedPersonality (){
            try{
                return this.$store.state.selectedPersonality
            }
            catch{
                console.log("Error finding current personality configuration")
                return undefined
            }
        },        
        
        loading_infos(){
            return this.$store.state.loading_infos;
        },
        is_fun_mode(){
            try{
                if (this.$store.state.config){
                    return this.$store.state.config.fun_mode;
                }
                else{
                    return false;
                }
            }
            catch(error){
                console.error("Oopsie! Looks like we hit a snag: ", error);
                return false;
            }
        },
        isModelOK(){
            return this.$store.state.isModelOk;
        },
        isGenerating(){
            return this.$store.state.isGenerating;
        },
        isConnected(){
            return this.$store.state.isConnected;
        },        
        ...mapState({
            versionId: state => state.versionId,
        }),
        progress_visibility: {
            get(){
                return self.progress_visibility_val;
            }
        },        
        version_info:{
            get(){
                if(this.$store.state.version!=undefined && this.$store.state.version!="unknown"){
                    return this.$store.state.version;
                }
                else{
                    return "...";
                }
            }
        },
        
        loading_infos:{
            get(){
                return this.$store.state.loading_infos;
            }
        },
        loading_progress:{
            get(){
                return this.$store.state.loading_progress;
            }
        },
        isModelOk:{
            get(){
                return this.$store.state.isModelOk;
            },
            set(val){
                this.$store.state.isModelOk=val
            }
        },
        isGenerating:{
            get(){
                return this.$store.state.isGenerating;
            },
            set(val){
                this.$store.state.isGenerating=val
            }
        },
        personality(){
            console.log("personality:", this.$store.state.config.personalities[this.$store.state.config.active_personality_id])
            const current_personality_name = this.$store.state.config.personalities[this.$store.state.config.active_personality_id]
            console.log("peronslities", this.$store.state.personalities[0])
            const personality = this.$store.state.personalities.find(personality => personality.full_path === current_personality_name);
            console.log("personality:", personality)
            return personality
        },
        prompts_list() {
            console.log(this.personality.prompts_list)
            return this.personality.prompts_list;
        },
        formatted_database_name() {
            const db_name = this.$store.state.config.discussion_db_name;
            const trimmed_name = db_name;
            return trimmed_name;
        },
        UseDiscussionHistory() {
            return this.$store.state.config.activate_skills_lib;
        }, 
        isReady() {
                return this.$store.state.ready;
        },
        databases(){            
            return this.$store.state.databases;
        },
        client_id() {
            return socket.id
        },
        showLeftPanel() {
           console.log("showLeftPanel")
           console.log(this.$store.state.leftPanelCollapsed)
           return this.$store.state.ready && !this.$store.state.leftPanelCollapsed;
        },
        showRightPanel() {
           console.log("showRightPanel")
           console.log(this.$store.state.rightPanelCollapsed)
           return this.$store.state.ready && !this.$store.state.rightPanelCollapsed;
        },        
        socketConnected() {
            console.log(" --- > Websocket connected")
            this.$store.commit('setIsConnected', true);
            return true
        },
        socketDisconnected() {
            this.$store.commit('setIsConnected', false);
            console.log(" --- > Websocket disconnected")
            return true
        },
        selectedDiscussions() {
            nextTick(() => {
                feather.replace()

            })
            return this.list.filter((item) => item.checkBoxValue == true)
        }
    }
}
</script>

<script setup>


import Discussion from '../components/Discussion.vue'
import ChoiceDialog from '@/components/ChoiceDialog.vue'
import ProgressBar from "@/components/ProgressBar.vue";
import InputBox from "@/components/input_box.vue";
import SkillsLibraryViewer from "@/components/SkillsViewer.vue"

import Message from '../components/Message.vue'
import ChatBox from '../components/ChatBox.vue'
import WelcomeComponent from '../components/WelcomeComponent.vue'

import feather from 'feather-icons'

import axios from 'axios'
import { nextTick, TransitionGroup } from 'vue'

import socket from '@/services/websocket.js'


import { onMounted } from 'vue'
import { initFlowbite } from 'flowbite'
import { store } from '../main'



// initialize components based on data attribute selectors
onMounted(() => {
    initFlowbite()
})

axios.defaults.baseURL = import.meta.env.VITE_LOLLMS_API_BASEURL
</script>
