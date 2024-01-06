// Project : lollms-webui
// Author : ParisNeo
// Description :
// All websocket stuff can be found here.
// More info can be found here https://socket.io/how-to/use-with-vue
// import { createApp } from 'vue';
import io from 'socket.io-client';

// fixes issues when people not hosting this site on local network
const URL = process.env.NODE_ENV === "production" ? "/" : (import.meta.env.VITE_LOLLMS_API)+"/";
console.log(URL)
const socket = new io(URL,{
    reconnection: true,           // Enable reconnection
    reconnectionAttempts: 10,      // Maximum reconnection attempts
    reconnectionDelay: 1000,      // Delay between reconnection attempts (in milliseconds)
  });

// const app = createApp(/* your root component */);

// app.config.globalProperties.$socket = socket;

// app.mount(/* your root element */);

export default socket;

