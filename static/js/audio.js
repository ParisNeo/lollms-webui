// Dirty fix for disabling speech synth for firefox browsers :()
if (!userAgent.match(/firefox|fxios/i)) {
  isStarted = false;
  isSpeaking = false;
  const SpeechRecognition = window.SpeechRecognition || webkitSpeechRecognition;
  const recognition = new SpeechRecognition();
  const synth = window.speechSynthesis || webkitspeechSynthesis;
  var voices = synth.getVoices();
  function prepre_audio() {
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 10;
    language_select = document.getElementById("language")
  }
  voices = [];
  function populateVoicesList() {
    voices = synth.getVoices();
    voice_select = document.getElementById("voice")
    voice_select.innerHTML = "";
    for (let i = 0; i < voices.length; i++) {
      if (
        voices[i].lang.startsWith(
          language_select.value.substring(0, 2)
        )
      ) {
        const option = document.createElement("option");
        option.textContent = `${voices[i].name} (${voices[i].lang})`;

        if (voices[i].default) {
          option.textContent += " — DEFAULT";
        }

        option.setAttribute("data-lang", voices[i].lang);
        option.setAttribute("data-name", voices[i].name);
        voice_select.appendChild(option);
      }
    }
    voice_select.addEventListener("change", function () {
    });
  }
  // Audio code
  function splitString(string, maxLength) {
    const sentences = string.match(/[^.!?]+[.!?]/g);
    const strings = [];
    let currentString = "";

    if (sentences) {
      for (const sentence of sentences) {
        if (currentString.length + sentence.length > maxLength) {
          strings.push(currentString);
          currentString = "";
        }

        currentString += `${sentence} `;
      }
    } else {
      strings.push(string);
    }

    if (currentString) {
      strings.push(currentString);
    }

    return strings;
  }
  function addListeners(button, utterThis) {
    utterThis.onstart = (event) => {
      isSpeaking = true;
      button.style.backgroundColor = "red";
      button.style.boxShadow = "2px 2px 0.5px #808080";
    };

    utterThis.onend = (event) => {
      isSpeaking = false;
      button.style.backgroundColor = "";
      button.style.boxShadow = "";
    };
  }

  function attachAudio_modules(div, container) {
    if (container.getElementsByClassName("audio-out-button").length > 0) {
      return;
    }
    const audio_out_button = document.createElement("button");
    audio_out_button.title = "Listen to message";
    audio_out_button.id = "audio-out-button";
    audio_out_button.classList.add("audio_btn",'bg-gray-500', 'hover:bg-gray-700', 'text-white', 'font-bold', 'py-0', 'px-0', 'rounded-r', "w-10", "h-10");
    audio_out_button.innerHTML = "🕪";
    audio_out_button.classList.add("audio-out-button");
    container.appendChild(audio_out_button);

    function play_audio() {
      console.log("Playing audio")
      if (isSpeaking) {

        audio_out_button.style.backgroundColor = "";
        audio_out_button.style.boxShadow = "";
        synth.cancel();
        isSpeaking = false;
      } else {
        isSpeaking = true;
        text = div.textContent;

        const selectedOption =
          voice_select.selectedOptions[0].getAttribute("data-name");
        var selectedVoice = null;
        for (let i = 0; i < voices.length; i++) {
          if (voices[i].name === selectedOption) {
            selectedVoice = voices[i];
          }
        }
        if (selectedVoice && selectedVoice.voiceURI === "native") {
          const utterThis = new SpeechSynthesisUtterance(text);
          utterThis.voice = selectedVoice;
          addListeners(audio_out_button, utterThis);
          synth.speak(utterThis);
        } else {
          console.log("Not native")
          texts = splitString(text, 200);
          console.log(`Text to say ${texts}`)
          texts.forEach((text) => {
            const utterThis = new SpeechSynthesisUtterance(text);
            utterThis.voice = selectedVoice;
            addListeners(audio_out_button, utterThis);
            synth.speak(utterThis);
          });
        }
      }
    }
    audio_out_button.addEventListener("click", () => {
      play_audio();
    });
    // TODO : activate using configuration file
    //if (global["auto_audio"]) {
    //  play_audio();
    //}
  }

  function add_audio_in_ui() {
    const input = document.getElementById("user-input");
    // const wrapper = document.createElement("div");
    // wrapper.classList.add("flex", "items-center");
    var btn = document.querySelectorAll("#audio_in_tool");

    var found = false;
    // Iterate through the children
    for (var i = 0; i < btn.length; i++) {
      var child = btn[i];
      // Check if the wrapper element contains the current child element
      if (input.parentNode.parentNode.contains(child)) {
        found = true;
      }
    }


    if (!found) {
      const audio_in_button = document.createElement("button");
      audio_in_button.title = "Type with your voice";
      audio_in_button.id = "audio_in_tool";
      audio_in_button.classList.add("audio_btn");
      audio_in_button.innerHTML = "🎤";

      input.parentNode.parentNode.insertBefore(
        audio_in_button,
        input.parentNode
      );

      input.classList.add("flex-1");
      audio_in_button.classList.add("ml-2");

      audio_in_button.addEventListener("click", () => {
        if (isStarted) {
          recognition.stop();
          isStarted = false;
        } else {
          recognition.lang = language_select.value;
          recognition.start();
          isStarted = true;
        }
      });

      recognition.addEventListener("result", (event) => {
        let transcript = "";
        for (const result of event.results) {
          transcript += result[0].transcript;
        }
        if (transcript != "") {
          input.value = transcript;
        }
      });

      recognition.addEventListener("start", () => {
        audio_in_button.style.backgroundColor = "red";
        audio_in_button.style.boxShadow = "2px 2px 0.5px #808080";
      });

      recognition.addEventListener("end", () => {
        audio_in_button.style.backgroundColor = "";
        audio_in_button.style.boxShadow = "";
      });
      }
  }
}
