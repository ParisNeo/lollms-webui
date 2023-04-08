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

}

populate_models()



const submitButton = document.getElementById('submit-model-params');
submitButton.addEventListener('click', (event) => {
  // Prevent default form submission
  event.preventDefault();

  modelInput = document.getElementById('model');

  seedInput = document.getElementById('seed');
  tempInput = document.getElementById('temp');
  nPredictInput = document.getElementById('n-predict');
  topKInput = document.getElementById('top-k');
  topPInput = document.getElementById('top-p');
  repeatPenaltyInput = document.getElementById('repeat-penalty');
  repeatLastNInput = document.getElementById('repeat-last-n');
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