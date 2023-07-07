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
                        class="text-2xl hover:text-primary  p-2 -m-2 w-full text-left flex flex-row items-center ">
                        <i data-feather="chevron-right" class="mr-2  flex-shrink-0"></i>

                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            System status</h3>
                        <div class="mr-2">|</div>

                        <div class=" text-base font-semibold cursor-pointer select-none items-center">

                            <div class="flex gap-2 items-center ">
                                <div>

                                    <div v-if="vramUsage.gpus && vramUsage.gpus.length == 1">


                                        <div class="flex gap-2 items-center " v-for="item in vramUsage.gpus">

                                            <!-- GPU IMAGE  -->
                                            <svg :title="item.gpu_model" aria-hidden="true"
                                                class="w-10 h-10  fill-secondary" viewBox="0 -3 82 66" fill="none"
                                                xmlns="http://www.w3.org/2000/svg">
                                                <path
                                                    d="M 5.9133057,14.000286 H 70.974329 a 8.9999999,8.9999999 0 0 1 8.999987,8.999998 V 47.889121 H 5.9133057 Z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1116" />
                                                <path d="m 5.9133057,28.634282 h -2.244251 v -9.367697 h 2.244251 z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1118" />
                                                <path d="M 5.9133057,42.648417 H 3.6690547 V 33.28072 h 2.244251 z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1120" />
                                                <path d="m 5.9133057,47.889121 v 4.42369"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1122" />
                                                <path d="M 5.9133057,14.000286 H 2.3482707"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1124" />
                                                <path d="M 2.3482707,14.000286 V 10.006515"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1126" />
                                                <path
                                                    d="m 74.31472,30.942798 a 11.594069,11.594069 0 0 0 -23.188136,0 11.594069,11.594069 0 0 0 23.188136,0 z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1128" />
                                                <path d="m 54.568046,22.699178 a 8.1531184,8.1531184 0 0 0 8.154326,8.24362"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1130" />
                                                <path
                                                    d="M 73.935201,28.000658 A 8.1531184,8.1531184 0 0 0 62.721525,30.944293"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1132" />
                                                <path
                                                    d="m 70.873258,39.186418 a 8.1531184,8.1531184 0 0 0 -8.152606,-8.24362"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1134" />
                                                <path
                                                    d="M 59.657782,42.124981 A 8.1531184,8.1531184 0 0 0 62.719435,30.940687"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1136" />
                                                <path
                                                    d="M 51.50515,33.881361 A 8.1531184,8.1531184 0 0 0 62.720652,30.942798"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1138" />
                                                <path
                                                    d="M 65.783521,19.760615 A 8.1531184,8.1531184 0 0 0 62.721869,30.944909"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1140" />
                                                <path
                                                    d="m 62.720652,22.789678 a 8.1531184,8.1531184 0 0 0 -3.06287,-3.029063"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1142" />
                                                <path
                                                    d="m 69.782328,26.864746 a 8.1531184,8.1531184 0 0 0 1.09093,-4.165568"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1144" />
                                                <path
                                                    d="m 69.781455,35.019358 a 8.1531184,8.1531184 0 0 0 4.154699,-1.137997"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1146" />
                                                <path d="m 62.722372,39.09293 a 8.1531184,8.1531184 0 0 0 3.064668,3.031085"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1148" />
                                                <path
                                                    d="m 55.659849,35.019358 a 8.1531184,8.1531184 0 0 0 -1.091803,4.16706"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1150" />
                                                <path
                                                    d="M 55.659849,26.866238 A 8.1531184,8.1531184 0 0 0 51.50515,28.004235"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1152" />
                                                <path d="m 22.744016,47.889121 h 38.934945 v 4.42369 H 22.744016 Z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1154" />
                                                <path d="m 20.54627,47.889121 h -4.395478 v 4.42369 h 4.395478 z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1156" />
                                                <path
                                                    d="m 40.205007,30.942798 a 11.594071,11.594071 0 0 0 -23.188141,0 11.594071,11.594071 0 0 0 23.188141,0 z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1158" />
                                                <path d="m 20.458317,22.699178 a 8.1531184,8.1531184 0 0 0 8.154342,8.24362"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1160" />
                                                <path
                                                    d="m 35.672615,26.864746 a 8.1531184,8.1531184 0 0 0 1.09093,-4.165568"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1162" />
                                                <path
                                                    d="M 39.825489,28.000658 A 8.1531184,8.1531184 0 0 0 28.611786,30.944293"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1164" />
                                                <path d="m 28.612659,39.09293 a 8.1531184,8.1531184 0 0 0 3.064669,3.031085"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1166" />
                                                <path
                                                    d="m 36.763545,39.186418 a 8.1531184,8.1531184 0 0 0 -8.152606,-8.24362"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1168" />
                                                <path
                                                    d="m 21.550126,35.019358 a 8.1531184,8.1531184 0 0 0 -1.091809,4.16706"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1170" />
                                                <path
                                                    d="M 25.54807,42.124981 A 8.1531184,8.1531184 0 0 0 28.609722,30.940687"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1172" />
                                                <path
                                                    d="m 21.550126,26.866238 a 8.1531184,8.1531184 0 0 0 -4.154684,1.137997"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1174" />
                                                <path
                                                    d="M 17.395442,33.881361 A 8.1531184,8.1531184 0 0 0 28.610939,30.942798"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1176" />
                                                <path
                                                    d="M 28.610939,22.789678 A 8.1531184,8.1531184 0 0 0 25.54807,19.760615"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1178" />
                                                <path
                                                    d="M 31.673809,19.760615 A 8.1531184,8.1531184 0 0 0 28.612156,30.944909"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1180" />
                                                <path
                                                    d="m 35.671742,35.019358 a 8.1531184,8.1531184 0 0 0 4.154673,-1.137997"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1182" />
                                            </svg>
                                            <h3 class="font-bold font-large text-lg">
                                                <div>{{ item.used_vram }} / {{ item.total_vram }} ({{ item.percentage }}%)
                                                </div>
                                            </h3>
                                        </div>
                                    </div>
                                    <div v-if="vramUsage.gpus && vramUsage.gpus.length >1">
                                        <div class="flex gap-2 items-center ">

                                            <!-- GPU IMAGE  -->
                                            <svg  aria-hidden="true"
                                                class="w-10 h-10  fill-secondary" viewBox="0 -3 82 66" fill="none"
                                                xmlns="http://www.w3.org/2000/svg">
                                                <path
                                                    d="M 5.9133057,14.000286 H 70.974329 a 8.9999999,8.9999999 0 0 1 8.999987,8.999998 V 47.889121 H 5.9133057 Z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1116" />
                                                <path d="m 5.9133057,28.634282 h -2.244251 v -9.367697 h 2.244251 z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1118" />
                                                <path d="M 5.9133057,42.648417 H 3.6690547 V 33.28072 h 2.244251 z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1120" />
                                                <path d="m 5.9133057,47.889121 v 4.42369"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1122" />
                                                <path d="M 5.9133057,14.000286 H 2.3482707"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1124" />
                                                <path d="M 2.3482707,14.000286 V 10.006515"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1126" />
                                                <path
                                                    d="m 74.31472,30.942798 a 11.594069,11.594069 0 0 0 -23.188136,0 11.594069,11.594069 0 0 0 23.188136,0 z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1128" />
                                                <path d="m 54.568046,22.699178 a 8.1531184,8.1531184 0 0 0 8.154326,8.24362"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1130" />
                                                <path
                                                    d="M 73.935201,28.000658 A 8.1531184,8.1531184 0 0 0 62.721525,30.944293"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1132" />
                                                <path
                                                    d="m 70.873258,39.186418 a 8.1531184,8.1531184 0 0 0 -8.152606,-8.24362"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1134" />
                                                <path
                                                    d="M 59.657782,42.124981 A 8.1531184,8.1531184 0 0 0 62.719435,30.940687"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1136" />
                                                <path
                                                    d="M 51.50515,33.881361 A 8.1531184,8.1531184 0 0 0 62.720652,30.942798"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1138" />
                                                <path
                                                    d="M 65.783521,19.760615 A 8.1531184,8.1531184 0 0 0 62.721869,30.944909"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1140" />
                                                <path
                                                    d="m 62.720652,22.789678 a 8.1531184,8.1531184 0 0 0 -3.06287,-3.029063"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1142" />
                                                <path
                                                    d="m 69.782328,26.864746 a 8.1531184,8.1531184 0 0 0 1.09093,-4.165568"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1144" />
                                                <path
                                                    d="m 69.781455,35.019358 a 8.1531184,8.1531184 0 0 0 4.154699,-1.137997"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1146" />
                                                <path d="m 62.722372,39.09293 a 8.1531184,8.1531184 0 0 0 3.064668,3.031085"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1148" />
                                                <path
                                                    d="m 55.659849,35.019358 a 8.1531184,8.1531184 0 0 0 -1.091803,4.16706"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1150" />
                                                <path
                                                    d="M 55.659849,26.866238 A 8.1531184,8.1531184 0 0 0 51.50515,28.004235"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1152" />
                                                <path d="m 22.744016,47.889121 h 38.934945 v 4.42369 H 22.744016 Z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1154" />
                                                <path d="m 20.54627,47.889121 h -4.395478 v 4.42369 h 4.395478 z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1156" />
                                                <path
                                                    d="m 40.205007,30.942798 a 11.594071,11.594071 0 0 0 -23.188141,0 11.594071,11.594071 0 0 0 23.188141,0 z"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1158" />
                                                <path d="m 20.458317,22.699178 a 8.1531184,8.1531184 0 0 0 8.154342,8.24362"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1160" />
                                                <path
                                                    d="m 35.672615,26.864746 a 8.1531184,8.1531184 0 0 0 1.09093,-4.165568"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1162" />
                                                <path
                                                    d="M 39.825489,28.000658 A 8.1531184,8.1531184 0 0 0 28.611786,30.944293"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1164" />
                                                <path d="m 28.612659,39.09293 a 8.1531184,8.1531184 0 0 0 3.064669,3.031085"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1166" />
                                                <path
                                                    d="m 36.763545,39.186418 a 8.1531184,8.1531184 0 0 0 -8.152606,-8.24362"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1168" />
                                                <path
                                                    d="m 21.550126,35.019358 a 8.1531184,8.1531184 0 0 0 -1.091809,4.16706"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1170" />
                                                <path
                                                    d="M 25.54807,42.124981 A 8.1531184,8.1531184 0 0 0 28.609722,30.940687"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1172" />
                                                <path
                                                    d="m 21.550126,26.866238 a 8.1531184,8.1531184 0 0 0 -4.154684,1.137997"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1174" />
                                                <path
                                                    d="M 17.395442,33.881361 A 8.1531184,8.1531184 0 0 0 28.610939,30.942798"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1176" />
                                                <path
                                                    d="M 28.610939,22.789678 A 8.1531184,8.1531184 0 0 0 25.54807,19.760615"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1178" />
                                                <path
                                                    d="M 31.673809,19.760615 A 8.1531184,8.1531184 0 0 0 28.612156,30.944909"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1180" />
                                                <path
                                                    d="m 35.671742,35.019358 a 8.1531184,8.1531184 0 0 0 4.154673,-1.137997"
                                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1"
                                                    id="path1182" />
                                            </svg>
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
                    <div class="mb-2" v-for="item in vramUsage.gpus">
                        <label class="flex items-center gap-1 ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            <!-- GPU IMAGE  -->
                            <svg aria-hidden="true" class="w-10 h-10 -my-5 fill-secondary" viewBox="0 -3 82 66" fill="none"
                                xmlns="http://www.w3.org/2000/svg">
                                <path
                                    d="M 5.9133057,14.000286 H 70.974329 a 8.9999999,8.9999999 0 0 1 8.999987,8.999998 V 47.889121 H 5.9133057 Z"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1116" />
                                <path d="m 5.9133057,28.634282 h -2.244251 v -9.367697 h 2.244251 z"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1118" />
                                <path d="M 5.9133057,42.648417 H 3.6690547 V 33.28072 h 2.244251 z"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1120" />
                                <path d="m 5.9133057,47.889121 v 4.42369"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1122" />
                                <path d="M 5.9133057,14.000286 H 2.3482707"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1124" />
                                <path d="M 2.3482707,14.000286 V 10.006515"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1126" />
                                <path
                                    d="m 74.31472,30.942798 a 11.594069,11.594069 0 0 0 -23.188136,0 11.594069,11.594069 0 0 0 23.188136,0 z"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1128" />
                                <path d="m 54.568046,22.699178 a 8.1531184,8.1531184 0 0 0 8.154326,8.24362"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1130" />
                                <path d="M 73.935201,28.000658 A 8.1531184,8.1531184 0 0 0 62.721525,30.944293"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1132" />
                                <path d="m 70.873258,39.186418 a 8.1531184,8.1531184 0 0 0 -8.152606,-8.24362"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1134" />
                                <path d="M 59.657782,42.124981 A 8.1531184,8.1531184 0 0 0 62.719435,30.940687"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1136" />
                                <path d="M 51.50515,33.881361 A 8.1531184,8.1531184 0 0 0 62.720652,30.942798"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1138" />
                                <path d="M 65.783521,19.760615 A 8.1531184,8.1531184 0 0 0 62.721869,30.944909"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1140" />
                                <path d="m 62.720652,22.789678 a 8.1531184,8.1531184 0 0 0 -3.06287,-3.029063"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1142" />
                                <path d="m 69.782328,26.864746 a 8.1531184,8.1531184 0 0 0 1.09093,-4.165568"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1144" />
                                <path d="m 69.781455,35.019358 a 8.1531184,8.1531184 0 0 0 4.154699,-1.137997"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1146" />
                                <path d="m 62.722372,39.09293 a 8.1531184,8.1531184 0 0 0 3.064668,3.031085"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1148" />
                                <path d="m 55.659849,35.019358 a 8.1531184,8.1531184 0 0 0 -1.091803,4.16706"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1150" />
                                <path d="M 55.659849,26.866238 A 8.1531184,8.1531184 0 0 0 51.50515,28.004235"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1152" />
                                <path d="m 22.744016,47.889121 h 38.934945 v 4.42369 H 22.744016 Z"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1154" />
                                <path d="m 20.54627,47.889121 h -4.395478 v 4.42369 h 4.395478 z"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1156" />
                                <path
                                    d="m 40.205007,30.942798 a 11.594071,11.594071 0 0 0 -23.188141,0 11.594071,11.594071 0 0 0 23.188141,0 z"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1158" />
                                <path d="m 20.458317,22.699178 a 8.1531184,8.1531184 0 0 0 8.154342,8.24362"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1160" />
                                <path d="m 35.672615,26.864746 a 8.1531184,8.1531184 0 0 0 1.09093,-4.165568"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1162" />
                                <path d="M 39.825489,28.000658 A 8.1531184,8.1531184 0 0 0 28.611786,30.944293"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1164" />
                                <path d="m 28.612659,39.09293 a 8.1531184,8.1531184 0 0 0 3.064669,3.031085"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1166" />
                                <path d="m 36.763545,39.186418 a 8.1531184,8.1531184 0 0 0 -8.152606,-8.24362"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1168" />
                                <path d="m 21.550126,35.019358 a 8.1531184,8.1531184 0 0 0 -1.091809,4.16706"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1170" />
                                <path d="M 25.54807,42.124981 A 8.1531184,8.1531184 0 0 0 28.609722,30.940687"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1172" />
                                <path d="m 21.550126,26.866238 a 8.1531184,8.1531184 0 0 0 -4.154684,1.137997"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1174" />
                                <path d="M 17.395442,33.881361 A 8.1531184,8.1531184 0 0 0 28.610939,30.942798"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1176" />
                                <path d="M 28.610939,22.789678 A 8.1531184,8.1531184 0 0 0 25.54807,19.760615"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1178" />
                                <path d="M 31.673809,19.760615 A 8.1531184,8.1531184 0 0 0 28.612156,30.944909"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1180" />
                                <path d="m 35.671742,35.019358 a 8.1531184,8.1531184 0 0 0 4.154673,-1.137997"
                                    style="fill:none;stroke:currentColor;stroke-width:2.5;stroke-opacity:1" id="path1182" />
                            </svg>
                            GPU usage:
                        </label>
                        <div class="flex flex-col mx-2">
                            <div><b>Model:&nbsp;</b>{{ item.gpu_model }}</div>
                            <div><b>Avaliable vram:&nbsp;</b>{{ item.available_space }}</div>
                            <div><b>GPU usage:&nbsp;</b> {{ item.used_vram }} / {{ item.total_vram }} ({{ item.percentage
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
            <!-- BINDING ZOO -->
            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="bzc_collapsed = !bzc_collapsed"
                        class="text-2xl hover:text-primary p-2 -m-2 w-full text-left flex flex-row items-center">
                        <i data-feather="chevron-right" class="mr-2 flex-shrink-0"></i>

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

                    <div v-if="bindings.length > 0" class="mb-2">
                        <label for="binding" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Bindings: ({{ bindings.length }})
                        </label>
                        <div class="overflow-y-auto no-scrollbar p-2 pb-0 grid lg:grid-cols-3 md:grid-cols-2 gap-4"
                            :class="bzl_collapsed ? '' : 'max-h-96'">
                            <TransitionGroup name="list">
                                <BindingEntry ref="bindingZoo" v-for="(binding, index) in bindings"
                                    :key="'index-' + index + '-' + binding.folder" :binding="binding"
                                    :on-selected="onSelectedBinding" :on-reinstall="onReinstallBinding"
                                    :on-install="onInstallBinding" :on-settings="onSettingsBinding"
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
                    <button @click.stop="mzc_collapsed = !mzc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 w-full text-left flex items-center">
                        <i :data-feather="mzc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2 flex-shrink-0"></i>
                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Models zoo</h3>
                        <div class="flex flex-row items-center">

                            <div v-if="!configFile.binding_name"
                                class="text-base text-red-600 flex gap-3 items-center mr-2">
                                <i data-feather="alert-triangle" class="flex-shrink-0"></i>
                                Select binding first!
                            </div>

                            <div v-if="!isModelSelected && configFile.binding_name"
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

                        <form>

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
                                    placeholder="Search models..." required v-model="searchModel"
                                    @keyup.stop="searchModel_func">
                                <button v-if="searchModel" @click.stop="searchModel = ''" type="button"
                                    class="text-white absolute right-2.5 bottom-2.5 bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm px-4 py-2 dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">
                                    Clear search</button>

                                <!-- @input="filterPersonalities()" -->

                            </div>
                        </form>

                    </div>
                    <div v-if="searchModel">
                        <div v-if="modelsFiltered.length > 0" class="mb-2">
                            <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                Search results: ({{ modelsFiltered.length }})
                            </label>

                            <div class="overflow-y-auto no-scrollbar p-2 pb-0 grid lg:grid-cols-3 md:grid-cols-2 gap-4"
                                :class="mzl_collapsed ? '' : 'max-h-96'">
                                <TransitionGroup name="list">
                                    <model-entry ref="modelZoo" v-for="(model, index) in modelsFiltered"
                                        :key="'index-' + index + '-' + model.title" :title="model.title" :icon="model.icon"
                                        :path="model.path" :owner="model.owner" :owner_link="model.owner_link"
                                        :license="model.license" :description="model.description"
                                        :is-installed="model.isInstalled" :on-install="onInstall"
                                        :on-uninstall="onUninstall" :on-selected="onSelected"
                                        :selected="model.title === configFile.model_name" :model="model"
                                        :model_type="model.model_type" :on-copy="onCopy" :on-copy-link="onCopyLink"
                                        :on-cancel-install="onCancelInstall" />
                                </TransitionGroup>
                            </div>
                        </div>

                    </div>
                    <div v-if="!searchModel">

                        <div v-if="models.length > 0" class="mb-2">
                            <label for="model" class="block ml-2 mb-2 text-sm font-medium text-gray-900 dark:text-white">
                                Models: ({{ models.length }})
                            </label>

                            <div class="overflow-y-auto no-scrollbar p-2 pb-0 grid lg:grid-cols-3 md:grid-cols-2 gap-4"
                                :class="mzl_collapsed ? '' : 'max-h-96'">
                                <TransitionGroup name="list">
                                    <model-entry ref="modelZoo" v-for="(model, index) in models"
                                        :key="'index-' + index + '-' + model.title" :title="model.title" :icon="model.icon"
                                        :path="model.path" :owner="model.owner" :owner_link="model.owner_link"
                                        :license="model.license" :description="model.description"
                                        :is-installed="model.isInstalled" :on-install="onInstall"
                                        :on-uninstall="onUninstall" :on-selected="onSelected"
                                        :selected="model.title === configFile.model_name" :model="model"
                                        :model_type="model.model_type" :on-copy="onCopy" :on-copy-link="onCopyLink"
                                        :on-cancel-install="onCancelInstall" />
                                </TransitionGroup>
                            </div>
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
                </div>

            </div>
            <!-- ADD MODELS -->
            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row p-3">
                    <button @click.stop="mzdc_collapsed = !mzdc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 w-full text-left flex items-center">
                        <i :data-feather="mzdc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2 flex-shrink-0"></i>
                        <h3 class="text-lg font-semibold cursor-pointer select-none mr-2">
                            Add models for binding</h3>
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
                <div :class="{ 'hidden': mzdc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">

                    <div class="mb-2">
                        <!-- HIDDEN UNTIL ITS FIXED
                        <div class="p-2 " v-if="!modelDownlaodInProgress">

                            <form>
                                <div class="mb-3">
                                    <label class="block mb-2 text-sm font-medium text-gray-900 dark:text-white"
                                        for="file_input">Upload model:</label>


                                    <input @change="setFileList"
                                        class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
                                        ref="fileDialogAddModel" type="file" multiple>
                                </div>

                                <button type="button" @click.stop="uploadLocalModel"
                                    class="text-white bg-blue-700 hover:bg-blue-800 focus:ring-4 focus:outline-none focus:ring-blue-300 font-medium rounded-lg text-sm w-full sm:w-auto px-5 py-2.5 text-center dark:bg-blue-600 dark:hover:bg-blue-700 dark:focus:ring-blue-800">Upload</button>


                            </form>

                        </div> -->

                        <div class="p-2  ">

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
            <!-- PERSONALITY ZOO -->
            <div
                class="flex flex-col mb-2  rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">


                <div class="flex flex-row p-3 items-center">
                    <button @click.stop="pzc_collapsed = !pzc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 text-left w-full  flex items-center">
                        <i :data-feather="pzc_collapsed ? 'chevron-right' : 'chevron-down'" class="mr-2 flex-shrink-0 "></i>
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
                                        <button @click.stop="onPersonalityMounted(item)">

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
                <div :class="{ 'hidden': pzc_collapsed }" class="flex flex-col mb-2 px-3 pb-0">
                    <!-- SEARCH BAR -->
                    <div class="mx-2 mb-4">

                        <form>
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
                        </form>

                    </div>
                    <div class="mx-2 mb-4" v-if="!searchPersonality">
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
                    <div class="mx-2 mb-4" v-if="!searchPersonality">
                        <label for="persCat" class="block  mb-2 text-sm font-medium text-gray-900 dark:text-white">
                            Personalities Category: ({{ persCatgArr.length }})
                        </label>
                        <select id="persCat" @change="update_setting('personality_category', $event.target.value, refresh)"
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
                                        :full_path="pers.full_path"
                                        :selected="configFile.active_personality_id == configFile.personalities.findIndex(item => item === pers.full_path)"
                                        :on-selected="onPersonalitySelected" :on-mounted="onPersonalityMounted" on-reinstall="onPersonalityReinstall"
                                        :on-settings="onSettingsPersonality" />
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
                class="flex flex-col mb-2 p-3 rounded-lg bg-bg-light-tone dark:bg-bg-dark-tone hover:bg-bg-light-tone-panel hover:dark:bg-bg-dark-tone-panel duration-150 shadow-lg">
                <div class="flex flex-row">
                    <button @click.stop="mc_collapsed = !mc_collapsed"
                        class="text-2xl hover:text-primary  p-2 -m-2 w-full text-left flex items-center">
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

                </div>
            </div>
        </div>
    </div>


    <YesNoDialog ref="yesNoDialog" class="z-20" />
    <AddModelDialog ref="addmodeldialog" />
    <MessageBox ref="messageBox" />
    <Toast ref="toast" />
    <UniversalForm ref="universalForm" class="z-20" />
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
import AddModelDialog from "@/components/AddModelDialog.vue";
import UniversalForm from '../components/UniversalForm.vue';
const bUrl = import.meta.env.VITE_GPT4ALL_API_BASEURL
axios.defaults.baseURL = import.meta.env.VITE_GPT4ALL_API_BASEURL
export default {
    components: {
        AddModelDialog,
        MessageBox,
        YesNoDialog,
        ModelEntry,
        // eslint-disable-next-line vue/no-unused-components
        PersonalityViewer,
        Toast,
        PersonalityEntry,
        BindingEntry,
        UniversalForm
    },
    data() {

        return {
            // install custom model
            addModelDialogVisibility: false,
            modelPath: '',
            // Zoo stuff
            models: [],
            personalities: [],
            personalitiesFiltered: [],
            modelsFiltered: [],
            bindings: [],
            // Accordeon stuff 
            collapsedArr: [],
            all_collapsed: true,
            bec_collapsed: true,
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
            vramUsage: {},
            mountedPersArr: [],
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

        //await socket.on('install_progress', this.progressListener);

    }, methods: {
        async constructor() {
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


            this.bindingsArr.sort((a, b) => a.name.localeCompare(b.name))
            this.modelsArr.sort()
            this.persLangArr.sort()
            this.persCatgArr.sort()
            this.persArr.sort()
            this.langArr.sort()


            await this.getPersonalitiesArr()


            this.bindings = await this.api_get_req("list_bindings")
            this.bindings.sort((a, b) => a.name.localeCompare(b.name))
            this.isLoading = false
            this.diskUsage = await this.api_get_req("disk_usage")
            this.ramUsage = await this.api_get_req("ram_usage")
            this.vramUsage = await this.getVramUsage()
            this.getMountedPersonalities()
            this.isMounted = true



        },
        async open_mzl(){
            this.mzl_collapsed = !this.mzl_collapsed; 
            console.log("Fetching models")
            //this.fetchModels();
        },        
        async getVramUsage() {
            const resp = await this.api_get_req("vram_usage")
            // {
            //   "gpu_0_total_vram": 11811160064,
            //   "gpu_0_used_vram": 3177185280,
            //   "nb_gpus": 1
            // }

            const gpuArr = []

            if (resp.nb_gpus > 0) {
                // Get keys
                const keys = Object.keys(resp)
                // for each gpu
                for (let i = 0; i < resp.nb_gpus; i++) {




                    const total_vram = resp[`gpu_${i}_total_vram`];
                    const used_vram = resp[`gpu_${i}_used_vram`];
                    const model = resp[`gpu_${i}_model`];
                    const percentage = (used_vram / total_vram) * 100
                    const available_space = total_vram - used_vram



                    gpuArr.push({
                        total_vram: this.computedFileSize(total_vram),
                        used_vram: this.computedFileSize(used_vram),
                        gpu_index: i,
                        gpu_model: model,
                        percentage: percentage.toFixed(2),
                        available_space: this.computedFileSize(available_space)
                    });

                }
                const result = {

                    "nb_gpus": resp.nb_gpus,
                    "gpus": gpuArr
                }
                //console.log('gpu usage: ',result)
                return result

            }
            else{
                const result = {
                "nb_gpus": 0,
                "gpus": []
                }
                //console.log('gpu usage: ',result)
                return result

            }



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
                    const index = this.$refs.modelZoo.findIndex(item => item.model.path == response.model_url && item.model.title == response.model_name && this.configFile.binding_name == response.binding_folder)
                    const modelEntry = this.models[index]

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
                    }
                }
            } else if (response.status === 'succeeded') {
                console.log("Received succeeded")

                console.log("Installed successfully")

                if (this.$refs.modelZoo) {
                    const index = this.$refs.modelZoo.findIndex(item => item.model.path == response.model_url && item.model.title == response.model_name && this.configFile.binding_name == response.binding_folder)
                    const modelEntry = this.models[index]

                    if (modelEntry) {
                        // Model found

                        modelEntry.installing = false
                        modelEntry.isInstalled = true

                    }
                }


                this.$refs.toast.showToast("Model:\n" + model_object.title + "\ninstalled!", 4, true)
                this.api_get_req("disk_usage").then(response => {
                    this.diskUsage = response
                })
            } else if (response.status === 'failed') {

                console.log("Install failed")
                // Installation failed or encountered an error
                if (this.$refs.modelZoo) {
                    const index = this.$refs.modelZoo.findIndex(item => item.model.path == response.model_url && item.model.title == response.model_name && this.configFile.binding_name == response.binding_folder)
                    const modelEntry = this.models[index]

                    if (modelEntry) {
                        // Model found

                        modelEntry.installing = false
                        modelEntry.isInstalled = false

                    }
                    console.error('Installation failed:', response.error);
                    this.$refs.toast.showToast("Model:\n" + model_object.title + "\nfailed to install!", 4, false)
                    this.api_get_req("disk_usage").then(response => {
                        this.diskUsage = response
                    })
                }
            }
        },
        showAddModelDialog() {
            this.$refs.addmodeldialog.showDialog("").then(() => {
                console.log(this.$refs.addmodeldialog.model_path);

                // Make a POST request to the "install model" endpoint
                const path = this.$refs.addmodeldialog.model_path;

                // Emit an event to the Socket.IO server
                socket.emit("install_model", { path: path }, (response) => {
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
            this.bec_collapsed = val
            this.mzc_collapsed = val
            this.pzc_collapsed = val
            this.bzc_collapsed = val
            this.pc_collapsed = val
            this.mc_collapsed = val
            this.sc_collapsed = val
            this.mzdc_collapsed = val

        },
        fetchBindings() {
            this.api_get_req("list_bindings")
            then(response => {
                this.bindings = response
                this.bindings.sort((a, b) => a.name.localeCompare(b.name))
            })
        },
        fetchMainConfig(){
            this.api_get_req("get_config").then(response => {
                this.getPersonalitiesArr().then(() => {
                    this.getMountedPersonalities()
                })

                console.log("Received config")
                this.configFile = response


            }).then(() => {
                this.api_get_req("get_current_personality_path_infos").then(response => {
                    this.configFile.personality_language = response["personality_language"]
                    this.configFile.personality_category = response["personality_category"]
                    this.configFile.personality_folder = response["personality_name"]
                    console.log("received infos")
                });
            })
        },

        fetchModels() {
            this.api_get_req("get_available_models")
            axios.get('/get_available_models')
                .then(response => {

                    this.models = response.data;
                    this.models.sort((a, b) => a.title.localeCompare(b.title))
                    this.fetchCustomModels()
                    this.models.forEach(model => {
                        if (model.title == this.configFile["model_name"]) {
                            model.selected = true;
                        }
                        else {
                            model.selected = false;
                        }
                    });

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
            this.api_get_req("disk_usage").then(response => {
                this.diskUsage = response
            })

            this.api_get_req("ram_usage").then(response => {
                this.ramUsage = response
            })
        },
        async onPersonalitySelected(pers) {
            console.log('on pers', pers)
            // eslint-disable-next-line no-unused-vars
            if (this.isLoading) {
                this.$refs.toast.showToast("Loading... please wait", 4, false)
            }
            this.isLoading = true
            console.log('ppa', pers)
            if (pers) {

                if (pers.selected) {
                    this.$refs.toast.showToast("Personality already selected", 4, true)
                    this.isLoading = false
                    return
                }


                //this.settingsChanged = true

                if (pers.isMounted && this.configFile.personalities.includes(pers.personality.full_path)) {

                    const res = await this.select_personality(pers)
                    console.log('pers is mounted', res)
                    if (res && res.status && res.active_personality_id > -1) {
                        this.$refs.toast.showToast("Selected personality:\n" + pers.name, 4, true)

                    } else {
                        this.$refs.toast.showToast("Error on select personality:\n" + pers.name, 4, false)
                    }
                    this.isLoading = false

                } else {
                    console.log('mounting pers')
                    this.onPersonalityMounted(pers)

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
        onCopyLink(modelEntry) {

            this.$refs.toast.showToast("Copied link to clipboard!", 4, true)
            navigator.clipboard.writeText(modelEntry.path);
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
            this.$refs.toast.showToast("Model installation aborted", 4, false)
            socket.emit('cancel_install', { model_name: modelEntry.model_name, binding_folder: modelEntry.binding_folder, model_url: modelEntry.model_url });
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
            this.addModel = { model_name: model_object.model.title, binding_folder: this.configFile.binding_name, model_url: model_object.path }
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
                        const index = this.models.findIndex((model) => model.path === path);
                        this.models[index].isInstalled = true;
                        this.showProgress = false;
                        model_object.installing = false

                        console.log("Received succeeded")
                        socket.off('install_progress', progressListener);
                        console.log("Installed successfully")
                        // Update the isInstalled property of the corresponding model

                        this.$refs.toast.showToast("Model:\n" + model_object.title + "\ninstalled!", 4, true)
                        this.api_get_req("disk_usage").then(response => {
                            this.diskUsage = response
                        })
                    }
                } else {
                    socket.off('install_progress', progressListener);
                    console.log("Install failed")
                    // Installation failed or encountered an error
                    model_object.installing = false;

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
        onInstallAddModel() {



            if (!this.addModel.url) {

                this.$refs.toast.showToast("Link is empty", 4, false)
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
                    this.modelDownlaodInProgress = true
                    if (this.addModel.progress == 100) {

                        this.modelDownlaodInProgress = false

                        console.log("Received succeeded")
                        socket.off('install_progress', progressListener);
                        console.log("Installed successfully")
                        // Update the isInstalled property of the corresponding model
                        this.addModel = {}
                        this.$refs.toast.showToast("Model:\n" + this.addModel.model_name + "\ninstalled!", 4, true)
                        this.api_get_req("disk_usage").then(response => {
                            this.diskUsage = response
                        })
                    }
                } else {
                    socket.off('install_progress', progressListener);
                    console.log("Install failed")
                    // Installation failed or encountered an error
                    this.modelDownlaodInProgress = false;


                    console.error('Installation failed:', response.error);
                    this.$refs.toast.showToast("Model:\n" + this.addModel.model_name + "\nfailed to install!", 4, false)
                    this.api_get_req("disk_usage").then(response => {
                        this.diskUsage = response
                    })
                }
            };

            socket.on('install_progress', progressListener);


            socket.emit('install_model', { path: path });
            console.log("Started installation, please wait");
        },
        uploadLocalModel() {


            if (this.uploadData.length == 0) {

                this.$refs.toast.showToast("No files to upload", 4, false)
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
                    this.modelDownlaodInProgress = true
                    if (this.addModel.progress == 100) {

                        this.modelDownlaodInProgress = false

                        console.log("Received succeeded")
                        socket.off('progress', progressListener);
                        console.log("Installed successfully")
                        // Update the isInstalled property of the corresponding model
                        this.addModel = {}
                        this.$refs.toast.showToast("Model:\n" + this.addModel.model_name + "\ninstalled!", 4, true)
                        this.api_get_req("disk_usage").then(response => {
                            this.diskUsage = response
                        })
                    }
                } else {
                    socket.off('progress', progressListener);
                    console.log("Install failed")
                    // Installation failed or encountered an error
                    this.modelDownlaodInProgress = false;


                    console.error('Installation failed:', response.error);
                    this.$refs.toast.showToast("Model:\n" + this.addModel.model_name + "\nfailed to install!", 4, false)
                    this.api_get_req("disk_usage").then(response => {
                        this.diskUsage = response
                    })
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

            this.$refs.yesNoDialog.askQuestion("Are you sure you want to delete this model?\n [" + model_object.title + "]", 'Yes', 'Cancel').then(yesRes => {
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
                            const index = this.models.findIndex((model) => model.path === model_object.path);
                            this.models[index].isInstalled = false;
                            if (model_object.model.isCustomModel) {
                                this.models = this.models.filter((model) => model.title !== model_object.title)
                            }
                            this.$refs.toast.showToast("Model:\n" + model_object.title + "\nwas uninstalled!", 4, true)
                            this.api_get_req("disk_usage").then(response => {
                                this.diskUsage = response
                            })
                        } else {
                            console.log("uninstalling failed", response)
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

                }

            })
        },
        onSelectedBinding(binding_object) {
            if (!binding_object.binding.installed) {
                this.$refs.toast.showToast("Binding is not installed:\n" + binding_object.binding.name, 4, false)
                return
            }
            if (this.configFile.binding_name != binding_object.binding.folder) {

                // disabled for now
                // if (binding_object.binding.folder === 'backend_template' || binding_object.binding.folder === 'binding_template') {
                //     this.$refs.toast.showToast("Cannot select template", 4, false)

                //     return
                // }
                this.update_binding(binding_object.binding.folder)
                this.fetchModels();
                //console.log('lol',binding_object)
            }
        },
        onInstallBinding(binding_object) {

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
        onReinstallBinding(binding_object) {
            this.isLoading = true
            axios.post('/reinstall_binding', { name: binding_object.binding.folder }).then((res) => {

                if (res) {
                    this.isLoading = false
                    console.log('reinstall_binding', res)
                    if (res.data.status) {
                        this.$refs.toast.showToast("Reinstalled binding successfully!", 4, true)
                    } else {
                        this.$refs.toast.showToast("Could not reinstall binding", 4, false)
                    }
                    return res.data;
                }
                this.isLoading = false
            })
                // eslint-disable-next-line no-unused-vars

                .catch(error => {
                    this.isLoading = false
                    this.$refs.toast.showToast("Could not reinstall binding\n" + error.message, 4, false)
                    return { 'status': false }
                });
        },
        onSettingsBinding(bindingEntry) {

            try {
                this.isLoading = true
                axios.get('/get_active_binding_settings').then(res => {
                    this.isLoading = false
                    if (res) {

                        console.log('binding sett', res)

                        if (res.data && Object.keys(res.data).length > 0) {

                            // open form

                            this.$refs.universalForm.showForm(res.data, "Binding settings - " + bindingEntry.binding.name, "Save changes", "Cancel").then(res => {
                                // send new data
                                try {
                                    axios.post('/set_active_binding_settings',
                                        res).then(response => {

                                            if (response && response.data) {
                                                console.log('binding set with new settings', response.data)
                                                this.$refs.toast.showToast("Binding settings updated successfully!", 4, true)

                                            } else {
                                                this.$refs.toast.showToast("Did not get binding settings responses.\n" + response, 4, false)
                                                this.isLoading = false
                                            }


                                        })
                                } catch (error) {
                                    this.$refs.toast.showToast("Did not get binding settings responses.\n Endpoint error: " + error.message, 4, false)
                                    this.isLoading = false
                                }



                            })
                        } else {
                            this.$refs.toast.showToast("Binding has no settings", 4, false)
                            this.isLoading = false
                        }

                    }
                })

            } catch (error) {
                this.isLoading = false
                this.$refs.toast.showToast("Could not open binding settings. Endpoint error: " + error.message, 4, false)
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
        // messagebox ok stuff
        onMessageBoxOk() {
            console.log("OK button clicked");
        },
        // Refresh stuff
        refresh() {

            this.fetchMainConfig();
            this.fetchBindings();
            this.fetchModels();
            this.fetchPersonalities();
            this.fetchHardwareInfos();

        },
        // Accordeon stuff
        toggleAccordion() {
            this.showAccordion = !this.showAccordion;
        },
        update_setting(setting_name_val, setting_value_val, next) {
            this.isLoading = true
            const obj = {
                setting_name: setting_name_val,
                setting_value: setting_value_val
            }

            axios.post('/update_setting', obj).then((res) => {

                if (res) {
                    this.isLoading = false
                    console.log('update_setting', res)
                    if (next !== undefined) {

                        next(res)
                    }
                    return res.data;
                }
                this.isLoading = false
            })
                // eslint-disable-next-line no-unused-vars

                .catch(error => {
                    this.isLoading = false
                    return { 'status': false }
                });
        },
        update_binding(value) {

            // eslint-disable-next-line no-unused-vars
            this.isLoading = true

            this.update_setting('binding_name', value, (res) => {

                const index = this.bindings.findIndex(item => item.folder == value)
                const item = this.bindings[index]
                if (item) {
                    item.installed = true
                }

                this.$refs.toast.showToast("Binding changed.", 4, true)
                this.settingsChanged = true
                this.isLoading = false

                // If binding changes then reset model
                this.update_model(null)
                this.configFile.model_name = null

                this.fetchMainConfig();
                this.fetchBindings();
                this.fetchModels();
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

            this.isLoading = true;
            axios.post('/apply_settings').then((res) => {
                this.isLoading = false;
                //console.log('apply-res',res)
                if (res.data.status) {

                    this.$refs.toast.showToast("Configuration changed successfully.", 4, true)
                    this.settingsChanged = false
                    //this.save_configuration()
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
            const config = await this.api_get_req("get_config")
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
            console.log('per filtered', this.personalitiesFiltered)
            this.isLoading = false

        },
        async filterPersonalities() {
            if (!this.searchPersonality) {
                this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.configFile.personality_category && item.language === this.configFile.personality_language)
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
                this.personalitiesFiltered = this.personalities.filter((item) => item.category === this.configFile.personality_category && item.language === this.configFile.personality_language)
                this.personalitiesFiltered.sort()
            }
            this.searchPersonalityInProgress = false

        },
        async filterModels() {
            if (!this.searchModel) {
                this.modelsFiltered = this.models
                this.modelsFiltered.sort()
                this.searchModelInProgress = false
                return
            }
            const searchTerm = this.searchModel.toLowerCase()
            const seachedModels = this.models.filter((item) => {

                if (item.title && item.title.toLowerCase().includes(searchTerm) || item.description && item.description.toLowerCase().includes(searchTerm) || item.path && item.path.toLowerCase().includes(searchTerm)) {
                    return item
                }

            })



            if (seachedModels.length > 0) {

                this.modelsFiltered = seachedModels.sort()
            } else {
                this.modelsFiltered = this.models
                this.modelsFiltered.sort()
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
                console.log(error.message, 'select_personality - settings')
                return
            }

        },
        async mountPersonality(pers) {
            this.isLoading = true
            console.log('mount pers', pers)
            if (!pers) { return }

            if (this.configFile.personalities.includes(pers.personality.full_path)) {
                this.isLoading = false
                this.$refs.toast.showToast("Personality already mounted", 4, false)

                return
            }

            const res = await this.mount_personality(pers.personality)
            console.log('mount_personality res', res)

            if (res && res.status && res.active_personality_id > -1 && res.personalities.includes(pers.personality.full_path)) {
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
                this.$refs.toast.showToast("Could not mount personality\nError: " + res.error + "\nResponse:\n" + res, 4, false)
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
                console.log('index', index)
                console.log("i:", i)
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
            //console.log('fig', this.configFile.personality_category)
            nextTick(() => {
                //console.log('accc', this.$refs.mountedPersonalities)
                //this.$store.state.mountedPersonalities = this.$refs.mountedPersonalities
            })

        },
        onPersonalityReinstall(persItem){
            console.log('on reinstall ', persItem)
            this.isLoading = true
            axios.post('/reinstall_binding', { name: binding_object.binding.folder }).then((res) => {

                if (res) {
                    this.isLoading = false
                    console.log('reinstall_binding', res)
                    if (res.data.status) {
                        this.$refs.toast.showToast("Reinstalled binding successfully!", 4, true)
                    } else {
                        this.$refs.toast.showToast("Could not reinstall binding", 4, false)
                    }
                    return res.data;
                }
                this.isLoading = false
            })
                // eslint-disable-next-line no-unused-vars

                .catch(error => {
                    this.isLoading = false
                    this.$refs.toast.showToast("Could not reinstall binding\n" + error.message, 4, false)
                    return { 'status': false }
                });
        },
        onPersonalityMounted(persItem) {
            //this.isLoading = true
            console.log('on sel ', persItem)

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

            //this.isLoading = false
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
            clearTimeout(this.searchModelTimer)
            if (this.searchModel) {
                this.searchModelInProgress = true
                setTimeout(this.filterModels, this.searchModelTimer)
            }
        }


    }, async mounted() {
        this.constructor()

    },
    activated() {
        if (this.isMounted) {
            this.constructor()
        }
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
        binding_name() {
            if (!this.isMounted) {
                return
            }
            const index = this.bindingsArr.findIndex(item => item.folder === this.configFile.binding_name)
            if (index > -1) {
                return this.bindingsArr[index].name

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
        searchModel(val) {
            if (val == "") {
                this.filterModels()
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
            const res = await this.$refs.yesNoDialog.askQuestion("Did You forgot to apply changes?\nYou need to apply changes before you leave, or else.", 'Apply configuration', 'Cancel')
            if (res) {
                this.applyConfiguration()

            }

            return false

        }
        if (!this.isModelSelected) {
            const res = await this.$refs.yesNoDialog.askQuestion("Did You forgot to select model?\nYou need to select model before you leave, or else.", 'Ok', 'Cancel')
            if (res) {
                //

            }

            return false

        }


    },
}
</script>

