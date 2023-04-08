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
                  addMessage('User', infos.message, infos.id, true);
                  elements = addMessage('GPT4ALL', '', infos.response_id, true);
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


function addMessage(sender, message, id, can_edit=false) {
  console.log(id)
  const messageElement = document.createElement('div');
  messageElement.classList.add('bg-secondary', 'drop-shadow-sm', 'p-4', 'mx-6', 'my-4', 'flex', 'flex-col', 'space-x-2');
  messageElement.classList.add(sender);
  messageElement.setAttribute('id', id);

  const senderElement = document.createElement('div');
  senderElement.classList.add('font-normal', 'underline', 'text-sm');
  senderElement.innerHTML = sender;

  const messageTextElement = document.createElement('div');
  messageTextElement.classList.add('font-medium', 'text-md');
  messageTextElement.innerHTML = message;
  // Create a hidden div element needed to buffer responses before commiting them to the visible message
  const hiddenElement = document.createElement('div');
  hiddenElement.style.display = 'none';
  hiddenElement.innerHTML = '';  

  messageElement.appendChild(senderElement);
  messageElement.appendChild(messageTextElement);
  if(can_edit)
  {
    const editButton = document.createElement('button');
    editButton.classList.add('bg-blue-500', 'hover:bg-blue-700', 'text-white', 'font-bold', 'py-2', 'px-4', 'rounded', 'my-2');
    editButton.innerHTML = 'Edit';
    editButton.addEventListener('click', () => {
        const inputField = document.createElement('input');
        inputField.type = 'text';
        inputField.classList.add('font-medium', 'text-md', 'border', 'border-gray-300', 'p-1');
        inputField.value = messageTextElement.innerHTML;

        editButton.style.display="none"
  
        const saveButton = document.createElement('button');
        saveButton.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-2', 'px-4', 'rounded', 'my-2', 'ml-2');
        saveButton.innerHTML = 'Save';
        saveButton.addEventListener('click', () => {
            const newText = inputField.value;
            messageTextElement.innerHTML = newText;
            // make request to update message
            const url = `/update_message?id=${id}&message=${newText}`;
            fetch(url)
              .then(response => {
                  if (!response.ok) {
                      throw new Error('Network response was not ok');
                  }
                  else{
                    console.log("Updated")
                  }
              })
              .catch(error => {
                  console.error('There was a problem updating the message:', error);
              });
            editButton.style.display="block"
            messageElement.replaceChild(messageTextElement, inputField);
            //messageElement.removeChild(inputField);
            messageElement.removeChild(saveButton);
        });
  
        messageElement.replaceChild(inputField, messageTextElement);
        messageElement.appendChild(saveButton);
        inputField.focus();
    });

    messageElement.appendChild(editButton);
  }
  chatWindow.appendChild(messageElement);
  chatWindow.appendChild(hiddenElement);

  // scroll to bottom of chat window
  chatWindow.scrollTop = chatWindow.scrollHeight;

  // Return all needed stuff
  return {'messageTextElement':messageTextElement, 'hiddenElement':hiddenElement}
}

const welcome_message = `
<div>
<code>This is a very early testing Web UI of GPT4All chatbot.
<br>Keep in mind that this is a 7B parameters model running on your own PC's CPU. It is literally 24 times smaller than GPT-3 in terms of parameter count.
<br>While it is still new and not as powerful as GPT-3.5 or GPT-4, it can still be useful for many applications.
<br>Any feedback and contribution is welcomed.
<br>This Web UI is a binding to the GPT4All model that allows you to test a chatbot locally on your machine. Feel free to ask questions or give instructions.</code>

<br>Examples:<br>
<code>
- A color description has been provided. Find the CSS code associated with that color. A light red color with a medium light shade of pink.<br>
- Come up with an interesting idea for a new movie plot. Your plot should be described with a title and a summary.<br>
- Reverse a string in python.<br>
- List 10 dogs.<br>
- Write me a poem about the fall of Julius Ceasar into a ceasar salad in iambic pentameter.<br>
- What is a three word topic describing the following keywords: baseball, football, soccer.<br>
- Act as ChefAI an AI that has the ability to create recipes for any occasion. Instruction: Give me a recipe for my next anniversary.<br>
</code>
</div>
<div>Welcome! I'm here to assist you with anything you need. What can I do for you today?</div>
`;

addMessage("GPT4ALL",welcome_message,0);

// Code for collapsable text
const collapsibles = document.querySelectorAll('.collapsible');
function uncollapse(id){
    console.log("uncollapsing")
    const content = document.querySelector(`#${id}`);
    content.classList.toggle('active');
}

