function selectOptionByText(selectElement, optionText) {
  for (let i = 0; i < selectElement.options.length; i++) {
    if (selectElement.options[i].text === optionText) {
      selectElement.selectedIndex = i;
      break;
    }
  }
}



fetch('/settings')
.then(response => response.text())
.then(html => {
  document.getElementById('settings').innerHTML = html;
  bindingInput = document.getElementById('binding');  
  modelInput = document.getElementById('model');
  personalityLanguageInput = document.getElementById('personalities_language');
  personalityCategoryInput = document.getElementById('personalities_category');
  personalityInput = document.getElementById('personalities');
  languageInput = document.getElementById('language');
  voiceInput = document.getElementById('voice');
  seedInput = document.getElementById('seed');
  tempInput = document.getElementById('temperature');
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

    
  function update_config(){
    fetch('/get_config')
      .then((response) => response.json())
      .then((data) => {
        console.log("Received config")
        console.log(data);
        selectOptionByText(bindingInput, data["binding"])
        selectOptionByText(modelInput, data["model"])
        selectOptionByText(personalityLanguageInput, data["personality_language"])
        selectOptionByText(personalityCategoryInput, data["personality_category"])
        selectOptionByText(personalityInput, data["personality"])
        languageInput.value = data["language"]
        voiceInput.value = data["voice"]
        seedInput.value = data["seed"]
        tempInput.value = data["temperature"]
        nPredictInput.value = data["n_predict"]
        topKInput.value = data["top_k"]
        topPInput.value = data["top_p"]
    
        repeatPenaltyInput.textContent  = data["repeat_penalty"]
        repeatLastNInput.textContent  = data["repeat_last_n"]
    
        temperatureValue.textContent =`Temperature(${data["temperature"]})`
        n_predictValue.textContent =`N Predict(${data["n_predict"]})`
        
        topkValue.textContent =`Top-K(${data["top_k"]})`
        toppValue.textContent =`Top-P(${data["top_p"]})`
    
        repeatPenaltyValue.textContent =`Repeat penalty(${data["repeat_penalty"]})`
        repeatLastNValue.textContent =`Repeat last N(${data["repeat_last_n"]})`
      })
      .catch((error) => {
        console.error('Error:', error);
      });

  }  
  
  bindingInput.addEventListener('input',() => {
    console.log(`Binding (${bindingInput.value})`)
    // Use fetch to send form values to Flask endpoint
    fetch('/set_binding', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({"binding":bindingInput.value}),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        if(data["status"]==="no_models_found"){
          alert("No models found for this binding. Make sure you select a binding that you have models for or download models from links in our repository")  
        }
        else{
          populate_settings();
          alert("Binding set successfully")  
        }
      })
      .catch((error) => {
        console.error('Error:', error);
        alert("Error setting configuration")
      });    
  })

  modelInput.addEventListener('input',() => {
    console.log(`Model (${modelInput.value})`)
    // Use fetch to send form values to Flask endpoint
    fetch('/set_model', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({"model":modelInput.value}),
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        populate_settings();
        alert("Binding set successfully")
      })
      .catch((error) => {
        console.error('Error:', error);
        alert("Error setting configuration")
      });    
  })


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
  


  
  const submitButton = document.getElementById('submit-model-params');
  submitButton.addEventListener('click', (event) => {
    // Prevent default form submission
    event.preventDefault();
  
    // Get form values and put them in an object
    const formValues = {
      seed: seedInput.value,
      binding: bindingInput.value,
      model: modelInput.value,
      personality_language:personalityLanguageInput.value,
      personality_category:personalityCategoryInput.value,
      personality: personalityInput.value,
      language: languageInput.value,
      voice: voiceInput.value,
      temperature: tempInput.value,
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

  populate_settings();

  function populate_settings(){
    // Get a reference to the <select> element
    const selectBinding = document.getElementById('binding');
    const selectModel = document.getElementById('model');
  
    const selectPersonalityLanguage = document.getElementById('personalities_language');
    const selectPersonalityCategory = document.getElementById('personalities_category');
    const selectPersonality = document.getElementById('personalities');
  
    function populate_bindings(){
      selectBinding.innerHTML = "";
      // Fetch the list of .bin files from the models subfolder
      fetch('/list_bindings')
      .then(response => response.json())
      .then(data => {
        if (Array.isArray(data)) {
          // data is an array
          data.forEach(filename => {
            const optionElement = document.createElement('option');
            optionElement.value = filename;
            optionElement.textContent = filename;
            selectBinding.appendChild(optionElement);
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
      selectModel.innerHTML=""
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
      const selectPersonalityLanguage = document.getElementById('personalities_language');
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
      const selectPersonalityCategory = document.getElementById('personalities_category');
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
      const selectPersonalityLanguage = document.getElementById('personalities_language');
        
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
  
  
    populate_bindings()
    populate_models()
    populate_personalities_languages()
    populate_personalities_categories()
    populate_personalities()
    setTimeout(update_config,100);
  
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
  

})
.catch(error => {
  console.error('Error loading settings page:', error);
});


