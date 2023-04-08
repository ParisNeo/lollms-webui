
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