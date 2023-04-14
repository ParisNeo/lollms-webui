
fetch('/settings')
.then(response => response.text())
.then(html => {
  document.getElementById('settings').innerHTML = html;
  
  modelInput = document.getElementById('model');
  personalityInput = document.getElementById('personalities');
  languageInput = document.getElementById('language');
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
      modelInput.value = data["model"]
      personalityInput.value = data["personality"]
      languageInput.value = data["language"]
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
      model: modelInput.value,
      seed: seedInput.value,
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
      })
      .catch((error) => {
        console.error('Error:', error);
      });
  });



})
.catch(error => {
  console.error('Error loading settings page:', error);
});

function populate_models(){
  // Get a reference to the <select> element
  const selectElement = document.getElementById('model');

  // Fetch the list of .bin files from the models subfolder
  fetch('/list_models')
    .then(response => response.json())
    .then(data => {
      if (Array.isArray(data)) {
        // data is an array
        const selectElement = document.getElementById('model');
        data.forEach(filename => {
          const optionElement = document.createElement('option');
          optionElement.value = filename;
          optionElement.textContent = filename;
          selectElement.appendChild(optionElement);
        });

        // fetch('/get_args')
        // .then(response=> response.json())
        // .then(data=>{
          
        // })
      } else {
        console.error('Expected an array, but received:', data);
      }
    });

  // Fetch the list of .yaml files from the models subfolder
  fetch('/list_personalities')
  .then(response => response.json())
  .then(data => {
    if (Array.isArray(data)) {
      // data is an array
      const selectElement = document.getElementById('personalities');
      data.forEach(filename => {
        const optionElement = document.createElement('option');
        optionElement.value = filename;
        optionElement.textContent = filename;
        selectElement.appendChild(optionElement);
      });

      // fetch('/get_args')
      // .then(response=> response.json())
      // .then(data=>{
        
      // })
    } else {
      console.error('Expected an array, but received:', data);
    }
  });

  // Fetch the list of .yaml files from the models subfolder
  fetch('/list_languages')
  .then(response => response.json())
  .then(data => {
    if (Array.isArray(data)) {
      // data is an array
      const selectElement = document.getElementById('language');
      data.forEach(row => {
        const optionElement = document.createElement('option');
        optionElement.value = row.value;
        optionElement.innerHTML = row.label;
        selectElement.appendChild(optionElement);
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

populate_models()

