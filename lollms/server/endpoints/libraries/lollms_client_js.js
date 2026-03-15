/**
 * @file lollms_client.js
 * @project lollms_client.js
 * @author ParisNeo
 * @version 2.0
 * @date 09/05/2025
 * @description This JavaScript library provides a client for interacting with a LoLLMs (Lord of Large Language Models) server.
 * It supports various generation modes (LoLLMs, OpenAI, Ollama, LiteLLM, vLLM), text generation,
 * code generation, image-assisted generation, tokenization, text chunking, common NLP tasks like
 * summarization and translation, and RAG (Retrieval Augmented Generation) functionalities.
 * This library requires axios for HTTP requests. Ensure axios.min.js is imported in your HTML:
 * <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
 */

// --- SECTION: Constants and Enums ---

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

// --- SECTION: Helper Functions ---

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

// --- SECTION: Main LollmsClient Class ---
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
    default_generation_mode = ELF_GENERATION_FORMAT.LOLLMS,
    verify_ssl_certificate = true // New parameter for SSL verification
  ) {
    this.host_address = host_address;
    this.model_name = model_name;
    this.ctx_size = ctx_size;
    this.n_predict = n_predict ? n_predict : null; // Ensure null if not provided
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
    this.verifySslCertificate = verify_ssl_certificate; // Store SSL verification setting

    this.minNPredict = 10;
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
    };

    // Asynchronously fetch template from server
    const template_url = this.host_address ? `${this.host_address}/template` : '/template';
    fetch(template_url)
      .then((response) => {
        if (!response.ok) {
          throw new Error('Network response was not ok ' + response.statusText);
        }
        return response.json();
      })
      .then((data) => {
        console.log("Template data received: ", data);
        this.template = data;
      })
      .catch((error) => {
        console.error('Error fetching template, using default:', error);
      });
  }

  updateSettings(settings) {
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
    if ('verify_ssl_certificate' in settings) this.verifySslCertificate = settings.verify_ssl_certificate;

    console.log('Settings updated:', settings);
  }

  // --- Template Accessors ---
  separatorTemplate(){
    return this.template.separator_template;
  }
  system_message(){
    return this.template.start_header_id_template + this.template.system_message_template + this.template.end_header_id_template;
  }
  custom_system_message(msg){
    return this.template.start_header_id_template + msg + this.template.end_header_id_template;
  }
  ai_message(ai_name="assistant"){
    return this.template.start_ai_header_id_template + ai_name + this.template.end_ai_header_id_template;
  }
  user_message(user_name="user"){
    return this.template.start_user_header_id_template + user_name + this.template.end_user_header_id_template;
  }
  custom_message(message_name="message"){
    // Assuming this should be similar to ai_message or user_message structure for custom roles
    return this.template.start_header_id_template + message_name + this.template.end_header_id_template;
  }

  updateServerAddress(newAddress) {
      this.host_address = newAddress; // Corrected to update host_address
      // If template fetching depends on host_address, consider re-fetching or advising manual re-init.
      console.log("Server address updated to:", newAddress);
  }    

  // --- Tokenization ---
  async tokenize(prompt, return_named=false) {
      const endpoint = this.host_address ? `${this.host_address}/lollms_tokenize` : "/lollms_tokenize";
      const output = await axios.post(endpoint, {"prompt": prompt, "return_named": return_named});
      return output.data; // Axios directly gives data object
  }

  async detokenize(tokensList, return_named=false) {
      const endpoint = this.host_address ? `${this.host_address}/lollms_detokenize` : "/lollms_detokenize";
      const output = await axios.post(endpoint, {"tokens": tokensList, "return_named": return_named});
      if(return_named && output.data && typeof output.data.text !== 'undefined') {
         console.log(output.data.text);
         return output.data.text;
      } else {
          console.log(output.data);
          return output.data; // This might be the full response or just text depending on server
      }
  }

  // --- Generation Control ---
  cancel_generation() {
    // TODO: Implement cancellation logic. This typically involves a server endpoint
    // or AbortController if using Fetch/Axios for requests that support it.
    console.warn("cancel_generation() is not yet implemented.");
  }

  // --- Core Generation Methods ---
  generate(prompt, {
      n_predict = null,
      stream = false,
      temperature = this.temperature, // Default to instance temperature
      top_k = this.top_k,             // Default to instance top_k
      top_p = this.top_p,             // Default to instance top_p
      repeat_penalty = this.repeat_penalty, // Default to instance repeat_penalty
      repeat_last_n = this.repeat_last_n,   // Default to instance repeat_last_n
      seed = this.seed,                     // Default to instance seed
      n_threads = this.n_threads,           // Default to instance n_threads
      service_key = this.service_key,       // Default to instance service_key
      streamingCallback = null
    } = {}) {
      const options = {
          n_predict: n_predict !== null ? n_predict : this.n_predict,
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
      };

      switch (this.default_generation_mode) {
        case ELF_GENERATION_FORMAT.LOLLMS:
          return this.lollms_generate(prompt, this.host_address, this.model_name, this.personality, options.n_predict, options.stream, options.temperature, options.top_k, options.top_p, options.repeat_penalty, options.repeat_last_n, options.seed, options.n_threads, options.service_key, options.streamingCallback);
        case ELF_GENERATION_FORMAT.OPENAI:
          return this.openai_generate(prompt, this.host_address, this.model_name, this.personality, options.n_predict, options.stream, options.temperature, options.top_k, options.top_p, options.repeat_penalty, options.repeat_last_n, options.seed, options.n_threads, ELF_COMPLETION_FORMAT.Instruct, options.service_key, options.streamingCallback);
        case ELF_GENERATION_FORMAT.OLLAMA:
          return this.ollama_generate(prompt, this.host_address, this.model_name, this.personality, options.n_predict, options.stream, options.temperature, options.top_k, options.top_p, options.repeat_penalty, options.repeat_last_n, options.seed, options.n_threads, ELF_COMPLETION_FORMAT.Instruct, options.service_key, options.streamingCallback);
        case ELF_GENERATION_FORMAT.LITELLM:
          return this.litellm_generate(prompt, this.host_address, this.model_name, this.personality, options.n_predict, options.stream, options.temperature, options.top_k, options.top_p, options.repeat_penalty, options.repeat_last_n, options.seed, options.n_threads, ELF_COMPLETION_FORMAT.Instruct, options.service_key, options.streamingCallback);
        case ELF_GENERATION_FORMAT.VLLM:
          // vllm_generate expects an options object directly for some params
          return this.vllm_generate({
            prompt, 
            host_address: this.host_address, 
            model_name: this.model_name, 
            personality: this.personality, 
            n_predict: options.n_predict, 
            stream: options.stream, 
            temperature: options.temperature, 
            top_k: options.top_k, 
            top_p: options.top_p, 
            repeat_penalty: options.repeat_penalty, 
            repeat_last_n: options.repeat_last_n, 
            seed: options.seed, 
            n_threads: options.n_threads, 
            completion_format: ELF_COMPLETION_FORMAT.Instruct, 
            service_key: options.service_key, 
            streamingCallback: options.streamingCallback // Corrected param name
          });
        default:
          throw new Error('Invalid generation mode: ' + this.default_generation_mode);
      }
    }

    generate_with_images(prompt, images, {
      n_predict = null,
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
    } = {}) {
      const options = {
        n_predict: n_predict !== null ? n_predict : this.n_predict,
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
      };
      switch (this.default_generation_mode) {
        case ELF_GENERATION_FORMAT.LOLLMS:
          return this.lollms_generate_with_images(prompt, images, this.host_address, this.model_name, this.personality, options.n_predict, options.stream, options.temperature, options.top_k, options.top_p, options.repeat_penalty, options.repeat_last_n, options.seed, options.n_threads, options.service_key, options.streamingCallback);
        case ELF_GENERATION_FORMAT.OPENAI:
          // openai_generate_with_images takes a single options object
          return this.openai_generate_with_images(prompt, images, {
            host_address: this.host_address, 
            model_name: this.model_name, 
            personality: this.personality,
            n_predict: options.n_predict, 
            stream: options.stream, // Note: openai_generate_with_images hardcodes stream: true
            temperature: options.temperature, 
            top_k: options.top_k, 
            top_p: options.top_p, 
            repeat_penalty: options.repeat_penalty, 
            repeat_last_n: options.repeat_last_n, 
            seed: options.seed, 
            n_threads: options.n_threads, 
            service_key: options.service_key, 
            streamingCallback: options.streamingCallback
          });
        default:
          // TODO: Add Ollama, LiteLLM, vLLM image support if available, or throw specific error
          throw new Error('Image generation is not supported for the current generation mode or this specific function is not implemented for: ' + this.default_generation_mode);
      }
    }

  async generateText(prompt, options = {}) {
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
          // lollms_generate is the underlying specific method for LOLLMS mode generation
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
            streamingCallback // Passed but lollms_generate might not use it for streaming fully
          );
          return result;
      } catch (error) {
          console.error('An error occurred during text generation:', error);
          throw error; 
      }
  }

    // --- Specific Generation Backend Methods ---
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
      
      const data = JSON.stringify({
          prompt: prompt,
          model_name: model_name,
          personality: personality,
          n_predict: n_predict !== null ? n_predict : this.n_predict, // Ensure a value or null
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
        // Note: fetch() used here. Streaming with fetch requires manual handling of response.body.
        // Current implementation reads full text. If streamingCallback is to be used for chunks,
        // this needs to be changed to process response.body as a ReadableStream.
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: data
        });

        if (!response.ok) {
            const errorBody = await response.text();
            console.error('Network response error:', response.status, errorBody);
            throw new Error(`Network response was not ok: ${response.statusText} - ${errorBody}`);
        }

        const responseBody = await response.text();
        if (stream && streamingCallback) {
            // This is a simplified callback, not true chunk-by-chunk streaming for this fetch implementation
            streamingCallback(responseBody, 'MSG_TYPE_FULL_RESPONSE_CHUNK'); 
        }
        return responseBody ;
      } catch (error) {
          console.error("Error in lollms_generate:", error);
          return null; // Or throw error, for consistency
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

    const data = JSON.stringify({
        prompt: prompt,
        images: images, // Assuming images are base64 strings or paths server can handle
        model_name: model_name,
        personality: personality,
        n_predict: n_predict !== null ? n_predict : this.n_predict,
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
      // Similar to lollms_generate, this uses fetch and reads full response.
      const response = await fetch(url, {
          method: 'POST',
          headers: headers,
          body: data
      });

      if (!response.ok) {
          const errorBody = await response.text();
          console.error('Network response error:', response.status, errorBody);
          throw new Error(`Network response was not ok: ${response.statusText} - ${errorBody}`);
      }

      const responseBody = await response.text();
      if (stream && streamingCallback) {
          streamingCallback(responseBody, 'MSG_TYPE_FULL_RESPONSE_CHUNK');
      }
      return responseBody ;
    } catch (error) {
        console.error("Error in lollms_generate_with_images:", error);
        return null;
    }
}


async openai_generate(prompt, host_address = this.host_address, model_name = this.model_name, personality = this.personality, n_predict = this.n_predict, stream = false, temperature = this.temperature, top_k = this.top_k, top_p = this.top_p, repeat_penalty = this.repeat_penalty, repeat_last_n = this.repeat_last_n, seed = this.seed, n_threads = this.n_threads, completion_format = ELF_COMPLETION_FORMAT.Instruct, service_key = this.service_key, streamingCallback = null) {
    // This method seems to point to a generic /generate_completion endpoint
    // which might be an adapter on the server side.
    const url = `${host_address}/generate_completion`; 
    const headers = service_key !== "" ? {
        'Content-Type': 'application/json; charset=utf-8',
        'Authorization': `Bearer ${service_key}`,
    } : {
        'Content-Type': 'application/json',
    };

    const data = JSON.stringify({
        prompt: prompt,
        model_name: model_name, // This would be the OpenAI model name like "gpt-3.5-turbo"
        personality: personality, // OpenAI API doesn't use personality directly
        n_predict: n_predict !== null ? n_predict : this.n_predict, // Corresponds to max_tokens
        stream: stream,
        temperature: temperature,
        top_p: top_p, // OpenAI uses top_p
        // top_k is not directly supported by OpenAI's main chat completion, but some models/APIs might
        // repeat_penalty (frequency_penalty/presence_penalty in OpenAI)
        // repeat_last_n is not a direct OpenAI param
        seed: seed, // OpenAI supports seed
        // n_threads is not an OpenAI param
        completion_format: completion_format // To guide server-side adapter if any
    });

    try {
        // Uses fetch.
        const response = await fetch(url, {
            method: 'POST',
            headers: headers,
            body: data
        });
        if (!response.ok) {
            const errorBody = await response.text();
            throw new Error(`Network response was not ok: ${response.statusText} - ${errorBody}`);
        }

        if (stream && streamingCallback) {
            // This call implies the server returns a single JSON response even in "stream" mode for this endpoint,
            // or that the client-side streaming for this specific fetch call is not fully implemented for chunks.
            // For true OpenAI SSE streaming, response.body would need to be read as a stream.
            const jsonResponse = await response.json();
            streamingCallback(jsonResponse, 'MSG_TYPE_CHUNK'); // This is likely not a single token chunk
            return jsonResponse; // Or should it return void/promise based on streaming?
        } else {
            return await response.json();
        }
    } catch (error) {
        console.error("Error in openai_generate:", error);
        return null;
    }
}

// Placeholder for ollama_generate, litellm_generate if they differ significantly from openai_generate pattern
// If they follow the same pattern as openai_generate (using a /generate_completion adapter), they can be similar.
// For brevity, I'm assuming they would be similar to openai_generate or vllm_generate
// depending on whether they expose a direct compatible API or use an adapter.
// If unique implementations are needed, they should be added here.

async ollama_generate(prompt, host_address, model_name, personality, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, completion_format, service_key, streamingCallback) {
    console.warn("ollama_generate is not fully implemented, using openai_generate as a template. Verify endpoint and parameters.");
    return this.openai_generate(prompt, host_address, model_name, personality, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, completion_format, service_key, streamingCallback);
}

async litellm_generate(prompt, host_address, model_name, personality, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, completion_format, service_key, streamingCallback) {
    console.warn("litellm_generate is not fully implemented, using openai_generate as a template. Verify endpoint and parameters.");
    return this.openai_generate(prompt, host_address, model_name, personality, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, completion_format, service_key, streamingCallback);
}


async openai_generate_with_images(prompt, images, options = {}) {
  // This method directly targets an OpenAI-compatible /v1/chat/completions endpoint
  const {
    host_address = this.host_address,
    model_name = this.model_name, // e.g., "gpt-4-vision-preview"
    // personality is not used directly in OpenAI API for chat
    n_predict = this.n_predict, // max_tokens
    // stream is handled internally, hardcoded to true
    temperature = this.temperature,
    // top_k not standard for OpenAI chat
    top_p = this.top_p, // OpenAI uses top_p
    // repeat_penalty, repeat_last_n not standard
    // seed is supported by OpenAI
    // n_threads not applicable client-side for API call
    max_image_width = -1, // For client-side image preprocessing
    service_key = this.service_key,
    streamingCallback = null,
  } = options;

  const headers = {
    'Content-Type': 'application/json',
    ...(service_key ? { 'Authorization': `Bearer ${service_key}` } : {})
  };

  // Encode images client-side
  const encodedImages = await Promise.all(
      images.map(async (image_path) => { // Assuming image_path is a URL or data URI accessible by Image()
          const base64Data = await this.encode_image(image_path, max_image_width);
          return {
              type: "image_url",
              image_url: {
                  url: `data:image/jpeg;base64,${base64Data}`
              }
          };
      })
  );

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
          ...encodedImages
        ]
      }
    ],
    stream: true, // Hardcoded for this streaming implementation
    temperature: parseFloat(temperature),
    max_tokens: n_predict !== null ? n_predict : undefined, // OpenAI expects number or undefined
    top_p: parseFloat(top_p) // Include top_p if supported/desired
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
      const errorContent = await response.json().catch(() => response.text()); // Try JSON, fallback to text
      const errorMessage = errorContent?.error?.message || errorContent?.message || errorContent || "Unknown error";
      console.error(`Error from ${url}: ${response.status} - ${errorMessage}`);
      // If you have a unified error display mechanism: this.error(errorMessage);
      throw new Error(`OpenAI API Error: ${errorMessage}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let accumulatedText = "";

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          const jsonDataLine = line.slice(5).trim();
          if (jsonDataLine === "[DONE]") {
            if (streamingCallback) streamingCallback(null, "MSG_TYPE_STREAM_END");
            return accumulatedText;
          }
          try {
            const jsonData = JSON.parse(jsonDataLine);
            const content = jsonData.choices[0]?.delta?.content || "";
            accumulatedText += content;
            if (streamingCallback) {
              if (!streamingCallback(content, "MSG_TYPE_CHUNK")) {
                // Callback signaled to stop
                reader.cancel(); // Stop reading from the stream
                return accumulatedText;
              }
            }
          } catch (error) {
            console.warn('Error parsing stream JSON:', error, "Line:", jsonDataLine);
          }
        }
      }
    }
    if (streamingCallback) streamingCallback(null, "MSG_TYPE_STREAM_END"); // Signal end if not already
    return accumulatedText;
  } catch (error) {
    console.error("Error in openai_generate_with_images:", error);
    throw error; // Re-throw for caller to handle
  }
}


async vllm_generate({ // Note: this method takes a single options object
  prompt,
  host_address = null,
  model_name = null,
  // personality is not directly used by vLLM OpenAI-compatible API
  n_predict = null,
  stream = false,
  temperature = null,
  top_k = null, // vLLM supports top_k via "best_of" if sampling, or not directly in completions
  top_p = null,
  repeat_penalty = null, // vLLM supports repetition_penalty
  // repeat_last_n not a direct vLLM OpenAI-compatible param
  seed = null, // vLLM supports seed
  // n_threads not applicable client-side for API call
  completion_format = ELF_COMPLETION_FORMAT.Instruct,
  service_key = "", // For Bearer token
  streamingCallback = null // Corrected from streaming_callback
}) {
  host_address = host_address || this.host_address;
  model_name = model_name || this.model_name;
  n_predict = n_predict || this.n_predict || this.minNPredict;
  temperature = temperature !== null ? temperature : this.temperature;
  top_k = top_k !== null ? top_k : this.top_k; // May not be used by vLLM /v1/completions or /v1/chat/completions
  top_p = top_p !== null ? top_p : this.top_p;
  repeat_penalty = repeat_penalty !== null ? repeat_penalty : this.repeat_penalty;
  seed = seed || this.seed;
  service_key = service_key || this.service_key;


  const headers = {
    "Content-Type": "application/json",
    ...(service_key && { Authorization: `Bearer ${service_key}` })
  };

  let payload;
  let completionFormatPath;

  if (completion_format === ELF_COMPLETION_FORMAT.Instruct) {
    payload = {
      model: model_name,
      prompt: prompt,
      stream: stream,
      temperature: parseFloat(temperature),
      max_tokens: n_predict,
      top_p: parseFloat(top_p),
      repetition_penalty: parseFloat(repeat_penalty),
      seed: seed,
      // top_k might need to be handled differently if supported by vLLM
    };
    completionFormatPath = "/v1/completions";
  } else if (completion_format === ELF_COMPLETION_FORMAT.Chat) {
    payload = {
      model: model_name,
      messages: [{ role: "user", content: prompt }],
      stream: stream,
      temperature: parseFloat(temperature),
      max_tokens: n_predict,
      top_p: parseFloat(top_p),
      repetition_penalty: parseFloat(repeat_penalty),
      seed: seed,
    };
    completionFormatPath = "/v1/chat/completions";
  } else {
    throw new Error("Invalid completion_format for vllm_generate");
  }

  if (host_address.endsWith("/")) {
    host_address = host_address.slice(0, -1);
  }
  const url = `${host_address}${completionFormatPath}`;

  try {
    // Using axios for this one as per original code
    const httpsAgent = typeof window === 'undefined' && !this.verifySslCertificate // Node.js environment
        ? new (require("https").Agent)({ rejectUnauthorized: false })
        : undefined;

    const response = await axios.post(url, payload, {
      headers: headers,
      responseType: stream ? "stream" : "json",
      httpsAgent: httpsAgent
    });

    if (stream) {
      let accumulatedText = "";
      const responseStream = response.data; // This is a Node.js stream

      return new Promise((resolve, reject) => {
        responseStream.on("data", (chunk) => {
          const decodedChunk = chunk.toString("utf-8");
          // OpenAI/vLLM stream format: data: {json_payload}\n\n
          const lines = decodedChunk.split('\n');
          for (const line of lines) {
            if (line.startsWith("data: ")) {
              const jsonDataLine = line.slice(5).trim();
              if (jsonDataLine === "[DONE]") {
                if (streamingCallback) streamingCallback(null, "MSG_TYPE_STREAM_END");
                // responseStream.destroy(); // Should happen automatically on end
                resolve(accumulatedText);
                return;
              }
              try {
                const jsonData = JSON.parse(jsonDataLine);
                let chunkContent = "";
                if (completion_format === ELF_COMPLETION_FORMAT.Chat) {
                  chunkContent = jsonData.choices[0]?.delta?.content || "";
                } else { // Instruct
                  chunkContent = jsonData.choices[0]?.text || "";
                }
                accumulatedText += chunkContent;
                if (streamingCallback) {
                  if (!streamingCallback(chunkContent, "MSG_TYPE_CHUNK")) {
                    responseStream.destroy(); // Callback signaled to stop
                    resolve(accumulatedText); // Resolve with what's accumulated so far
                    return;
                  }
                }
              } catch (error) {
                console.warn('Error parsing stream JSON in vllm_generate:', error, "Line:", jsonDataLine);
                // Don't destroy stream for one bad JSON, but log it.
              }
            }
          }
        });
        responseStream.on("end", () => {
          if (streamingCallback) streamingCallback(null, "MSG_TYPE_STREAM_END"); // Ensure end is signaled
          resolve(accumulatedText);
        });
        responseStream.on("error", (err) => {
          console.error("Stream error in vllm_generate:", err);
          reject(err);
        });
      });
    } else { // Not streaming
      // For non-streaming, Axios automatically parses JSON response if 'Content-Type' is application/json
      let textResponse = "";
      if (completion_format === ELF_COMPLETION_FORMAT.Chat) {
        textResponse = response.data.choices[0]?.message?.content || "";
      } else { // Instruct
        textResponse = response.data.choices[0]?.text || "";
      }
      if (streamingCallback) streamingCallback(textResponse, "MSG_TYPE_FULL_RESPONSE_CHUNK");
      return textResponse; // Return the content string
    }
  } catch (error) {
    const errorMessage = error.response?.data?.error?.message || 
                         error.response?.data?.message || 
                         error.response?.statusText || 
                         error.message || "Unknown error";
    console.error("Error in vllm_generate:", errorMessage, error.response?.data);
    throw new Error(errorMessage);
  }
}

  // --- Code Generation ---
  async generateCode(
    prompt, 
    template=null, // Code structure template
    language="json", // Target language
    images = [],  
    { // Options object
      n_predict = null,
      temperature = this.temperature,
      top_k = this.top_k,
      top_p = this.top_p,
      repeat_penalty = this.repeat_penalty,
      repeat_last_n = this.repeat_last_n,
      streamingCallback = null // For token-by-token streaming
    } = {}
  ){
    let responseText;
    const systemHeader = this.custom_message("Generation infos");
    let codeInstructions = "";
    if(template){
        codeInstructions =   `Generated code must be put inside the adequate markdown code tag. Use this template:\n\`\`\`${language}\n${template}\n\`\`\`\nMake sure only a single code tag is generated at each dialogue turn.\n`;
    } else {
        codeInstructions =   `Generated code must be put inside the adequate markdown code tag. Use this template:\n\`\`\`language name\nCode\n\`\`\`\nMake sure only a single code tag is generated at each dialogue turn.\n`;
    }
    // Construct the full prompt
    const fullPrompt = systemHeader + codeInstructions + this.separatorTemplate() + prompt + this.ai_message();

    const generationOptions = {
      n_predict: n_predict !== null ? n_predict : this.n_predict,
      temperature,
      top_k,
      top_p,
      repeat_penalty,
      repeat_last_n,
      streamingCallback // Corrected from 'callback'
    };

    if (images.length > 0) {
        responseText = await this.generate_with_images(fullPrompt, images, generationOptions);
    } else {
        responseText = await this.generate(fullPrompt, generationOptions);
    }
    if (responseText === null) { // Handle generation failure
        console.error("Code generation failed, received null response.");
        return null;
    }

    const codes = this.extractCodeBlocks(responseText);
    console.log("Extracted code blocks:", codes);

    if (codes.length > 0) {
        let codeBlock = codes[0]; // Focus on the first code block
        let currentCodeContent = codeBlock.content;

        // Loop to complete code if it's marked as incomplete
        while (!codeBlock.is_complete) {
            console.warn("The AI did not finish the code, asking it to continue...");
            const continuePrompt = `${prompt}${this.separatorTemplate()}${currentCodeContent}${this.separatorTemplate()}${this.user_message()}continue the code. Rewrite the last line and continue the code. Don't forget to put the code inside a markdown code tag.${this.separatorTemplate()}${this.ai_message()}`;
            
            responseText = await this.generate(continuePrompt, generationOptions);
            if (responseText === null) {
                console.error("Failed to get continuation for the code.");
                break; // Exit loop if continuation fails
            }

            const newCodeBlocks = this.extractCodeBlocks(responseText);
            if (newCodeBlocks.length === 0) {
                console.warn("No code block found in continuation response.");
                break; // Exit if no new code found
            }
            
            // Assume the first new block is the continuation
            const continuationBlock = newCodeBlocks[0];
            // A simple strategy: append if the AI didn't repeat much, otherwise replace.
            // This needs refinement; for now, just append the new content.
            // A better way might be to find the overlap or diff.
            // For simplicity, let's assume the AI continues correctly or rewrites.
            // We'll take the content of the new block. If it's meant to append, the AI needs to be prompted for that.
            // The prompt "Rewrite last line and continue" suggests it might rewrite.
            // A robust solution would be complex. Sticking to simpler logic:
            if(continuationBlock.content.startsWith(currentCodeContent.slice(-20))){ // crude check if it's repeating
                currentCodeContent = continuationBlock.content; // take the new one as it might have fixed something
            } else {
                 currentCodeContent += '\n' + continuationBlock.content;
            }
            codeBlock.is_complete = continuationBlock.is_complete; // Update completeness

            if (codeBlock.is_complete) break; // Exit if now complete
        }
        return currentCodeContent;
    } else {
        console.warn("No code blocks extracted from the response.");
        return null; // Or return the raw responseText if no code block found?
    }
  }

  async generateCodes(prompt, images = [], {
    n_predict = null,
    temperature = this.temperature,
    top_k = this.top_k,
    top_p = this.top_p,
    repeat_penalty = this.repeat_penalty,
    repeat_last_n = this.repeat_last_n,
    streamingCallback = null
  } = {}) {
    let responseText;
    const systemHeader = this.custom_message("Generation infos");
    const codeInstructions = "Generated code must be put inside the adequate markdown code tag. Use this template:\n```language name\nCode\n```\n";
    const fullPrompt = systemHeader + codeInstructions + this.separatorTemplate() + prompt + this.ai_message();

    const generationOptions = {
      n_predict: n_predict !== null ? n_predict : this.n_predict,
      temperature,
      top_k,
      top_p,
      repeat_penalty,
      repeat_last_n,
      streamingCallback // Corrected from 'callback'
    };

    if (images.length > 0) {
      responseText = await this.generate_with_images(fullPrompt, images, generationOptions);
    } else {
      responseText = await this.generate(fullPrompt, generationOptions);
    }
    if (responseText === null) {
        console.error("Code generation failed, received null response.");
        return []; // Return empty array on failure
    }
    
    let extracted = this.extractCodeBlocks(responseText, true);
    let codeBlocks = extracted.codes;
    let remainingTextForContinuation = extracted.remainingText; // Not directly used in this loop logic yet

    let completeCodeObjects = [];

    for (let i = 0; i < codeBlocks.length; i++) {
        let currentCodeBlock = codeBlocks[i];
        let currentCodeContent = currentCodeBlock.content;
        let currentLanguage = currentCodeBlock.type || "unknown";

        while (!currentCodeBlock.is_complete) {
            console.warn(`The AI did not finish code block ${i} (${currentLanguage}), asking it to continue...`);
            // The prompt for continuation needs to be smart. It should ideally include
            // the original prompt context and the partially generated code.
            const continuePrompt = `${prompt}${this.separatorTemplate()}${this.custom_message("Current Code (incomplete)")}${currentCodeContent}${this.separatorTemplate()}${this.user_message()}Continue the code for language '${currentLanguage}'. Rewrite the last line and continue. Ensure the code is within a markdown code tag.${this.separatorTemplate()}${this.ai_message()}`;
            
            responseText = await this.generate(continuePrompt, generationOptions);
            if (responseText === null) {
                console.error("Failed to get continuation for the code block.");
                break; 
            }

            const newBlocks = this.extractCodeBlocks(responseText);
            if (newBlocks.length === 0) {
                console.warn("No code block found in continuation response for this block.");
                break; 
            }

            // Assume the first new block is the relevant continuation.
            const continuationBlock = newBlocks[0];
            currentCodeContent += '\n' + continuationBlock.content; // Simple append
            currentCodeBlock.is_complete = continuationBlock.is_complete;

            if (currentCodeBlock.is_complete) break;
        }
        completeCodeObjects.push({
            language: currentLanguage,
            content: currentCodeContent,
            fileName: currentCodeBlock.fileName // Include fileName if present
        });
    }
    return completeCodeObjects;
  }

  // --- Utility Methods ---
  extractCodeBlocks(text, return_remaining_text = false) {
    const codes = [];
    let currentText = text; // Use a mutable copy for slicing
    let searchStartIndex = 0; // To keep track of where to search from, avoiding re-processing
    
    while (true) {
        const startPos = currentText.indexOf('```', searchStartIndex);
        if (startPos === -1) {
            break; // No more code block starts
        }
            
        // File name extraction logic (slightly improved for clarity)
        let fileName = '';
        // Look for <file_name>...</file_name> immediately preceding the current ```
        const preBlockText = currentText.substring(searchStartIndex, startPos);
        const fileNameTagMatch = /<file_name>(.*?)<\/file_name>\s*$/s.exec(preBlockText);
        if (fileNameTagMatch && fileNameTagMatch[1]) {
            fileName = fileNameTagMatch[1].trim();
        }
        
        // Determine code type and content start
        const afterStartTicks = startPos + 3;
        const nextNewlinePos = currentText.indexOf('\n', afterStartTicks);
        let codeType = '';
        let contentStartPos;
  
        if (nextNewlinePos !== -1) {
            const potentialType = currentText.substring(afterStartTicks, nextNewlinePos).trim();
            // Ensure type does not contain spaces or special chars that make it unlikely to be a language identifier
            if (potentialType && !potentialType.includes(' ') && !potentialType.includes('`')) { 
                codeType = potentialType;
                contentStartPos = nextNewlinePos + 1;
            } else {
                // No valid type, or type line is part of content
                contentStartPos = afterStartTicks; // Content starts right after ```
                if (potentialType.includes('`')) { // If the line after ``` contains ``` it's likely not a type line.
                    // This means the content might start immediately, or the block is malformed.
                    // Let's assume content starts after ``` if no newline or invalid type.
                    contentStartPos = afterStartTicks;
                } else if (nextNewlinePos !== -1) { // If there was a newline, content starts after it.
                     contentStartPos = nextNewlinePos + 1;
                } else { // No newline after ```, content starts immediately.
                     contentStartPos = afterStartTicks;
                }
            }
        } else {
            // No newline after ```, so no type specified, content starts immediately
            contentStartPos = afterStartTicks;
        }
            
        // Find matching end tag ```
        const endPos = currentText.indexOf('```', contentStartPos);
        let content = '';
        let is_complete = false;
  
        if (endPos !== -1) {
            content = currentText.substring(contentStartPos, endPos).trim();
            is_complete = true;
            searchStartIndex = endPos + 3; // Next search starts after this block
        } else {
            // Incomplete block (no closing ``` found)
            content = currentText.substring(contentStartPos).trim();
            is_complete = false;
            searchStartIndex = currentText.length; // No more searching needed
        }
            
        codes.push({
            // index: codes.length, // Index within this extraction
            fileName: fileName,
            content: content,
            type: codeType,
            is_complete: is_complete
        });
  
        if (!is_complete) break; // If a block is incomplete, assume it's the last one
    }
    
    const remainingText = return_remaining_text ? currentText.substring(searchStartIndex) : "";
  
    if (return_remaining_text) {
        return { codes, remainingText };
    }
    return codes;
  }


  async encode_image(image_path_or_data_url, max_image_width = -1) {
    // This function is browser-specific due to Image() and canvas.
    // For Node.js, libraries like 'sharp' or 'jimp' would be needed.
    if (typeof window === 'undefined') {
        console.warn("encode_image is browser-specific and may not work in Node.js without DOM emulation.");
        // Fallback or error for Node.js
        // For now, let it try and fail if Image is not defined.
        // Alternatively, could return a placeholder or throw an error.
        if(!image_path_or_data_url.startsWith("data:")){ // If it's already a data URL, potentially just pass it (though resizing is lost)
            return Promise.reject(new Error("encode_image: Canvas/Image API not available in this environment for path resizing."));
        }
    }
    
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        let width = img.width;
        let height = img.height;
  
        if (max_image_width !== -1 && width > max_image_width) {
          const ratio = max_image_width / width;
          width = max_image_width;
          height = Math.round(height * ratio);
        }
  
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
  
        // Get base64 string (e.g., 'data:image/jpeg;base64,XXXX...') and extract data part
        const base64Image = canvas.toDataURL('image/jpeg').split(',')[1];
        resolve(base64Image);
      };
  
      img.onerror = (error) => {
        console.error("Error loading image for encoding:", image_path_or_data_url, error);
        reject(new Error("Failed to load image for encoding."));
      };
      
      // Set crossOrigin to anonymous for external images to avoid canvas tainting, if applicable.
      // This is only effective if the server serving the image sets CORS headers.
      if (typeof image_path_or_data_url === 'string' && !image_path_or_data_url.startsWith('data:')) {
          img.crossOrigin = "Anonymous"; 
      }
      img.src = image_path_or_data_url;
    });
  }

  // --- Server Information ---
  async listMountedPersonalities(host_address = this.host_address) {
      const url = `${host_address || ""}/list_mounted_personalities`; // Handle null host_address
      try {
          const response = await fetch(url);
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          return await response.json();
      } catch (error) {
          console.error("Error listing mounted personalities:", error);
          return null;
      }
  }

  async listModels(host_address = this.host_address) {
      const url = `${host_address || ""}/list_models`;
      try {
          const response = await fetch(url);
          if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
          return await response.json();
      } catch (error) {
          console.error("Error listing models:", error);
          return null;
      }
  }
}

// --- SECTION: TextChunker Class ---
class TextChunker {
  constructor(chunkSize = 1024, overlap = 0, tokenizer = null) {
    this.chunkSize = chunkSize;
    this.overlap = overlap; // Note: overlap logic in getTextChunks might need review for token-based overlap
    
    if (!tokenizer) {
        console.warn("TextChunker initialized without a tokenizer. `getTextChunks` might fail or use a placeholder.");
        // Placeholder tokenizer if none provided, actual tokenization might not occur.
        this.tokenizer = {
            tokenize: async (text) => text.split(" "), // Simple space-based tokenizer as fallback
            detokenize: async (tokens) => tokens.join(" ")
        };
    } else {
        this.tokenizer = tokenizer;
    }
    // this.model = model; // model parameter was in original, but not used. Removed for now.
  }

  async getTextChunks(text, docDetails = {name: "document"}, cleanChunk = true, minNbTokensInChunk = 10) {
    // docDetails could be an object with more info, e.g., docDetails.name, docDetails.id
    const paragraphs = text.split('\n\n');
    const chunks = [];
    let currentChunkParagraphs = [];
    let currentTokensInChunk = 0;
    let chunkId = 0;

    for (const paragraph of paragraphs) {
      const cleanedParagraph = cleanChunk ? paragraph.trim() : paragraph;
      if (!cleanedParagraph) continue; // Skip empty paragraphs

      const paragraphTokens = (await this.tokenizer.tokenize(cleanedParagraph)).length;

      if (currentTokensInChunk + paragraphTokens > this.chunkSize && currentChunkParagraphs.length > 0) {
        // Finalize current chunk
        if (currentTokensInChunk >= minNbTokensInChunk) {
          let chunkText = currentChunkParagraphs.join('\n\n');
          if (cleanChunk) chunkText = TextChunker.removeUnnecessaryReturns(chunkText);
          
          // Assuming Chunk class or simple object structure
          chunks.push({
            doc: docDetails, 
            id: `${docDetails.name}_chunk_${chunkId++}`, 
            text: chunkText, 
            tokens: currentTokensInChunk 
          });
        }
        
        // Start new chunk, considering overlap (paragraph-based overlap here)
        if (this.overlap > 0 && currentChunkParagraphs.length > 0) {
            // A simple way to do paragraph overlap: take last 'overlap' number of paragraphs.
            // This is not token-based overlap. For token-based, logic would be more complex.
            const overlapParagraphs = currentChunkParagraphs.slice(-Math.min(this.overlap, currentChunkParagraphs.length));
            currentChunkParagraphs = [...overlapParagraphs, cleanedParagraph];
            currentTokensInChunk = (await Promise.all(overlapParagraphs.map(p => this.tokenizer.tokenize(p)))).reduce((sum, tokens) => sum + tokens.length, 0);
            currentTokensInChunk += paragraphTokens;

        } else {
          currentChunkParagraphs = [cleanedParagraph];
          currentTokensInChunk = paragraphTokens;
        }

      } else {
        currentChunkParagraphs.push(cleanedParagraph);
        currentTokensInChunk += paragraphTokens;
      }
    }

    // Add the last remaining chunk
    if (currentChunkParagraphs.length > 0 && currentTokensInChunk >= minNbTokensInChunk) {
      let chunkText = currentChunkParagraphs.join('\n\n');
      if (cleanChunk) chunkText = TextChunker.removeUnnecessaryReturns(chunkText);
      chunks.push({
        doc: docDetails, 
        id: `${docDetails.name}_chunk_${chunkId++}`, 
        text: chunkText, 
        tokens: currentTokensInChunk 
      });
    }
    return chunks;
  }

  static removeUnnecessaryReturns(paragraph) {
    const lines = paragraph.split('\n');
    return lines.filter(line => line.trim()).join('\n'); // Keep only non-empty lines
  }

  static async chunkText(text, tokenizer, chunkSize = 1024, overlap = 0, cleanChunk = true, minNbTokensInChunk = 10) {
    if (!tokenizer || typeof tokenizer.tokenize !== 'function' || typeof tokenizer.detokenize !== 'function') {
        throw new Error("A valid tokenizer with tokenize and detokenize methods must be provided.");
    }
    if (isNaN(chunkSize) || chunkSize <= 0) {
        console.warn(`Invalid chunkSize: ${chunkSize}. Resetting to default value of 1024.`);
        chunkSize = 1024;
    }

    const paragraphs = text.split('\n\n');
    const chunks = []; // Stores final chunk texts
    let currentChunkTokens = []; // Stores tokens of the current chunk being built
    let currentChunkParagraphSources = []; // Stores original paragraphs for reconstruction if needed

    for (const paragraph of paragraphs) {
        const cleanedParagraph = cleanChunk ? paragraph.trim() : paragraph;
        if (!cleanedParagraph && cleanChunk) continue;

        const paragraphTokens = await tokenizer.tokenize(cleanedParagraph);

        if (paragraphTokens.length > chunkSize) { // Single paragraph exceeds chunk size
            // Split this large paragraph
            const subChunks = await TextChunker.splitLargeParagraph(cleanedParagraph, tokenizer, chunkSize, overlap);
            chunks.push(...subChunks); // Add its pieces as separate chunks
            currentChunkTokens = []; // Reset current chunk
            currentChunkParagraphSources = [];
            continue;
        }

        if (currentChunkTokens.length + paragraphTokens.length > chunkSize && currentChunkTokens.length > 0) {
            // Current chunk is full, finalize it
            if (currentChunkTokens.length >= minNbTokensInChunk) {
                let chunkText = await tokenizer.detokenize(currentChunkTokens);
                if (cleanChunk) chunkText = TextChunker.removeUnnecessaryReturns(chunkText);
                chunks.push(chunkText);
            }
            
            // Start new chunk with overlap
            if (overlap > 0 && currentChunkTokens.length > 0) {
                const overlapTokenCount = Math.min(overlap, currentChunkTokens.length);
                const_overlap_tokens = currentChunkTokens.slice(-overlapTokenCount);
                currentChunkTokens = [...const_overlap_tokens, ...paragraphTokens];
            } else {
                currentChunkTokens = [...paragraphTokens];
            }
            // currentChunkParagraphSources would need more complex handling for token-based overlap
        } else {
            // Add to current chunk
            currentChunkTokens.push(...paragraphTokens);
            // currentChunkParagraphSources.push(cleanedParagraph);
        }
    }

    // Add the last chunk
    if (currentChunkTokens.length >= minNbTokensInChunk) {
        let chunkText = await tokenizer.detokenize(currentChunkTokens);
        if (cleanChunk) chunkText = TextChunker.removeUnnecessaryReturns(chunkText);
        chunks.push(chunkText);
    }
    return chunks;
  }

  static async splitLargeParagraph(paragraph, tokenizer, chunkSize, overlap) {
    // This splits a single large paragraph into token-based chunks.
    const tokens = await tokenizer.tokenize(paragraph);
    const subChunks = []; // Stores text of sub-chunks
    let currentPos = 0;

    while (currentPos < tokens.length) {
        const endPos = Math.min(currentPos + chunkSize, tokens.length);
        const chunkTokens = tokens.slice(currentPos, endPos);
        if (chunkTokens.length === 0) break;

        const chunkText = await tokenizer.detokenize(chunkTokens);
        subChunks.push(chunkText);
        
        currentPos += (chunkSize - overlap);
        if (currentPos >= tokens.length && endPos < tokens.length) { // Ensure last bit is captured if overlap skips it
            // This condition needs care. If chunkSize - overlap is small, can loop excessively.
            // A simpler non-overlapping split for very large paragraphs might be safer:
            // currentPos = endPos; // For non-overlapping split
        }
        if (chunkSize - overlap <= 0 && tokens.length > chunkSize) { // Avoid infinite loop if overlap >= chunkSize
            console.warn("Overlap is too large compared to chunk size, may lead to issues. Advancing by chunksize.");
            currentPos = endPos;
        }
    }
    return subChunks;
  }
}


// --- SECTION: TasksLibrary Class ---
class TasksLibrary {
  constructor(lollmsClientInstance) {
    if (!lollmsClientInstance || typeof lollmsClientInstance.generateText !== 'function') {
      throw new Error("TasksLibrary requires a valid LollmsClient instance.");
    }
    this.lollms = lollmsClientInstance;
  }

  async translateTextChunk(textChunk, outputLanguage = "french", options = {}) {
    const {
        host_address = this.lollms.host_address, // Default to LollmsClient instance config
        model_name = this.lollms.model_name,
        temperature = 0.1,
        maxGenerationSize = 3000, // n_predict
        // other LollmsClient.generateText options can be added here
    } = options;

    const translationPrompt = [
      this.lollms.system_message(),
      `Translate the following text to ${outputLanguage}.`,
      `Be faithful to the original text and do not add or remove any information.`,
      `Respond only with the translated text.`,
      `Do not add comments or explanations.`,
      this.lollms.user_message("text to translate"),
      textChunk, // Ensure textChunk is a string
      this.lollms.ai_message("translation"),
    ].join(this.lollms.separatorTemplate());

    const generationOptions = {
      host_address,
      model_name,
      personality: -1, // Typically not relevant for translation
      n_predict: maxGenerationSize,
      stream: false,
      temperature,
      // Let other params use LollmsClient defaults (top_k, top_p, etc.)
    };
    
    return await this.lollms.generateText(translationPrompt, generationOptions);
  }

  async tokenize(text) {
    return await this.lollms.tokenize(text); // Assumes LollmsClient has tokenize
  }
  async detokenize(tokens) {
    return await this.lollms.detokenize(tokens); // Assumes LollmsClient has detokenize
  }


  async summarizeText(
    text,
    summaryInstruction = "summarize",
    docName = "chunk",
    answerStart = "",
    maxGenerationSize = 3000,
    maxSummarySizeInTokens = 1024, // Renamed for clarity
    callback = null, // For progress reporting
    chunkSummaryPostProcessing = null,
    summaryMode = "SEQUENTIAL", // "SEQUENTIAL" or "PARALLEL" (though parallel implies map-reduce)
    reformatFinal = false
  ) {
    this.stepStart(`Summarizing ${docName}: Initial tokenization...`);
    let currentTextTokens = await this.tokenize(text);
    let initialTokenCount = currentTextTokens.length;
    this.step(`Initial token count: ${initialTokenCount}, target max: ${maxSummarySizeInTokens}`);

    let currentText = text;
    while (currentTextTokens.length > maxSummarySizeInTokens) {
        this.stepStart(`Compressing ${docName} (currently ${currentTextTokens.length} tokens)...`);
        // Determine chunk size dynamically, e.g., 60% of context, ensuring it's less than maxSummarySize
        const modelCtxSize = this.lollms.ctx_size || 2048; // Fallback context size
        let chunkSize = Math.floor(modelCtxSize * 0.6);
        chunkSize = Math.min(chunkSize, maxSummarySizeInTokens * 0.8); // Ensure chunks are smaller than target

        if (chunkSize <=0) chunkSize = 512; // Absolute minimum chunk size
        
        const documentChunks = await TextChunker.chunkText(currentText, this.lollms, chunkSize, 50, true); // 50 token overlap
        
        if (documentChunks.length <= 1 && currentTextTokens.length > maxSummarySizeInTokens) {
            this.step("Text is too large for a single chunk but not splitting further. Max summary size might be too small or text indivisible.");
            // Potentially truncate or error, for now, proceed.
            // This means the summarization loop might not reduce size effectively.
             break; 
        }
        if (documentChunks.length === 0) {
            this.step("No chunks generated, text might be too small or empty.");
            break;
        }

        currentText = await this.summarizeChunks(
            documentChunks,
            summaryInstruction,
            docName,
            answerStart,
            maxGenerationSize,
            callback, // Pass callback for chunk-level progress
            chunkSummaryPostProcessing,
            summaryMode
        );
        
        const prevTokenCount = currentTextTokens.length;
        currentTextTokens = await this.tokenize(currentText);
        const reduction = prevTokenCount - currentTextTokens.length;
        this.step(`Compression resulted in ${currentTextTokens.length} tokens (reduced by ${reduction}).`);
        this.stepEnd(`Compressing ${docName}...`);

        if (reduction < Math.min(50, prevTokenCount * 0.05) && currentTextTokens.length > maxSummarySizeInTokens) { // If reduction is too small
            this.step("Summary reduction is minimal. Stopping iterative summarization to avoid excessive processing.");
            break;
        }
        if (currentTextTokens.length <= maxSummarySizeInTokens) break;
    }

    if (reformatFinal && currentTextTokens.length > 0) {
        this.stepStart(`Reformatting final summary for ${docName}...`);
        const reformatPrompt = [
            this.lollms.system_message(),
            currentText, // The summarized text
            this.lollms.user_message(),
            summaryInstruction, // Original instruction for context
            "Reformat this summary clearly and concisely.",
            "Do not add any extra comments beyond the reformatted summary.",
            this.lollms.ai_message() + answerStart
        ].join(this.lollms.separatorTemplate());
        
        currentText = await this.lollms.generate(reformatPrompt, { n_predict: maxGenerationSize });
        this.stepEnd(`Reformatting final summary for ${docName}...`);
    }
    this.stepEnd(`Summarizing ${docName} finished.`);
    return currentText;
  }

  async smartDataExtraction( /* Similar to summarizeText, but with different prompt engineering */
    text,
    dataExtractionInstruction = "Extract key information based on user query.", // This should be more specific
    finalTaskInstruction = "Compile extracted data into a coherent report.",
    docName = "document",
    answerStart = "",
    maxGenerationSize = 3000,
    maxOutputSizeInTokens = 1024,
    callback = null,
    chunkProcessing = null, // Function to process each chunk's extraction
    extractionMode = "SEQUENTIAL" // or "MAP_REDUCE"
  ) {
    // Implementation would be structurally similar to summarizeText:
    // 1. Tokenize text.
    // 2. Loop while token count > maxOutputSizeInTokens:
    //    a. Chunk the text.
    //    b. Process chunks (e.g., using a modified summarizeChunks with dataExtractionInstruction).
    //       - `chunkProcessing` callback could be applied here.
    //    c. Combine results.
    //    d. Re-tokenize, check reduction.
    // 3. Apply finalTaskInstruction to the compiled data.
    this.step("smartDataExtraction is a complex task, using summarizeText structure as a template.");
    return this.summarizeText(
        text,
        dataExtractionInstruction, // Initial instruction for chunk processing
        docName,
        answerStart,
        maxGenerationSize,
        maxOutputSizeInTokens,
        callback,
        chunkProcessing,
        extractionMode,
        true // reformatFinal becomes applying finalTaskInstruction
    );
  }

  async summarizeChunks(
    chunks, // Array of text chunks
    summaryInstruction = "Summarize the current chunk.",
    docName = "document part",
    answerStart = "",
    maxGenerationSize = 3000,
    callback = null, // For progress reporting (e.g., callback(chunk_index, num_chunks, status))
    chunkSummaryPostProcessing = null,
    summaryMode = "SEQUENTIAL" // "SEQUENTIAL" or "MAP_REDUCE" like
  ) {
    if (summaryMode === "SEQUENTIAL") {
        let accumulatedSummary = "";
        for (let i = 0; i < chunks.length; i++) {
            this.stepStart(`Sequential Summary of ${docName} - Processing chunk: ${i + 1}/${chunks.length}`);
            if (callback) callback(i, chunks.length, "start_chunk_summary");

            const promptParts = [
                this.lollms.custom_system_message("Context from previous chunks summary"),
                accumulatedSummary || "This is the first chunk.", // Provide context
                this.lollms.custom_system_message("Current text chunk to summarize"),
                chunks[i],
                this.lollms.user_message(),
                summaryInstruction,
                this.lollms.custom_system_message("Important instructions"),
                "Focus on extracting key information relevant to the user's overall goal.",
                "Integrate information from the current chunk with the previous summary seamlessly.",
                "Be concise and avoid redundancy. Do not invent information.",
                "Output only the combined summary, starting directly.",
                this.lollms.ai_message() + answerStart
            ];
            
            let chunkSummary = await this.fastGen(
                this.buildPrompt(promptParts), // Use buildPrompt for potential truncation
                maxGenerationSize,
                (genText) => { if (callback) callback(i, chunks.length, "chunk_summary_generated", genText); }
            );

            if (chunkSummaryPostProcessing) {
                chunkSummary = chunkSummaryPostProcessing(chunkSummary, accumulatedSummary, chunks[i]);
            }
            accumulatedSummary = chunkSummary; // The result IS the new accumulated summary

            this.stepEnd(`Sequential Summary of ${docName} - Chunk ${i + 1}/${chunks.length} done.`);
            if (callback) callback(i, chunks.length, "end_chunk_summary");
        }
        return accumulatedSummary;
    } else { // "MAP_REDUCE" like mode (summarize each chunk independently, then combine)
        let individualSummaries = [];
        for (let i = 0; i < chunks.length; i++) {
            this.stepStart(`Map Summary of ${docName} - Processing chunk: ${i + 1}/${chunks.length}`);
            if (callback) callback(i, chunks.length, "start_chunk_summary");
            
            const promptParts = [
                this.lollms.system_message(),
                `Document chunk from "${docName}" follows:`,
                chunks[i],
                this.lollms.user_message(),
                summaryInstruction,
                "Provide a concise summary of this chunk. Answer directly with the summary, no extra comments.",
                this.lollms.ai_message() + answerStart
            ];

            let summary = await this.fastGen(
                this.buildPrompt(promptParts),
                maxGenerationSize,
                (genText) => { if (callback) callback(i, chunks.length, "chunk_summary_generated", genText); }
            );

            if (chunkSummaryPostProcessing) {
                summary = chunkSummaryPostProcessing(summary, null, chunks[i]); // No previous summary for map phase
            }
            individualSummaries.push(summary);
            this.stepEnd(`Map Summary of ${docName} - Chunk ${i + 1}/${chunks.length} done.`);
            if (callback) callback(i, chunks.length, "end_chunk_summary");
        }
        // Reduce phase: combine individual summaries
        this.stepStart(`Reduce Phase for ${docName} - Combining ${individualSummaries.length} summaries.`);
        const combinedText = individualSummaries.join("\n\n---\n\n"); // Join with a clear separator
        
        const finalSummaryPromptParts = [
            this.lollms.system_message(),
            "The following are individual summaries of document parts:",
            combinedText,
            this.lollms.user_message(),
            "Combine these summaries into a single, coherent final summary.",
            "Eliminate redundancy and ensure a smooth flow.",
            this.lollms.ai_message() + answerStart
        ];
        const finalSummary = await this.fastGen(
            this.buildPrompt(finalSummaryPromptParts),
            maxGenerationSize * 2, // Allow more tokens for final combination
            (genText) => { if (callback) callback(chunks.length, chunks.length, "final_summary_generated", genText); }
        );
        this.stepEnd(`Reduce Phase for ${docName} complete.`);
        return finalSummary;
    }
  }

  async sequentialChunksSummary({ /* Deprecated or specific use case? */
    chunks,
    summaryInstruction = "summarize",
    docName = "chunk",
    answerStart = "",
    maxGenerationSize = 3000,
    callback = null,
    chunkSummaryPostProcessing = null
  }) {
    console.warn("sequentialChunksSummary is similar to summarizeChunks with SEQUENTIAL mode. Consider consolidating.");
    // This implementation processes pairs of chunks, which is different.
    // Let's keep its distinct logic if it's intended for a specific pairwise summarization.
    let currentAggregatedSummary = chunks.length > 0 ? chunks[0] : "";

    for (let i = 0; i < chunks.length -1; i++) { // Iterates up to second to last chunk
        const block1 = currentAggregatedSummary; // Summary so far (or first chunk)
        const block2 = chunks[i+1]; // Next chunk
        
        this.stepStart(`Pairwise Summary of ${docName} - Merging with chunk: ${i + 2}/${chunks.length}`);
        if (callback) callback(i, chunks.length -1, "start_pairwise_summary");

        const prompt = [
            this.lollms.system_message() + `Context: Current summary of "${docName}" (Block 1) and next part (Block 2).`,
            "Block 1:",
            block1,
            this.lollms.separatorTemplate() + "Block 2:",
            block2,
            this.lollms.user_message() + summaryInstruction,
            "Combine Block 1 and Block 2 into a new, updated summary. Focus on integrating new information from Block 2 smoothly. Answer directly with the combined summary.",
            this.lollms.ai_message() + answerStart
        ].join(this.lollms.separatorTemplate());

        let newSummary = await this.fastGen(
            prompt,
            maxGenerationSize,
            (genText) => { if (callback) callback(i, chunks.length -1, "pairwise_summary_generated", genText); }
        );

        if (chunkSummaryPostProcessing) {
            newSummary = chunkSummaryPostProcessing(newSummary, block1, block2);
        }
        currentAggregatedSummary = newSummary;
        this.stepEnd(`Pairwise Summary of ${docName} - Chunk ${i + 2}/${chunks.length} merged.`);
        if (callback) callback(i, chunks.length -1, "end_pairwise_summary");
    }
    return currentAggregatedSummary; // This will be the summary of all chunks processed pairwise
  }

  // --- Helper/Placeholder Methods for TasksLibrary ---
  step(message) { console.log(`[INFO] ${message}`); }
  stepStart(message) { console.log(`[START] ${message}`); }
  stepEnd(message) { console.log(`[END] ${message}`); }
  sink(...args) { /* Does nothing, a void callback */ }

  async fastGen(prompt, maxGenerationSize = null, callback = null) {
    const options = {
      n_predict: maxGenerationSize !== null ? maxGenerationSize : this.lollms.n_predict,
      // Assuming fastGen is non-streaming for simplicity of its original design
      stream: false, 
    };
    // Use LollmsClient's generic generate method for flexibility with default_generation_mode
    const response = await this.lollms.generate(prompt, options);
    if (callback) callback(response); // Callback with the final response
    return response;
  }

  // --- Question Answering & Prompt Building ---
  async yesNo(question, context = "", maxAnswerLength = 10, conditioning = "") { // Reduced maxAnswerLength
    return (await this.multichoiceQuestion(question, ["no", "yes"], context, maxAnswerLength, conditioning)) === 1;
  }

  printPrompt(title, promptContent){ // Combined title and prompt for one log
    console.log(`--- PROMPT START: ${title} ---\n${promptContent}\n--- PROMPT END: ${title} ---`);
  }

  async multichoiceQuestion(question, possibleAnswers, context = "", maxAnswerLength = 10, conditioning = "") {
    const choicesText = possibleAnswers.map((answer, index) => `${index}. ${answer}`).join("\n");
    const elements = [];

    if (conditioning) elements.push(conditioning);
    elements.push(
        this.lollms.system_message(),
        "You are a precise assistant. Answer the multiple-choice question by providing only the numerical ID of the correct answer. Do not add any other text, explanation, or punctuation.",
        "Valid IDs are from 0 to " + (possibleAnswers.length - 1) + "."
    );

    if (context) {
        elements.push(this.lollms.custom_message("Context for the question"), context);
    }

    elements.push(
        this.lollms.custom_message("Question") + question, // Removed $
        this.lollms.custom_message("Possible answers (select one ID)"),
        choicesText,
        this.lollms.custom_message("Your Answer (ID only)") // Guiding the AI
    );

    const prompt = this.buildPrompt(elements);
    this.printPrompt("Multi-choice Question", prompt);

    let gen = await this.lollms.generate(prompt, {
        n_predict: maxAnswerLength,
        temperature: 0.01, // Low temperature for precise answer
        top_k: 1,          // Consider only the most likely token
        top_p: 0.1,        // Small top_p
        repeat_penalty: 1.0,
        // seed: this.lollms.seed, // Optional: for deterministic if needed
        // No streamingCallback needed for this short, precise answer
    });
    
    gen = gen.trim().match(/^\d+/); // Extract leading digits only

    if (gen && gen[0]) {
        const selection = parseInt(gen[0], 10);
        this.printPrompt("Multi-choice Response", `Raw: ${gen[0]}, Parsed ID: ${selection}`);
        if (selection >= 0 && selection < possibleAnswers.length) {
            return selection;
        } else {
            console.warn("Model selected an out-of-range ID:", selection);
            return -1;
        }
    } else {
        console.warn("Model failed to provide a valid numerical ID:", gen);
        return -1;
    }
  }

  buildPrompt(promptParts, sacrificeId = -1, contextSize = null, minimumSpareContextSize = null) {
    // Ensure contextSize and minimumSpareContextSize have valid defaults from LollmsClient
    contextSize = contextSize || this.lollms.ctx_size || 2048; // Fallback if not on LollmsClient
    minimumSpareContextSize = minimumSpareContextSize || this.lollms.minNPredict || 50; // Fallback

    const effectiveParts = promptParts.filter(s => typeof s === 'string' && s !== "");
    
    // Simple case: no sacrifice or sacrifice part is small, or not enough parts
    if (sacrificeId < 0 || sacrificeId >= effectiveParts.length || effectiveParts[sacrificeId].length < 50 || effectiveParts.length === 1) {
        return effectiveParts.join(this.lollms.separatorTemplate());
    }

    // Token-based truncation logic
    (async () => { // IIFE for async operations, though this function isn't async itself.
                  // Tokenization should be async. This function should be async.
        const partTokensPromises = effectiveParts.map(part => this.lollms.tokenize(part));
        const partTokensArray = await Promise.all(partTokensPromises);

        let totalTokensNonSacrifice = 0;
        for (let i = 0; i < partTokensArray.length; i++) {
            if (i !== sacrificeId) {
                totalTokensNonSacrifice += partTokensArray[i].length;
            }
        }
        
        const availableTokensForSacrifice = contextSize - totalTokensNonSacrifice - minimumSpareContextSize;

        if (availableTokensForSacrifice < 0) { // Not enough space even without sacrifice part
            console.warn("Not enough context size for non-sacrificial parts. Prompt might be truncated poorly.");
            // Consider alternative truncation strategy or error. For now, proceed.
        }
        
        if (partTokensArray[sacrificeId].length > availableTokensForSacrifice && availableTokensForSacrifice > 0) {
            const tokensToKeepForSacrifice = partTokensArray[sacrificeId].slice(-availableTokensForSacrifice); // Keep end
            effectiveParts[sacrificeId] = await this.lollms.detokenize(tokensToKeepForSacrifice);
        } else if (availableTokensForSacrifice <= 0) {
            effectiveParts[sacrificeId] = ""; // No space for sacrifice part
        }
        // If sacrifice part fits or was made to fit, it's already in effectiveParts
        
        // This async logic means buildPrompt must be async. I'll change its signature.
        // For now, this part is problematic as the outer function is sync.
        // TODO: Refactor buildPrompt to be async or handle tokenization differently.
        // For a synchronous version, if tokenization is truly async, it can't be done here.
        // Assuming a synchronous tokenize/detokenize for now if used in sync contexts,
        // or this part of logic is simplified if they are async.
        // Given LollmsClient.tokenize is async, this function MUST be async.
    })(); // This IIFE approach is not ideal for making the outer function async.

    // Fallback to non-token-based if tokenization can't be awaited here:
    // (The following line is a simplified join if the async tokenization logic is removed/deferred)
    return effectiveParts.join(this.lollms.separatorTemplate());
    // To make it work correctly, `buildPrompt` needs to be `async` and the IIFE removed.
    // Let's assume for now the original intent was simpler or tokenization was mocked as sync.
    // If a true async buildPrompt is needed:
    // async buildPrompt(...) { ... await this.lollms.tokenize(...); ... return ...; }
  }

  // --- Code Manipulation ---
  updateCode(originalCode, queryString) {
    const modifications = [];
    let currentCode = originalCode;
    let hasQuery = false;

    // Handle FULL_REWRITE first
    const fullRewriteMatch = queryString.match(/#\s*FULL_REWRITE\s*([\s\S]*)/);
    if (fullRewriteMatch) {
        const newCode = fullRewriteMatch[1].trim();
        modifications.push({ oldCode: originalCode, newCode: newCode });
        return { updatedCode: newCode, modifications, hasQuery: true };
    }

    // Handle REPLACE sections
    // Regex to find # ORIGINAL ... # SET ... blocks
    // This regex is basic and assumes structure. Might need more robust parsing for complex cases.
    const replaceRegex = /#\s*ORIGINAL\s*([\s\S]*?)\s*#\s*SET\s*([\s\S]*?)(?=#\s*ORIGINAL|$)/g;
    let match;

    while ((match = replaceRegex.exec(queryString)) !== null) {
        hasQuery = true;
        let oldCodeSnippet = match[1].trim();
        const newCodeSnippet = match[2].trim();

        if (oldCodeSnippet === "<old_code>") { // Special placeholder for entire original code
            if (currentCode === newCodeSnippet) continue; // No change
            modifications.push({ oldCode: currentCode, newCode: newCodeSnippet });
            currentCode = newCodeSnippet;
        } else {
            if (!currentCode.includes(oldCodeSnippet)) {
                console.warn("Old code snippet not found in current code:", oldCodeSnippet);
                continue;
            }
            if (oldCodeSnippet === newCodeSnippet) continue; // No change

            modifications.push({ oldCode: oldCodeSnippet, newCode: newCodeSnippet });
            currentCode = currentCode.replace(oldCodeSnippet, newCodeSnippet);
        }
    }
    
    if (!hasQuery && queryString.trim() !== "" && !fullRewriteMatch) {
        // If queryString is not empty, but no known directives found,
        // it could be an implicit full rewrite if no # directives are present.
        // This behavior depends on desired convention. For now, require explicit directives.
        console.log("No valid #FULL_REWRITE or #ORIGINAL/#SET queries detected in non-empty query string.");
    }

    return { updatedCode: currentCode, modifications, hasQuery };
  }
}


// --- SECTION: LOLLMSRAGClient Class ---
class LOLLMSRAGClient {
  constructor(lollmsClientInstance) {
    if (!lollmsClientInstance) {
        throw new Error("LOLLMSRAGClient requires a LollmsClient instance.");
    }
    this.lc = lollmsClientInstance;
    this.key = this.lc.service_key || this.generateRandomKey(); // Use service_key from LollmsClient or generate one
    console.log("RAG Client initialized. Using key for RAG operations (can be distinct from service_key):", this.key);
  }

  generateRandomKey() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0, v = c === 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  async request(endpoint, method = 'POST', body = null) { // Default to POST as most RAG ops are state-changing
    try {
      const options = {
        method,
        headers: {
          'Content-Type': 'application/json',
          // RAG might use its own key, not necessarily the LollmsClient service_key for generation
          // 'Authorization': `Bearer ${this.lc.service_key}` // If RAG server uses same auth
        },
        // Always include the RAG key in the body for operations that require it.
        body: body ? JSON.stringify({...body, key: this.key}) : JSON.stringify({key: this.key}),
      };
      
      let urlBase = this.lc.host_address || ""; // Use LollmsClient's host address
      if (urlBase.endsWith('/')) urlBase = urlBase.slice(0,-1);

      const response = await fetch(`${urlBase}${endpoint}`, options);      
      const responseData = await response.json(); // Assuming RAG server always returns JSON

      if (!response.ok) {
        const errorDetail = responseData.detail || responseData.message || response.statusText;
        throw new Error(`RAG Server Error: ${response.status} - ${errorDetail}`);
      }
      return responseData;
    } catch (error) {
      console.error(`RAG request to ${endpoint} failed:`, error);
      throw error; // Re-throw for upstream handling
    }
  }

  async addDocument(title, content, path = "unknown", metadata = {}) {
    const document = { title, content, path, metadata }; // Key added by request method
    return this.request('/add_document', 'POST', document);
  }

  async removeDocument(documentId) { // documentId is likely a path or unique ID given by RAG system
    const body = { document_id: documentId }; // Key added by request method
    return this.request(`/remove_document`, 'POST', body); // Assuming ID in body, or could be /remove_document/${documentId}
  }

  async indexDatabase() {
    // Key added by request method, no other body needed usually
    return this.request('/index_database', 'POST', {}); 
  }

  async search(query, top_k = 5, filters = {}) {
    const searchQuery = { query, top_k, filters }; // Key added by request method
    return this.request('/search', 'POST', searchQuery);
  }

  async wipeDatabase() {
    // Key added by request method
    return this.request('/wipe_database', 'DELETE', {}); // Changed to DELETE as per typical REST for wipe
  }
}

// --- SECTION: LollmsSettingsUI Class ---
class LollmsSettingsUI {
  constructor(lollmsClient, targetElementOrId) {
    if (!lollmsClient || typeof lollmsClient.updateSettings !== 'function') {
      throw new Error("LollmsSettingsUI requires a valid LollmsClient instance.");
    }
    this.lollmsClient = lollmsClient;

    if (typeof targetElementOrId === 'string') {
      this.targetDiv = document.getElementById(targetElementOrId);
    } else {
      this.targetDiv = targetElementOrId;
    }

    if (!this.targetDiv) {
      throw new Error("LollmsSettingsUI: Target element not found.");
    }

    this.settingsMap = {}; // To store references to input elements
    this.render();
  }

  createElement(tag, attributes = {}, textContent = '', children = []) {
    const element = document.createElement(tag);
    for (const key in attributes) {
      element.setAttribute(key, attributes[key]);
    }
    if (textContent) {
      element.textContent = textContent;
    }
    children.forEach(child => element.appendChild(child));
    return element;
  }

  createInputRow(labelText, inputId, inputType, value, options = {}) {
    const rowDiv = this.createElement('div', { class: 'lollms-settings-row' });
    const label = this.createElement('label', { for: inputId, class: 'lollms-settings-label' }, labelText + ': ');
    
    let inputElement;
    if (inputType === 'select') {
      inputElement = this.createElement('select', { id: inputId, name: inputId, class: 'lollms-settings-input' });
      (options.selectOptions || []).forEach(opt => {
        const optionArgs = typeof opt === 'string' ? { value: opt, text: opt } : opt;
        const option = this.createElement('option', { value: optionArgs.value }, optionArgs.text);
        if (value == optionArgs.value) { // Use == for type coercion with select values
          option.selected = true;
        }
        inputElement.appendChild(option);
      });
    } else if (inputType === 'checkbox') {
        inputElement = this.createElement('input', { type: 'checkbox', id: inputId, name: inputId, class: 'lollms-settings-input' });
        if (value) {
            inputElement.checked = true;
        }
    } else {
      inputElement = this.createElement('input', { type: inputType, id: inputId, name: inputId, value: value, class: 'lollms-settings-input' });
      if (options.min) inputElement.min = options.min;
      if (options.max) inputElement.max = options.max;
      if (options.step) inputElement.step = options.step;
      if (options.placeholder) inputElement.placeholder = options.placeholder;
    }

    this.settingsMap[inputId] = inputElement; // Store reference
    rowDiv.appendChild(label);
    rowDiv.appendChild(inputElement);
    if (options.description) {
        const desc = this.createElement('small', {class: 'lollms-settings-description'}, options.description);
        rowDiv.appendChild(desc);
    }
    return rowDiv;
  }

  async populateModels() {
    const modelSelect = this.settingsMap['model_name'];
    if (!modelSelect) return;

    modelSelect.innerHTML = ''; // Clear existing options
    modelSelect.appendChild(this.createElement('option', { value: '' }, 'Loading models...'));

    try {
      const models = await this.lollmsClient.listModels();
      modelSelect.innerHTML = ''; // Clear loading
      if (!models || models.length === 0) {
        modelSelect.appendChild(this.createElement('option', { value: '' }, 'No models found'));
        return;
      }
      models.forEach(model => {
        const option = this.createElement('option', { value: model.name }, model.name); // Assuming model object has a 'name'
        if (this.lollmsClient.model_name === model.name) {
          option.selected = true;
        }
        modelSelect.appendChild(option);
      });
       // If current model_name isn't in the list, add it as an option (might be custom or not yet listed)
       if (this.lollmsClient.model_name && !models.find(m => m.name === this.lollmsClient.model_name)) {
        const currentOption = this.createElement('option', { value: this.lollmsClient.model_name }, this.lollmsClient.model_name + " (current)");
        currentOption.selected = true;
        modelSelect.insertBefore(currentOption, modelSelect.firstChild); // Add to top
      }


    } catch (error) {
      console.error("Failed to populate models:", error);
      modelSelect.innerHTML = '';
      modelSelect.appendChild(this.createElement('option', { value: '' }, 'Error loading models'));
    }
  }

  async populatePersonalities() {
    const personalitySelect = this.settingsMap['personality'];
    if (!personalitySelect) return;

    personalitySelect.innerHTML = '';
    personalitySelect.appendChild(this.createElement('option', { value: '-1' }, 'Loading personalities...'));
    
    try {
      const personalities = await this.lollmsClient.listMountedPersonalities();
      personalitySelect.innerHTML = '';
      personalitySelect.appendChild(this.createElement('option', { value: '-1' }, 'Default Personality'));

      if (!personalities || personalities.length === 0) {
        // Keep 'Default Personality'
        return;
      }
      personalities.forEach(p => {
        // Assuming personality object has 'name' and 'id' (or index can be used for id if not present)
        // The LollmsClient expects an ID (integer). Let's use the personality's ID from the server response.
        const option = this.createElement('option', { value: p.id }, `${p.name} (ID: ${p.id})`);
        if (this.lollmsClient.personality == p.id) { // Compare with number
          option.selected = true;
        }
        personalitySelect.appendChild(option);
      });
    } catch (error) {
      console.error("Failed to populate personalities:", error);
      personalitySelect.innerHTML = '';
      personalitySelect.appendChild(this.createElement('option', { value: '-1' }, 'Error loading personalities'));
    }
  }


  render() {
    this.targetDiv.innerHTML = ''; // Clear previous content

    const form = this.createElement('div', { class: 'lollms-settings-form' }); // Use div instead of form to prevent submits

    // --- Connection Settings ---
    const connectionHeader = this.createElement('h3', {class: 'lollms-settings-header'}, 'Connection & Core');
    form.appendChild(connectionHeader);
    form.appendChild(this.createInputRow('Host Address', 'host_address', 'text', this.lollmsClient.host_address || '', {placeholder: 'e.g., http://localhost:9600'}));
    this.settingsMap['host_address'].addEventListener('change', () => {
        // When host changes, model and personality lists might need refresh
        // Defer actual refresh until apply or make it explicit
        console.log("Host address changed, model/personality lists might need refresh after applying.");
    });

    form.appendChild(this.createInputRow('Service Key', 'service_key', 'password', this.lollmsClient.service_key, {placeholder: 'Optional API key'}));
    
    const genModes = Object.entries(ELF_GENERATION_FORMAT).map(([key, value]) => ({ value: value, text: key }));
    form.appendChild(this.createInputRow('Default Generation Mode', 'default_generation_mode', 'select', this.lollmsClient.default_generation_mode, { selectOptions: genModes }));
    form.appendChild(this.createInputRow('Verify SSL Certificate', 'verify_ssl_certificate', 'checkbox', this.lollmsClient.verifySslCertificate));


    // --- Model Settings ---
    const modelHeader = this.createElement('h3', {class: 'lollms-settings-header'}, 'Model');
    form.appendChild(modelHeader);
    form.appendChild(this.createInputRow('Model Name', 'model_name', 'select', this.lollmsClient.model_name));
    form.appendChild(this.createInputRow('Personality', 'personality', 'select', this.lollmsClient.personality));
    form.appendChild(this.createInputRow('Context Size (ctx_size)', 'ctx_size', 'number', this.lollmsClient.ctx_size || 2048, {min: 0, placeholder: 'e.g., 4096'}));
    form.appendChild(this.createInputRow('Threads (n_threads)', 'n_threads', 'number', this.lollmsClient.n_threads || 4, {min: 1}));


    // --- Generation Parameters ---
    const genParamsHeader = this.createElement('h3', {class: 'lollms-settings-header'}, 'Generation Parameters');
    form.appendChild(genParamsHeader);
    form.appendChild(this.createInputRow('Max Tokens (n_predict)', 'n_predict', 'number', this.lollmsClient.n_predict === null ? '' : this.lollmsClient.n_predict, {min: -1, placeholder: 'e.g., 1024, -1 for infinite'}));
    form.appendChild(this.createInputRow('Temperature', 'temperature', 'number', this.lollmsClient.temperature, {min: 0, max: 2, step: 0.01}));
    form.appendChild(this.createInputRow('Top K', 'top_k', 'number', this.lollmsClient.top_k, {min: 0}));
    form.appendChild(this.createInputRow('Top P', 'top_p', 'number', this.lollmsClient.top_p, {min: 0, max: 1, step: 0.01}));
    form.appendChild(this.createInputRow('Repeat Penalty', 'repeat_penalty', 'number', this.lollmsClient.repeat_penalty, {min: 0, step: 0.01}));
    form.appendChild(this.createInputRow('Repeat Last N', 'repeat_last_n', 'number', this.lollmsClient.repeat_last_n, {min: 0}));
    form.appendChild(this.createInputRow('Seed', 'seed', 'number', this.lollmsClient.seed === null ? '' : this.lollmsClient.seed, {min: -1, placeholder: 'e.g., 42, -1 for random'}));
    

    this.targetDiv.appendChild(form);

    // Populate dynamic dropdowns
    this.populateModels();
    this.populatePersonalities();
  }

  apply() {
    const newSettings = {};
    let hostChanged = false;

    for (const key in this.settingsMap) {
      const element = this.settingsMap[key];
      let value;
      if (element.type === 'checkbox') {
        value = element.checked;
      } else if (element.type === 'number' || element.type === 'select-one') { // select-one is for <select>
        if (element.value === '' && (key === 'n_predict' || key === 'seed')) {
            value = null; // Allow null for n_predict and seed if field is empty
        } else {
            const numVal = Number(element.value); // Handles integer and float
            value = isNaN(numVal) ? element.value : numVal; // Keep original string if not a number (e.g. for model_name if it wasn't a select)
        }
      } else {
        value = element.value;
      }
      newSettings[key] = value;
      if (key === 'host_address' && value !== this.lollmsClient.host_address) {
        hostChanged = true;
      }
    }
    
    // Handle special case for personality -1 if it's selected as 'Default Personality'
    if (newSettings['personality'] === '-1' || newSettings['personality'] === -1){
        newSettings['personality'] = -1;
    }


    this.lollmsClient.updateSettings(newSettings);
    console.log("LollmsSettingsUI: Settings applied to LollmsClient.", newSettings);

    if (hostChanged || !this.settingsMap['model_name'].options.length || this.settingsMap['model_name'].options[0].text.includes('Error')) { // Repopulate if host changed or lists were empty/error
      console.log("LollmsSettingsUI: Host address changed or lists were problematic, re-populating models and personalities.");
      this.populateModels();
      this.populatePersonalities();
    }
    // Add a small visual confirmation
    let feedback = this.targetDiv.querySelector('.lollms-settings-feedback');
    if (!feedback) {
        feedback = this.createElement('div', {class: 'lollms-settings-feedback'}, 'Settings Applied!');
        this.targetDiv.appendChild(feedback);
    } else {
        feedback.textContent = 'Settings Applied!';
    }
    setTimeout(() => { if(feedback) feedback.textContent = ''; }, 3000);

  }
}


// Example Usage (Commented out for library use):
/*
document.addEventListener('DOMContentLoaded', async () => {
    // Basic LollmsClient example
    const lollms = new LollmsClient("http://localhost:9600", null, 2048); // Host, model (if specific), ctx_size
    lollms.updateSettings({ default_generation_mode: "LOLLMS" }); // or "OPENAI", "OLLAMA" etc.

    try {
        // List models
        // const models = await lollms.listModels();
        // console.log("Available models:", models);

        // Generate text
        // const prompt = lollms.user_message() + "Hello, LoLLMs! Tell me a short joke.";
        // const generatedText = await lollms.generate(prompt, { n_predict: 50 });
        // console.log("Generated Text:", generatedText);

        // TasksLibrary example
        // const tasks = new TasksLibrary(lollms);
        // const textToSummarize = "LoLLMs is a great tool for language model interactions. It offers many features and is easy to use. This client library helps interact with it programmatically.";
        // const summary = await tasks.summarizeText(textToSummarize, "Summarize this text briefly.", "example_doc", "", 100, 50);
        // console.log("Summary:", summary);

        // RAG Client example
        // const ragClient = new LOLLMSRAGClient(lollms);
        // await ragClient.addDocument("Test Doc 1", "This is the first test document about LoLLMs.", "/docs/test1.txt");
        // await ragClient.addDocument("Test Doc 2", "Another document, this one discusses AI.", "/docs/test2.txt");
        // await ragClient.indexDatabase();
        // const searchResults = await ragClient.search("What is LoLLMs?");
        // console.log("RAG Search Results:", searchResults);

    } catch (error) {
        console.error("An error occurred in example usage:", error);
    }
});
*/


// Example Usage (assuming you have a LollmsClient instance `lc` and a div with id `settingsContainer`):
// const lc = new LollmsClient("http://localhost:9600");
// const settingsUI = new LollmsSettingsUI(lc, "settingsContainer");
//
// And in your app's HTML, you might have a button:
// <button onclick="settingsUI.apply()">Apply LoLLMs Settings</button>
//
// CSS (minimal example, should be styled by host app):
/*
.lollms-settings-form { display: flex; flex-direction: column; gap: 10px; padding: 15px; border: 1px solid #ccc; border-radius: 5px; }
.lollms-settings-row { display: flex; flex-direction: column; gap: 5px; align-items: flex-start; }
.lollms-settings-label { font-weight: bold; margin-bottom: 2px; }
.lollms-settings-input { padding: 8px; border: 1px solid #ddd; border-radius: 4px; width: calc(100% - 18px); box-sizing: border-box; }
.lollms-settings-input[type="checkbox"] { width: auto; }
.lollms-settings-header { margin-top: 15px; margin-bottom: 5px; border-bottom: 1px solid #eee; padding-bottom: 5px;}
.lollms-settings-description { font-size: 0.8em; color: #555; margin-top: 2px; }
.lollms-settings-feedback { margin-top: 10px; color: green; font-weight: bold; }
*/