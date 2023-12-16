<template>
    <div class="flex-row w-[800]px y-overflow scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
        <div ref="webglContainer">
        <div class="flex-col y-overflow scrollbar-thin scrollbar-track-bg-light-tone scrollbar-thumb-bg-light-tone-panel hover:scrollbar-thumb-primary dark:scrollbar-track-bg-dark-tone dark:scrollbar-thumb-bg-dark-tone-panel dark:hover:scrollbar-thumb-primary active:scrollbar-thumb-secondary">
          <div v-if="!activePersonality || !activePersonality.scene_path" class="text-center">
            <!-- Display text when there's no scene_path or empty avatar -->
            Personality does not have a 3d avatar.
          </div>
          <div v-if="!activePersonality || (!activePersonality.avatar || activePersonality.avatar === '')" class="text-center">
            Personality does not have an avatar.
          </div>
          <FloatingFrame />
          <AudioFrame />
          <div class="floating-frame2">
            <div v-html="htmlContent"></div>
          </div>
        </div>
        </div>
    </div>
</template>
  
  <script>
  import * as THREE from 'three';
  import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
  import { TextureLoader } from 'three';
  import FloatingFrame from '@/components/FloatingFrame.vue';
  import AudioFrame from '@/components/AudioFrame.vue';
  
  
  export default {
    data(){  
      return {
          activePersonality: null
      }
    },
    props: {
      personality: {
        type: Object,
        default: () => ({}),
      },
    },
    components: {
      FloatingFrame,
      AudioFrame
    },
    computed: {
        isReady:{
            get() {
                return this.$store.state.ready;
            },
        },
    },
    watch: {
      '$store.state.mountedPersArr': 'updatePersonality',
      '$store.state.config.active_personality_id': 'updatePersonality',
    },
    async mounted() {
        while (this.isReady === false) {
            await new Promise((resolve) => setTimeout(resolve, 100)); // Wait for 100ms
        }
        console.log("Personality:", this.personality)
        this.initWebGLScene();
        this.updatePersonality();
    },
    beforeDestroy() {
      // Clean up WebGL resources here
    },
    methods: {
      initWebGLScene() {
        // Set up your Three.js scene here
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.renderer = new THREE.WebGLRenderer();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.$refs.webglContainer.appendChild(this.renderer.domElement);
  
        // Example: Add a cube to the scene
        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 }); // Phong material for better shading
        this.cube = new THREE.Mesh(geometry, material);
        this.scene.add(this.cube);
  
        // Add lights
        const ambientLight = new THREE.AmbientLight(0x404040); // Ambient light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.5); // Directional light
        directionalLight.position.set(0, 1, 0); // Set light direction
        this.scene.add(ambientLight);
        this.scene.add(directionalLight);
  
        this.camera.position.z = 5;
  
        // Animation loop
        this.animate();
      },
      updatePersonality() {
        const { mountedPersArr, config } = this.$store.state;
        
        // Get the active personality based on active_personality_id
        this.activePersonality = mountedPersArr[config.active_personality_id];

        // Check if the active personality has an avatar
        if (this.activePersonality.avatar) {
            this.showBoxWithAvatar(this.activePersonality.avatar);
        } else {
            this.showDefaultCube();
        }

        // Update the personality property
        this.$emit('update:personality', this.activePersonality);
      },
      loadScene(scenePath) {
        const loader = new GLTFLoader();
        loader.load(scenePath, (gltf) => {
          // Remove existing cube
          this.scene.remove(this.cube);
  
          // Add loaded model to the scene
          this.cube = gltf.scene;
          this.scene.add(this.cube);
        });
      },
      showBoxWithAvatar(avatarUrl) {
        // Check if the cube exists in the scene
        if (this.cube) {
            // Remove existing cube
            this.scene.remove(this.cube);
        }
  
        // Create a box with avatar texture
        const geometry = new THREE.BoxGeometry();
        const texture = new TextureLoader().load(avatarUrl);
        const material = new THREE.MeshBasicMaterial({ map: texture });
        this.cube = new THREE.Mesh(geometry, material);
        this.scene.add(this.cube);
      },
      showDefaultCube() {
        // Remove existing cube
        this.scene.remove(this.cube);
  
        // Create a default cube
        const geometry = new THREE.BoxGeometry();
        const material = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
        this.cube = new THREE.Mesh(geometry, material);
        this.scene.add(this.cube);
      },
      animate() {
        requestAnimationFrame(this.animate);
  
        // Rotate the cube
        if (this.cube) {
          this.cube.rotation.x += 0.01;
          this.cube.rotation.y += 0.01;
        }
  
        this.renderer.render(this.scene, this.camera);
      },
    },
  };
  </script>
  
  <style>
  #webglContainer {
    top: 0;
    left: 0;
  }
  .floating-frame2 {
    margin: 15px;
    float: left;
    width: 800px;
    height: auto;
    border: 1px solid #000;
    border-radius: 4px;
    overflow: hidden;
    min-height: 200px;
    z-index: 5000;
  }
  </style>
  