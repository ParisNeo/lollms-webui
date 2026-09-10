######
# Project       : lollms
# File          : binding.py
# Author        : ParisNeo with the help of the community
# Underlying 
# engine author : llmman
# license       : Apache 2.0
# Description   : 
# Binding for llmman (https://github.com/llmmanorg/llmman), a local model runner that
# serves the Ollama API on port 17434; reuses the ollama_ai binding with a different address.
######
import importlib.util
import os
from pathlib import Path
from lollms.helpers import ASCIIColors

_spec = importlib.util.spec_from_file_location("ollama_ai", Path(__file__).parent.parent / "ollama_ai" / "__init__.py")
_ollama_ai = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_ollama_ai)

__author__ = "parisneo"
__github__ = "https://github.com/ParisNeo/lollms_bindings_zoo"
__copyright__ = "Copyright 2023, "
__license__ = "Apache 2.0"

binding_name = "Llmman"
binding_folder_name = ""

def _default_address():
    # llmman honours LLMMAN_HOST as [host][:port]; default bind is 127.0.0.1:17434
    host = os.environ.get("LLMMAN_HOST", "").strip() or "127.0.0.1:17434"
    if ":" not in host:
        host += ":17434"
    return host if host.startswith("http") else f"http://{host}"

class Llmman(_ollama_ai.Ollama):
    binding_path = Path(__file__).parent
    default_address = _default_address()

    def install(self):
        _ollama_ai.LLMBinding.install(self)
        ASCIIColors.success("Installed successfully")
        ASCIIColors.error("----------------------")
        ASCIIColors.error("Attention please")
        ASCIIColors.error("----------------------")
        ASCIIColors.error("You need to install llmman (https://github.com/llmmanorg/llmman) and start it with `llmman serve`.")

    def get_available_models(self, app=None):
        # llmman pulls OCI artifacts / hf.co models, not the Ollama library: list what the server has.
        try:
            model_names = self.list_models()
        except Exception as ex:
            ASCIIColors.warning(f"Couldn't list models from llmman server at {self.binding_config.address}: {ex}")
            model_names = []
        return [{
            "category": "generic",
            "datasets": "unknown",
            "icon": "",
            "last_commit_time": "2023-09-17 17:21:17+00:00",
            "license": "unknown",
            "model_creator": "",
            "model_creator_link": "https://github.com/llmmanorg/llmman",
            "name": name,
            "provider": None,
            "rank": "1.0",
            "type": "api",
            "variants": [{"name": name, "size": 0}]
        } for name in model_names]


if __name__=="__main__":
    from lollms.paths import LollmsPaths
    from lollms.main_config import LOLLMSConfig
    from lollms.app import LollmsApplication
    lollms_paths = LollmsPaths.find_paths(tool_prefix="",force_local=True, custom_default_cfg_path="configs/config.yaml")
    config = LOLLMSConfig.autoload(lollms_paths)
    lollms_app = LollmsApplication("",config, lollms_paths, False, False,False, False)

    oai = Llmman(config, lollms_paths,lollmsCom=lollms_app)
    oai.install()
    oai.binding_config.save()
    config.binding_name= "llmman"
    config.model_name="gemma4"
    config.save_config()
