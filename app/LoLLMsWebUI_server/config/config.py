from parser import parser
import shutil
from pathlib import Path


def make_config(lollms_paths):
    args = parser.parse_args()

    # Configuration loading part
    config = LOLLMSConfig.autoload(lollms_paths)

    # Override values in config with command-line arguments
    for arg_name, arg_value in vars(args).items():
        if arg_value is not None:
            config[arg_name] = arg_value

    # Copy user
    # Assuming the current file's directory contains the 'assets' subfolder
    current_file_dir = Path(__file__).parent
    assets_dir = current_file_dir / "assets"
    default_user_avatar = assets_dir / "default_user.svg"    
    user_avatar_path = lollms_paths.personal_user_infos_path / "default_user.svg"
    if not user_avatar_path.exists():
        # If the user avatar doesn't exist, copy the default avatar from the assets folder
        shutil.copy(default_user_avatar, user_avatar_path)
    # executor = ThreadPoolExecutor(max_workers=1)
    # app.config['executor'] = executor
    # Check if .no_gpu file exists
    no_gpu_file = Path('.no_gpu')
    if no_gpu_file.exists():
        # If the file exists, change self.config.use_gpu to False
        config.enable_gpu = False
        config.save_config()
        
        # Remove the .no_gpu file
        no_gpu_file.unlink()
    return config