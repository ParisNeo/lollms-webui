function showTab(tabId) {
  // hide all tabs
  var tabs = document.getElementsByClassName('tab-pane');
  for (var i = 0; i < tabs.length; i++) {
    tabs[i].style.display = 'none';
  }
  // show the selected tab
  console.log(tabId)
  var tab = document.getElementById(tabId);
  tab.style.display = 'block';
}

// show the main tab by default
showTab('main');
// add event listeners to the tab links
var tabLinks = document.getElementsByTagName('a');
for (var i = 0; i < tabLinks.length; i++) {
  tabLinks[i].addEventListener('click', function (event) {
    event.preventDefault();
    var tabId = this.getAttribute('href').substring(1);
    showTab(tabId);
  });
}

fetch('/main')
  .then(response => response.text())
  .then(html => {
    document.getElementById('main').innerHTML = html;
    // First time we populate the discussions list
    populate_discussions_list()
    populate_menu();
    load_discussion();
    update_main();
    db_export();

    // Dirty fix for disabling speech synth for firefox browsers :()
    if (!userAgent.match(/firefox|fxios/i)) {
      prepre_audio();
      add_audio_in_ui();
      populateVoicesList();
    }

  })
  .catch(error => {
    console.error('Error loading main page:', error);
  });
