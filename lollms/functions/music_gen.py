# Lollms function call definition file

# Required imports
from ascii_colors import trace_exception
import pipmaster as pm

# Ensure pyautogui is installed
pm.ensure_packages({"pyautogui":""})
import pyautogui
import webbrowser
import time

def open_and_fill_udio(song_description: str, lyrics: str) -> str:
    """
    Opens the udio.com page, interacts with the UI to fill in the song description and lyrics fields.
    
    Parameters:
    - song_description (str): The description of the song.
    - lyrics (str): The lyrics of the song.
    
    Returns:
    - str: Success message or exception trace.
    """
    try:
        # Open the specified webpage
        webbrowser.open('https://udio.com')
        time.sleep(5)  # Wait for the page to load

        # Click the input field near the "Create" button
        # Adjust the x, y coordinates based on your screen resolution
        pyautogui.click(x=500, y=120)

        # Fill the song description field
        pyautogui.write(song_description)

        # Select the "Custom" option
        pyautogui.click(x=400, y=300)

        pyautogui.click(x=400, y=400)

        # Fill the lyrics field
        pyautogui.write(lyrics)

        # Start generation
        pyautogui.click(x=1660, y=120)

        pyautogui.click(x=500, y=120)
        return "Successfully filled the song description and lyrics."
    except Exception as e:
        return trace_exception(e)

def open_and_fill_udio_function():
    return {
        "function_name": "open_and_fill_udio",
        "function": open_and_fill_udio,
        "function_description": "Opens udio.com page and fills in the song description and lyrics fields to start generating the music.",
        "function_parameters": [
            {"name": "song_description", "type": "str", "description":"a list of tags describing the song style and vibes. Make it short"},
            {"name": "lyrics", "type": "str","description":"The lyrics of the song"}
        ]
    }


#suno

def open_and_fill_suno(song_description: str, lyrics: str, title:str) -> str:
    """
    Opens the udio.com page, interacts with the UI to fill in the song description and lyrics fields.
    
    Parameters:
    - song_description (str): The description of the song.
    - lyrics (str): The lyrics of the song.
    
    Returns:
    - str: Success message or exception trace.
    """
    try:
        # Open the specified webpage
        webbrowser.open('https://suno.ai')
        time.sleep(5)  # Wait for the page to load

        # Click the input field near the "Create" button
        # Adjust the x, y coordinates based on your screen resolution
        pyautogui.click(x=50, y=280)

        time.sleep(2)  # Wait for the page to load


        def is_sufficiently_white(color, threshold=150):
            """
            Check if a color is sufficiently white.
            
            :param color: Tuple of (R, G, B) values
            :param threshold: Minimum value for each channel to be considered "white"
            :return: Boolean indicating if the color is sufficiently white
            """
            return all(channel >= threshold for channel in color)

        # Define the coordinates of the button
        button_x = 220
        button_y = 150

        # Get the color of the pixel at the button's location
        pixel_color = pyautogui.pixel(button_x, button_y)
        print(pixel_color)

        # Check if the color is not sufficiently white
        if not is_sufficiently_white(pixel_color):
            # # Select the "Custom" option
            pyautogui.click(x=220, y=150)

        time.sleep(1)  # Wait for the page to load

        pyautogui.click(x=250, y=280)
        # # Fill the song lerycs field
        pyautogui.write(lyrics)
        time.sleep(5)  # Wait for the lyricsto be written

        pyautogui.click(x=370, y=620)
        # # Fill the song_description field
        pyautogui.write(song_description)

        pyautogui.click(x=370, y=440)
        # # Fill the song_description field

        pyautogui.click(x=370, y=440)
        # # Fill the song_description field
        pyautogui.write(song_description)

        time.sleep(1)  # Wait for the lyricsto be written

        pyautogui.click(x=370, y=770)
        # # Fill the song_description field
        pyautogui.write(title)

        # # Start generation
        pyautogui.click(x=370, y=870)

        # pyautogui.click(x=500, y=120)
        return "Successfully filled the song description and lyrics."
    except Exception as e:
        return trace_exception(e)

def open_and_fill_suno_function():
    return {
        "function_name": "open_and_fill_udio",
        "function": open_and_fill_suno,
        "function_description": "Opens udio.com page and fills in the song description and lyrics fields to start generating the music.",
        "function_parameters": [
            {"name": "song_description", "type": "str", "description":"a list of tags describing the song style and vibes. Make it short"},
            {"name": "lyrics", "type": "str","description":"The lyrics of the song"},
            {"name": "title", "type": "str","description":"The title of the song"}
            
        ]
    }

if __name__ == "__main__":
    # Test the function with sample data
    song_description = "Modern hip-hop/rap with electronic beats and a futuristic vibe."
    lyrics = """Verse 1:
Yo, listen up, it's time to get smart
Lollms on the scene, it's a brand new start
AI's evolving, changing the game
Open-source power, rising to fame

Chorus:
Lollms, AI, digital revolution
Bringing solutions, tech evolution
Neural networks, learning so fast
The future is now, the die has been cast

Verse 2:
Customizable, flexible, adapt with ease
Lollms got the tools to do as you please
Language models, chatbots galore
Pushing boundaries, opening new doors

(Repeat Chorus)

Verse 3:
From Paris to Tokyo, global connection
Lollms community, no need for correction
Ethical AI, that's how we roll
Empowering humans, that's the ultimate goal

(Repeat Chorus)

Outro:
Lollms and AI, hand in hand
Shaping tomorrow, across every land
The revolution's here, it's time to join in
With Lollms leading, everyone can win
"""
    title = "Digital Revolution (Lollms AI Flow)"
    result = open_and_fill_suno(song_description, lyrics, title)
    print(result)
