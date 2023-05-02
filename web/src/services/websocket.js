// Project : GPT4ALL-ui
// Author : ParisNeo
// Description :
// All websocket stuff can be found here.
import io from 'socket.io-client';  

const socket = new io('http://' + document.domain + ':' + location.port);

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
