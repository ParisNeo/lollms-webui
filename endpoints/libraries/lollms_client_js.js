// This requires axios
// In the html don't forget to import axios.min.js cdn
// <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>



// JavaScript equivalent of the ELF_GENERATION_FORMAT enum
const ELF_GENERATION_FORMAT = {
  LOLLMS: 0,
  OPENAI: 1,
  OLLAMA: 2,
  LITELLM: 3,
  VLLM: 4
};

// JavaScript equivalent of the ELF_COMPLETION_FORMAT enum
const ELF_COMPLETION_FORMAT = {
  Instruct: 0,
  Chat: 1
};

// Ensuring the objects are immutable
Object.freeze(ELF_GENERATION_FORMAT);
Object.freeze(ELF_COMPLETION_FORMAT);

// Helper function to convert string to ELF_GENERATION_FORMAT
function convertToGenerationFormat(mode) {
  if (typeof mode === 'string') {
      // Convert string to uppercase for case-insensitive comparison
      const upperMode = mode.toUpperCase();
      
      // Find matching key in ELF_GENERATION_FORMAT
      for (const [key, value] of Object.entries(ELF_GENERATION_FORMAT)) {
          if (key === upperMode) {
              return value;
          }
      }
      // If no match found, return default LOLLMS (0)
      return ELF_GENERATION_FORMAT.LOLLMS;
  }
  // If not a string, return the value as is
  return mode;
}
class LollmsClient {
  constructor(
    host_address = null,
    model_name = null,
    ctx_size = null,
    personality = -1,
    n_predict = null,
    temperature = 0.1,
    top_k = 50,
    top_p = 0.95,
    repeat_penalty = 0.8,
    repeat_last_n = 40,
    seed = null,
    n_threads = 8,
    service_key = "",
    default_generation_mode = ELF_GENERATION_FORMAT.LOLLMS
  ) {
    // Handle the import or initialization of tiktoken equivalent in JavaScript
    // this.tokenizer = new TikTokenJS('gpt-3.5-turbo-1106'); // This is hypothetical

    this.host_address = host_address;
    this.model_name = model_name;
    this.ctx_size = ctx_size;
    this.n_predict = n_predict?n_predict:null;
    this.personality = personality;
    this.temperature = temperature;
    this.top_k = top_k;
    this.top_p = top_p;
    this.repeat_penalty = repeat_penalty;
    this.repeat_last_n = repeat_last_n;
    this.seed = seed;
    this.n_threads = n_threads;
    this.service_key = service_key;
    this.default_generation_mode = convertToGenerationFormat(default_generation_mode);
    this.minNPredict = 10
    this.template = {
      start_header_id_template: "!@>",
      end_header_id_template: ": ",
      separator_template: "\n",
      start_user_header_id_template: "!@>",
      end_user_header_id_template: ": ",
      end_user_message_id_template: "",
      start_ai_header_id_template: "!@>",
      end_ai_header_id_template: ": ",
      end_ai_message_id_template: "",
      system_message_template: "system"
    }
    fetch('/template')
    .then((response) => {
      if (!response.ok) {
        throw new Error('Network response was not ok ' + response.statusText);
      }
      return response.json();
    })
    .then((data) => {
      console.log("data: ", data);
      this.template = data;
    })
    .catch((error) => {
      console.error('Error fetching template:', error);
    });

  }
  updateSettings(settings) {
    // Update each setting if it's provided in the settings object
    if ('host_address' in settings) this.host_address = settings.host_address;
    if ('model_name' in settings) this.model_name = settings.model_name;
    if ('ctx_size' in settings) this.ctx_size = settings.ctx_size;
    if ('n_predict' in settings) this.n_predict = settings.n_predict;
    if ('personality' in settings) this.personality = settings.personality;
    if ('temperature' in settings) this.temperature = settings.temperature;
    if ('top_k' in settings) this.top_k = settings.top_k;
    if ('top_p' in settings) this.top_p = settings.top_p;
    if ('repeat_penalty' in settings) this.repeat_penalty = settings.repeat_penalty;
    if ('repeat_last_n' in settings) this.repeat_last_n = settings.repeat_last_n;
    if ('seed' in settings) this.seed = settings.seed;
    if ('n_threads' in settings) this.n_threads = settings.n_threads;
    if ('service_key' in settings) this.service_key = settings.service_key;
    if ('default_generation_mode' in settings) this.default_generation_mode = convertToGenerationFormat(settings.default_generation_mode);

    // You might want to add some validation or type checking here

    console.log('Settings updated:', settings);
  }

  separatorTemplate(){
    return this.template.separator_template;
  }
  system_message(){
    return this.template.start_header_id_template+this.template.system_message_template+this.template.end_header_id_template
  }
  custom_system_message(msg){
    return this.template.start_header_id_template+msg+this.template.end_header_id_template
  }
  ai_message(ai_name="assistant"){
    return this.template.start_ai_header_id_template+ai_name+this.template.end_ai_header_id_template
  }
  user_message(user_name="user"){
    return this.template.start_user_header_id_template+user_name+this.template.end_user_header_id_template
  }
  custom_message(message_name="message"){
    return this.template.start_ai_header_id_template+message_name+this.template.end_ai_header_id_template
  }
  updateServerAddress(newAddress) {
      this.serverAddress = newAddress;
    }    
  async tokenize(prompt, return_named=false) {
      /**
       * Tokenizes the given prompt using the model's tokenizer.
       *
       * @param {string} prompt - The input prompt to be tokenized.
       * @returns {Array} A list of tokens representing the tokenized prompt.
       */
      const output = await axios.post("/lollms_tokenize", {"prompt": prompt, "return_named": return_named});
      if(return_named)
      {
        return output.data  
      }
      else{
        return output.data
      }
    }
  async detokenize(tokensList, return_named=false) {
      /**
       * Detokenizes the given list of tokens using the model's tokenizer.
       *
       * @param {Array} tokensList - A list of tokens to be detokenized.
       * @returns {string} The detokenized text as a string.
       */
      const output = await axios.post("/lollms_detokenize", {"tokens": tokensList, "return_named": return_named});
      if(return_named)
        {
         console.log(output.data.text)
         return output.data.text
        }
        else{
          console.log(output.data)
          return output.data
        }
  }
cancel_generation() {
  // TODO: implement
}

  generate(prompt, {
      n_predict = null,
      stream = false,
      temperature = 0.1,
      top_k = 50,
      top_p = 0.95,
      repeat_penalty = 0.8,
      repeat_last_n = 40,
      seed = null,
      n_threads = 8,
      service_key = "",
      streamingCallback = null
    } = {}) {
      switch (this.default_generation_mode) {
        case ELF_GENERATION_FORMAT.LOLLMS:
          return this.lollms_generate(prompt, this.host_address, this.model_name, -1, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, service_key, streamingCallback);
        case ELF_GENERATION_FORMAT.OPENAI:
          return this.openai_generate(prompt, this.host_address, this.model_name, -1, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, ELF_COMPLETION_FORMAT.INSTRUCT, service_key, streamingCallback);
        case ELF_GENERATION_FORMAT.OLLAMA:
          return this.ollama_generate(prompt, this.host_address, this.model_name, -1, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, ELF_COMPLETION_FORMAT.INSTRUCT, service_key, streamingCallback);
        case ELF_GENERATION_FORMAT.LITELLM:
          return this.litellm_generate(prompt, this.host_address, this.model_name, -1, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, ELF_COMPLETION_FORMAT.INSTRUCT, service_key, streamingCallback);
        case ELF_GENERATION_FORMAT.VLLM:
          return this.vllm_generate(prompt, this.host_address, this.model_name, -1, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, ELF_COMPLETION_FORMAT.INSTRUCT, service_key, streamingCallback);
        default:
          throw new Error('Invalid generation mode');
      }
    }
    generate_with_images(prompt, images,
      n_predict = null,
      stream = false,
      temperature = 0.1,
      top_k = 50,
      top_p = 0.95,
      repeat_penalty = 0.8,
      repeat_last_n = 40,
      seed = null,
      n_threads = 8,
      service_key = "",
      streamingCallback = null
    ) {
      switch (this.default_generation_mode) {
        case ELF_GENERATION_FORMAT.LOLLMS:
          return this.lollms_generate_with_images(prompt, images, this.host_address, this.model_name, -1, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, service_key, streamingCallback);
        case ELF_GENERATION_FORMAT.OPENAI:
          return this.openai_generate_with_images(prompt, images, this.host_address, this.model_name, -1, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, ELF_COMPLETION_FORMAT.INSTRUCT, service_key, streamingCallback);
        default:
          throw new Error('Invalid generation mode');
      }
    }
  async generateText(prompt, options = {}) {
      // Destructure with default values from `this` if not provided in `options`
      const {
          host_address = this.host_address,
          model_name = this.model_name,
          personality = this.personality,
          n_predict = this.n_predict,
          stream = false,
          temperature = this.temperature,
          top_k = this.top_k,
          top_p = this.top_p,
          repeat_penalty = this.repeat_penalty,
          repeat_last_n = this.repeat_last_n,
          seed = this.seed,
          n_threads = this.n_threads,
          service_key = this.service_key,
          streamingCallback = null
      } = options;

      try {
          const result = await this.lollms_generate(
          prompt,
          host_address,
          model_name,
          personality,
          n_predict,
          stream,
          temperature,
          top_k,
          top_p,
          repeat_penalty,
          repeat_last_n,
          seed,
          n_threads,
          service_key,
          streamingCallback
          );
          return result;
      } catch (error) {
          // Handle any errors that occur during generation
          console.error('An error occurred during text generation:', error);
          throw error; // Re-throw the error if you want to allow the caller to handle it as well
      }
  }
    async lollms_generate(prompt, host_address = this.host_address, model_name = this.model_name, personality = this.personality, n_predict = this.n_predict, stream = false, temperature = this.temperature, top_k = this.top_k, top_p = this.top_p, repeat_penalty = this.repeat_penalty, repeat_last_n = this.repeat_last_n, seed = this.seed, n_threads = this.n_threads, service_key = this.service_key, streamingCallback = null) {
      let url;
      if(host_address!=null){
        url = `${host_address}/lollms_generate`;
      }
      else{
        url = `/lollms_generate`;
      }
      const headers = service_key !== "" ? {
          'Content-Type': 'application/json; charset=utf-8',
          'Authorization': `Bearer ${service_key}`,
      } : {
          'Content-Type': 'application/json',
      };
      console.log("n_predict:",n_predict)
      console.log("self.n_predict:",this.n_predict)
      const data = JSON.stringify({
          prompt: prompt,
          model_name: model_name,
          personality: personality,
          n_predict: n_predict?n_predict:this.n_predict,
          stream: stream,
          temperature: temperature,
          top_k: top_k,
          top_p: top_p,
          repeat_penalty: repeat_penalty,
          repeat_last_n: repeat_last_n,
          seed: seed,
          n_threads: n_threads
      });

      try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: data
        });

        // Check if the response is okay
        if (!response.ok) {
            throw new Error('Network response was not ok ' + response.statusText);
        }

        // Read the response as plaintext
        const responseBody = await response.text();
        console.log(responseBody)
        return responseBody ;
      } catch (error) {
          console.error(error);
          return null;
      }
  }
  async lollms_generate_with_images(prompt, images, host_address = this.host_address, model_name = this.model_name, personality = this.personality, n_predict = this.n_predict, stream = false, temperature = this.temperature, top_k = this.top_k, top_p = this.top_p, repeat_penalty = this.repeat_penalty, repeat_last_n = this.repeat_last_n, seed = this.seed, n_threads = this.n_threads, service_key = this.service_key, streamingCallback = null) {
    let url;
    if(host_address!=null){
      url = `${host_address}/lollms_generate_with_images`;
    }
    else{
      url = `/lollms_generate_with_images`;
    }
    const headers = service_key !== "" ? {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': `Bearer ${service_key}`,
    } : {
        'Content-Type': 'application/json',
    };
    console.log("n_predict:",n_predict)
    console.log("self.n_predict:",this.n_predict)
    const data = JSON.stringify({
        prompt: prompt,
        images: images,
        model_name: model_name,
        personality: personality,
        n_predict: n_predict?n_predict:this.n_predict,
        stream: stream,
        temperature: temperature,
        top_k: top_k,
        top_p: top_p,
        repeat_penalty: repeat_penalty,
        repeat_last_n: repeat_last_n,
        seed: seed,
        n_threads: n_threads
    });

    try {
      const response = await fetch(url, {
          method: 'POST',
          headers: headers,
          body: data
      });

      // Check if the response is okay
      if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText);
      }

      // Read the response as plaintext
      const responseBody = await response.text();
      console.log(responseBody)
      return responseBody ;
    } catch (error) {
        console.error(error);
        return null;
    }
}


async openai_generate(prompt, host_address = this.host_address, model_name = this.model_name, personality = this.personality, n_predict = this.n_predict, stream = false, temperature = this.temperature, top_k = this.top_k, top_p = this.top_p, repeat_penalty = this.repeat_penalty, repeat_last_n = this.repeat_last_n, seed = this.seed, n_threads = this.n_threads, ELF_COMPLETION_FORMAT = "vllm instruct", service_key = this.service_key, streamingCallback = null) {
    const url = `${host_address}/generate_completion`;
    const headers = service_key !== "" ? {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': `Bearer ${service_key}`,
    } : {
        'Content-Type': 'application/json',
    };

    const data = JSON.stringify({
        prompt: prompt,
        model_name: model_name,
        personality: personality,
        n_predict: n_predict,
        stream: stream,
        temperature: temperature,
        top_k: top_k,
        top_p: top_p,
        repeat_penalty: repeat_penalty,
        repeat_last_n: repeat_last_n,
        seed: seed,
        n_threads: n_threads,
        completion_format: ELF_COMPLETION_FORMAT
    });

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: data
        });
        if (stream && streamingCallback) {
            // Note: Streaming with Fetch API in the browser might not work as expected because Fetch API does not support HTTP/2 server push.
            // You would need a different approach for real-time streaming.
            streamingCallback(await response.json(), 'MSG_TYPE_CHUNK');
        } else {
            return await response.json();
        }
    } catch (error) {
        console.error("Error generating completion:", error);
        return null;
    }
}


async openai_generate_with_images(prompt, images, options = {}) {
  const {
    host_address = this.host_address,
    model_name = this.model_name,
    personality = this.personality,
    n_predict = this.n_predict,
    stream = false,
    temperature = this.temperature,
    top_k = this.top_k,
    top_p = this.top_p,
    repeat_penalty = this.repeat_penalty,
    repeat_last_n = this.repeat_last_n,
    seed = this.seed,
    n_threads = this.n_threads,
    max_image_width = -1,
    service_key = this.service_key,
    streamingCallback = null,
  } = options;

  const headers = {
    'Content-Type': 'application/json',
    ...(service_key ? { 'Authorization': `Bearer ${service_key}` } : {})
  };

  const data = {
    model: model_name,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "text",
            text: prompt
          },
          ...images.map(image_path => ({
            type: "image_url",
            image_url: {
              url: `data:image/jpeg;base64,${this.encode_image(image_path, max_image_width)}`
            }
          }))
        ]
      }
    ],
    stream: true,
    temperature: parseFloat(temperature),
    max_tokens: n_predict
  };

  const completion_format_path = "/v1/chat/completions";
  const url = `${host_address.endsWith("/") ? host_address.slice(0, -1) : host_address}${completion_format_path}`;

  try {
    const response = await fetch(url, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(data)
    });

    if (!response.ok) {
      const content = await response.json();
      if (response.status === 400) {
        this.error(content.error?.message || content.message);
      } else if (response.status === 404) {
        console.error(await response.text());
      }
      return;
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let text = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const jsonData = JSON.parse(line.slice(5).trim());
            const content = jsonData.choices[0]?.delta?.content || "";
            text += content;
            if (streamingCallback) {
              if (!streamingCallback(content, "MSG_TYPE_CHUNK")) {
                return text;
              }
            }
          } catch (error) {
            // Handle JSON parsing error
          }
        } else if (line.startsWith("{")) {
          try {
            const jsonData = JSON.parse(line);
            if (jsonData.object === "error") {
              this.error(jsonData.message);
              return text;
            }
          } catch (error) {
            this.error("Couldn't generate text, verify your key or model name");
          }
        } else {
          text += line;
          if (streamingCallback) {
            if (!streamingCallback(line, "MSG_TYPE_CHUNK")) {
              return text;
            }
          }
        }
      }
    }

    return text;
  } catch (error) {
    console.error("Error in openai_generate_with_images:", error);
    throw error;
  }
}


async vllm_generate({
  prompt,
  host_address = null,
  model_name = null,
  personality = null,
  n_predict = null,
  stream = false,
  temperature = null,
  top_k = null,
  top_p = null,
  repeat_penalty = null,
  repeat_last_n = null,
  seed = null,
  n_threads = null,
  completion_format = ELF_COMPLETION_FORMAT.Instruct, // Instruct or Chat
  service_key = "",
  streaming_callback = null
}) {
  // Set default values to instance variables if optional arguments are null
  host_address = host_address || this.host_address;
  model_name = model_name || this.model_name;
  n_predict = n_predict || this.n_predict || this.minNPredict;
  personality = personality !== null ? personality : this.personality;
  temperature = temperature !== null ? temperature : this.temperature;
  top_k = top_k !== null ? top_k : this.top_k;
  top_p = top_p !== null ? top_p : this.top_p;
  repeat_penalty = repeat_penalty !== null ? repeat_penalty : this.repeat_penalty;
  repeat_last_n = repeat_last_n !== null ? repeat_last_n : this.repeat_last_n;
  seed = seed || this.seed;
  n_threads = n_threads || this.n_threads;

  const headers = {
    "Content-Type": "application/json",
    ...(service_key && { Authorization: `Bearer ${service_key}` })
  };

  let data;
  let completionFormatPath;

  if (completion_format === ELF_COMPLETION_FORMAT.Instruct) {
    data = {
      model: model_name,
      prompt: prompt,
      stream: stream,
      temperature: parseFloat(temperature),
      max_tokens: n_predict
    };
    completionFormatPath = "/v1/completions";
  } else if (completion_format === ELF_COMPLETION_FORMAT.Chat) {
    data = {
      model: model_name,
      messages: [
        {
          role: "user",
          content: prompt
        }
      ],
      stream: stream,
      temperature: parseFloat(temperature),
      max_tokens: n_predict
    };
    completionFormatPath = "/v1/chat/completions";
  }

  if (host_address.endsWith("/")) {
    host_address = host_address.slice(0, -1);
  }

  const url = `${host_address}${completionFormatPath}`;

  try {
    const response = await axios.post(url, data, {
      headers: headers,
      responseType: stream ? "stream" : "json",
      httpsAgent: this.verifySslCertificate
        ? undefined
        : new (require("https").Agent)({ rejectUnauthorized: false })
    });

    if (stream) {
      let text = "";
      response.data.on("data", (chunk) => {
        const decoded = chunk.toString("utf-8");
        if (decoded.startsWith("data: ")) {
          try {
            const jsonData = JSON.parse(decoded.slice(5).trim());
            let chunkContent = "";
            if (completion_format === ELF_COMPLETION_FORMAT.Chat) {
              chunkContent = jsonData.choices[0]?.delta?.content || "";
            } else {
              chunkContent = jsonData.choices[0]?.text || "";
            }
            text += chunkContent;
            if (streaming_callback) {
              if (!streaming_callback(chunkContent, "MSG_TYPE_CHUNK")) {
                response.data.destroy();
              }
            }
          } catch (error) {
            response.data.destroy();
          }
        }
      });

      return new Promise((resolve, reject) => {
        response.data.on("end", () => resolve(text));
        response.data.on("error", (err) => reject(err));
      });
    } else {
      return response.data;
    }
  } catch (error) {
    if (error.response) {
      const errorMessage =
        error.response.data?.error?.message ||
        error.response.data?.message ||
        "Unknown error occurred";
      console.error(errorMessage);
      throw new Error(errorMessage);
    } else {
      console.error(error.message);
      throw error;
    }
  }
}

async encode_image(image_path, max_image_width = -1) {
  // In a browser environment, we'll use the File API and canvas
  // For Node.js, you'd need to use libraries like 'sharp' or 'jimp'
  
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      let width = img.width;
      let height = img.height;

      // Resize if necessary
      if (max_image_width !== -1 && width > max_image_width) {
        const ratio = max_image_width / width;
        width = max_image_width;
        height = Math.round(height * ratio);
      }

      // Create a canvas to draw the image
      const canvas = document.createElement('canvas');
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext('2d');

      // Draw the image on the canvas
      ctx.drawImage(img, 0, 0, width, height);

      // Convert to base64
      const base64Image = canvas.toDataURL('image/jpeg').split(',')[1];
      resolve(base64Image);
    };

    img.onerror = (error) => reject(error);

    // Load the image from the provided path
    img.src = image_path;
  });
}
async generateCode(
  prompt, 
  template=null,
  language="json",
  images = [],  
  {
    n_predict = null,
    temperature = 0.1,
    top_k = 50,
    top_p = 0.95,
    repeat_penalty = 0.8,
    repeat_last_n = 40,
    streamingCallback = null
  } = {}
){
  let response;
  const systemHeader = this.custom_message("Generation infos");
  let codeInstructions = "";
  if(template){
      codeInstructions =   "Generated code must be put inside the adequate markdown code tag. Use this template:\n```"+language+"\n"+template+"\n```\nMake sure only a single code tag is generated at each dialogue turn.\n";
  }
  else{
      codeInstructions =   "Generated code must be put inside the adequate markdown code tag. Use this template:\n```language name\nCode\n```\nMake sure only a single code tag is generated at each dialogue turn.\n";
  }
  const fullPrompt = systemHeader + codeInstructions + this.separatorTemplate() + prompt + this.ai_message();

  if (images.length > 0) {
      response = await this.generate_with_images(fullPrompt, images, {
        n_predict: n_predict,
        temperature: temperature,
        top_k: top_k,
        top_p: top_p,
        repeat_penalty: repeat_penalty,
        repeat_last_n: repeat_last_n,
        callback: streamingCallback
    });
  } else {
      response = await this.generate(fullPrompt, {
        n_predict: n_predict,
        temperature: temperature,
        top_k: top_k,
        top_p: top_p,
        repeat_penalty: repeat_penalty,
        repeat_last_n: repeat_last_n,
        callback: streamingCallback
    });
  }

  const codes = this.extractCodeBlocks(response);
  console.log(codes)
  if (codes.length > 0) {
      let code = '';
      if (!codes[0].is_complete) {
          code = codes[0].content.split('\n').slice(0, -1).join('\n');
          while (!codes[0].is_complete) {
              console.warn("The AI did not finish the code, let's ask it to continue")
              const continuePrompt = prompt + self.separator_template + code + self.separator_template + this.user_message() + "continue the code. Rewrite last line and continue the code. Don't forget to put the code inside a markdown code tag." + this.separatorTemplate() + this.aiFullHeader;
              response = await this.generate(continuePrompt, {
                  n_predict: n_predict,
                  temperature: temperature,
                  top_k: top_k,
                  top_p: top_p,
                  repeat_penalty: repeat_penalty,
                  repeat_last_n: repeat_last_n,
                  callback: streamingCallback
              });
              const codes = this.extractCodeBlocks(response);
              if (codes.length === 0) break;
              
              if (!codes[0].is_complete) {
                  code += '\n' + codes[0].content.split('\n').slice(0, -1).join('\n');
              } else {
                  code += '\n' + codes[0].content;
              }
          }
      } else {
          code = codes[0].content;
      }
      return code;
  } else {
      return null;
  }
}
async generateCodes(prompt, images = [], {
  n_predict = null,
  temperature = 0.1,
  top_k = 50,
  top_p = 0.95,
  repeat_penalty = 0.8,
  repeat_last_n = 40,
  streamingCallback = null
} = {}) {
  let response;
  const systemHeader = this.custom_message("Generation infos");
  const codeInstructions = "Generated code must be put inside the adequate markdown code tag. Use this template:\n```language name\nCode\n```\n";
  const fullPrompt = systemHeader + codeInstructions + this.separatorTemplate() + prompt;

  if (images.length > 0) {
    response = await this.generate_with_images(fullPrompt, images, {
      n_predict,
      temperature,
      top_k,
      top_p,
      repeat_penalty,
      repeat_last_n,
      callback: streamingCallback
    });
  } else {
    response = await this.generate(fullPrompt, {
      n_predict,
      temperature,
      top_k,
      top_p,
      repeat_penalty,
      repeat_last_n,
      callback: streamingCallback
    });
  }

  let codes = this.extractCodeBlocks(response);
  let completeCodes = [];

  while (codes.length > 0) {
    let currentCode = codes.shift();
    let codeContent = currentCode.content;

    while (!currentCode.is_complete) {
      console.warn("The AI did not finish the code, let's ask it to continue");
      const continuePrompt = prompt + self.separator_template + codeContent + self.separator_template + this.user_message() + "continue the code. Rewrite last line and continue the code." + this.separatorTemplate() + this.aiFullHeader;
      
      response = await this.generate(continuePrompt, {
        n_predict,
        temperature,
        top_k,
        top_p,
        repeat_penalty,
        repeat_last_n,
        callback: streamingCallback
      });

      const newCodes = this.extractCodeBlocks(response);
      if (newCodes.length === 0) break;

      // Append the content of the first new code block
      codeContent += '\n' + newCodes[0].content;
      currentCode = newCodes[0];

      // If there are more code blocks, add them to the codes array
      if (newCodes.length > 1) {
        codes = [...newCodes.slice(1), ...codes];
      }
    }

    completeCodes.push({
      language: currentCode.language,
      content: codeContent
    });
  }

  return completeCodes;
}
extractCodeBlocks(text, return_remaining_text = false) {
  const codes = [];
  let remainingText = text;
  let currentIndex = 0;
  
  while (true) {
      // Find next code block start
      const startPos = remainingText.indexOf('```');
      if (startPos === -1) {
          break;
      }
          
      // Check for file name before code block
      let fileName = '';
      const fileNameMatch = remainingText.slice(0, startPos).lastIndexOf('<file_name>');
      if (fileNameMatch !== -1) {
          const fileNameEnd = remainingText.slice(0, startPos).lastIndexOf('</file_name>');
          if (fileNameEnd !== -1 && fileNameMatch < fileNameEnd) {
              fileName = remainingText.slice(fileNameMatch + 11, fileNameEnd).trim();
          }
      }
      
      // Get code type if specified
      let codeType = '';
      const nextNewline = remainingText.indexOf('\n', startPos + 3);
      let contentStart;
      
      if (nextNewline !== -1) {
          const potentialType = remainingText.slice(startPos + 3, nextNewline).trim();
          if (potentialType) {
              codeType = potentialType;
              contentStart = nextNewline + 1;
          } else {
              contentStart = startPos + 3;
          }
      } else {
          contentStart = startPos + 3;
      }
          
      // Find matching end tag
      let pos = contentStart;
      let is_complete = false;
      
      // Find the closing backticks
      const endPos = remainingText.indexOf('```', contentStart);
      
      if (endPos !== -1) {
          // Found matching end tag
          const content = remainingText.slice(contentStart, endPos).trim();
          is_complete = true;
          codes.push({
              index: currentIndex,
              fileName: fileName,
              content: content,
              type: codeType,
              is_complete: true
          });
          remainingText = remainingText.slice(endPos + 3);
      } else {
          // Handle incomplete code block
          const content = remainingText.slice(contentStart).trim();
          codes.push({
              index: currentIndex,
              fileName: fileName,
              content: content,
              type: codeType,
              is_complete: false
          });
          remainingText = '';
      }
          
      currentIndex++;
  }
  
  if (return_remaining_text) {
      return { codes, remainingText };
  }
  return codes;
}



async listMountedPersonalities(host_address = this.host_address) {
    const url = `${host_address}/list_mounted_personalities`;

    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
}

async listModels(host_address = this.host_address) {
    const url = `${host_address}/list_models`;

    try {
        const response = await fetch(url);
        return await response.json();
    } catch (error) {
        console.error(error);
        return null;
    }
}
}

class TextChunker {
  constructor(chunkSize = 1024, overlap = 0, tokenizer = null, model = null) {
    this.chunkSize = chunkSize;
    this.overlap = overlap;
    this.tokenizer = tokenizer || new TikTokenTokenizer();
    this.model = model;
  }

  async getTextChunks(text, doc, cleanChunk = true, minNbTokensInChunk = 10) {
    const paragraphs = text.split('\n\n');
    const chunks = [];
    let currentChunk = [];
    let currentTokens = 0;
    let chunkId = 0;

    for (const paragraph of paragraphs) {
      const cleanedParagraph = cleanChunk ? paragraph.trim() : paragraph;
      const paragraphTokens = (await this.tokenizer.tokenize(cleanedParagraph)).length;

      if (currentTokens + paragraphTokens > this.chunkSize) {
        if (currentTokens > minNbTokensInChunk) {
          let chunkText = currentChunk.join('\n\n');
          if (cleanChunk) {
            chunkText = TextChunker.removeUnnecessaryReturns(chunkText);
          }
          const chunk = new Chunk(doc, '', chunkText, currentTokens, chunkId);
          chunkId++;
          chunks.push(chunk);
        }

        if (this.overlap > 0) {
          currentChunk = [...currentChunk.slice(-this.overlap), cleanedParagraph];
        } else {
          currentChunk = [cleanedParagraph];
        }
        currentTokens = currentChunk.reduce(async (sum, p) => sum + await this.tokenizer.tokenize(p).length, 0);
      } else {
        currentChunk.push(cleanedParagraph);
        currentTokens += paragraphTokens;
      }
    }

    if (currentChunk.length > 0 && currentTokens > minNbTokensInChunk) {
      let chunkText = currentChunk.join('\n\n');
      if (cleanChunk) {
        chunkText = TextChunker.removeUnnecessaryReturns(chunkText);
      }
      const chunk = new Chunk(doc, '', chunkText, currentTokens, chunkId);
      chunks.push(chunk);
    }

    return chunks;
  }

  static removeUnnecessaryReturns(paragraph) {
    const lines = paragraph.split('\n');
    return lines.filter(line => line.trim()).join('\n');
  }

  static async chunkText(text, tokenizer, chunkSize = 1024, overlap = 0, cleanChunk = true, minNbTokensInChunk = 10) {
    // Validate chunkSize
    if (isNaN(chunkSize) || chunkSize <= 0) {
        console.warn(`Invalid chunkSize: ${chunkSize}. Resetting to default value of 1024.`);
        chunkSize = 1024;
    }

    const paragraphs = text.split('\n\n');
    const chunks = [];
    let currentChunk = [];
    let currentTokens = 0;

    console.log("Starting text chunking...");
    console.log(`Using chunkSize: ${chunkSize}, overlap: ${overlap}, minNbTokensInChunk: ${minNbTokensInChunk}`);

    for (const paragraph of paragraphs) {
        const cleanedParagraph = cleanChunk ? paragraph.trim() : paragraph;
        const paragraphTokens = (await tokenizer.tokenize(cleanedParagraph)).length;

        console.log(`Processing paragraph: "${cleanedParagraph}"`);
        console.log(`Paragraph tokens: ${paragraphTokens}`);
        console.log(`Current tokens before adding: ${currentTokens}`);

        // Handle case where a single paragraph exceeds chunkSize
        if (paragraphTokens > chunkSize) {
            console.log(`Paragraph exceeds chunk size. Splitting...`);
            const splitParagraphs = await this.splitLargeParagraph(cleanedParagraph, tokenizer, chunkSize, overlap);
            for (const subChunk of splitParagraphs) {
                chunks.push(subChunk);
                console.log(`Chunk created from large paragraph: "${subChunk}"`);
            }
            continue;
        }

        // If adding this paragraph exceeds the chunk size
        if (currentTokens + paragraphTokens > chunkSize) {
            if (currentTokens >= minNbTokensInChunk) {
                let chunkText = currentChunk.join('\n\n');
                if (cleanChunk) {
                    chunkText = TextChunker.removeUnnecessaryReturns(chunkText);
                }
                chunks.push(chunkText);
                console.log(`Intermediate chunk created and added: "${chunkText}"`);
            } else {
                console.log("Skipping chunk creation due to insufficient tokens.");
            }

            // Handle overlap
            if (overlap > 0) {
                currentChunk = currentChunk.slice(-overlap); // Keep only the overlapping part
            } else {
                currentChunk = [];
            }

            currentChunk.push(cleanedParagraph);
            currentTokens = paragraphTokens; // Reset token count to the new paragraph's tokens
        } else {
            // Add paragraph to the current chunk
            currentChunk.push(cleanedParagraph);
            currentTokens += paragraphTokens;
        }

        console.log(`Current chunk after processing: ${currentChunk.join(' | ')}`);
        console.log(`Current tokens after processing: ${currentTokens}`);
    }

    // Add the last chunk if it meets the minimum token requirement
    if (currentChunk.length > 0 && currentTokens >= minNbTokensInChunk) {
        let chunkText = currentChunk.join('\n\n');
        if (cleanChunk) {
            chunkText = TextChunker.removeUnnecessaryReturns(chunkText);
        }
        chunks.push(chunkText);
        console.log(`Final chunk created and added: "${chunkText}"`);
    } else {
        console.log("No final chunk created due to insufficient tokens.");
    }

    console.log("Final Chunks:");
    console.log(chunks);
    return chunks;
  }

  // Helper function to split a large paragraph into smaller chunks
  static async splitLargeParagraph(paragraph, tokenizer, chunkSize, overlap) {
    const tokens = await tokenizer.tokenize(paragraph);
    const chunks = [];
    let start = 0;

    while (start < tokens.length) {
        const end = Math.min(start + chunkSize, tokens.length);
        const chunkTokens = tokens.slice(start, end);
        const chunkText = await tokenizer.detokenize(chunkTokens);
        chunks.push(chunkText);

        start += chunkSize - overlap; // Move start forward with overlap
    }

    return chunks;
  }


}

class TasksLibrary {
constructor(lollms) {
  this.lollms = lollms;
}

async translateTextChunk(textChunk, outputLanguage = "french", host_address = null, model_name = null, temperature = 0.1, maxGenerationSize = 3000) {
  const translationPrompt = [
    `${this.lollms.system_message()}`,
    `Translate the following text to ${outputLanguage}.`,
    `Be faithful to the original text and do not add or remove any information.`,
    `Respond only with the translated text.`,
    `Do not add comments or explanations.`,
    `${this.lollms.user_message("text to translate")}`,
    `${textChunk}`,
    `${this.lollms.ai_message("translation")}`,
  ].join("\n");

  const translated = await this.lollms.generateText(
    translationPrompt,
    host_address,
    model_name,
    -1, // personality
    maxGenerationSize, // n_predict
    false, // stream
    temperature, // temperature
    undefined, // top_k, using undefined to fallback on LollmsClient's default
    undefined, // top_p, using undefined to fallback on LollmsClient's default
    undefined, // repeat_penalty, using undefined to fallback on LollmsClient's default
    undefined, // repeat_last_n, using undefined to fallback on LollmsClient's default
    undefined, // seed, using undefined to fallback on LollmsClient's default
    undefined, // n_threads, using undefined to fallback on LollmsClient's default
    undefined // service_key, using undefined to fallback on LollmsClient's default
  );

  return translated;
}

async tokenize(text) {
  // Assuming the LollmsClient has a method to tokenize text
  return await this.lollms.tokenize(text);
}

async summarizeText(
  text,
  summaryInstruction = "summarize",
  docName = "chunk",
  answerStart = "",
  maxGenerationSize = 3000,
  maxSummarySize = 1024,
  callback = null,
  chunkSummaryPostProcessing = null,
  summaryMode = "SEQUENTIAL",
  reformat=false
) {
  console.log("Tokenizing incoming text:")
  let tk = await this.tokenize(text);
  let prevLen = tk.length;
  let documentChunks = null;
  console.log(`Text size: ${prevLen}/${maxSummarySize}`)

  while (tk.length > maxSummarySize && (documentChunks === null || documentChunks.length > 1)) {
      this.stepStart(`Compressing ${docName}...`);
      let chunkSize=1024;
      if(this.lollms.ctxSize){
        chunkSize = Math.floor(this.lollms.ctxSize * 0.6);
      }
      console.log("Chunk size:",chunkSize)
      documentChunks = await TextChunker.chunkText(text, this.lollms, chunkSize, 0, true);
      text = await this.summarizeChunks(
          documentChunks,
          summaryInstruction,
          docName,
          answerStart,
          maxGenerationSize,
          callback,
          chunkSummaryPostProcessing,
          summaryMode
      );
      tk = await this.tokenize(text);
      let dtkLn = prevLen - tk.length;
      prevLen = tk.length;
      this.step(`Current text size: ${prevLen}, max summary size: ${maxSummarySize}`);
      this.stepEnd(`Compressing ${docName}...`);
      if (dtkLn <= 10) break; // it is not summarizing
  }
  if(reformat){
    text = await this.lollms.generate(
      [
          this.lollms.system_message(),
          `${text}`,
          this.lollms.system_message(),
          summaryInstruction,
          "Do not add any extra comments.",
          this.lollms.system_message() + answerStart
      ].join("\n"),
    );
  }
  return text;
}

async smartDataExtraction(
  text,
  dataExtractionInstruction = "summarize the current chunk.",
  finalTaskInstruction = "reformulate with better wording",
  docName = "chunk",
  answerStart = "",
  maxGenerationSize = 3000,
  maxSummarySize = 1024,
  callback = null,
  chunkSummaryPostProcessing = null,
  summaryMode = "SEQUENTIAL"
) {
  let tk = await this.tokenize(text);
  let prevLen = tk.length;

  while (tk.length > maxSummarySize) {
    let chunkSize=1024;
    if(this.lollms.ctxSize){
      chunkSize = Math.floor(this.lollms.ctxSize * 0.6);
    }
    let documentChunks = await TextChunker.chunkText(text, this.lollms, chunkSize, 0, true);
      text = await this.summarizeChunks(          
          documentChunks,
          dataExtractionInstruction,
          docName,
          answerStart,
          maxGenerationSize,
          callback,
          chunkSummaryPostProcessing,
          summaryMode
      );
      tk = await this.tokenize(text);
      let dtkLn = prevLen - tk.length;
      prevLen = tk.length;
      this.step(`Current text size: ${prevLen}, max summary size: ${maxSummarySize}`);
      if (dtkLn <= 10) break; // it is not summarizing
  }

  this.stepStart("Rewriting ...");
  text = await this.summarizeChunks(
      [text],
      finalTaskInstruction,
      docName,
      answerStart,
      maxGenerationSize,
      callback,
      chunkSummaryPostProcessing,
      summaryMode
  );
  this.stepEnd("Rewriting ...");

  return text;
}

async summarizeChunks(
  chunks,
  summaryInstruction = "summarize the current chunk.",
  docName = "chunk",
  answerStart = "",
  maxGenerationSize = 3000,
  callback = null,
  chunkSummaryPostProcessing = null,
  summaryMode = "SEQUENTIAL"
) {
  if (summaryMode === "SEQUENTIAL") {
      let summary = "";
      for (let i = 0; i < chunks.length; i++) {
          this.stepStart(`Summary of ${docName} - Processing chunk: ${i + 1}/${chunks.length}`);
          console.log(`chunk:${i}`);
          console.log(chunks[i]);
          summary = `${answerStart}` + await this.fastGen(
              [
                  this.lollms.custom_system_message("Previous chunks summary"),
                  `${summary}`,
                  this.lollms.custom_system_message("Current text chunk"),
                  `${chunks[i]}`,
                  this.lollms.user_message(),
                  summaryInstruction,
                  this.lollms.custom_system_message("important"),
                  "Keep only information relevant to the context provided by the user",
                  "The output must keep information from the previous chunks summary and add the current chunk extracted information.",
                  "Be precise and do not invent information that does not exist in the previous chunks summary or the current chunk.",
                  "Do not add any extra comments and start your message directly by the summary.",
                  this.lollms.ai_message() + answerStart
              ].join("\n"),
              maxGenerationSize,
              callback
          );
          if (chunkSummaryPostProcessing) {
              summary = chunkSummaryPostProcessing(summary);
          }
          this.stepEnd(`Summary of ${docName} - Processing chunk: ${i + 1}/${chunks.length}`);
      }
      return summary;
  } else {
      let summaries = [];
      for (let i = 0; i < chunks.length; i++) {
          this.stepStart(`Summary of ${docName} - Processing chunk: ${i + 1}/${chunks.length}`);
          let summary = `${answerStart}` + await this.fastGen(
              [
                  `${this.lollms.system_message()}Document_chunk [${docName}]${this.lollms.system_message()}`,
                  `${chunks[i]}`,
                  `${this.lollms.system_message()}${summaryInstruction}`,
                  "Answer directly with the summary with no extra comments.",
                  `${this.lollms.system_message()}summary${this.lollms.system_message()}`,
                  `${answerStart}`
              ].join("\n"),
              maxGenerationSize,
              callback
          );
          if (chunkSummaryPostProcessing) {
              summary = chunkSummaryPostProcessing(summary);
          }
          summaries.push(summary);
          this.stepEnd(`Summary of ${docName} - Processing chunk: ${i + 1}/${chunks.length}`);
      }
      return summaries.join("\n");
  }
}

async sequentialChunksSummary({
  chunks,
  summaryInstruction = "summarize",
  docName = "chunk",
  answerStart = "",
  maxGenerationSize = 3000,
  callback = null,
  chunkSummaryPostProcessing = null
}) {
  let summaries = [];

  for (let i = 0; i < chunks.length; i++) {
      let chunk1 = i < chunks.length - 1 ? chunks[i + 1] : "";
      let chunk = i > 0 ? summaries[summaries.length - 1] : chunks[i];

      this.stepStart(`Summary of ${docName} - Processing chunk: ${i + 1}/${chunks.length}`);
      let summary = `${answerStart}` + await this.fastGen(
          [
              `${this.lollms.system_message()}Document_chunk: ${docName}${this.lollms.system_message()}`,
              "Block1:",
              `${chunk}`,
              "Block2:",
              `${chunk1}`,
              `${this.lollms.system_message()}${summaryInstruction}`,
              "Answer directly with the summary with no extra comments.",
              `${this.lollms.system_message()}summary${this.lollms.system_message()}`,
              `${answerStart}`
          ].join("\n"),
          maxGenerationSize,
          callback
      );
      if (chunkSummaryPostProcessing) {
          summary = chunkSummaryPostProcessing(summary);
      }
      summaries.push(summary);
      this.stepEnd(`Summary of ${docName} - Processing chunk: ${i + 1}/${chunks.length}`);
  }
  return summaries.join("\n");
}

// Placeholder methods for step stepStart, stepEnd, fastGen
step(message) {
  console.log(message);
}

stepStart(message) {
  console.log(message);
}

stepEnd(message) {
  console.log(message);
}

async fastGen(prompt, maxGenerationSize, callback) {
  // Use the LollmsClient to generate text
  const response = await this.lollms.generateText(prompt);
  if (callback) callback(response);
  return response;
}

async yesNo(question, context = "", maxAnswerLength = 50, conditioning = "") {
  /**
   * Analyzes the user prompt and answers whether it is asking to generate an image.
   *
   * @param {string} question - The user's message.
   * @param {string} context - The context for the question.
   * @param {number} maxAnswerLength - The maximum length of the generated answer.
   * @param {string} conditioning - An optional system message to put at the beginning of the prompt.
   * @returns {boolean} True if the user prompt is asking to generate an image, False otherwise.
   */
  return this.multichoiceQuestion(question, ["no", "yes"], context, maxAnswerLength, conditioning) > 0;
}

printPrompt(prompt){
  console.log(prompt);

}

async multichoiceQuestion(question, possibleAnswers, context = "", maxAnswerLength = 50, conditioning = "") {
  /**
   * Interprets a multi-choice question from a user's response. This function expects only one choice as true. 
   * All other choices are considered false. If none are correct, returns -1.
   *
   * @param {string} question - The multi-choice question posed by the user.
   * @param {Array} possibleAnswers - A list containing all valid options for the chosen value.
   * @param {string} context - The context for the question.
   * @param {number} maxAnswerLength - Maximum string length allowed while interpreting the users' responses.
   * @param {string} conditioning - An optional system message to put at the beginning of the prompt.
   * @returns {number} Index of the selected option within the possibleAnswers list. Or -1 if there was no match found among any of them.
   */

  const choices = possibleAnswers.map((answer, index) => `${index}. ${answer}`).join("\n");
  const elements = conditioning ? [conditioning] : [];
  elements.push(
      this.lollms.system_message(),
      "Answer this multi choices question.",
      "Answer with an id from the possible answers.",
      "Do not answer with an id outside this possible answers."
  );

  if (context) {
      elements.push(
          this.lollms.custom_message("context"),
          context
      );
  }

  elements.push(
      this.lollms.custom_message(`question`)+`$${question}`,
      this.lollms.custom_message(`possible answers`),
      choices,
      this.lollms.custom_message("answer")
  );

  const prompt = this.buildPrompt(elements);
  let gen = await this.lollms.generate(prompt, {
      n_predict: maxAnswerLength,
      temperature: 0.1,
      top_k: 50,
      top_p: 0.9,
      repeat_penalty: 1.0,
      repeat_last_n: 50,
      callback: this.sink
  })
  gen = gen.trim().replace("", "").replace("", "");

  const selection = gen.trim().split(" ")[0].replace(",", "").replace(".", "");
  this.printPrompt("Multi choice selection", prompt + gen);

  try {
      return parseInt(selection, 10);
  } catch (error) {
      console.log("Model failed to answer the question");
      return -1;
  }
}

buildPrompt(promptParts, sacrificeId = -1, contextSize = null, minimumSpareContextSize = null) {
  /**
   * Builds the prompt for code generation.
   *
   * @param {Array<string>} promptParts - A list of strings representing the parts of the prompt.
   * @param {number} sacrificeId - The ID of the part to sacrifice.
   * @param {number} contextSize - The size of the context.
   * @param {number} minimumSpareContextSize - The minimum spare context size.
   * @returns {string} - The built prompt.
   */
  if (contextSize === null) {
      contextSize = this.lollms.ctxSize;
  }
  if (minimumSpareContextSize === null) {
      minimumSpareContextSize = this.lollms.minNPredict;
  }

  if (sacrificeId === -1 || promptParts[sacrificeId].length < 50) {
      return promptParts.filter(s => s !== "").join("\n");
  } else {
      const partTokens = [];
      let nbTokens = 0;

      for (let i = 0; i < promptParts.length; i++) {
          const part = promptParts[i];
          const tk = this.lollms.tokenize(part);
          partTokens.push(tk);
          if (i !== sacrificeId) {
              nbTokens += tk.length;
          }
      }

      let sacrificeText = "";
      if (partTokens[sacrificeId].length > 0) {
          const sacrificeTk = partTokens[sacrificeId];
          const tokensToKeep = sacrificeTk.slice(-(contextSize - nbTokens - minimumSpareContextSize));
          sacrificeText = this.lollms.detokenize(tokensToKeep);
      }

      promptParts[sacrificeId] = sacrificeText;
      return promptParts.filter(s => s !== "").join("\n");
  }
}

/**
 * Updates the given code based on the provided query string.
 * The query string can contain two types of modifications:
 * 1. FULL_REWRITE: Completely replaces the original code with the new code.
 * 2. REPLACE: Replaces specific code snippets within the original code.
 *
 * @param {string} originalCode - The original code to be updated.
 * @param {string} queryString - The string containing the update instructions.
 * @returns {object} - An object with the following properties:
 *   - updatedCode: The updated code.
 *   - modifications: An array of objects representing the changes made, each with properties 'oldCode' and 'newCode'.
 *   - hasQuery: A boolean indicating whether the queryString contained any valid queries.
 */
updateCode(originalCode, queryString) {
  const queries = queryString.split('# REPLACE\n');
  let updatedCode = originalCode;
  const modifications = [];

  // Check if there's a FULL_REWRITE first
  const fullRewriteStart = queryString.indexOf('# FULL_REWRITE');
  if (fullRewriteStart !== -1) {
    const newCode = queryString.slice(fullRewriteStart + 14).trim();
    updatedCode = newCode;
    modifications.push({
      oldCode: originalCode,
      newCode
    });
    return {
      updatedCode,
      modifications,
      hasQuery: true
    };
  }

  if (queries.length === 1 && queries[0].trim() === '') {
    console.log("No queries detected");
    return {
      updatedCode,
      modifications: [],
      hasQuery: false
    };
  }

  for (const query of queries) {
    if (query.trim() === '') continue;

    const originalCodeStart = query.indexOf('# ORIGINAL\n') + 11;
    const originalCodeEnd = query.indexOf('\n# SET\n');
    let oldCode = query.slice(originalCodeStart, originalCodeEnd);

    const newCodeStart = query.indexOf('# SET\n') + 6;
    const newCode = query.slice(newCodeStart);

    const modification = {
      oldCode: oldCode.trim(),
      newCode: newCode.trim()
    };
    if(oldCode =="<old_code>"){
      oldCode = originalCode
    }
    console.log("oldCode:")
    console.log(oldCode)
    console.log("newCode:")
    console.log(newCode)
    console.log("Before update", updatedCode);
    if(oldCode===updatedCode){
      console.log("Changing the whole content")
      updatedCode = newCode
    }
    else{
      updatedCode = updatedCode.replace(oldCode, newCode.trim());
    }
    console.log("After update", updatedCode);
    modifications.push(modification);

  }

  return {
    updatedCode,
    modifications,
    hasQuery: true
  };
}
}
class LOLLMSRAGClient {
  constructor(lc) {
    this.lc = lc;
    this.key = lc.service_key || this.generateRandomKey();
    console.log("Connecting to server with key:", this.key);
  }

  generateRandomKey() {
    // Generate a random key (UUID v4)
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  async request(endpoint, method = 'GET', body = null) {
    try {
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : null,
      };
      let response ="";
      if (this.lc.host_address!=null){
        response = await fetch(`${this.lc.host_address}${endpoint}`, options);
      }
      else{
        response = await fetch(`${endpoint}`, options);        
      }
      const data = await response.json();

      if (!response.ok) {
        throw new Error(`Error: ${data.detail || response.statusText}`);
      }

      return data;
    } catch (error) {
      console.error("Request failed:", error);
      throw new Error(`Error: ${error.message}`);
    }
  }

  async addDocument(title, content, path = "unknown") {
    const document = { title, content, path, key: this.key };
    return this.request('/add_document', 'POST', document);
  }

  async removeDocument(documentId) {
    const body = { key: this.key };
    return this.request(`/remove_document/${documentId}`, 'POST', body);
  }

  async indexDatabase() {
    const body = { key: this.key };
    console.log("Sending request to index database with body:", body);

    try {
        const response = await this.request('/index_database', 'POST', body, {
            'Content-Type': 'application/json'
        });
        console.log("Index database response:", response);
        return response;
    } catch (error) {
        console.error("Error indexing database:", error);
        throw error;
    }
  }
  async search(query) {
    const searchQuery = { query, key: this.key };
    return this.request('/search', 'POST', searchQuery);
  }

  async wipeDatabase() {
    const body = { key: this.key };
    return this.request('/wipe_database', 'DELETE', body);
  }
}


// Example usage:
// const ragClient = new RAGClient('http://localhost:8000', 'your_bearer_token');
// ragClient.addDocument('My Title', 'This is the content of the document.')
//     .then(response => console.log(response))
//     .catch(error => console.error(error));
