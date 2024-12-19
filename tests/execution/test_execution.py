import platform
import subprocess
from pathlib import Path

from ascii_colors import get_trace_exception, trace_exception

if __name__ == "__main__":
    # Create a temporary file.
    code = "print('Hello world');input('hi')"
    message_id = 102
    root_folder = Path(r"E:\lollms\discussion_databases\html stuff\105")
    root_folder.mkdir(parents=True, exist_ok=True)
    tmp_file = root_folder / f"ai_code_{message_id}.py"
    with open(tmp_file, "w", encoding="utf8") as f:
        f.write(code)

    try:
        # Determine the platform and open a terminal to execute the Python code.
        system = platform.system()
        if system == "Windows":
            subprocess.Popen(
                f"""start cmd /k "cd /d {root_folder} && python {tmp_file} && pause" """,
                shell=True,
            )
        elif system == "Darwin":  # macOS
            subprocess.Popen(
                [
                    "open",
                    "-a",
                    "Terminal",
                    f'cd "{root_folder}" && python "{tmp_file}"',
                ],
                shell=True,
            )
        elif system == "Linux":
            subprocess.Popen(
                [
                    "x-terminal-emulator",
                    "-e",
                    f'bash -c "cd \\"{root_folder}\\" && python \\"{tmp_file}\\"; exec bash"',
                ],
                shell=True,
            )
        else:
            raise Exception(f"Unsupported platform: {system}")

    except Exception as ex:
        error_message = f"Error executing Python code: {ex}"
        error_json = {
            "output": "<div class='text-red-500'>"
            + error_message
            + "\n"
            + get_trace_exception(ex)
            + "</div>",
            "execution_time": 0,
        }
