
function load_discussion(discussion=0){
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
        var container = document.getElementById('chat-window');
        container.innerHTML = '';
        messages.forEach(message => {
          console.log(`Adding message ${message.type}`)
          if(message.type==0){
            console.log("Showing message")
            addMessage(message.sender, message.content, message.id, message.rank, true);
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
  const discussionsList = document.querySelector('#discussions-list');
  discussionsList.innerHTML = "";
  fetch('/list_discussions')
    .then(response => response.json())
    .then(discussions => {
      discussions.forEach(discussion => {
        const buttonWrapper = document.createElement('div');
        //buttonWrapper.classList.add('flex', 'space-x-2', 'mt-2');
        buttonWrapper.classList.add('flex', 'items-center', 'mt-2', 'px-2', 'py-1', 'text-left');
        
        const renameButton = document.createElement('button');
        renameButton.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-0', 'px-0', 'rounded',"w-10","h-10");
        const renameImg = document.createElement('img');
        renameImg.src = "/static/images/edit_discussion.png";
        renameImg.classList.add('py-2', 'px-2', 'rounded', 'w-15', 'h-15');
        renameButton.appendChild(renameImg);

        //renameButton.style.backgroundImage = "/rename_discussion.svg"; //.textContent = 'Rename';
        renameButton.addEventListener('click', () => {
          const dialog = document.createElement('dialog');
          dialog.classList.add('bg-white', 'rounded', 'p-4');

          const inputLabel = document.createElement('label');
          inputLabel.textContent = 'New name: ';
          const inputField = document.createElement('input');
          inputField.classList.add('border', 'border-gray-400', 'rounded', 'py-1', 'px-2');
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
          renameConfirmButton.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-2', 'px-4', 'rounded', 'ml-2');
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
        deleteButton.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-0', 'px-0', 'rounded',"w-10","h-10");
        const deleteImg = document.createElement('img');
        deleteImg.src = "/static/images/delete_discussion.png";
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
        deleteButton.addEventListener('click', () => {

        });

        const discussionButton = document.createElement('button');
        discussionButton.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-2', 'px-4', 'rounded', 'ml-2', 'w-full');
        discussionButton.textContent = discussion.title;
        discussionButton.addEventListener('click', () => {
          console.log(`Showing messages for discussion ${discussion.id}`);
          load_discussion(discussion);
        });


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


// adding export discussion button
const exportDiscussionButton = document.querySelector('#export-discussion-button');

exportDiscussionButton.addEventListener('click', () => {
  fetch(`/export_discussion`)
  .then(response => response.text())
  .then(data => {
    const filename = window.prompt('Please enter a filename:', 'discussion.txt');
    if (filename !== null) {
      const text = data.replace(/\n/g, "\r\n");
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
const resetDBButton = document.querySelector('#reset-discussions-btn');
resetDBButton.addEventListener('click', () => {

});
newDiscussionBtn.addEventListener('click', () => {
  const chatWindow = document.getElementById('chat-window');

  const discussionName = prompt('Enter a name for the new discussion:');
  if (discussionName) {
    const sendbtn = document.querySelector("#submit-input")
    const waitAnimation = document.querySelector("#wait-animation")
    sendbtn.style.display="none";
    waitAnimation.style.display="block";

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
        addMessage("GPT4ALL", data.welcome_message,0);
        
        populate_discussions_list()
        sendbtn.style.display="block";
        waitAnimation.style.display="none";
    })
    .catch(error => {
      // Handle any errors that occur
      console.error(error);
    });
    

  }
});
