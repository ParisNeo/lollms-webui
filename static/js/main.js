function update_main(){
  const chatWindow = document.getElementById('chat-window');
  const chatForm = document.getElementById('chat-form');
  const userInput = document.getElementById('user-input');
  
  chatForm.addEventListener('submit', event => {
      event.preventDefault();
  
      // get user input and clear input field
      message = userInput.value;
      userInput.value = '';
      
      // add user message to chat window
      const sendbtn = document.querySelector("#submit-input")
      const waitAnimation = document.querySelector("#wait-animation")
      sendbtn.style.display="none";
      waitAnimation.style.display="block";
      fetch('/bot', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ message })
      }).then(function(response) {
          const stream = new ReadableStream({
              start(controller) {
                  const reader = response.body.getReader();
                  function push() {
                      reader.read().then(function(result) {
                          if (result.done) {
                              sendbtn.style.display="block";
                              waitAnimation.style.display="none";
                              controller.close();
                              return;
                          }
                          controller.enqueue(result.value);
                          push();
                      })
                  }
                  push();
              }
          });
          const textDecoder = new TextDecoder();
          const readableStreamDefaultReader = stream.getReader();
          let entry_counter = 0
          function readStream() {
              readableStreamDefaultReader.read().then(function(result) {
                  if (result.done) {
                      return;
                  }
  
                  text = textDecoder.decode(result.value);
  
                  // The server will first send a json containing information about the message just sent
                  if(entry_counter==0)
                  {
                    // We parse it and
                    infos = JSON.parse(text)
                    console.log(infos)
                    addMessage('User', infos.message, infos.id, 0, can_edit=true);
                    elements = addMessage(infos.sender, '', infos.response_id, 0, can_edit=true);
                    messageTextElement=elements['messageTextElement'];
                    hiddenElement=elements['hiddenElement'];
                    entry_counter ++;
                  }
                  else{
                    // For the other enrtries, these are just the text of the chatbot
                    for (const char of text) {
                          txt = hiddenElement.innerHTML;
                          if (char != '\f') {
                            txt += char
                            hiddenElement.innerHTML = txt
                            messageTextElement.innerHTML = txt.replace(/\n/g, "<br>")
                          }
  
                      // scroll to bottom of chat window
                      chatWindow.scrollTop = chatWindow.scrollHeight;
                    }
                    entry_counter ++;   
                  }
  
                  readStream();
              });
          }
          readStream();
      });
  
  });
  
  const welcome_message = `
  Welcome! I'm here to assist you with anything you need. What can I do for you today?
  `;
  
  addMessage("GPT4ALL",welcome_message,0,0,false);
  
}
fetch('/main')
.then(response => response.text())
.then(html => {
  document.getElementById('main').innerHTML = html;
  update_main();
})
.catch(error => {
  console.error('Error loading main page:', error);
});
