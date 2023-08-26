# Extension building manual

## What is an extension
Extensions are little projects built by the community that can be plugged to the generation process to allow users to bring new ideas to the project without feature-creaping it.

There are many types of extensions:
1 - pipeline extensions
These extensions have no UI, they only intercept the communication between the user and the AI, perform some modifications or operations, then submit them to the discussion to enritch it. For example:
- Net enabled LoLLMs (under construction at https://github.com/ParisNeo/Net_enabled-LoLLMs-Extension) : An extension that offers a special personality that indicates to the chatbot that whenever the user is asking a question it has no answer to, it should invoke a search function. The extension intercepts this keyword, do the research on the net then mirror it back to the AI. The AI can then use those inputs to formulate an answer.
- Image enabled LoLLMs : An extension that uses Blip to convert an image into text that can be interpreted by the AI and used in the discussion.

The extension should offer a yaml file that describes it to allow the system to integrate it.

```yaml
# This is a lollms extension project
# Project name : Models tester
# Author : ParisNeo
# Description :
# This extension allows applying the model on a bunch of questions at once and recover answers in a text file

name: LoLLMs-Models-Tester-Extension
author: ParisNeo
description: |
        This extension allows applying the model on a bunch of questions at once and recover answers in a text file
version: 1.0

# UI metadata
has_ui: true

# binding metadata
can_trigger_the_model : 

# Conditionning override
override_current_personality: true
adds_conditionning: false
conditionning_text: "Respond to my questions."
prefix_text: "Q:"
suffix_text: "A:"

# Send commands to model
sends_commands_to_model: true

# Recover model output
uses_model_output : true
recover_word_by_word : false
recover_generated_text : true
```

The extension should have a extension.py file on its root that implements Extensions interface:

