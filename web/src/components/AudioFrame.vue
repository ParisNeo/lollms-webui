<template>
  <div class="floating-frame">
    <img v-if="isAudioActive" :src="imageDataUrl" alt="Spectrogram" width="300" height="300" />
    <div class="controls">
      <button v-if="!isAudioActive" class="w-full bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" @click="startAudioStream">Activate Audio</button>
      <button v-if="isAudioActive" class="w-full bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" @click="stopAudioStream">Deactivate Audio</button>
    </div>
  </div>
</template>
  
<script>
  import socket from '@/services/websocket.js';
  
  export default {
    data() {
      return {
        isAudioActive: false,
        imageDataUrl: null
      };
    },
    methods: {
      startAudioStream() {
        this.isAudioActive = true;
        socket.emit('start_audio_stream');
      },
      stopAudioStream() {
        this.isAudioActive = false;
        this.imageData = null;
        socket.emit('stop_audio_stream');
      }
    },
    mounted() {
      socket.on('update_spectrogram', (imageBase64) => {
        if (this.isAudioActive) {
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
    width: 800px;
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
  