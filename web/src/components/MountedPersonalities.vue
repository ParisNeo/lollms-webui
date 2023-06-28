<template>
    <!-- LIST OF MOUNTED PERSONALITIES -->


    <div class="w-fit select-none">


        <div class="flex -space-x-4 " v-if="mountedPersArr.length > 1">


            <img :src="bUrl + mountedPers.avatar" @error="personalityImgPlacehodler"
                class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 group-hover:border-secondary  border-secondary"
                :title="mountedPers.name" :key="mountedPers.key">

            <div class="flex items-center justify-center w-8 h-8 cursor-pointer text-xs font-medium text-white bg-gray-700 border-2 border-white rounded-full hover:bg-gray-600 dark:border-gray-800"
                @click.stop="toggleShowPersList" title="Click to show more">+{{ mountedPersArr.length - 1 }}</div>
        </div>
        <div class="flex -space-x-4 " v-if="mountedPersArr.length == 1">
            <img :src="bUrl + mountedPers.avatar" @error="personalityImgPlacehodler"
                class="w-8 h-8 rounded-full object-fill text-red-700 border-2 active:scale-90 group-hover:border-secondary cursor-pointer  border-secondary"
                :title="mountedPers.name" @click.stop="toggleShowPersList" :key="mountedPers.key">
        </div>

    </div>
</template>

<script>
import axios from "axios";
import defaultPersonalityImgPlaceholder from "../assets/logo.svg"
import { nextTick } from "vue";

const bUrl = import.meta.env.VITE_GPT4ALL_API_BASEURL
axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
    name: 'MountedPersonalities',
    props: {
        onShowPersList: Function,
    },
    setup() {


        return {
            configFile: {},
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
            this.show = !this.show
            this.onShowPersList(this)
        },
        async constructor() {
            
            this.configFile = await this.api_get_req("get_config")
            this.getPersonalitiesArr()
            let personality_path_infos = await this.api_get_req("get_current_personality_path_infos")
            this.configFile.personality_language = personality_path_infos["personality_language"]
            this.configFile.personality_category = personality_path_infos["personality_category"]
            this.configFile.personality_folder = personality_path_infos["personality_name"]


            
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
            // this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.configFile.personality_category && item.language === this.configFile.personality_language)
            // this.personalitiesFiltered.sort()

       
                this.getMountedPersonalities()
                nextTick(()=>{
                    this.$forceUpdate()
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
            console.log('fig', this.configFile.personality_category)

            this.mountedPers = this.personalities[this.personalities.findIndex(item => item.full_path == this.configFile.personalities[this.configFile.active_personality_id])]
            const dd = new Date()
            this.mountedPers.key = dd.getTime()
        },
    }
}
</script>

