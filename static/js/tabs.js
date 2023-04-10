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
        tabLinks[i].addEventListener('click', function(event) {
        event.preventDefault();
        var tabId = this.getAttribute('href').substring(1);
        showTab(tabId);
    });
}