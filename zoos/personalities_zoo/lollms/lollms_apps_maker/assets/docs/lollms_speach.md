# Lollms speach

## Audio Transcription API

Endpoint: POST /transcribe
Request: multipart/form-data with WAV file (key: "file")
Response: JSON { "transcription": "Transcribed text" }

Example (Axios):
```javascript
const axios = require('axios');
const FormData = require('form-data');
const fs = require('fs');

async function transcribeAudio(filePath) {
  const formData = new FormData();
  formData.append('file', fs.createReadStream(filePath));

  try {
    const response = await axios.post('/transcribe', formData, {
      headers: { ...formData.getHeaders() }
    });
    return response.data.transcription;
  } catch (error) {
    throw error.response ? error.response.data : error.message;
  }
}

// Usage: transcribeAudio('audio.wav').then(console.log).catch(console.error);
```

Note: Requires 'axios' and 'form-data' packages. Only accepts WAV files.

# Text-to-Speech API

## 1. TTS File Endpoint

Converts text to speech and returns a WAV file.

- **URL**: `/tts/file`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "text": "Text to convert to speech",
    "speaker": "optional_speaker_name",
    "language": "en"
  }
  ```
- **Response**: WAV file download

## 2. TTS Stream Endpoint

Converts text to speech and returns audio stream.

- **URL**: `/tts/stream`
- **Method**: `POST`
- **Request Body**: Same as TTS File Endpoint
- **Response**: Audio stream (WAV format)

## 3. Get Available Voices Endpoint

Returns a list of available voices for TTS.

- **URL**: `/tts/voices`
- **Method**: `GET`
- **Response**: JSON array of voice names
  ```json
  {
    "voices": ["voice1", "voice2", "voice3"]
  }
  ```

## Usage Example (JavaScript/Axios):

```javascript
const axios = require('axios');

async function textToSpeech(text, speaker = null, language = 'en', stream = false) {
  const endpoint = stream ? '/tts/stream' : '/tts/file';
  const response = await axios.post(`${endpoint}`, {
    text,
    speaker,
    language
  }, {
    responseType: stream ? 'arraybuffer' : 'blob'
  });

  if (stream) {
    // Handle stream data
    console.log('Audio data received:', response.data);
  } else {
    // Handle file download
    const blob = new Blob([response.data], { type: 'audio/wav' });
    const url = window.URL.createObjectURL(blob);
    // Use url to play audio or create download link
  }
}

async function getAvailableVoices() {
  try {
    const response = await axios.get('/tts/voices');
    console.log('Available voices:', response.data.voices);
    return response.data.voices;
  } catch (error) {
    console.error('Error fetching voices:', error);
  }
}

// Usage
textToSpeech('Hello, world!', 'main_voice', 'en', false)
  .then(() => console.log('TTS completed'))
  .catch(console.error);

getAvailableVoices()
  .then(voices => console.log('Fetched voices:', voices))
  .catch(console.error);
```

Note: Adjust the host and port in the axios request URL as needed.