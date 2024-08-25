# Lollms Text to Image Library
1. Include the library:
   ```html
   <script src="/lollms_assets/js/lollms_tti"></script>
   ```

2. Initialize in your JavaScript:
   ```javascript
   const ttiClient = new LollmsTTI();
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

This library simplifies image generation requests to the LoLLMs backend, handling the API call and image display.