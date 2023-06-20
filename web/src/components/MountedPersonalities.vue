<template>
    <!-- LIST OF MOUNTED PERSONALITIES -->
    <div
        class=" text-base font-semibold cursor-pointer select-none items-center flex flex-row overflow-visible overflow-x-auto scrollbar-thin scrollbar-track-bg-light scrollbar-thumb-bg-light-tone hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark dark:scrollbar-thumb-bg-dark-tone dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
        <!-- LIST -->
        <div class="flex -space-x-4 items-center ">
            <!-- ITEM -->
            <div class="relative  hover:-translate-y-2 duration-300 hover:z-10 shrink-0 "
                v-for="(item, index) in mountedPersArr" :key="index + '-' + item.name">
                <div class="group items-center flex flex-row">
                    <button @click.stop="onPersonalitySelected(item)">

                        <img :src="bUrl + item.avatar" @error="personalityImgPlacehodler"
                            class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 group-hover:border-secondary "
                            :class="configFile.active_personality_id == configFile.personalities.indexOf(item.full_path) ? 'border-secondary' : 'border-transparent z-0'"
                            :title="item.name">
                    </button>
                    <button @click.stop="onPersonalityMounted(item)">

                        <span
                            class="hidden group-hover:block top-0 left-7 absolute active:scale-90 bg-bg-light dark:bg-bg-dark rounded-full border-2  border-transparent"
                            title="Unmount personality">
                            <!-- UNMOUNT BUTTON -->
                            <svg aria-hidden="true" class="w-4 h-4 text-red-600 hover:text-red-500 " fill="currentColor"
                                viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
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
</template>

<script>
import axios from "axios";
import defaultPersonalityImgPlaceholder from "../assets/logo.svg"

const bUrl = import.meta.env.VITE_GPT4ALL_API_BASEURL
axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
    name: 'MountedPersonalities',
    setup() {


        return {
            configFile: {},
            mountedPersArr: [],
            personalities: [],
            bUrl: bUrl,
            isMounted: false,
            isLoading:false
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
        async constructor() {
            this.configFile = await this.api_get_req("get_config")
            let personality_path_infos = await this.api_get_req("get_current_personality_path_infos")
            this.configFile.personality_language = personality_path_infos["personality_language"]
            this.configFile.personality_category = personality_path_infos["personality_category"]
            this.configFile.personality_folder = personality_path_infos["personality_name"]

            await this.getPersonalitiesArr().then(() => {
                this.getMountedPersonalities()
                this.$forceUpdate()
            })
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
            this.isLoading = true
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
            this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.configFile.personality_category && item.language === this.configFile.personality_language)
            this.personalitiesFiltered.sort()

            this.isLoading = false

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

            this.isLoading = true
        },
        async onPersonalitySelected(pers) {
            // eslint-disable-next-line no-unused-vars
            if (this.isLoading) {
                this.$refs.toast.showToast("Loading... please wait", 4, false)
            }
            this.isLoading = true
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


                this.isLoading = false
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
                this.isLoading = true
                const res = await axios.post('/unmount_personality', obj);
                this.isLoading = false

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
            this.isLoading = true
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
            this.isLoading = false

        },
        async unmountPersonality(pers) {
            this.isLoading = true
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

            this.isLoading = false
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
            console.log('fig', this.configFile.personality_category)

        },
    }
}
</script>

