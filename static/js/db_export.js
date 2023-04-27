function db_export(){
    const chatWindow = document.getElementById('chat-window');
    const exportButton = document.getElementById('export-button');
    exportButton.title = "Export database";
    exportButton.addEventListener('click', () => {
        const messages = Array.from(chatWindow.querySelectorAll('.message')).map(messageElement => {
            const senderElement = messageElement.querySelector('.sender');
            const messageTextElement= messageElement.querySelector('.message-text');
            const sender = senderElement.textContent;
            const messageText = messageTextElement.textContent;
            return { sender, messageText };
            });
        const exportFormat = 'json'; // replace with desired export format
    
        if (exportFormat === 'text') {
            const exportText = messages.map(({ sender, messageText }) => `${sender}: ${messageText}`).join('\n');
            downloadTextFile(exportText);
        } else if (exportFormat === 'json') {
            fetch('/export')
            .then(response => response.json())
            .then(data => {
                db_data = JSON.stringify(data)
              // Do something with the data, such as displaying it on the page
              console.log(db_data);
              downloadJsonFile(db_data);
            })
            .catch(error => {
              // Handle any errors that occur
              console.error(error);
            });
        } else {
            console.error(`Unsupported export format: ${exportFormat}`);
        }
    });
    
    function downloadTextFile(text) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    downloadUrl(url);
    }
    
    function downloadJsonFile(json) {
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    downloadUrl(url);
    }
    
    function downloadUrl(url) {
    const link = document.createElement('a');
    link.href = url;
    link.download = 'discussions.json';
    link.click();
    }
    
}
