<template>
    <!-- LIST OF MOUNTED PERSONALITIES -->


    <div class="w-fit select-none">

        <div class="flex -space-x-4 " v-if="mountedPersArr.length > 1">
            <img :src="bUrl + mountedPers.avatar" @error="personalityImgPlacehodler"
                class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:z-20 hover:-translate-y-2 duration-150  border-secondary cursor-pointer"
                :title="'Active personality: '+mountedPers.name" >

            <div class="flex items-center justify-center w-8 h-8 cursor-pointer text-xs font-medium bg-bg-light dark:bg-bg-dark border-2 hover:border-secondary  rounded-full hover:bg-bg-light-tone dark:hover:bg-bg-dark-tone dark:border-gray-800 hover:z-20 hover:-translate-y-2 duration-150 active:scale-90"
                @click.stop="toggleShowPersList" title="Click to show more">+{{ mountedPersArr.length - 1 }}</div>
        </div>
        <div class="flex -space-x-4 " v-if="mountedPersArr.length == 1">
            <img :src="bUrl + this.$store.state.mountedPers.avatar" @error="personalityImgPlacehodler"
                class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 hover:z-20 cursor-pointer  border-secondary"
                :title="'Active personality: '+this.$store.state.mountedPers.name" @click.stop="toggleShowPersList" >
        </div>
        <div v-if="mountedPersArr.length == 0" title="Loading personalities">
            <!-- SPINNER -->
            <div role="status">
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
        </div>

    </div>
</template>

<script>
import axios from "axios";
import defaultPersonalityImgPlaceholder from "../assets/logo.svg"
import { nextTick } from "vue";
import { useStore } from 'vuex'; // Import the useStore function
import { computed } from 'vue'; // Import the computed function
import { watch, ref } from 'vue';

const bUrl = import.meta.env.VITE_GPT4ALL_API_BASEURL
axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL


export default {
    name: 'MountedPersonalities',
    props: {
        onShowPersList: Function,
        onReady:Function,
    },
    data() {
        return {
            configFile: null,
            mountedPersArr: [],
            personalities: [],
            bUrl: bUrl,
            isMounted: false,
            mountedPers: {},
            show: false

        }
    },
    async mounted() {
        await this.constructor()
        this.isMounted = true
    },
    async activated() {
        if (this.isMounted) {
            await this.constructor()
        }

    },
    methods: {
        toggleShowPersList() {
            //this.show = !this.show
            this.onShowPersList()
        },
        async constructor() {
            const store = useStore();
            this.configFile = store.state.config
            console.log('configFile')
            console.log(this.configFile)
            await new Promise((resolve) => {
                const waitForPersonalities = setInterval(() => {
                if (store.state.personalities) {
                    clearInterval(waitForPersonalities);
                    resolve();
                }
                }, 100);
            });            
            this.personalities = store.state.personalities
            console.log('personalities')
            console.log(this.personalities)

            let personality_path_infos = store.state.config.personalities[store.state.config.active_personality_id]
            console.log('personality_path_infos')
            console.log(personality_path_infos)
            this.configFile.personality_language = personality_path_infos["personality_language"];
            this.configFile.personality_category = personality_path_infos["personality_category"];
            this.configFile.personality_folder = personality_path_infos["personality_name"];
            this.mountedPersArr = store.state.mountedPersArr
            console.log(this.mountedPersArr);
            console.log("Ready")
            this.onReady();
            /*
            if(this.configFile===null){
                console.log("No config file found.\nreloading")
                this.configFile = await this.api_get_req("get_config")
            } */          
        },
        async api_get_req(endpoint) {
            try {
                const res = await axios.get("/" + endpoint);

                if (res) {

                    return res.data

                }
            } catch (error) {
                console.log(error.message, 'api_get_req - mountedPersonalities')
                return
            }


        },
        async getPersonalitiesArr() {

            this.personalities = []
            const dictionary = await this.api_get_req("get_all_personalities")
            const config = await this.api_get_req("get_config")
            //this.configFile=config
            //console.log('asdas',config)
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

                        const isMounted = config.personalities.includes(langkey + '/' + catkey + '/' + item.folder)
                        // if (isMounted) {
                        //     console.log(item)
                        // }
                        let newItem = {}
                        newItem = item
                        newItem.category = catkey // add new props to items
                        newItem.language = langkey // add new props to items
                        newItem.full_path = langkey + '/' + catkey + '/' + item.folder // add new props to items
                        newItem.isMounted = isMounted // add new props to items
                        return newItem
                    })


                    if (this.personalities.length == 0) {
                        this.personalities = modPersArr
                    } else {
                        this.personalities = this.personalities.concat(modPersArr)
                    }
                }

            }

            this.personalities.sort((a, b) => a.name.localeCompare(b.name))


       
                this.getMountedPersonalities()
                nextTick(()=>{
                  
                })

        },
        personalityImgPlacehodler(event) {
            event.target.src = defaultPersonalityImgPlaceholder
        },
        onPersonalityMounted(persItem) {

            if (this.configFile.personalities.includes(persItem.full_path)) {
                //this.$refs.toast.showToast("Personality already mounted", 4, false)
                //return
                //persItem.ismounted = false
                if (this.configFile.personalities.length == 1) {
                    this.$refs.toast.showToast("Can't unmount last personality", 4, false)

                } else {
                    this.unmountPersonality(persItem)

                }
            } else {
                //persItem.ismounted = true
                this.mountPersonality(persItem)

            }


        },
        async onPersonalitySelected(pers) {
            // eslint-disable-next-line no-unused-vars
            if (this.isLoading) {
                this.$refs.toast.showToast("Loading... please wait", 4, false)
            }

            console.log('ppa', pers)
            if (pers) {

                if (pers.selected) {
                    this.$refs.toast.showToast("Personality already selected", 4, true)
                    return
                }


                this.settingsChanged = true

                if (pers.isMounted) {

                    const res = await this.select_personality(pers)
                    if (res) {
                        if (res.status) {
                            this.$refs.toast.showToast("Selected personality:\n" + pers.name, 4, true)

                        }
                    }


                } else {
                    this.onPersonalityMounted(pers)

                }



            }

        },
        async mount_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - mount_personality' } }

            try {
                const obj = {
                    language: pers.language,
                    category: pers.category,
                    folder: pers.folder
                }
                const res = await axios.post('/mount_personality', obj);

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
        async select_personality(pers) {
            if (!pers) { return { 'status': false, 'error': 'no personality - select_personality' } }
            console.log('select pers', pers)
            const id = this.configFile.personalities.findIndex(item => item === pers.full_path)

            const obj = {
                id: id
            }


            try {
                const res = await axios.post('/select_personality', obj);

                if (res) {
                    this.configFile = await this.api_get_req("get_config")
                    let personality_path_infos = await this.api_get_req("get_current_personality_path_infos")
                    this.configFile.personality_language = personality_path_infos["personality_language"]
                    this.configFile.personality_category = personality_path_infos["personality_category"]
                    this.configFile.personality_folder = personality_path_infos["personality_name"]
                    return res.data

                }
            } catch (error) {
                console.log(error, 'select_personality - settings')
                return
            }

        },
        async mountPersonality(pers) {

            console.log('mount pers', pers)
            if (!pers) { return }

            if (this.configFile.personalities.includes(pers.personality.full_path)) {
                this.$refs.toast.showToast("Personality already mounted", 4, false)
                return
            }

            const res = await this.mount_personality(pers.personality)
            console.log('mount_personality res', res)

            if (res.status) {
                this.configFile.personalities = res.personalities
                this.$refs.toast.showToast("Personality mounted", 4, true)
                pers.isMounted = true

                const res2 = await this.select_personality(pers.personality)
                if (res2.status) {
                    this.$refs.toast.showToast("Selected personality:\n" + pers.personality.name, 4, true)

                }
                this.getMountedPersonalities()
            } else {
                pers.isMounted = false
                this.$refs.toast.showToast("Could not mount personality\nError: " + res.error, 4, false)
            }


        },
        async unmountPersonality(pers) {

            if (!pers) { return }

            const res = await this.unmount_personality(pers.personality || pers)


            if (res.status) {
                this.configFile.personalities = res.personalities
                this.$refs.toast.showToast("Personality unmounted", 4, true)
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
                this.getMountedPersonalities()
                // Select some other personality
                const lastPers = this.mountedPersArr[this.mountedPersArr.length - 1]

                console.log(lastPers, this.mountedPersArr.length)
                // const res2 = await this.select_personality(lastPers.personality)
                const res2 = await this.select_personality(pers.personality)
                if (res2.status) {
                    this.$refs.toast.showToast("Selected personality:\n" + lastPers.name, 4, true)

                }


            } else {
                this.$refs.toast.showToast("Could not unmount personality\nError: " + res.error, 4, false)
            }


        },
        getMountedPersonalities() {

            let mountedPersArr = []
            console.log(this.configFile.personalities.length)
            // console.log('perrs listo',this.personalities)
            for (let i = 0; i < this.configFile.personalities.length; i++) {
                const full_path_item = this.configFile.personalities[i]
                const index = this.personalities.findIndex(item => item.full_path == full_path_item)

                const pers = this.personalities[index]
                if (pers) {
                    mountedPersArr.push(pers)
                }
                else {
                    mountedPersArr.push(this.personalities[this.personalities.findIndex(item => item.full_path == "english/generic/lollms")])
                }
            }
            this.mountedPersArr = []
            this.mountedPersArr = mountedPersArr
            //this.mountedPersArr = mountedPersArr
            console.log('getMountedPersonalities', mountedPersArr)
            console.log('fig', this)

            this.mountedPers = this.personalities[this.personalities.findIndex(item => item.full_path == this.configFile.personalities[this.configFile.active_personality_id])]

        },
    }
}
</script>

