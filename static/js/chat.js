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







function add_collapsible_div(discussion_title, text, id) {
    // Create the outer box element
    const box = document.createElement('div');
    box.classList.add('bg-gray-100', 'rounded-lg', 'p-4');
  
    // Create the title element
    const title = document.createElement('h2');
    title.classList.add('text-lg', 'font-medium');
    title.textContent = discussion_title;
  
    // Create the toggle button element
    const toggleBtn = document.createElement('button');
    toggleBtn.classList.add('focus:outline-none');
    toggleBtn.id = `${id}-toggle-btn`;
  
    // Create the expand icon element
    const expandIcon = document.createElement('path');
    expandIcon.id = `${id}-expand-icon`;
    expandIcon.setAttribute('d', 'M5 5h10v10H5z');
  
    // Create the collapse icon element
    const collapseIcon = document.createElement('path');
    collapseIcon.id = `${id}-collapse-icon`;
    collapseIcon.setAttribute('d', 'M7 10h6');
  
    // Add the icons to the toggle button element
    toggleBtn.appendChild(expandIcon);
    toggleBtn.appendChild(collapseIcon);
  
    // Create the content element
    const content = document.createElement('div');
    content.id = `${id}-box-content`;
    content.classList.add('mt-4');
    content.textContent = text; 
    // Add the title, toggle button, and content to the box element
    // Create the title and toggle button container element
    const titleToggleContainer = document.createElement('div');
    titleToggleContainer.classList.add('flex', 'justify-between', 'items-center');

    // Add the title and toggle button to the container element
    titleToggleContainer.appendChild(title);
    titleToggleContainer.appendChild(toggleBtn);

    // Add the container element to the box element
    box.appendChild(titleToggleContainer);
    box.appendChild(content);
  
    // Add the box to the document
    document.body.appendChild(box);
  
    // Add the CSS styles to the head of the document
    const css = `
      #${id}-box-content {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.2s ease-out;
      }
  
      #${id}-box-content.expanded {
        max-height: 1000px;
        transition: max-height 0.5s ease-in;
      }
  
      #${id}-toggle-btn:focus #${id}-collapse-icon {
        display: block;
      }
  
      #${id}-toggle-btn:focus #${id}-expand-icon {
        display: none;
      }
  
      #${id}-collapse-icon {
        display: none;
      }
    `;
    const head = document.head || document.getElementsByTagName('head')[0];
    const style = document.createElement('style');
    style.type = 'text/css';
    style.appendChild(document.createTextNode(css));
    head.appendChild(style);
  
    // Add the JavaScript code to toggle the box
    const toggleBtnEl = document.querySelector(`#${id}-toggle-btn`);
    const boxContentEl = document.querySelector(`#${id}-box-content`);
  
    toggleBtnEl.addEventListener('click', function() {
      boxContentEl.classList.toggle('expanded');
    });
    return box
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
//welcome_message = add_collapsible_div("Note:", text, 'hints');

addMessage("GPT4ALL",welcome_message,0);

// Code for collapsable text
const collapsibles = document.querySelectorAll('.collapsible');
function uncollapse(id){
    console.log("uncollapsing")
    const content = document.querySelector(`#${id}`);
    content.classList.toggle('active');
}

