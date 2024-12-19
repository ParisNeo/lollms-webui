import subprocess
from pathlib import Path

from ascii_colors import ASCIIColors
from lollms.paths import LollmsPaths

global_path = Path(__file__).parent.parent.parent / "global_paths_cfg.yaml"
ASCIIColors.yellow(f"global_path: {global_path}")
lollms_paths = LollmsPaths(global_path)
output_folder = lollms_paths.personal_outputs_path / "audio_out"

ASCIIColors.red(
    ".____    ________  .____    .____       _____    _________         ____  __________________________________ "
)
ASCIIColors.red(
    "|    |   \_____  \ |    |   |    |     /     \  /   _____/         \   \/  /\__    ___/\__    ___/   _____/ "
)
ASCIIColors.red(
    "|    |    /   |   \|    |   |    |    /  \ /  \ \_____  \   ______  \     /   |    |     |    |  \_____  \  "
)
ASCIIColors.red(
    "|    |___/    |    \    |___|    |___/    Y    \/        \ /_____/  /     \   |    |     |    |  /        \ "
)
ASCIIColors.red(
    "|_______ \_______  /_______ \_______ \____|__  /_______  /         /___/\  \  |____|     |____| /_______  / "
)
ASCIIColors.red(
    "        \/       \/        \/       \/       \/        \/                \_/                            \/  "
)

ASCIIColors.red(" Forked from daswer123's XTTS server")
ASCIIColors.red(" Integration in lollms by ParisNeo using daswer123's webapi ")

subprocess.Popen(
    [
        "python",
        "-m",
        "xtts_api_server",
        "-o",
        f"{output_folder}",
        "-sf",
        f"{lollms_paths.custom_voices_path}",
    ]
)
