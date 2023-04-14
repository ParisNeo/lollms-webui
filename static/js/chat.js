function addMessage(sender, message, id, rank=0, can_edit=false) {
    const chatWindow = document.getElementById('chat-window');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
  
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

      const resendButton = document.createElement('button');
      resendButton.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-0', 'px-0', 'rounded',"w-10","h-10");
      resendButton.style.float = 'right'; // set the float property to right    
      resendButton.style.display='inline-block'
      resendButton.innerHTML = '';
      const resendImg = document.createElement('img');
      resendImg.src = "/static/images/refresh.png";
      resendImg.classList.add('py-1', 'px-1', 'rounded', 'w-10', 'h-10');
      resendButton.appendChild(resendImg)
      resendButton.addEventListener('click', () => {
        // get user input and clear input field
        message = userInput.value;
        userInput.value = '';
        
        // add user message to chat window
        const sendbtn = document.querySelector("#submit-input")
        const waitAnimation = document.querySelector("#wait-animation")
        sendbtn.style.display="none";
        waitAnimation.style.display="block";

        fetch("/run_to", {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                id: id,
                message: message
            })
          })
          .then(function(response) {
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

      const editButton = document.createElement('button');
      editButton.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-0', 'px-0', 'rounded',"w-10","h-10");
      editButton.style.float = 'right'; // set the float property to right    
      editButton.style.display='inline-block'
      editButton.innerHTML = '';
      const editImg = document.createElement('img');
      editImg.src = "/static/images/edit_discussion.png";
      editImg.classList.add('py-1', 'px-1', 'rounded', 'w-10', 'h-10');
      editButton.appendChild(editImg)
  
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
  
      const deleteButton = document.createElement('button');
      deleteButton.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-0', 'px-0', 'rounded',"w-10","h-10");
      deleteButton.style.float = 'right'; // set the float property to right    
      deleteButton.style.display='inline-block'
      deleteButton.innerHTML = '';
      const deleteImg = document.createElement('img');
      deleteImg.src = "/static/images/delete_discussion.png";
      deleteImg.classList.add('py-2', 'px-2', 'rounded', 'w-15', 'h-15');
      deleteButton.appendChild(deleteImg)
      deleteButton.addEventListener('click', () => {
          const url = `/delete_message?id=${id}`;
          fetch(url)
          .then(response => response.json())
          .then(data => {
              console.log(data.new_rank)
              messageElement.style.display="none"
          })
          .catch(error => {
              console.error('There was a problem updating the message:', error);
          });
      });
      const rank_up = document.createElement('button');
      rank_up.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-0', 'px-0', 'rounded',"w-10","h-10");
      rank_up.style.float = 'right'; // set the float property to right    
      rank_up.style.display='inline-block'
      rank_up.innerHTML = '';
      const thumbUpImg = document.createElement('img');
      thumbUpImg.src = "/static/images/thumb_up.png";
      thumbUpImg.classList.add('py-2', 'px-2', 'rounded', 'w-15', 'h-15');
      rank_up.appendChild(thumbUpImg)
      const thumbUpBadge = document.createElement('span');
      thumbUpBadge.innerText = "";
      thumbUpBadge.classList.add('inline-flex', 'items-center', 'justify-center', 'h-4', 'w-4', 'rounded-full', 'bg-red-500', 'text-white', 'text-xs', 'top-0', 'right-0');
      rank_up.appendChild(thumbUpBadge)
  
      rank_up.addEventListener('click', () => {
          const url = `/message_rank_up?id=${id}`;
          fetch(url)
          .then(response => response.json())
          .then(data => {
              console.log(data.new_rank)
              if(data.new_rank>0){
                  thumbUpBadge.innerText=`${data.new_rank}`
                  thumbDownBadge.innerText=``
                  thumbUpBadge.display=`block`
                  thumbDownBadge.display='none'
              }
              else if(data.new_rank<0){
                  thumbUpBadge.innerText=``
                  thumbDownBadge.innerText=`${data.new_rank}`
                  thumbUpBadge.display=`none`
                  thumbDownBadge.display='block'
              }
              else{
                  thumbUpBadge.innerText=``
                  thumbDownBadge.innerText=``
                  thumbUpBadge.display=`none`
                  thumbDownBadge.display='none'
              }
          })
          .catch(error => {
              console.error('There was a problem updating the message:', error);
          });
      });
  
      const rank_down = document.createElement('button');
      rank_down.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-0', 'px-0', 'rounded',"w-10","h-10");
      rank_down.style.float = 'right'; // set the float property to right    
      rank_down.style.display='inline-block'
      rank_down.innerHTML = '';
      const thumbDownImg = document.createElement('img');
      thumbDownImg.src = "/static/images/thumb_down.png";
      thumbDownImg.classList.add('py-2', 'px-2', 'rounded', 'w-15', 'h-15');
      rank_down.appendChild(thumbDownImg)
      const thumbDownBadge = document.createElement('span');
      thumbDownBadge.innerText = "";
      thumbDownBadge.classList.add('inline-flex', 'items-center', 'justify-center', 'h-4', 'w-4', 'rounded-full', 'bg-red-500', 'text-white', 'text-xs', 'top-0', 'right-0');
      rank_down.appendChild(thumbDownBadge)
  
      rank_down.addEventListener('click', () => {
          const url = `/message_rank_down?id=${id}`;
          fetch(url)
          .then(response => response.json())
          .then(data => {
              console.log(data)
              if(data.new_rank>0){
                  thumbUpBadge.innerText=`${data.new_rank}`
                  thumbDownBadge.innerText=``
                  thumbUpBadge.display=`block`
                  thumbDownBadge.display='none'
              }
              else if(data.new_rank<0){
                  thumbUpBadge.innerText=``
                  thumbDownBadge.innerText=`${data.new_rank}`
                  thumbUpBadge.display=`none`
                  thumbDownBadge.display='block'
              }
              else{
                  thumbUpBadge.innerText=``
                  thumbDownBadge.innerText=``
                  thumbUpBadge.display=`none`
                  thumbDownBadge.display='none'
              }
          })
          .catch(error => {
              console.error('There was a problem updating the message:', error);
          });
      });
      buttonsContainer.appendChild(editButton);
      buttonsContainer.appendChild(resendButton);
      buttonsContainer.appendChild(deleteButton);
      
      buttonsContainer.appendChild(rank_up);
      buttonsContainer.appendChild(rank_down);
      messageElement.appendChild(buttonsContainer);
      if(rank>0){
          thumbUpBadge.innerText=`${rank}`
          thumbDownBadge.innerText=``
          thumbUpBadge.display=`block`
          thumbDownBadge.display='none'
      }
      else if(rank<0){
          thumbUpBadge.innerText=``
          thumbDownBadge.innerText=`${rank}`
          thumbUpBadge.display=`none`
          thumbDownBadge.display='block'
      }
      else{
          thumbUpBadge.innerText=``
          thumbDownBadge.innerText=``
          thumbUpBadge.display=`none`
          thumbDownBadge.display='none'
      }
  
    }
    chatWindow.appendChild(messageElement);
    chatWindow.appendChild(hiddenElement);

    attachAudio_modules(messageTextElement);
  
    // scroll to bottom of chat window
    chatWindow.scrollTop = chatWindow.scrollHeight;
  
    // Return all needed stuff
    return {
        'messageTextElement':messageTextElement, 
        'hiddenElement':hiddenElement
    }
}