<template>
  <div class="floating-frame bg-white" :style="{ bottom: position.bottom + 'px', right: position.right + 'px', 'z-index': zIndex }" @mousedown.stop="startDrag" @mouseup.stop="stopDrag">
    <div class="handle" @mousedown.stop="startDrag" @mouseup.stop="stopDrag">Drag Me</div>
    
    <p v-if="isMaximized && imageDataUrl==null" :src="imageDataUrl" alt="Webcam Frame" width="300" height="300" >Loading. Please wait...</p>
    <div class="controls">
      <button v-if="!isMaximized" class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded" @click="startVideoStream"><i data-feather='video'></i></button>
      <button v-if="isMaximized" class="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded" @click="stopVideoStream"><i data-feather='video'></i></button>
      <span v-if="isMaximized">FPS: {{ frameRate }}</span>
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
      isMaximized: false,
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
    startVideoStream() {
      this.isMaximized = true;
      socket.emit('start_webcam_video_stream');
      nextTick(() => {
          feather.replace()
        })
    },
    stopVideoStream() {
      this.isMaximized = false;
      this.imageData = null;
      socket.emit('stop_webcam_video_stream');
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
    socket.on('video_stream_image', (imageBase64) => {
      if (this.isMaximized) {
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

<style scoped>
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

/* Add a container for the floating frames and apply flexbox */
.container {
  display: flex;
  justify-content: flex-start;
  align-items: flex-start;
  flex-wrap: wrap;
}
</style>
