import subprocess
from pathlib import Path
import requests
from tqdm import tqdm
from api.config import save_config

class Install:
    def __init__(self, api):
        # Get the current directory
        current_dir = Path(__file__).resolve().parent
        install_file = current_dir / ".installed"

        if not install_file.exists():
            print("-------------- GPTQ binding -------------------------------")
            print("This is the first time you are using this binding.")
            print("Installing ...")
            # Example of installing py torche
            try:
                print("Checking pytorch")
                import torch
                import torchvision
                if torch.cuda.is_available():
                    print("CUDA is supported.")
                else:
                    print("CUDA is not supported. Reinstalling PyTorch with CUDA support.")
                    self.reinstall_pytorch_with_cuda()
            except Exception as ex:
                self.reinstall_pytorch_with_cuda()

            # Step 2: Install dependencies using pip from requirements.txt
            requirements_file = current_dir / "requirements.txt"
            subprocess.run(["pip", "install", "--upgrade", "--no-cache-dir", "-r", str(requirements_file)])

            # Create the models folder
            models_folder = Path(f"./models/{Path(__file__).parent.stem}")
            models_folder.mkdir(exist_ok=True, parents=True)

            # The local config can be used to store personal information that shouldn't be shared like chatgpt Key 
            # or other personal information
            # This file is never commited to the repository as it is ignored by .gitignore
            # You can remove this if you don't need custom local configurations
            """
            self._local_config_file_path = Path(__file__).parent/"config_local.yaml"
            if  not self._local_config_file_path.exists():
                config = {
                    #Put your default configurations here
                }
                save_config(config, self._local_config_file_path)
            """
            
            #Create the install file (a file that is used to insure the installation was done correctly)
            with open(install_file,"w") as f:
                f.write("ok")
            print("Installed successfully")
        
        
    def reinstall_pytorch_with_cuda(self):
        """Installs pytorch with cuda (if you have a gpu) 
        """
        subprocess.run(["pip", "install", "torch", "torchvision", "torchaudio", "--no-cache-dir", "--index-url", "https://download.pytorch.org/whl/cu117"])
        