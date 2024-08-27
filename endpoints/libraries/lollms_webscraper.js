class WebScraper {
    constructor() {}
  
    async fetchHTML(url) {
      try {
        const response = await fetch(url);
        const text = await response.text();
        return new DOMParser().parseFromString(text, 'text/html');
      } catch (error) {
        console.error(`Error fetching the HTML: ${error}`);
        throw error;
      }
    }
  
    extractData(doc, selector) {
      const data = [];
      const elements = doc.querySelectorAll(selector);
      elements.forEach(element => {
        data.push(element.textContent.trim());
      });
      return data;
    }
  
    async scrape(url, selector) {
      const doc = await this.fetchHTML(url);
      return this.extractData(doc, selector);
    }
  }
  
  // Expose the WebScraper class to the global window object
  window.WebScraper = WebScraper;
  