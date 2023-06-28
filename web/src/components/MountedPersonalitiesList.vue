<template>
    <!-- LIST OF MOUNTED PERSONALITIES -->
    <div
        class="text-left overflow-visible text-base font-semibold cursor-pointer select-none items-center flex flex-row overflow-x-auto -my-2 pr-2 scrollbar-thin scrollbar-track-bg-light scrollbar-thumb-bg-light-tone hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark dark:scrollbar-thumb-bg-dark-tone dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
        <!-- LIST -->
        <div v-if="mountedPersArr.length > 0" class="m-2">
            <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                Mounted Personalities: ({{ mountedPersArr.length }})
            </label>
            <div class="overflow-y-auto no-scrollbar p-2 pb-0 grid lg:grid-cols-4 md:grid-cols-2 gap-4 max-h-96">
                <TransitionGroup name="bounce">
                    <personality-entry ref="personalitiesZoo" v-for="(pers, index) in mountedPersArr"
                        :key="'index-' + index + '-' + pers.name" :personality="pers" :full_path="pers.full_path"
                        :selected="configFile.personalities[configFile.active_personality_id]==pers.full_path"
                        :on-selected="onPersonalitySelected" :on-mounted="onPersonalityMounted"
                        :on-settings="onSettingsPersonality" />
                </TransitionGroup>
            </div>
        </div>



        <Toast ref="toast">
        </Toast>
        <UniversalForm ref="universalForm" class="z-20" />
    </div>
</template>

<script>
import axios from "axios";
import defaultPersonalityImgPlaceholder from "../assets/logo.svg"
import PersonalityEntry from './PersonalityEntry.vue'
import Toast from './Toast.vue'
import UniversalForm from './UniversalForm.vue';
const bUrl = import.meta.env.VITE_GPT4ALL_API_BASEURL
axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
    props: {



    },
    components: {
        PersonalityEntry,
        Toast,
        UniversalForm,
    },
    name: 'MountedPersonalitiesList',
    setup() {


        return {
            configFile: {},
            mountedPersArr: [],
            personalities: [],
            bUrl: bUrl,
            isMounted: false,
            isLoading: false
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
            this.configFile = await this.api_get_req("get_config").then(()=>{
              this.getPersonalitiesArr().then(() => {
                this.getMountedPersonalities()
                this.$forceUpdate()
            })
            })
            let personality_path_infos = await this.api_get_req("get_current_personality_path_infos")
            this.configFile.personality_language = personality_path_infos["personality_language"]
            this.configFile.personality_category = personality_path_infos["personality_category"]
            this.configFile.personality_folder = personality_path_infos["personality_name"]

            await this.getPersonalitiesArr()
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

            // this.getMountedPersonalities()
            //     this.$forceUpdate()

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
                            await this.constructor()

                            this.$refs.toast.showToast("Selected personality:\n" + pers.name, 4, true)
                           
                        }
                    }


                } else {
                    this.onPersonalityMounted(pers)

                }


                this.isLoading = false
            }

        },
        onSettingsPersonality(persEntry) {
            try {
                this.isLoading = true
                axios.get('/get_active_personality_settings').then(res => {
                    this.isLoading = false
                    if (res) {

                        console.log('pers sett', res)
                        if (res.data && Object.keys(res.data).length > 0) {

                            this.$refs.universalForm.showForm(res.data, "Personality settings - " + persEntry.personality.name, "Save changes", "Cancel").then(res => {

                                // send new data
                                try {
                                    axios.post('/set_active_personality_settings',
                                        res).then(response => {

                                            if (response && response.data) {
                                                console.log('personality set with new settings', response.data)
                                                this.$refs.toast.showToast("Personality settings updated successfully!", 4, true)

                                            } else {
                                                this.$refs.toast.showToast("Did not get Personality settings responses.\n" + response, 4, false)
                                                this.isLoading = false
                                            }


                                        })
                                } catch (error) {
                                    this.$refs.toast.showToast("Did not get Personality settings responses.\n Endpoint error: " + error.message, 4, false)
                                    this.isLoading = false
                                }

                            })
                        } else {
                            this.$refs.toast.showToast("Personality has no settings", 4, false)
                            this.isLoading = false
                        }

                    }
                })

            } catch (error) {
                this.isLoading = false
                this.$refs.toast.showToast("Could not open personality settings. Endpoint error: " + error.message, 4, false)
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
            console.log('fig', this.configFile)

        },
    }
}
</script>

