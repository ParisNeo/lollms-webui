
function populate_discussions_list()
{
  // Populate discussions list
  const discussionsList = document.querySelector('#discussions-list');
  discussionsList.innerHTML = "";
  fetch('/discussions')
    .then(response => response.json())
    .then(discussions => {
      discussions.forEach(discussion => {
        const buttonWrapper = document.createElement('div');
        //buttonWrapper.classList.add('flex', 'space-x-2', 'mt-2');
        buttonWrapper.classList.add('flex', 'items-center', 'mt-2', 'py-4', 'text-left');
        
        const renameButton = document.createElement('button');
        renameButton.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-0', 'px-0', 'rounded', 'mr-2');
        const renameImg = document.createElement('img');
        renameImg.src = "/static/images/edit_discussion.png";
        renameImg.style.width='20px'
        renameImg.style.height='20px'
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
        deleteButton.classList.add('bg-green-500', 'hover:bg-green-700', 'text-white', 'font-bold', 'py-0', 'px-0', 'rounded', 'ml-2');
        const deleteImg = document.createElement('img');
        deleteImg.src = "/static/images/delete_discussion.png";
        deleteImg.style.width='20px'
        deleteImg.style.height='20px'

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
        discussionButton.classList.add('flex-grow', 'w-full', 'bg-blue-500', 'hover:bg-blue-700', 'text-white', 'font-bold', 'py-2', 'px-4', 'rounded', 'text-left', 'hover:text-white');
        discussionButton.textContent = discussion.title;
        discussionButton.addEventListener('click', () => {
          // send query with discussion id to reveal discussion messages
          fetch('/get_messages', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify({ id: discussion.id })
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
                    addMessage(message.sender, message.content, message.id, true);
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
          console.log(`Showing messages for discussion ${discussion.id}`);
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

// First time we populate the discussions list
populate_discussions_list()



const newDiscussionBtn = document.querySelector('#new-discussion-btn');

newDiscussionBtn.addEventListener('click', () => {
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
        console.log(`New chat ${data}`)
        // Select the new discussion
        //selectDiscussion(discussionId);
        chatWindow.innerHTML=""
        addMessage("GPT4ALL", welcome_message,0);
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
