document.getElementById('extensions-link').addEventListener('click', loadExtensionsPage);


function loadExtensionsPage(event) {
    event.preventDefault(); // Prevent the default link behavior

    fetch('/extensions')
      .then(response => response.text())
      .then(html => {
        document.getElementById('extensions').innerHTML = html;
      })
      .catch(error => {
        console.error('Error loading extensions page:', error);
      });
  }