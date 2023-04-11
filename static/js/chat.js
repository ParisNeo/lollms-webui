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
                  addMessage('User', infos.message, infos.id, 0, can_edit=true);
                  elements = addMessage('GPT4ALL', '', infos.response_id, 0, can_edit=true);
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


function addMessage(sender, message, id, rank=0, can_edit=false) {
  console.log(id)
  const messageElement = document.createElement('div');
  messageElement.classList.add('bg-secondary', 'drop-shadow-sm', 'p-4', 'mx-6', 'my-4', 'flex', 'flex-col', 'space-x-2', 'rounded-lg', 'shadow-lg', 'bg-gray-800', 'hover:bg-gray-700', 'transition-colors', 'duration-300');
  
  //messageElement.classList.add(sender);
  messageElement.setAttribute('id', id);

  const senderElement = document.createElement('div');
  senderElement.classList.add('font-normal', 'underline', 'text-sm');
  senderElement.innerHTML = sender;

  const messageTextElement = document.createElement('div');
  messageTextElement.classList.add('font-medium', 'text-md');
  messageTextElement.innerText = message;
  // Create a hidden div element needed to buffer responses before commiting them to the visible message
  const hiddenElement = document.createElement('div');
  hiddenElement.style.display = 'none';
  hiddenElement.innerHTML = '';  

  messageElement.appendChild(senderElement);
  messageElement.appendChild(messageTextElement);
  if(can_edit)
  {
    // Create buttons container
    const buttonsContainer = document.createElement('div');
    // Add the 'flex' class to the div
    buttonsContainer.classList.add('flex');

    // Add the 'justify-end' class to the div
    buttonsContainer.classList.add('justify-end'); 

    // Set the width and height of the container to 100%
    buttonsContainer.style.width = '100%';
    buttonsContainer.style.height = '100%';
           
    const editButton = document.createElement('button');
    editButton.classList.add('my-1','mx-1','outline-none','px-4','bg-accent','text-white','rounded-md','hover:bg-[#7ba0ea]','active:bg-blue-100','transition-colors','ease-in-out');
    editButton.style.float = 'right'; // set the float property to right    
    editButton.style.display='inline-block'
    editButton.innerHTML = 'Edit';
    editButton.addEventListener('click', () => {
        const inputField = document.createElement('input');
        inputField.type = 'text';
        inputField.classList.add('font-medium', 'text-md', 'border', 'border-gray-300', 'p-1');
        inputField.value = messageTextElement.innerHTML;

        buttonsContainer.style.display="none"
  
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
              buttonsContainer.style.display='inline-block'
              messageElement.replaceChild(messageTextElement, inputField);
              //messageElement.removeChild(inputField);
              messageElement.removeChild(saveButton);
        });
  
        messageElement.replaceChild(inputField, messageTextElement);
        messageElement.appendChild(saveButton);
        inputField.focus();
    });

    const rank_up = document.createElement('button');
    rank_up.classList.add('my-1','mx-1','outline-none','px-4','bg-accent','text-white','rounded-md','hover:bg-[#7ba0ea]','active:bg-[#3d73e1]','transition-colors','ease-in-out');
    rank_up.style.float = 'right'; // set the float property to right    
    rank_up.style.display='inline-block'
    rank_up.innerHTML = 'Up';
    rank_up.addEventListener('click', () => {
        const url = `/message_rank_up?id=${id}`;
        fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log(data.new_rank)
            if(data.new_rank>0){
                rank_up.innerText=`Up(${data.new_rank})`
                rank_down.innerText=`Down`
            }
            else if(data.new_rank<0){
                rank_up.innerText=`Up`
                rank_down.innerText=`Down(${data.new_rank})`
            }
            else{
                rank_up.innerText=`Up`
                rank_down.innerText=`Down`
            }
        })
        .catch(error => {
            console.error('There was a problem updating the message:', error);
        });
    });

    const rank_down = document.createElement('button');
    rank_down.classList.add('my-1','mx-1','outline-none','px-4','bg-accent','text-white','rounded-md','hover:bg-[#7ba0ea]','active:bg-[#3d73e1]','transition-colors','ease-in-out');
    rank_down.style.float = 'right'; // set the float property to right    
    rank_down.style.display='inline-block'
    rank_down.innerHTML = 'Down';
    rank_down.addEventListener('click', () => {
        const url = `/message_rank_down?id=${id}`;
        fetch(url)
        .then(response => response.json())
        .then(data => {
            console.log(data)
            if(data.new_rank>0){
                rank_up.innerText=`Up(${data.new_rank})`
                rank_down.innerText=`Down`
            }
            else if(data.new_rank<0){
                rank_up.innerText=`Up`
                rank_down.innerText=`Down(${data.new_rank})`
            }
        })
        .catch(error => {
            console.error('There was a problem updating the message:', error);
        });
    });

    buttonsContainer.appendChild(editButton);
    buttonsContainer.appendChild(rank_up);
    buttonsContainer.appendChild(rank_down);
    messageElement.appendChild(buttonsContainer);
    if(rank>0){
        rank_up.innerText=`Up(${rank})`
        rank_down.innerText=`Down`
    }
    else if(rank<0){
        rank_up.innerText=`Up`
        rank_down.innerText=`Down(${rank})`
    }

  }
  chatWindow.appendChild(messageElement);
  chatWindow.appendChild(hiddenElement);

  // scroll to bottom of chat window
  chatWindow.scrollTop = chatWindow.scrollHeight;

  // Return all needed stuff
  return {'messageTextElement':messageTextElement, 'hiddenElement':hiddenElement}
}

const welcome_message = `
This is a very early testing Web UI of GPT4All chatbot.
Keep in mind that this is a 7B parameters model running on your own PC's CPU. It is literally 24 times smaller than GPT-3 in terms of parameter count.
While it is still new and not as powerful as GPT-3.5 or GPT-4, it can still be useful for many applications.
Many people are building models out there and you can try the models and compare them yourself.
Any feedback and contribution is welcomed.
This Web UI is a binding to the GPT4All model that allows you to test a chatbot locally on your machine. Feel free to ask questions or give instructions.

Examples:

- A color description has been provided. Find the CSS code associated with that color. A light red color with a medium light shade of pink.
- Come up with an interesting idea for a new movie plot. Your plot should be described with a title and a summary.
- Reverse a string in python.
- List 10 dogs.
- Write me a poem about the fall of Julius Ceasar into a ceasar salad in iambic pentameter.
- What is a three word topic describing the following keywords: baseball, football, soccer.
- Act as ChefAI an AI that has the ability to create recipes for any occasion. Instruction: Give me a recipe for my next anniversary.
- who is Abraham Lincoln?.
- write a letter to my collegue and tell him I can't make it to work today. Make it humorous.
- write a poem about love between two AIs.
Welcome! I'm here to assist you with anything you need. What can I do for you today?
`;

addMessage("GPT4ALL",welcome_message,0,0,false);

// Code for collapsable text
const collapsibles = document.querySelectorAll('.collapsible');
function uncollapse(id){
    console.log("uncollapsing")
    const content = document.querySelector(`#${id}`);
    content.classList.toggle('active');
}

