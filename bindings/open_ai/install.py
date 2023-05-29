import subprocess
from pathlib import Path
import requests
from tqdm import tqdm
from api.config import save_config
import yaml
class Install:
    def __init__(self, api):
        # Get the current directory
        current_dir = Path(__file__).resolve().parent
        install_file = current_dir / ".installed"

        if not install_file.exists():
            print("-------------- OpenAI Binding -------------------------------")
            print("This is the first time you are using this binding.")
            print("Installing ...")
            # Step 2: Install dependencies using pip from requirements.txt
            requirements_file = current_dir / "requirements.txt"
            subprocess.run(["pip", "install", "--upgrade", "--no-cache-dir", "-r", str(requirements_file)])

            # Create the models folder
            models_folder = Path(f"./models/{Path(__file__).parent.stem}")
            models_folder.mkdir(exist_ok=True, parents=True)

            #Create 
            self._local_config_file_path = Path(__file__).parent/"config_local.yaml"
            if not self._local_config_file_path.exists():
                key = input("Please enter your Open AI Key")
                config={
                    "openai_key":key
                }
                self.config = save_config(config, self._local_config_file_path)
            #Create the install file (a file that is used to insure the installation was done correctly)
            with open(install_file,"w") as f:
                f.write("ok")
            print("Installed successfully")
            
    def reinstall_pytorch_with_cuda(self):
        """Installs pytorch with cuda (if you have a gpu) 
        """        
        subprocess.run(["pip", "install", "torch", "torchvision", "torchaudio", "--no-cache-dir", "--index-url", "https://download.pytorch.org/whl/cu117"])


    def create_config_file(self):
        """
        Create a config_local.yaml file with predefined data.

        The function creates a config_local.yaml file with the specified data. The file is saved in the parent directory
        of the current file.

        Args:
            None

        Returns:
            None
        """
        data = {
            "pdf_file_path":  "" # Path to the PDF that will be discussed
        }
        path = Path(__file__).parent.parent / 'config_local.yaml'
        with open(path, 'w') as file:
            yaml.dump(data, file)