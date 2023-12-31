from lollms.paths import LollmsPaths
from pathlib import Path
from ascii_colors import ASCIIColors
import subprocess

global_path = Path(__file__).parent.parent.parent/"global_paths_cfg.yaml"
ASCIIColors.yellow(f"global_path: {global_path}")
lollms_paths = LollmsPaths(global_path)
output_folder = lollms_paths.personal_outputs_path/"audio_out"
subprocess.Popen(["python", "-m", "xtts_api_server", "-o", f"{output_folder}", "-sf", f"{lollms_paths.custom_voices_path}"])