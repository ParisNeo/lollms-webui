
function load_discussion(discussion=0){
  var chatWindow = document.getElementById('chat-window');

  if(discussion)
  {
    console.log(discussion.id)
    body = { id: discussion.id }
  }
  else{
    body = {  }
  }
  // send query with discussion id to reveal discussion messages
  fetch('/load_discussion', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(body)
  })
  .then(response => {
    if (response.ok) {
      response.text().then(data => {
        const messages = JSON.parse(data);
        console.log(messages)
        // process messages
        chatWindow.innerHTML = '';
        messages.forEach(message => {
          console.log(`Adding message ${message.type}`)
          if(message.type==0){
            console.log("Showing message")
            addMessage(message.sender, message.content, message.id, message.rank, true);
            // scroll to bottom of chat window
            chatWindow.scrollTop = chatWindow.scrollHeight;
          }
        });
          });
    } else {
      alert('Failed to query the discussion');
    }
  })
  .catch(error => {
    console.error('Failed to get messages:', error);
    alert('Failed to get messages');
  });
}

function populate_discussions_list()
{
  // Populate discussions list
  const discussionsList = document.getElementById('discussions-list');
  discussionsList.innerHTML = "";
  fetch('/list_discussions')
    .then(response => response.json())
    .then(discussions => {
      discussions.forEach(discussion => {
        const buttonWrapper = document.createElement('div');
        //buttonWrapper.classList.add('flex', 'space-x-2', 'mt-2');
        buttonWrapper.classList.add('drop-shadow-sm', 'p-1', 'mx-2', 'my-2', 'flex', 'flex-row', 'space-x-2', 'rounded-lg', 'shadow-lg', 'bg-gray-200', 'dark:bg-gray-800', 'transition-colors', 'duration-300', 'text-left');
        
        const renameButton = document.createElement('button');
        renameButton.classList.add('bg-gray-400', 'hover:bg-gray-800', 'dark:hover:bg-gray-700', 'text-white', 'dark:text-white', 'font-bold', 'py-0', 'px-0', 'rounded',"w-10","h-10");
        const renameImg = document.createElement('img');
        renameImg.src = "/static/images/edit_discussion.png";
        renameButton.title = "Rename discussion";
        renameImg.classList.add('py-2', 'px-2', 'rounded', 'w-15', 'h-15');
        renameButton.appendChild(renameImg);

        //renameButton.style.backgroundImage = "/rename_discussion.svg"; //.textContent = 'Rename';
        renameButton.addEventListener('click', () => {
          const dialog = document.createElement('dialog');
          dialog.classList.add('bg-gray-500', 'text-white', 'rounded', 'p-4');

          const inputLabel = document.createElement('label');
          inputLabel.textContent = 'New name: ';
          const inputField = document.createElement('input');
          inputField.classList.add('border', "px-2", "mx-2", 'bg-gray-800', 'border-gray-400', 'rounded', 'py-1', 'px-2');
          inputField.setAttribute('type', 'text');
          inputField.setAttribute('name', 'title');
          inputField.setAttribute('value', discussion.title);
          inputLabel.appendChild(inputField);
          dialog.appendChild(inputLabel);

          const cancelButton = document.createElement('button');
          cancelButton.textContent = 'Cancel';
          cancelButton.addEventListener('click', () => {
            dialog.close();
          });

          const renameConfirmButton = document.createElement('button');
          renameConfirmButton.classList.add('bg-gray-500', 'hover:bg-gray-700', 'text-white', 'dark:text-white', 'font-bold', 'py-1', 'px-0', 'rounded', 'ml-2');
          renameConfirmButton.textContent = 'Rename';
          renameConfirmButton.addEventListener('click', () => {
            const newTitle = inputField.value;
            if (newTitle === '') {
              alert('New name cannot be empty');
            } else {
              fetch('/rename', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json'
                },
                body: JSON.stringify({ id: discussion.id, title: newTitle })
              })
              .then(response => {
                if (response.ok) {
                  discussion.title = newTitle;
                  discussionButton.textContent = newTitle;
                  dialog.close();
                } else {
                  alert('Failed to rename discussion');
                }
              })
              .catch(error => {
                console.error('Failed to rename discussion:', error);
                alert('Failed to rename discussion');
              });
            }
          });
      
          dialog.appendChild(cancelButton);
          dialog.appendChild(renameConfirmButton);
          document.body.appendChild(dialog);
          dialog.showModal();
        });
        const deleteButton = document.createElement('button');
        deleteButton.classList.add('bg-gray-400', 'hover:bg-gray-800', 'dark:hover:bg-gray-700', 'text-black', 'dark:text-white', 'font-bold', 'py-0', 'px-0', 'rounded',"w-10","h-10");
        const deleteImg = document.createElement('img');
        deleteImg.src = "/static/images/delete_discussion.png";
        deleteButton.title = "Delete discussion";
        deleteImg.classList.add('py-2', 'px-2', 'rounded', 'w-15', 'h-15');

        deleteButton.addEventListener('click', () => {
          fetch('/delete_discussion', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ id: discussion.id})
            })
            .then(response => {
              if (response.ok) {
                  buttonWrapper.remove();
              } else {
                alert('Failed to delete discussion');
              }
            })
            .catch(error => {
              console.error('Failed to delete discussion:', error);
              alert('Failed to delete discussion');
            });        
          
        });

        deleteButton.appendChild(deleteImg);

        const discussionButton = document.createElement('button');
        discussionButton.id = discussion.id;
        discussionButton.classList.add('isButton', 'hover:bg-gray-800', 'dark:hover:bg-gray-700', 'text-black', 'dark:text-white', 'font-bold', 'py-2', 'px-4', 'rounded', 'ml-2', 'w-full');
        discussionButton.textContent = discussion.title;
        discussionButton.title = "Open discussion";
        
        //Indicates currently selected (Active) discussion
        discussionButton.addEventListener('click', () => {
          console.log(`Showing messages for discussion ${discussion.id}`);
          load_discussion(discussion);
          const btnElList = document.querySelectorAll('.isButton');
          btnElList.forEach(element => {
            if (element.classList.contains('activeDiscussion')) {
              element.classList.remove('activeDiscussion');
            }
          });
          discussionButton.classList.add('activeDiscussion');
        });
        
        const btnElList = document.querySelectorAll('.isButton');
        
        btnElList.forEach(btnEl => {
          btnEl.addEventListener('click', () => {
            btnEl.querySelector('activeDiscussion')?.classList.remove('activeDiscussion');
          });
        })

        buttonWrapper.appendChild(renameButton);
        buttonWrapper.appendChild(deleteButton);
        buttonWrapper.appendChild(discussionButton);
        discussionsList.appendChild(buttonWrapper);
      });
  })
  .catch(error => {
  console.error('Failed to get discussions:', error);
  alert('Failed to get discussions');
  });
}

function populate_menu(){
  // adding export discussion button
  const exportDiscussionButton = document.querySelector('#export-discussion-button');
  exportDiscussionButton.title = "Export discussion to a file";
  exportDiscussionButton.addEventListener('click', () => {
    fetch(`/export_discussion`)
    .then(response => response.json())
    .then(data => {
      discussion_text = data["discussion_text"]
      copyToClipboard(discussion_text)
      const filename = window.prompt('Please enter a filename:', 'discussion.txt');
      if (filename !== null) {
        const text = discussion_text;
        const blob = new Blob([text], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = filename;
        link.click();
        URL.revokeObjectURL(url);
      }
    }).catch(function(error){

    });  
  });
  const actionBtns = document.querySelector('#action-buttons');
  actionBtns.appendChild(exportDiscussionButton);

  const newDiscussionBtn = document.querySelector('#new-discussion-btn');
  newDiscussionBtn.title = "Create new discussion";
  const resetDBButton = document.querySelector('#reset-discussions-btn');
  resetDBButton.title = "Reset all discussions/database";
  resetDBButton.addEventListener('click', () => {

  });
  newDiscussionBtn.addEventListener('click', () => {
    const chatWindow = document.getElementById('chat-window');

    const discussionName = prompt('Enter a name for the new discussion:');
    if (discussionName) {
      const sendbtn = document.querySelector("#submit-input")
      const waitAnimation = document.querySelector("#wait-animation")
      const stopGeneration = document.querySelector("#stop-generation")
      sendbtn.style.display="none";
      waitAnimation.style.display="block";
      stopGeneration.style.display="block";
      

      // Add the discussion to the discussion list
      const discussionItem = document.createElement('li');
      discussionItem.textContent = discussionName;
      fetch(`/new_discussion?title=${discussionName}`)
      .then(response => response.json())
      .then(data => {
          console.log(`New chat ${data.welcome_message}`)
          // Select the new discussion
          //selectDiscussion(discussionId);
          chatWindow.innerHTML=""
          addMessage(data.sender, data.welcome_message,0);
          
          populate_discussions_list()
          sendbtn.style.display="block";
          waitAnimation.style.display="none";
          stopGeneration.style.display="none";
        })
      .catch(error => {
        // Handle any errors that occur
        console.error(error);
      });
      

    }
  });

}