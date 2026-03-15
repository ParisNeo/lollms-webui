class LollmsTTI {
    constructor(baseUrl = '') {
      this.baseUrl = baseUrl;
    }
    
    setBaseUrl(baseUrl){
      this.baseUrl = baseUrl;
    }
    updateSettings(settings) {
      // Update each setting if it's provided in the settings object
      if ('host_address' in settings) this.baseUrl = settings.host_address;
      if ('baseUrl' in settings) this.baseUrl = settings.baseUrl;
    }
     
    async generateImage(prompt, negativePrompt = '', width = 512, height = 512) {
      const url = `${this.baseUrl}/generate_image`;
      const requestBody = {
        prompt,
        negative_prompt: negativePrompt,
        width,
        height
      };
  
      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify(requestBody)
        });
  
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
  
        const data = await response.json();
        return data.image; // This is the base64 encoded image
      } catch (error) {
        console.error('Error generating image:', error);
        throw error;
      }
    }
  
    createImageElement(base64Image) {
      const img = document.createElement('img');
      img.src = `data:image/jpeg;base64,${base64Image}`;
      img.alt = 'Generated Image';
      return img;
    }
  
    async generateAndDisplayImage(prompt, negativePrompt = '', width = 512, height = 512, container) {
      try {
        const base64Image = await this.generateImage(prompt, negativePrompt, width, height);
        const imgElement = this.createImageElement(base64Image);
        console.log("base64Image", base64Image)
        container.appendChild(imgElement);
      } catch (error) {
        console.error('Error generating and displaying image:', error);
        container.innerHTML = `<p>Error generating image: ${error.message}</p>`;
      }
    }
  }
  
