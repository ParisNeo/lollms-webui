# Getting Started with LoLLMs

Welcome to LoLLMs (Lord of Large Language Multimodal Systems)! This guide provides detailed steps to install, configure, and start using LoLLMs, a versatile AI platform created by ParisNeo in September 2023. Designed for tasks ranging from text generation to multimodal operations, LoLLMs is primarily installed using release files (`lollms_setup.bat` for Windows and `lollms_setup.sh` for Linux) available on GitHub. Follow these steps to get up and running as of March 6, 2025.

## Step 1: Install LoLLMs Using Release Files
LoLLMs is best installed using pre-built release scripts from the [GitHub releases page](https://github.com/ParisNeo/lollms-webui/releases), automating the setup process for the web UI and core components.

### For Windows Users
- **Download the Script**: Visit [GitHub releases](https://github.com/ParisNeo/lollms-webui/releases) and download `lollms_setup.bat` (e.g., from v9.6, the latest as of March 2025).
- **Run the Script**: Double-click `lollms_setup.bat`. A command-line window will open, guiding you through:
  - Setting up a personal folder for data and models.
  - Selecting hardware (CPU or GPU with CUDA support).
  - Installing dependencies and at least one model from the Models Zoo.
- **Follow Prompts**: Answer the on-screen questions (e.g., "Do you want to install a model now?"). If prompted about antivirus warnings, proceed as these are noted as false positives [LOLLMS WebUI Tutorial](https://parisneo.github.io/lollms-webui/tutorials/noobs_tutorial.html).

### For Linux Users
- **Download the Script**: From the same [GitHub releases page](https://github.com/ParisNeo/lollms-webui/releases), download `lollms_setup.sh`.
- **Run the Script**: Open a terminal, navigate to the download directory (e.g., `cd ~/Downloads`), and execute:
```bash
bash lollms_setup.sh
```
Ensure the script is executable (chmod +x lollms_setup.sh if needed).
The script clones the repository, sets up a Conda environment, and prompts for configuration (e.g., hardware and model selection).
- **Follow Prompts:** Respond to setup questions, such as installing CUDA for GPU support or opting for CPU-only mode.
- **Note:** While a graphical installer (lollms_setup.exe) exists for Windows Download – LoLLMs, this guide focuses on .bat and .sh as the primary methods per user preference. The scripts ensure a complete setup, including the web UI, unlike the pip install lollms alternative, which is more developer-oriented.
## Step 2: Launch the Web UI
After installation, the script typically launches the LoLLMs Web UI automatically. If not, or after restarting your system:
- **Windows:** Run lollms.bat (created during setup) from the installation directory.
- **Linux:** Run bash lollms.sh from the same directory.
Access the Interface: Open your browser and go to http://localhost:7860. You’ll see the main chat screen, ready for interaction.
## Step 3: Select a Personality
The web UI features a selector for the Personalities Zoo, offering over 500 AI personas for tasks like coding, image generation, or text analysis:
- Navigate to the personality dropdown or menu (exact location may vary by version).
- Choose a persona (e.g., a coding expert or creative writer) based on your task.
This selection tailors the AI’s responses to your needs.
## Step 4: Start a Conversation
Open the Chat Interface: The main screen displays a chat bar at the bottom.
- **Type Your Query:** Enter a question or command (e.g., “Write a Python function” or “Generate an image of a cat”).
- **Press Enter:** The selected personality will respond, leveraging the installed model.
## Step 5: Explore Features and Commands
Use the Help Command: Type help in the chat bar to see a list of available commands and features specific to your chosen personality.
Try Multimodal Tasks: Experiment with capabilities like:
- **Text-to-Image: “Create an image of a sunset.”
- **Speech-to-Text:** Upload audio (if supported by the persona).
- **Text-to-Music:** “Compose a melody from this poem.”
- **Advanced Features:** Access the Services Zoo (backend integrations) or Function Calls Zoo (custom actions) via the UI or documentation for complex workflows.
Troubleshooting
- **Installation Issues:** If the script fails, ensure Python 3.10+ and Git are installed (Linux) or check antivirus settings (Windows).
- **Model Loading:** Verify sufficient disk space and review logs if models don’t load Reddit Community for LoLLMs.
- **Community Support:** Seek help on Reddit or GitHub issues.
Tables for Clarity
| **Step**              | **Action**                                      | **Windows**                  | **Linux**                    |
|-----------------------|------------------------------------------------|-----------------------------|-----------------------------|
| Install               | Download and run setup script                  | Double-click `lollms_setup.bat` | `bash lollms_setup.sh`     |
| Launch Web UI         | Start the interface                            | Run `lollms.bat`            | `bash lollms.sh`           |
| Access UI             | Open browser to localhost                      | [http://localhost:7860](http://localhost:7860) | Same                   |

| **Component**         | **Description**                                              |
|-----------------------|--------------------------------------------------------------|
| Personalities Zoo     | Over 500 AI personas for specialized tasks                  |
| Services Zoo          | Backend services for API integrations, data processing       |
| Function Calls Zoo    | Callable functions for custom actions or workflows          |