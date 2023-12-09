<template>
  <div class="floating-frame">
    <img v-if="isVideoActive" :src="imageDataUrl" alt="Webcam Frame" width="300" height="300" />
    <div class="controls">
      <button v-if="!isVideoActive" class="w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" @click="startVideoStream">Activate Video</button>
      <button v-if="isVideoActive" class="w-full bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" @click="stopVideoStream">Deactivate Video</button>
    </div>
  </div>
</template>
  
<script>
  import socket from '@/services/websocket.js';
  
  export default {
    data() {
      return {
        isVideoActive: false,
        imageDataUrl: null
      };
    },
    methods: {
      startVideoStream() {
        this.isVideoActive = true;
        socket.emit('start_webcam_video_stream');
      },
      stopVideoStream() {
        this.isVideoActive = false;
        this.imageData = null;
        socket.emit('stop_webcam_video_stream');
      }
    },
    mounted() {
      socket.on('image', (imageBase64) => {
        if (this.isVideoActive) {
          this.imageDataUrl = 'data:image/jpeg;base64,' + imageBase64;
        }
      });
    }
  };
  </script>
  
  <style>
  .floating-frame {
    margin: 15px;
    float: left;
    width: 200px;
    height: auto;
    border: 1px solid #000;
    border-radius: 4px;
    overflow: hidden;
    z-index: 5000;
  }
  
  .floating-frame img {
    width: 100%;
    height: auto;
  }
  
  .controls {
    margin-top: 10px;
  }
  </style>
  