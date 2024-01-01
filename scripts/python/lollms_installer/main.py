from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
from lollms.paths import LollmsPaths
from lollms.utilities import check_and_install_torch, PackageManager
from pathlib import Path
from ascii_colors import ASCIIColors
import subprocess
from pathlib import Path

from starlette.responses import FileResponse
from starlette.requests import Request

root_path =Path(__file__).parent.parent.parent.parent
global_path = root_path/"global_paths_cfg.yaml"
ASCIIColors.yellow(f"global_path: {global_path}")
lollms_paths = LollmsPaths(global_path)
shared_folder = lollms_paths.personal_path/"shared"
sd_folder = shared_folder / "auto_sd"
output_dir = lollms_paths.personal_path / "outputs/sd"
output_dir.mkdir(parents=True, exist_ok=True)
script_path = sd_folder / "lollms_sd.bat"
output_folder = lollms_paths.personal_outputs_path/"audio_out"

ASCIIColors.red("                                     ")
ASCIIColors.red(" __    _____ __    __    _____ _____ ")
ASCIIColors.red("|  |  |     |  |  |  |  |     |   __|")
ASCIIColors.red("|  |__|  |  |  |__|  |__| | | |__   |")
ASCIIColors.red("|_____|_____|_____|_____|_|_|_|_____|")
ASCIIColors.red(" Configurator                        ")
ASCIIColors.red(" LoLLMS configuratoin tool")
ASCIIColors.yellow(f"Root dir : {root_path}")
app = FastAPI(debug=True)

class Item(BaseModel):
    name: str
    price: float

# Serve the index.html file for all routes
@app.get("/{full_path:path}")
async def serve_index(request: Request, full_path: Path):
    if str(full_path).endswith(".js"):
        return FileResponse(root_path/"scripts/python/lollms_installer/frontend/dist"/full_path, media_type="application/javascript")    
    return FileResponse(root_path/"scripts/python/lollms_installer/frontend/dist/index.html")

app.mount("/", StaticFiles(directory=root_path/"scripts/python/lollms_installer/frontend/dist"), name="static")

@app.post("/start_installing")
def start_installing(item: Item):

    # Your code here
    return {"message": "Item created successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)