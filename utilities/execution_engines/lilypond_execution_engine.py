"""
project: lollms_webui
file: lilypond_execution_engine.py 
author: LilyPond integration
description: 
    This is a utility for executing LilyPond code in LOLLMS
"""

import shutil
import subprocess
import time
from pathlib import Path

import pipmaster as pm
from ascii_colors import trace_exception
from lollms.client_session import Client
from lollms.utilities import discussion_path_to_url, show_yes_no_dialog

from lollms_webui import LOLLMSWebUI

lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()


def check_and_install_lilypond():
    """Check if LilyPond is installed and install it if needed"""
    if not pm.is_installed("lilypond"):
        if not show_yes_no_dialog(
            "Installation", "LilyPond is not installed. Do you want to install it?"
        ):
            return {"status": False, "error": "User refused LilyPond installation!"}
        try:
            pm.install("lilypond")
            return {"status": True}
        except Exception as ex:
            return {"status": False, "error": f"Failed to install LilyPond: {str(ex)}"}
    return {"status": True}


def execute_lilypond(code, client: Client, message_id):
    """Execute LilyPond code and return the result"""
    try:
        # Check LilyPond installation
        check_result = check_and_install_lilypond()
        if not check_result["status"]:
            return {"output": check_result["error"], "execution_time": 0}

        # Start timer
        start_time = time.time()

        # Import LilyPond after installation check
        import lilypond

        # Create work directory in discussion folder
        root_folder = client.discussion.discussion_folder
        root_folder.mkdir(parents=True, exist_ok=True)

        # Create LilyPond file
        ly_file = root_folder / f"score_{message_id}.ly"
        ly_file.write_text(code, encoding="utf8")

        # Get the PDF and MIDI outputs
        pdf_file = ly_file.with_suffix(".pdf")
        midi_file = ly_file.with_suffix(".mid")

        # Compile the file
        subprocess.run(
            [lilypond.executable(), str(ly_file)], check=True, cwd=root_folder
        )

        # Create links to files
        if (
            not "http" in lollmsElfServer.config.host
            and not "https" in lollmsElfServer.config.host
        ):
            host = "http://" + lollmsElfServer.config.host
        else:
            host = lollmsElfServer.config.host

        pdf_link = (
            f"{host}:{lollmsElfServer.config.port}{discussion_path_to_url(pdf_file)}"
        )
        midi_link = (
            f"{host}:{lollmsElfServer.config.port}{discussion_path_to_url(midi_file)}"
        )

        # Create output HTML
        output = f"""
        <div>
            <h3>LilyPond Output:</h3>
            <p><a href="{pdf_link}" target="_blank">View PDF Score</a></p>
            <p><a href="{midi_link}" target="_blank">Download MIDI</a></p>
            <embed src="{pdf_link}" type="application/pdf" width="100%" height="600px">
        </div>
        """

        execution_time = time.time() - start_time
        return {"output": output, "execution_time": execution_time}

    except Exception as ex:
        trace = trace_exception(ex)
        return {
            "output": f"Error executing LilyPond code:\n{trace}",
            "execution_time": 0,
        }
