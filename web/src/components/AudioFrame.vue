<template>
  <div class="floating-frame bg-white" :style="{ bottom: position.bottom + 'px', right: position.right + 'px', 'z-index': zIndex } " @mousedown.stop="startDrag" @mouseup.stop="stopDrag">
    <div class="handle" @mousedown.stop="startDrag" @mouseup.stop="stopDrag">Drag Me</div>
    <img v-if="isAudioActive && imageDataUrl != null" :src="imageDataUrl" alt="Spectrogram" width="300" height="300" />
    <div class="controls">
      <button v-if="!isAudioActive" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" @click="startAudioStream"><i data-feather="mic"></i> </button>
      <button v-if="isAudioActive" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" @click="stopAudioStream"><i data-feather="mic"></i></button>
      <span v-if="isAudioActive">FPS: {{ frameRate }}</span>
    </div>
  </div>
</template>

<script>
import socket from '@/services/websocket.js';
import feather from 'feather-icons'
import { nextTick } from 'vue'

export default {
  data() {
    return {
      isAudioActive: false,
      imageDataUrl: null,
      isDragging: false,
      position: { bottom: 0, right: 0 },
      dragStart: { x: 0, y: 0 },
      zIndex: 0, // Add a data property for z-index
      frameRate: 0,
      frameCount: 0,
      lastFrameTime: Date.now(),      
    };
  },
  methods: {
    startAudioStream() {
      socket.emit('start_audio_stream', ()=>{this.isAudioActive = true;});
      nextTick(() => {
          feather.replace()
        })
    },
    stopAudioStream() {
      socket.emit('stop_audio_stream', ()=>{this.isAudioActive = false;this.imageDataUrl = null});
      nextTick(() => {
          feather.replace()
        })
    },
    startDrag(event) {
      this.isDragging = true;
      this.zIndex = 5001; // Increase z-index when dragging starts
      this.dragStart.x = event.clientX;
      this.dragStart.y = event.clientY;
      document.addEventListener('mousemove', this.drag);
      document.addEventListener('mouseup', this.stopDrag);
    },
    drag(event) {
      if (this.isDragging) {
        const deltaX = event.clientX - this.dragStart.x;
        const deltaY = event.clientY - this.dragStart.y;
        this.position.bottom -= deltaY;
        this.position.right -= deltaX;
        this.dragStart.x = event.clientX;
        this.dragStart.y = event.clientY;
      }
    },
    stopDrag() {
      this.isDragging = false;
      this.zIndex = 0; // Reset z-index when dragging stops
      document.removeEventListener('mousemove', this.drag);
      document.removeEventListener('mouseup', this.stopDrag);
    }
  },
  mounted() {
    feather.replace();
    socket.on('update_spectrogram', (imageBase64) => {
      if (this.isAudioActive) {
        this.imageDataUrl = 'data:image/jpeg;base64,' + imageBase64;
        this.frameCount++;
        const now = Date.now();
        const delta = now - this.lastFrameTime;
        if (delta >= 1000) { // Calculate FPS every second
          this.frameRate = this.frameCount;
          this.frameCount = 0;
          this.lastFrameTime = now;
        }        

      }
    });
  }
};
</script>

<style>
.floating-frame {
  margin: 15px;
  float: left;
  height: auto;
  border: 1px solid #000;
  border-radius: 4px;
  overflow: hidden;
  z-index: 5000;
  position: fixed;
  cursor: move;
  bottom: 0;
  right: 0;
}

.handle {
  width: 100%;
  height: 20px;
  background: #ccc;
  cursor: move;
  text-align: center;
}

.floating-frame img {
  width: 100%;
  height: auto;
}

.controls {
  margin-top: 10px;
}
</style>
