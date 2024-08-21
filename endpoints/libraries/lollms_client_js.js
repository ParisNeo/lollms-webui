// This requires axios
// In the html don't forget to import axios.min.js cdn
// <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>



// JavaScript equivalent of the ELF_GENERATION_FORMAT enum
const ELF_GENERATION_FORMAT = {
  LOLLMS: 0,
  OPENAI: 1,
  OLLAMA: 2,
  LITELLM: 2
};

// JavaScript equivalent of the ELF_COMPLETION_FORMAT enum
const ELF_COMPLETION_FORMAT = {
  Instruct: 0,
  Chat: 1
};

// Ensuring the objects are immutable
Object.freeze(ELF_GENERATION_FORMAT);
Object.freeze(ELF_COMPLETION_FORMAT);


class LollmsClient {
  constructor(
    host_address = null,
    model_name = null,
    ctx_size = 4096,
    personality = -1,
    n_predict = 4096,
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
    this.n_predict = n_predict?n_predict:4096;
    this.personality = personality;
    this.temperature = temperature;
    this.top_k = top_k;
    this.top_p = top_p;
    this.repeat_penalty = repeat_penalty;
    this.repeat_last_n = repeat_last_n;
    this.seed = seed;
    this.n_threads = n_threads;
    this.service_key = service_key;
    this.default_generation_mode = default_generation_mode;
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
  system_message(){
    return this.template.start_header_id_template+this.template.system_message_template+this.template.end_header_id_template
  }
  ai_message(ai_name="assistant"){
    return this.template.start_ai_header_id_template+ai_name+this.template.end_ai_header_id_template
  }
  user_message(user_name="user"){
    return this.template.start_user_header_id_template+user_name+this.template.end_user_header_id_template
  }
  updateServerAddress(newAddress) {
      this.serverAddress = newAddress;
    }    
  async tokenize(prompt) {
      /**
       * Tokenizes the given prompt using the model's tokenizer.
       *
       * @param {string} prompt - The input prompt to be tokenized.
       * @returns {Array} A list of tokens representing the tokenized prompt.
       */
      const output = await axios.post("/lollms_tokenize", {"prompt": prompt});
      return output.data.named_tokens
    }
  async detokenize(tokensList) {
      /**
       * Detokenizes the given list of tokens using the model's tokenizer.
       *
       * @param {Array} tokensList - A list of tokens to be detokenized.
       * @returns {string} The detokenized text as a string.
       */
      const output = await axios.post("/lollms_detokenize", {"tokens": tokensList});
      console.log(output.data.text)
      return output.data.text
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
        default:
          throw new Error('Invalid generation mode');
      }
    }
    generate_with_images(prompt, images, {
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
          return this.lollms_generate_with_images(prompt, images, this.host_address, this.model_name, -1, n_predict, stream, temperature, top_k, top_p, repeat_penalty, repeat_last_n, seed, n_threads, service_key, streamingCallback);
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

class TasksLibrary {
constructor(lollms) {
  this.lollms = lollms;
}

async translateTextChunk(textChunk, outputLanguage = "french", host_address = null, model_name = null, temperature = 0.1, maxGenerationSize = 3000) {
  const translationPrompt = [
    `!@>system:`,
    `Translate the following text to ${outputLanguage}.`,
    `Be faithful to the original text and do not add or remove any information.`,
    `Respond only with the translated text.`,
    `Do not add comments or explanations.`,
    `!@>text to translate:`,
    `${textChunk}`,
    `!@>translation:`,
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
async summarizeText(textChunk, summaryLength = "short", host_address = null, model_name = null, temperature = 0.1, maxGenerationSize = null) {
  const summaryPrompt = [
    `system:`,
    `Summarize the following text in a ${summaryLength} manner.`,
    `Keep the summary concise and to the point.`,
    `Include all key points and do not add new information.`,
    `Respond only with the summary.`,
    `text to summarize:`,
    `${textChunk}`,
    `summary:`,
  ].join("\n");

  const summary = await this.lollms.generateText(
    summaryPrompt,
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

  return summary;
}

yesNo(question, context = "", maxAnswerLength = 50, conditioning = "") {
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

multichoiceQuestion(question, possibleAnswers, context = "", maxAnswerLength = 50, conditioning = "") {
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
  const startHeaderIdTemplate = this.config.start_header_id_template;
  const endHeaderIdTemplate = this.config.end_header_id_template;
  const systemMessageTemplate = this.config.system_message_template;

  const choices = possibleAnswers.map((answer, index) => `${index}. ${answer}`).join("\n");
  const elements = conditioning ? [conditioning] : [];
  elements.push(
      `${startHeaderIdTemplate}${systemMessageTemplate}${endHeaderIdTemplate}`,
      "Answer this multi choices question.",
      "Answer with an id from the possible answers.",
      "Do not answer with an id outside this possible answers."
  );

  if (context) {
      elements.push(
          `${startHeaderIdTemplate}context${endHeaderIdTemplate}`,
          context
      );
  }

  elements.push(
      `${startHeaderIdTemplate}question${endHeaderIdTemplate}${question}`,
      `${startHeaderIdTemplate}possible answers${endHeaderIdTemplate}`,
      choices,
      `${startHeaderIdTemplate}answer${endHeaderIdTemplate}`
  );

  const prompt = this.buildPrompt(elements);
  const gen = this.lollms.generate(prompt, {
      n_predict: maxAnswerLength,
      temperature: 0.1,
      top_k: 50,
      top_p: 0.9,
      repeat_penalty: 1.0,
      repeat_last_n: 50,
      callback: this.sink
  }).trim().replace("", "").replace("", "");

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
      contextSize = this.config.ctxSize;
  }
  if (minimumSpareContextSize === null) {
      minimumSpareContextSize = this.config.minNPredict;
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

extractCodeBlocks(text) {
  const codeBlockRegex = /```([\s\S]*?)```/g;
  const codeBlocks = [];
  let match;
  let index = 0;

  while ((match = codeBlockRegex.exec(text)) !== null) {
    const [fullMatch, content] = match;
    const blockLines = content.trim().split('\n');
    let type = 'language-specific';
    let blockContent = content.trim();

    // Check if the first line is a language specifier
    if (blockLines.length > 1 && blockLines[0].trim().length > 0 && !blockLines[0].includes(' ')) {
      type = blockLines[0].trim().toLowerCase();
      blockContent = blockLines.slice(1).join('\n').trim();
    }

    codeBlocks.push({
      index: index++,
      file_name: '',
      content: blockContent,
      type: type
    });
  }

  return codeBlocks;
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
  constructor(baseURL, apiKey) {
      this.baseURL = baseURL;
      this.apiKey = apiKey;
  }

  async request(endpoint, method = 'GET', body = null) {
      const headers = {
          'Authorization': this.apiKey,
          'Content-Type': 'application/json',
      };

      const options = {
          method,
          headers,
      };

      if (body) {
          options.body = JSON.stringify(body);
      }

      const response = await fetch(`${this.baseURL}${endpoint}`, options);

      if (!response.ok) {
          const errorData = await response.json();
          throw new Error(`Error: ${errorData.detail || response.statusText}`);
      }

      return response.json();
  }

  async addDocument(title, content, path = "unknown") {
      const document = { title, content, path };
      return this.request('/add_document', 'POST', document);
  }

  async removeDocument(documentId) {
      return this.request(`/remove_document/${documentId}`, 'POST');
  }

  async indexDatabase() {
      return this.request('/index_database', 'POST');
  }

  async search(query) {
      const searchQuery = { query };
      return this.request('/search', 'POST', searchQuery);
  }

  async wipeDatabase() {
      return this.request('/wipe_database', 'DELETE');
  }
}

// Example usage:
// const ragClient = new RAGClient('http://localhost:8000', 'your_bearer_token');
// ragClient.addDocument('My Title', 'This is the content of the document.')
//     .then(response => console.log(response))
//     .catch(error => console.error(error));
