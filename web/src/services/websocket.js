// Project : GPT4ALL-ui
// Author : ParisNeo
// Description :
// All websocket stuff can be found here.
// More info can be found here https://socket.io/how-to/use-with-vue
import { createApp } from 'vue';
import io from 'socket.io-client';


const socket = new io(import.meta.env.VITE_GPT4ALL_API );

socket.onopen = () => {
  console.log('WebSocket connection established.');
};

socket.onclose = (event) => {
  console.log('WebSocket connection closed:', event.code, event.reason);
};

socket.onerror = (error) => {
  console.error('WebSocket error:', error);
  socket.disconnect()
};

socket.on("connect", () => {
  console.log('WebSocket connected (websocket)');
});

socket.on("disconnect", () => {
  console.log('WebSocket disonnected (websocket)');
});

const app = createApp(/* your root component */);

app.config.globalProperties.$socket = socket;

app.mount(/* your root element */);

export default socket;

