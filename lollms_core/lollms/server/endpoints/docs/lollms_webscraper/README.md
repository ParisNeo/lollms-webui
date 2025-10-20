# WebScraper.js

WebScraper.js is a lightweight JavaScript library designed for web scraping tasks directly from the browser. It allows you to fetch and extract data from web pages using CSS selectors. This library is ideal for simple scraping tasks where you need to gather text content from static web pages.

## Features

- **Fetch HTML Content**: Retrieve HTML content from a specified URL.
- **Extract Data**: Use CSS selectors to extract text content from HTML elements.
- **Browser Compatible**: Designed to work in a browser environment using native JavaScript APIs.

## Installation

To use WebScraper.js in your project, include it in your HTML file using a `<script>` tag:

```html
<script src="/lollms_assets/js/webscraper"></script>
```

## Usage

Here's a basic example of how to use WebScraper.js to scrape data from a web page:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Scraper Test</title>
</head>
<body>
    <h1>Web Scraper Test</h1>
    <script src="/lollms_assets/js/webscraper"></script>
    <script>
        (async () => {
            const scraper = new WebScraper();
            const url = 'https://example.com';
            const selector = 'h1'; // Change this to the CSS selector you want to use
            const data = await scraper.scrape(url, selector);
            console.log(data);
        })();
    </script>
</body>
</html>
```

## Important Considerations

- **CORS Restrictions**: Be aware of Cross-Origin Resource Sharing (CORS) restrictions when making HTTP requests from the browser. Ensure that the server hosting the target URL allows cross-origin requests.
- **Security and Compliance**: Always ensure that your web scraping activities comply with the terms of service of the websites you are accessing.
- **Dynamic Content**: This library does not handle JavaScript-rendered content. For more complex scraping tasks, consider using a headless browser like Puppeteer in a Node.js environment.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue if you have any suggestions or improvements.

## Author

Created by ParisNeo, a computer geek passionate about AI.
