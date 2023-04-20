
fetch('/settings')
.then(response => response.text())
.then(html => {
  document.getElementById('settings').innerHTML = html;
  backendInput = document.getElementById('backend');  
  modelInput = document.getElementById('model');
  personalityInput = document.getElementById('personalities');
  languageInput = document.getElementById('language');
  voiceInput = document.getElementById('voice');
  seedInput = document.getElementById('seed');
  tempInput = document.getElementById('temp');
  nPredictInput = document.getElementById('n-predict');
  topKInput = document.getElementById('top-k');
  topPInput = document.getElementById('top-p');
  repeatPenaltyInput = document.getElementById('repeat-penalty');
  repeatLastNInput = document.getElementById('repeat-last-n');
  
  temperatureValue = document.getElementById('temperature-value');
  n_predictValue = document.getElementById('n-predict-value');
  topkValue = document.getElementById('top-k-value');
  toppValue = document.getElementById('top-p-value');
  
  repeatPenaltyValue = document.getElementById('repeat-penalty-value');
  repeatLastNValue = document.getElementById('repeat-last-n');
  
  tempInput.addEventListener('input',() => {
    temperatureValue.textContent =`Temperature(${tempInput.value})`
  })
  
  nPredictInput.addEventListener('input',() => {
    n_predictValue.textContent =`N Predict(${nPredictInput.value})`
  })
  
  topKInput.addEventListener('input',() => {
    topkValue.textContent =`Top-K(${topKInput.value})`
  })
  
  topPInput.addEventListener('input',() => {
    toppValue.textContent =`Top-P(${topPInput.value})`
  })
  
  repeatPenaltyInput.addEventListener('input',() => {
    repeatPenaltyValue.textContent =`Repeat penalty(${repeatPenaltyInput.value})`
  })
  
  repeatLastNInput.addEventListener('input',() => {
    repeatLastNValue.textContent =`Repeat last N(${repeatLastNInput.value})`
  })
  
  
  
  fetch('/get_config')
    .then((response) => response.json())
    .then((data) => {
      console.log(data);
      backendInput.value = data["backend"]
      modelInput.value = data["model"]
      personalityInput.value = data["personality"]
      languageInput.value = data["language"]
      voiceInput.value = data["voice"]
      seedInput.value = data["seed"]
      tempInput.value = data["temp"]
      nPredictInput.value = data["n_predict"]
      topKInput.value = data["top_k"]
      topPInput.value = data["top_p"]
  
      repeatPenaltyInput.textContent  = data["repeat_penalty"]
      repeatLastNInput.textContent  = data["repeat_last_n"]
  
      temperatureValue.textContent =`Temperature(${data["temp"]})`
      n_predictValue.textContent =`N Predict(${data["n_predict"]})`
      
      topkValue.textContent =`Top-K(${data["top_k"]})`
      toppValue.textContent =`Top-P(${data["top_p"]})`
  
      repeatPenaltyValue.textContent =`Repeat penalty(${data["repeat_penalty"]})`
      repeatLastNValue.textContent =`Repeat last N(${data["repeat_last_n"]})`
    })
    .catch((error) => {
      console.error('Error:', error);
    });
  
  
  const submitButton = document.getElementById('submit-model-params');
  submitButton.addEventListener('click', (event) => {
    // Prevent default form submission
    event.preventDefault();
  
    // Get form values and put them in an object
    const formValues = {
      seed: seedInput.value,
      backend: backendInput.value,
      model: modelInput.value,
      personality: personalityInput.value,
      language: languageInput.value,
      voice: voiceInput.value,
      temp: tempInput.value,
      nPredict: nPredictInput.value,
      topK: topKInput.value,
      topP: topPInput.value,
      repeatPenalty: repeatPenaltyInput.value,
      repeatLastN: repeatLastNInput.value
    };
    console.log(formValues);
    // Use fetch to send form values to Flask endpoint
    fetch('/update_model_params', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(formValues),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        alert("Configuration set successfully")
      })
      .catch((error) => {
        console.error('Error:', error);
        alert("Error setting configuration")
      });
  });



})
.catch(error => {
  console.error('Error loading settings page:', error);
});

function populate_models(){
  // Get a reference to the <select> element
  const selectBackend = document.getElementById('backend');
  const selectModel = document.getElementById('model');

  const selectPersonalityLanguage = document.getElementById('personalities_language');
  const selectPersonalityCategory = document.getElementById('personalities_category');
  const selectPersonality = document.getElementById('personalities');

  function populate_backends(){
    // Fetch the list of .bin files from the models subfolder
    fetch('/list_backends')
    .then(response => response.json())
    .then(data => {
      if (Array.isArray(data)) {
        // data is an array
        data.forEach(filename => {
          const optionElement = document.createElement('option');
          optionElement.value = filename;
          optionElement.textContent = filename;
          selectBackend.appendChild(optionElement);
        });

        // fetch('/get_args')
        // .then(response=> response.json())
        // .then(data=>{
          
        // })
      } else {
        console.error('Expected an array, but received:', data);
      }
    });
  }

  function populate_models(){
  // Fetch the list of .bin files from the models subfolder
  fetch('/list_models')
    .then(response => response.json())
    .then(data => {
      if (Array.isArray(data)) {
        // data is an array
        data.forEach(filename => {
          const optionElement = document.createElement('option');
          optionElement.value = filename;
          optionElement.textContent = filename;
          selectModel.appendChild(optionElement);
        });

        // fetch('/get_args')
        // .then(response=> response.json())
        // .then(data=>{
          
        // })
      } else {
        console.error('Expected an array, but received:', data);
      }
    });
  }
  function populate_personalities_languages(){
    selectPersonalityLanguage.innerHTML=""
    // Fetch the list of .yaml files from the models subfolder
    fetch('/list_personalities_languages')
    .then(response => response.json())
    .then(data => {
      if (Array.isArray(data)) {
        // data is an array
        data.forEach(filename => {
          const optionElement = document.createElement('option');
          optionElement.value = filename;
          optionElement.textContent = filename;
          selectPersonalityLanguage.appendChild(optionElement);
        });

        // fetch('/get_args')
        // .then(response=> response.json())
        // .then(data=>{
          
        // })
      } else {
        console.error('Expected an array, but received:', data);
      }
    });
  }
  function populate_personalities_categories(){
  selectPersonalityCategory.innerHTML=""
  // Fetch the list of .yaml files from the models subfolder
  fetch('/list_personalities_categories')
  .then(response => response.json())
  .then(data => {
    if (Array.isArray(data)) {
      // data is an array
      data.forEach(filename => {
        const optionElement = document.createElement('option');
        optionElement.value = filename;
        optionElement.textContent = filename;
        selectPersonalityCategory.appendChild(optionElement);
      });
    } else {
      console.error('Expected an array, but received:', data);
    }
  });
  }
  function populate_personalities(){
  selectPersonality.innerHTML=""
  // Fetch the list of .yaml files from the models subfolder
  fetch('/list_personalities')
  .then(response => response.json())
  .then(data => {
    if (Array.isArray(data)) {
      // data is an array
      data.forEach(filename => {
        const optionElement = document.createElement('option');
        optionElement.value = filename;
        optionElement.textContent = filename;
        selectPersonality.appendChild(optionElement);
      });
    } else {
      console.error('Expected an array, but received:', data);
    }
  });
  }
  
  function set_personality_language(lang, callback) {
    fetch(`/set_personality_language?language=${lang}`)
      .then(response => response.json())
      .then(data => {
          callback(data);
      });
  }

  // Example usage: call another function after set_personality_language returns
  selectPersonalityLanguage.addEventListener('click', function() {
    set_personality_language(selectPersonalityLanguage.value, function(data) {
      console.log('Response received:', data);
      populate_personalities_categories();
    });
  });

  function set_personality_category(category, callback) {
    fetch(`/set_personality_category?category=${category}`)
      .then(response => response.json())
      .then(data => {
        callback()
      });
  }

  // Example usage: call another function after set_personality_category returns
  selectPersonalityCategory.addEventListener('click', function() {
    set_personality_category(selectPersonalityCategory.value, function(data) {
      console.log('Response received:', data);
      populate_personalities();
    });
  });


  populate_backends()
  populate_models()
  populate_personalities_languages()
  populate_personalities_categories()
  populate_personalities()

  // Fetch the list of .yaml files from the models subfolder
  fetch('/list_languages')
  .then(response => response.json())
  .then(data => {
    if (Array.isArray(data)) {
      // data is an array
      const selectLanguage = document.getElementById('language');
      data.forEach(row => {
        const optionElement = document.createElement('option');
        optionElement.value = row.value;
        optionElement.innerHTML = row.label;
        selectLanguage.appendChild(optionElement);
      });
    } else {
      console.error('Expected an array, but received:', data);
    }
  });

}
