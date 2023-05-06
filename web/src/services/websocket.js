// Project : GPT4ALL-ui
// Author : ParisNeo
// Description :
// All websocket stuff can be found here.
// More info can be found here https://socket.io/how-to/use-with-vue
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
};

export default socket;
