# Lollms function call definition file
# File Name: music_generator.py
# Author: ParisNeo
# Description: This function generates music based on a given prompt and duration, saving the output to a unique file in the discussion folder.

# Import necessary libraries
try:
    import pipmaster as pm
    pm.ensure_packages({"torch":"","torchaudio":"","audiocraft":""})

    import torchaudio
    from audiocraft.models import musicgen
    from ascii_colors import trace_exception
    from functools import partial

    # Function to generate music
    def generate_music(processor, client, generation_prompt: str, duration: int, model_name: str = "facebook/musicgen-melody", device: str="cuda:0") -> str:
        """
        Generates music based on the given prompt and duration, saving it to a unique file in the discussion folder.
        
        Parameters:
        - processor: The processor object used for managing the generation process.
        - client: The client object containing discussion information.
        - generation_prompt: The prompt for music generation.
        - duration: The duration of the music in seconds.
        - model_name: The name of the pretrained music generation model.
        - device: The device to run the model on (e.g., 'cpu' or 'cuda').
        
        Returns:
        - The path of the saved music file.
        """
        
        try:
            # Load the pretrained music generation model
            music_model = musicgen.MusicGen.get_pretrained(model_name, device=device)
            
            # Set generation parameters
            music_model.set_generation_params(duration=duration)
            
            # Generate music
            res = music_model.generate([generation_prompt])
            
            # Create output folder if it doesn't exist
            output_folder = client.discussion.discussion_folder / "generated_music"
            output_folder.mkdir(parents=True, exist_ok=True)

            # Generate a unique file name
            output_file = output_folder / f"music_generation_{len(list(output_folder.glob('*.wav')))}.wav"

            # Save the generated music to the specified file
            torchaudio.save(output_file, res.reshape(1, -1).cpu(), 32000)
            
            # Return the path of the saved file
            return str(output_file)
        except Exception as e:
            return trace_exception(e)

    # Metadata function for the music generation function
    def generate_music_function(processor, client):
        return {
            "function_name": "generate_music",  # The function name in string
            "function": partial(generate_music, processor=processor, client=client),  # The function to be called with preset parameters
            "function_description": "Generates music based on a prompt and duration, saving it to a unique file in the discussion folder.",  # Description of the function
            "function_parameters": [               # Parameters needed for the function
                {"name": "generation_prompt", "type": "str"},
                {"name": "duration", "type": "int"},
                {"name": "model_name", "type": "str"},
                {"name": "device", "type": "str"}
            ]
        }
except:
    from functools import partial

    def generate_music(processor, client, generation_prompt: str, duration: int, model_name: str = "facebook/musicgen-melody", device: str="cuda:0") -> str:
        pass
    def generate_music_function(processor, client):
        return {
            "function_name": "generate music is not available",  # The function name in string
            "function": partial(generate_music,processor, client),  # The function to be called with preset parameters
            "function_description": "This function is not availabe.",  # Description of the function
            "function_parameters":[]
        }
