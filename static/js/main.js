function update_main(){
  const chatWindow = document.getElementById('chat-window');
  const chatForm = document.getElementById('chat-form');
  const userInput = document.getElementById('user-input');
  const stopGeneration = document.getElementById("stop-generation")
    
  stopGeneration.addEventListener('click', (event) =>{
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
    message = userInput.value;
    userInput.value = '';
    
    // add user message to chat window
    const sendbtn = document.querySelector("#submit-input")
    const waitAnimation = document.querySelector("#wait-animation")
    const stopGeneration = document.querySelector("#stop-generation")
    
    sendbtn.style.display="none";
    waitAnimation.style.display="block";
    stopGeneration.style.display = "block";
    console.log("Sending message to bot")

    user_msg = addMessage('',message, 0, 0, can_edit=true);
    bot_msg = addMessage('', '', 0, 0, can_edit=true);
    // scroll to bottom of chat window
    chatWindow.scrollTop = chatWindow.scrollHeight;

    var socket = io.connect('http://' + document.domain + ':' + location.port);
    entry_counter = 0;

    socket.on('connect', function() {
        socket.emit('connected', {prompt: message});
        entry_counter = 0;
    });
    socket.on('disconnect', function() {
      
      entry_counter = 0;
    });
    socket.on()

    socket.on('infos', function(msg) {
      user_msg.setSender(msg.user);
      user_msg.setMessage(msg.message);
      user_msg.setID(msg.id);
      bot_msg.setSender(msg.bot);
      bot_msg.setID(msg.response_id);
    });

    socket.on('message', function(msg) {
          text = msg.data;
          console.log(text)
          // For the other enrtries, these are just the text of the chatbot
          txt = bot_msg.hiddenElement.innerHTML;
          txt += text
          bot_msg.hiddenElement.innerHTML         = txt;
          bot_msg.messageTextElement.innerHTML    = txt;
          // scroll to bottom of chat window
          chatWindow.scrollTop = chatWindow.scrollHeight;
    });

    socket.on('final',function(msg){
      text = msg.data;
      bot_msg.hiddenElement.innerHTML         = text
      bot_msg.messageTextElement.innerHTML    = text
      sendbtn.style.display="block";
      waitAnimation.style.display="none";
      stopGeneration.style.display = "none";
      socket.disconnect();
    });
    //socket.emit('stream-text', {text: text});
  }
  chatForm.addEventListener('submit', event => {
      event.preventDefault();
      submit_form();
  });  
  userInput.addEventListener("keyup", function(event) {
    // Check if Enter key was pressed while holding Shift
    // Also check if Shift + Ctrl keys were pressed while typing
    // These combinations override the submit action
    const shiftPressed = event.shiftKey;
    const ctrlPressed = event.ctrlKey && !event.metaKey;

    if ((!shiftPressed) && event.key === "Enter") {
        submit_form();
    }
    // Restore original functionality for the remaining cases
    else if (!shiftPressed && ctrlPressed) {
      setTimeout(() => {
        userInput.focus();
        contentEditable.value += event.data;
        lastValue.innerHTML = userInput.value;
      }, 0);
    }
  });
}