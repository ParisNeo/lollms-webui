import json
import shutil
import subprocess
import time
from pathlib import Path
import os
import sys
import sysconfig # More reliable way to get script paths

import tqdm
from ascii_colors import ASCIIColors, get_trace_exception, trace_exception
from fastapi import APIRouter, FastAPI, File, Request, UploadFile, routing
# Assuming lollms imports are correct and available in the context
from lollms.client_session import Client
from lollms.databases.discussions_database import DiscussionsDB
from lollms.main_config import BaseConfig
from lollms.types import MSG_OPERATION_TYPE
from lollms.utilities import discussion_path_to_url
from pydantic import BaseModel
from starlette.responses import StreamingResponse

# Assuming lollmsElfServer instance is correctly obtained
from lollms_webui import LOLLMSWebUI
lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()


def execute_latex(code, client: Client, message_id):
    # Start the timer.
    start_time = time.time()

    # Create a temporary file.
    root_folder = client.discussion.discussion_folder
    root_folder.mkdir(parents=True, exist_ok=True)
    tmp_file = root_folder / f"latex_file_{message_id}.tex"
    with open(tmp_file, "w", encoding="utf-8") as f:
        f.write(code)

    pdf_file = tmp_file.with_suffix(".pdf")
    log_file = tmp_file.with_suffix(".log") # For potentially reading log output
    execution_path = tmp_file.parent

    # --- Prepare environment and command ---
    env = os.environ.copy()
    detailed_log_output = ""
    error_output = ""
    last_return_code = 0

    try:
        # 1. Find Python Scripts directory for Pygments
        scripts_dir = sysconfig.get_path('scripts')
        if scripts_dir and os.path.exists(scripts_dir):
            current_path = env.get('PATH', '')
            # Prepend script path - crucial for finding pygmentize
            new_path = f"{scripts_dir}{os.pathsep}{current_path}"
            env['PATH'] = new_path
            ASCIIColors.print(f"INFO: Added Python scripts path to subprocess PATH: {scripts_dir}", ASCIIColors.color_green)
        else:
            ASCIIColors.warning("Could not find Python scripts directory via sysconfig. 'pygmentize' might not be found if needed.")

        # 2. Determine pdflatex command
        if lollmsElfServer.config.pdf_latex_path and Path(lollmsElfServer.config.pdf_latex_path).exists():
            pdflatex_command = str(Path(lollmsElfServer.config.pdf_latex_path).resolve())
            ASCIIColors.print(f"INFO: Using configured pdflatex path: {pdflatex_command}", ASCIIColors.color_green)
        else:
            pdflatex_command = "pdflatex"
            ASCIIColors.print("INFO: Using default 'pdflatex' command from system PATH.", ASCIIColors.color_green)


        # 3. Check if minted package is used (heuristic)
        # We add shell-escape *only* if minted is likely used.
        use_shell_escape = r'\usepackage{minted}' in code
        if use_shell_escape:
             ASCIIColors.print("INFO: Detected '\\usepackage{minted}', enabling -shell-escape.", ASCIIColors.color_yellow)


        # 4. Construct base command list
        command = [
            pdflatex_command,
            # Add shell-escape ONLY if needed
            *(['-shell-escape'] if use_shell_escape else []),
            '-interaction=nonstopmode', # Prevent stopping on minor errors
            f'-output-directory={execution_path}', # Keep aux files together
            tmp_file.name # Just the filename, as we use cwd
        ]

        ASCIIColors.print(f"INFO: Running command: {' '.join(command)}", ASCIIColors.color_cyan)
        ASCIIColors.print(f"INFO: Working directory: {execution_path}", ASCIIColors.color_cyan)

        # 5. Execute pdflatex multiple times (max 3)
        max_runs = 3
        success = False
        for i in range(max_runs):
            ASCIIColors.print(f"--- pdflatex Pass {i+1}/{max_runs} ---", ASCIIColors.color_magenta)
            result = subprocess.run(
                command,
                cwd=execution_path,
                capture_output=True,
                text=True,
                encoding='utf-8', # Be explicit
                errors='replace', # Handle potential encoding issues in LaTeX logs
                env=env, # Pass the modified environment
                check=False # Don't raise exception on failure yet
            )
            last_return_code = result.returncode
            # Append log output for debugging
            detailed_log_output += f"\n--- Pass {i+1} stdout ---\n{result.stdout[-1500:]}" # Keep last part
            detailed_log_output += f"\n--- Pass {i+1} stderr ---\n{result.stderr}"

            if result.returncode == 0:
                ASCIIColors.print(f"INFO: Pass {i+1} successful.", ASCIIColors.color_green)
                # Check if PDF exists after first successful run
                if i==0 and not pdf_file.exists():
                    ASCIIColors.warning(f"WARNING: Pass 1 succeeded but {pdf_file.name} not found. LaTeX might have issues.")
                # Ideally, check aux file changes to see if another run is needed,
                # but for simplicity, we'll run up to max_runs or until first success
                # Check if pdf is generated
                if pdf_file.exists():
                    success = True
                    # break # Exit loop on first success generating pdf
                # else: continue, maybe next pass generates it
            else:
                ASCIIColors.error(f"ERROR: Pass {i+1} failed with return code {result.returncode}.")
                error_output = f"pdflatex failed on pass {i+1}.\n"
                # Attempt to read the log file for more detailed LaTeX errors
                try:
                    if log_file.exists():
                         error_output += f"Tail of {log_file.name}:\n...\n" + log_file.read_text(encoding='utf-8', errors='replace')[-1500:]
                except Exception as log_ex:
                    error_output += f"(Could not read log file: {log_ex})"
                # Include stderr as well
                if result.stderr:
                    error_output += "\nStderr:\n" + result.stderr

                break # Stop processing on first error

            # Optional: Check aux file stability here if needed

        # 6. Final check after loops
        if not success and not pdf_file.exists():
             ASCIIColors.error("ERROR: pdflatex finished but no PDF file was generated.")
             if not error_output: # If no error was explicitly caught above
                 error_output = "Compilation finished without errors, but no PDF was produced. Check LaTeX code and logs."
                 # Add log file tail if possible
                 try:
                     if log_file.exists():
                          error_output += f"\nTail of {log_file.name}:\n...\n" + log_file.read_text(encoding='utf-8', errors='replace')[-1500:]
                 except Exception as log_ex:
                     error_output += f"(Could not read log file: {log_ex})"


    except FileNotFoundError:
        trace_exception("pdflatex command not found")
        error_output = f"ERROR: '{pdflatex_command}' command not found. Is pdflatex installed and included in the system's or configured PATH?"
        last_return_code = -1 # Indicate command not found
    except Exception as ex:
        trace_exception(ex)
        error_output = f"An unexpected error occurred during LaTeX execution: {ex}"
        last_return_code = -2 # Indicate unexpected error

    # Stop the timer.
    execution_time = time.time() - start_time

    # --- Construct the response ---
    output_html = ""
    if pdf_file.exists():
        pdf_file_url_path = str(pdf_file).replace("\\", "/") # Ensure forward slashes
        if not lollmsElfServer.config.host.startswith(("http://", "https://")):
            host = "http://" + lollmsElfServer.config.host
        else:
            host = lollmsElfServer.config.host

        url = f"{host}:{lollmsElfServer.config.port}{discussion_path_to_url(pdf_file_url_path)}"
        output_html += f"<div>PDF file generated successfully: <a href='{url}' target='_blank'>{pdf_file.name}</a></div><br>"

    if last_return_code != 0:
        # Include error output if compilation failed or had issues
        output_html += f"<div class='text-red-500 font-semibold'>Execution failed (Code: {last_return_code})</div>"
        output_html += f"<div class='text-red-500 whitespace-pre-wrap'>{error_output}</div><br>"
        # Optionally include full logs for debugging
        output_html += (
            "<details><summary>View Full Compilation Log (Debug)</summary>"
            f"<pre class='text-xs whitespace-pre-wrap'>{detailed_log_output}</pre>"
            "</details>"
        )

    elif not pdf_file.exists():
         # Success code 0, but no PDF - should ideally be caught above, but double-check
        output_html += f"<div class='text-orange-500 font-semibold'>Warning: Compilation reported success, but no PDF file was found.</div>"
        output_html += (
            "<details><summary>View Compilation Log (Debug)</summary>"
            f"<pre class='text-xs whitespace-pre-wrap'>{detailed_log_output}</pre>"
            "</details>"
        )
    else:
        # Success and PDF exists
         output_html += f"<div class='text-green-500 font-semibold'>Compilation successful.</div>"
         # Optionally add logs even on success
         # output_html += (
         #    "<details><summary>View Compilation Log</summary>"
         #    f"<pre class='text-xs whitespace-pre-wrap'>{detailed_log_output}</pre>"
         #    "</details>"
         #)

    # Final JSON structure
    result_json = {
        "output": output_html,
        "execution_time": round(execution_time, 2),
    }
    return result_json

# Note: The original code had slightly different JSON structures for success/error.
# This version consolidates into one structure where the 'output' HTML string
# contains all relevant information (success link, errors, logs).