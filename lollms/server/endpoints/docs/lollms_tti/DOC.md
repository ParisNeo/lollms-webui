# Lollms Text to Image Library
1. Include the library:
   ```html
   <script src="/lollms_assets/js/lollms_tti"></script>
   ```

2. Initialize in your JavaScript:
   ```javascript
   const ttiClient = new LollmsTTI();// You can also add a parameter BaseUrl which is by default "http://localhost:9600"
   ```

3. Generate and display an image:
   ```javascript
   const container = document.getElementById('image-container');
   await ttiClient.generateAndDisplayImage('prompt', 'negative prompt', 512, 512, container); // The container must be a div
   ```

4. Or generate image separately:
   ```javascript
   ttiClient.generateImage('prompt', 'negative prompt', 512, 512)// prompt, negative prompt, width, height
     .then(base64Image => {
       // Use base64Image
     });
   ```
5. To change the server base url, we can use:
   ```javascript
   ttiClient.setBaseUrl("http://localhost:9600"); // Change to the right server address
   ```
   

This library simplifies image generation requests to the LoLLMs backend, handling the API call and image display.
