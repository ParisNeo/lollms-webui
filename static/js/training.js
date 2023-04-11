document.getElementById('training-link').addEventListener('click', loadHelpPage);


function loadHelpPage(event) {
    event.preventDefault(); // Prevent the default link behavior

    fetch('/training')
      .then(response => response.text())
      .then(html => {
        document.getElementById('training').innerHTML = html;
      })
      .catch(error => {
        console.error('Error loading help page:', error);
      });
  }