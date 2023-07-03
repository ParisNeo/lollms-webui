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
        globals.is_generating = true
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