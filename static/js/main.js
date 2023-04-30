var globals={
  is_generating:false,
  chatWindow:undefined,
  chatForm:undefined,
  userInput:undefined,
  stopGeneration:undefined,
  sendbtn:undefined,
  waitAnimation:undefined
}

function send_message(service_name, parameters){
  var socket = io.connect('http://' + document.domain + ':' + location.port);
  globals.socket = socket
  globals.is_generating = false
  socket.on('connect', function() {
      entry_counter = 0;
      if(globals.is_generating){
        globals.socket.disconnect()
      }
      else{
        globals.socket.emit(service_name, parameters);
        globals.is_generating = true
      }

  });
  socket.on('disconnect', function() {
    console.log("disconnected")
    entry_counter = 0;
    console.log("Disconnected")
    globals.sendbtn.style.display="block";
    globals.waitAnimation.style.display="none";
    globals.stopGeneration.style.display = "none";    
  });


  socket.on('infos', function(msg) {
    if(globals.user_msg){
      globals.user_msg.setSender(msg.user);
      globals.user_msg.setMessage(msg.message);
      globals.user_msg.setID(msg.id);
    }
    globals.bot_msg.setSender(msg.bot);
    globals.bot_msg.setID(msg.response_id);
    globals.bot_msg.messageTextElement.innerHTML    = `Generating answer. Please stand by...`;    
  });

  socket.on('waiter', function(msg) {
    globals.bot_msg.messageTextElement.innerHTML    = `Generating answer. Please stand by...`;    
  });
  
  socket.on('message', function(msg) {
        text = msg.data;
        // For the other enrtries, these are just the text of the chatbot

        globals.bot_msg.messageTextElement.innerHTML    = marked.marked(text);
        // scroll to bottom of chat window
        globals.chatWindow.scrollTop = globals.chatWindow.scrollHeight;
  });

  socket.on('final',function(msg){
    text = msg.data;
    globals.bot_msg.hiddenElement.innerHTML         = text
    globals.bot_msg.messageTextElement.innerHTML    = marked.marked(text)
    socket.disconnect()

  });  
}

function update_main(){
  globals.chatWindow = document.getElementById('chat-window');
  globals.chatForm = document.getElementById('chat-form');
  globals.userInput = document.getElementById('user-input');
  globals.stopGeneration = document.getElementById("stop-generation")
  globals.sendbtn = document.querySelector("#submit-input")
  globals.waitAnimation = document.querySelector("#wait-animation")
  
  globals.stopGeneration.addEventListener('click', (event) =>{
    event.preventDefault();
    console.log("Stop clicked");
    fetch('/stop_gen')
    .then(response => response.json())
    .then(data => {
        console.log(data);
    });
      
  })


  function submit_form(){
    console.log("Submitting")
  
    // get user input and clear input field
    message = globals.userInput.value;
    globals.userInput.value = '';    
    globals.sendbtn.style.display="none";
    globals.waitAnimation.style.display="block";
    globals.stopGeneration.style.display = "block";
    console.log("Sending message to bot")

    globals.user_msg = addMessage('',message, 0, 0, can_edit=true);
    globals.bot_msg = addMessage('', '', 0, 0, can_edit=true);
    // scroll to bottom of chat window
    globals.chatWindow.scrollTop = globals.chatWindow.scrollHeight;

    entry_counter = 0;
    send_message('generate_msg',{prompt: message})


    //socket.emit('stream-text', {text: text});
  }
  globals.chatForm.addEventListener('submit', event => {
      event.preventDefault();
      submit_form();
  });  
  globals.userInput.addEventListener("keyup", function(event) {
    // Check if Enter key was pressed while holding Shift
    // Also check if Shift + Ctrl keys were pressed while typing
    // These combinations override the submit action
    const shiftPressed = event.shiftKey;
    const ctrlPressed = event.ctrlKey && !event.metaKey;

    if ((!shiftPressed) && event.key === "Enter") {
        submit_form();
    }
  });
}