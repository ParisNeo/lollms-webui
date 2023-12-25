<template>
    <div class="painting-component">
      <canvas
        ref="canvas"
        :width="canvasWidth"
        :height="canvasHeight"
        @mousedown="startPainting"
        @mousemove="paint"
        @mouseup="stopPainting"
        @mouseleave="stopPainting"
      ></canvas>
      <div class="controls">
        <label for="stroke-width">Stroke Width:</label>
        <input type="number" id="stroke-width" v-model="strokeWidth" min="1" max="50" />
        <label for="stroke-color">Stroke Color:</label>
        <input type="color" id="stroke-color" v-model="strokeColor" />
        <button @click="undoStroke">Undo</button>
        <button @click="saveDrawing">Save</button>
        <button @click="loadDrawing">Load</button>
      </div>
    </div>
  </template>
  
  <script>
  export default {
    name: 'PaintingComponent',
    data() {
      return {
        canvasWidth: 800,
        canvasHeight: 600,
        strokeWidth: 5,
        strokeColor: '#000000',
        isPainting: false,
        strokes: [],
        undoneStrokes: [],
        canvas: null,
        ctx: null,
      };
    },
    mounted() {
      this.initCanvas();
    },
    methods: {
      initCanvas() {
        this.canvas = this.$refs.canvas;
        this.ctx = this.canvas.getContext('2d');
        this.ctx.lineCap = 'round';
        this.ctx.lineJoin = 'round';
      },
      startPainting(event) {
        const { offsetX, offsetY } = event;
        this.ctx.beginPath();
        this.ctx.moveTo(offsetX, offsetY);
        this.isPainting = true;
      },
      paint(event) {
        if (this.isPainting) {
          const { offsetX, offsetY } = event;
          this.ctx.lineTo(offsetX, offsetY);
          this.ctx.strokeStyle = this.strokeColor;
          this.ctx.lineWidth = this.strokeWidth;
          this.ctx.stroke();
          this.undoneStrokes = []; // Clear the undone strokes as a new stroke is made
        }
      },
      stopPainting() {
        if (this.isPainting) {
          this.ctx.closePath();
          this.isPainting = false;
          this.strokes.push(this.canvas.toDataURL()); // Save the current state
        }
      },
      undoStroke() {
        if (this.strokes.length > 0) {
          this.undoneStrokes.push(this.strokes.pop());
          this.reloadCanvas();
        }
      },
      reloadCanvas() {
        if (this.strokes.length > 0) {
          const lastStroke = new Image();
          lastStroke.onload = () => {
            this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
            this.ctx.drawImage(lastStroke, 0, 0);
          };
          lastStroke.src = this.strokes[this.strokes.length - 1];
        } else {
          this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
        }
      },
      saveDrawing() {
        const dataURL = this.canvas.toDataURL("image/png");
        const link = document.createElement('a');
        link.download = 'painting.png';
        link.href = dataURL;
        link.click();
      },
      loadDrawing() {
        const input = document.createElement('input');
        input.type = 'file';
        input.onchange = e => {
          const file = e.target.files[0];
          const reader = new FileReader();
          reader.onload = readerEvent => {
            const img = new Image();
            img.onload = () => {
              this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
              this.ctx.drawImage(img, 0, 0);
              this.strokes.push(this.canvas.toDataURL());
            };
            img.src = readerEvent.target.result;
          };
          reader.readAsDataURL(file);
        };
        input.click();
      }
    }
  };
  </script>
  
  <style scoped>
  .painting-component {
    border: 1px solid #ccc;
    padding: 10px;
  }
  
  .controls {
    margin-top: 10px;
  }
  
  .controls label {
    margin-right: 5px;
  }
  
  .controls button {
    margin-left: 10px;
  }
  </style>
  