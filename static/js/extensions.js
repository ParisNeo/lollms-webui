document.getElementById('extensions-link').addEventListener('click', loadHelpPage);


function loadHelpPage(event) {
    event.preventDefault(); // Prevent the default link behavior

    fetch('/extensions')
      .then(response => response.text())
      .then(html => {
        document.getElementById('extensions').innerHTML = html;
      })
      .catch(error => {
        console.error('Error loading help page:', error);
      });
  }