// Project : lollms-webui
// Author : ParisNeo
// Description :
// All websocket stuff can be found here.
// More info can be found here https://socket.io/how-to/use-with-vue
// import { createApp } from 'vue';
import io from 'socket.io-client';

// fixes issues when people not hosting this site on local network
const URL = process.env.NODE_ENV === "production" ? undefined : (import.meta.env.VITE_LOLLMS_API);
const socket = new io(URL);


socket.onerror = (error) => {
  console.error('WebSocket error:', error);
  socket.disconnect()
};

// const app = createApp(/* your root component */);

// app.config.globalProperties.$socket = socket;

// app.mount(/* your root element */);

export default socket;

