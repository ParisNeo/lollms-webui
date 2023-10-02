import subprocess
import signal
from lollms.helpers import get_trace_exception
from pathlib import Path
from lollms.helpers import ASCIIColors
from flask import request


def execute_python_code(self):
    """Executes Python code and returns the output."""
    
    data = request.get_json()
    code = data["code"]

    ASCIIColors.info("Executing python code:")
    ASCIIColors.yellow(code)

    def spawn_process(code):
        """Executes Python code and returns the output as JSON."""

        # Start the timer.
        start_time = time.time()

        # Create a temporary file.
        tmp_file = self.lollms_paths.personal_data_path/"ai_code.py"
        with open(tmp_file,"w") as f:
            f.write(code)

        try:
            # Execute the Python code in a temporary file.
            process = subprocess.Popen(
                ["python", str(tmp_file)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            # Get the output and error from the process.
            output, error = process.communicate()
        except Exception as ex:
            # Stop the timer.
            execution_time = time.time() - start_time
            error_message = f"Error executing Python code: {ex}"
            error_json = {"output": "<div class='text-red-500'>"+ex+"\n"+get_trace_exception(ex)+"</div>", "execution_time": execution_time}
            return json.dumps(error_json)

        # Stop the timer.
        execution_time = time.time() - start_time

        # Check if the process was successful.
        if process.returncode != 0:
            # The child process threw an exception.
            error_message = f"Error executing Python code: {error.decode('utf8')}"
            error_json = {"output": "<div class='text-red-500'>"+error_message+"</div>", "execution_time": execution_time}
            return json.dumps(error_json)

        # The child process was successful.
        output_json = {"output": output.decode("utf8"), "execution_time": execution_time}
        return json.dumps(output_json)
    return spawn_process(code)

def copy_files(self, src, dest):
    for item in os.listdir(src):
        src_file = os.path.join(src, item)
        dest_file = os.path.join(dest, item)
        
        if os.path.isfile(src_file):
            shutil.copy2(src_file, dest_file)
    

    
def reset(self):
    os.kill(os.getpid(), signal.SIGINT)  # Send the interrupt signal to the current process
    subprocess.Popen(['python', 'app.py'])  # Restart the app using subprocess

    return 'App is resetting...'


def find_extension(self, path:Path, filename:str, exts:list)->Path:
    for ext in exts:
        full_path = path/(filename+ext)
        if full_path.exists():
            return full_path
    return None

def restart_program(self):
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info(" ╔══════════════════════════════════════════════════╗")
    ASCIIColors.info(" ║              Restarting backend                  ║")
    ASCIIColors.info(" ╚══════════════════════════════════════════════════╝")
    ASCIIColors.info("")
    ASCIIColors.info("")
    ASCIIColors.info("")
    run_restart_script(self.args)