document.getElementById('help-link').addEventListener('click', loadHelpPage);


function loadHelpPage(event) {
    event.preventDefault(); // Prevent the default link behavior

    fetch('/help')
      .then(response => response.text())
      .then(html => {
        document.getElementById('help').innerHTML = html;
      })
      .catch(error => {
        console.error('Error loading help page:', error);
      });
  }