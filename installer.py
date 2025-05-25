#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
from pathlib import Path # pathlib is part of Python's standard library
import importlib # For checking module availability without immediate import

# --- Bootstrap Dependencies ---
# Ensure PyYAML is installed for the installer itself.
# This block must be very early, before PyYAML is actually used.
# Structure: { "pip_package_name": "import_module_name" }
_INSTALLER_DEPENDENCIES_MAP = {"PyYAML": "yaml"}
_dependencies_installed_this_run = False

for pip_package_name, module_to_import in _INSTALLER_DEPENDENCIES_MAP.items():
    try:
        importlib.import_module(module_to_import)
    except ImportError:
        print(f"Installer dependency '{pip_package_name}' (module '{module_to_import}') not found. Attempting to install...")
        try:
            # Use check_call to ensure pip command succeeds
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_package_name])
            print(f"Successfully installed '{pip_package_name}'.")
            _dependencies_installed_this_run = True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install '{pip_package_name}' using pip.")
            print(f"Please try installing it manually:")
            print(f"  {sys.executable} -m pip install {pip_package_name}")
            print(f"Error details: {e}")
            sys.exit(1)
        except FileNotFoundError:
            # This means 'python -m pip' command failed, likely pip isn't installed or python path is wrong
            print(f"ERROR: Could not execute pip using '{sys.executable} -m pip'.")
            print(f"Please ensure pip is installed and accessible for this Python interpreter.")
            print(f"You might need to install/reinstall Python or manually install pip.")
            sys.exit(1)

if _dependencies_installed_this_run:
    print("Installer dependencies were installed. Restarting the installer script to load them...")
    # Re-execute the script with the same arguments
    # os.execv replaces the current process, ensuring the new env includes the installed package
    try:
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except Exception as e:
        print(f"ERROR: Failed to restart the script after installing dependencies: {e}")
        print("Please run the script again manually.")
        sys.exit(1)
    # The script will exit here if execv is successful

# Now we can safely import yaml
try:
    import yaml
except ImportError:
    # This should ideally not happen if the above block worked, but as a safeguard:
    print("ERROR: PyYAML dependency check/install failed.")
    print("Please ensure PyYAML is installed correctly ('pip install PyYAML') and try again.")
    sys.exit(1)


# --- Configuration ---
REPO_URL = "https://github.com/ParisNeo/lollms-webui.git"
# TARGET_PYTHON_VERSION will be set in main() based on the current interpreter
# ENV_NAME will be set later based on user choice


# --- Helper Functions ---

def print_notice(message):
    """Prints a formatted notice message."""
    print(f"\n--- {message} ---")

def print_success(message):
    """Prints a formatted success message."""
    print(f"\n✅ SUCCESS: {message}")

def print_warning(message):
    """Prints a formatted warning message."""
    print(f"\n⚠️ WARNING: {message}")

def print_error(message, exit_code=1):
    """Prints a formatted error message and optionally exits."""
    print(f"\n❌ ERROR: {message}")
    if exit_code is not None:
        sys.exit(exit_code)

def run_command(command, cwd=None, env=None, capture_output=True, text=True, check=True, shell=False, success_codes=(0,)):
    """
    Runs a shell command with enhanced error reporting and options.
    Allows specifying acceptable success codes.
    """
    command_str = ' '.join(command) if isinstance(command, list) else command
    print(f"\n> Running: {command_str}" + (f" in {cwd}" if cwd else ""))
    try:
        process = subprocess.run(
            command,
            cwd=cwd,
            env=env,
            capture_output=capture_output,
            text=text,
            check=False, # We check manually based on success_codes
            shell=shell, # Use shell=True cautiously
            encoding=sys.stdout.encoding if text else None, # Match console encoding
            errors='replace' if text else None
        )
        # Check if the return code is in the allowed success codes
        if check and process.returncode not in success_codes:
            stderr_output = process.stderr.strip() if process.stderr else ""
            stdout_output = process.stdout.strip() if process.stdout else ""
            error_message = f"Command failed with exit code {process.returncode}"
            if stderr_output:
                error_message += f"\nStderr:\n{stderr_output}"
            if stdout_output:
                 error_message += f"\nStdout:\n{stdout_output}" # Sometimes errors go to stdout
            print_error(error_message) # Exits by default

        # Print output even if successful, if captured
        if capture_output:
            if process.stdout: print(process.stdout.strip())
            # Also print stderr on success, as it might contain warnings
            if process.stderr: print("Stderr:", process.stderr.strip(), file=sys.stderr)

        return process
    except FileNotFoundError:
        print_error(f"Command not found: {command[0] if isinstance(command, list) else command.split()[0]}. Please ensure it's installed and in your PATH.")
    except subprocess.CalledProcessError as e: # Should be caught by manual check now, but keep as safety net
        stderr_output = e.stderr.strip() if e.stderr else ""
        stdout_output = e.stdout.strip() if e.stdout else ""
        print_error(f"Command failed unexpectedly with CalledProcessError exit code {e.returncode}:\n{stderr_output}\n{stdout_output}")
    except Exception as e:
        print_error(f"An unexpected error occurred while running command '{command_str}': {e}")

def check_command_exists(command_name):
    """Checks if a command exists using a simple version/help flag."""
    print(f"> Checking for command: {command_name}...")
    is_windows = platform.system() == "Windows"
    # Common flags that usually work without side effects
    test_flags = ['--version', 'version', '--help', 'help']
    
    cmd_found = False
    for flag in test_flags:
        try:
            cmd_to_run = [command_name, flag]
            # Some commands might need shell=True on Windows (like conda sometimes)
            use_shell = is_windows and command_name in ["conda"]
            
            process = subprocess.run(
                cmd_to_run,
                capture_output=True,
                text=True,
                check=False, # Don't exit on non-zero, just check return code
                shell=use_shell,
                timeout=5 # Add a timeout to prevent hangs
            )
            # Success if FileNotFoundError is not raised and return code is often 0 for version/help
            # Some help flags might return non-zero, so mainly rely on not getting FileNotFoundError
            cmd_found = True 
            break # Found it, no need to try other flags
        except FileNotFoundError:
            continue # Try next flag or fail if no flags work
        except subprocess.TimeoutExpired:
            print_warning(f"Checking command '{command_name}' timed out.")
            continue # Command might exist but is unresponsive
        except Exception: # Catch any other potential errors during check
            continue

    if cmd_found:
        print(f"  '{command_name}' seems to be available.")
        return True
    else:
        print(f"  '{command_name}' not found or not executable in PATH.")
        return False

def get_user_path(prompt, default=None, must_exist=False, create_if_not_exist=False):
    """Gets a valid path from the user with prompts and validation."""
    while True:
        default_prompt = f" (Enter for default: '{default}')" if default else ""
        user_input = input(f"{prompt}{default_prompt}: ").strip()

        if not user_input and default:
            user_input = default
        elif not user_input:
            print_warning("Path cannot be empty.")
            continue

        try:
            # Expand ~ and resolve .. etc., make absolute
            path = Path(user_input).expanduser().resolve()

            if must_exist and not path.exists():
                 print_warning(f"Path does not exist: {path}")
                 continue

            if create_if_not_exist and not path.exists():
                try:
                    # Create directories recursively, ok if they already exist
                    path.mkdir(parents=True, exist_ok=True)
                    print(f"  Created directory: {path}")
                except PermissionError:
                     print_warning(f"Permission denied: Could not create directory {path}")
                     continue # Ask again
                except Exception as e:
                    print_warning(f"Could not create directory {path}: {e}")
                    continue # Ask again

            # Additional check: write permission for the target/parent directory
            check_dir = path if path.is_dir() else path.parent
            if not os.access(check_dir, os.W_OK):
                 print_warning(f"No write permission in directory: {check_dir}")
                 if create_if_not_exist and not path.exists():
                      print_warning(f"Directory {path} was created, but writing inside might still fail.")
                 elif not must_exist:
                     # Warn user if they are selecting a dir they can't write into
                      pass
                 else:
                     continue # If it must exist and we can't write, ask again


            return path
        except Exception as e:
            # Catch potential errors during path resolution/manipulation
            print_warning(f"Invalid path entered or error processing path: {e}")

def get_python_executable_path(env_base_path, env_manager, lollms_webui_root, env_name):
    """
    Gets the path to the Python executable within the created environment.
    env_base_path: The directory *of* the environment (for venv/uv) or the root *containing* envs (for conda/pyenv)
    lollms_webui_root: The root directory where lollms-webui is being installed.
    env_name: The specific name of the environment being used.
    """
    system = platform.system()
    is_windows = system == "Windows"
    python_exe_path = None

    print(f"> Locating Python executable for '{env_name}' using '{env_manager}'...")

    if env_manager == "conda":
        # Conda envs can be in standard location or specified with --prefix
        try:
            # Check standard location first
            conda_base_result = run_command(['conda', 'info', '--base'], capture_output=True, text=True, check=True, shell=is_windows)
            conda_base = Path(conda_base_result.stdout.strip())
            standard_env_path = conda_base / "envs" / env_name
            
            # Check if env exists at standard path
            if standard_env_path.exists() and (standard_env_path / ("python.exe" if is_windows else "bin/python")).exists():
                 env_path = standard_env_path
            else:
                 # If not standard, parse `conda env list --json` for the specific env name
                 result = run_command(['conda', 'env', 'list', '--json'], capture_output=True, text=True, check=True, shell=is_windows)
                 import json # Safe because yaml depends on json
                 envs_info = json.loads(result.stdout)
                 env_dirs = envs_info.get('envs', [])
                 found_path_str = next((p for p in env_dirs if Path(p).name == env_name or Path(p).resolve() == Path(env_name).resolve()), None) # Check name or if absolute path matches

                 if found_path_str:
                      env_path = Path(found_path_str)
                 else:
                      # Check if it was created inside the project dir (e.g., --prefix ./)
                      prefix_env_path = lollms_webui_root / env_name
                      if prefix_env_path.exists() and (prefix_env_path / "conda-meta").exists():
                           env_path = prefix_env_path
                      else:
                           print_warning(f"Could not reliably determine Conda environment path for '{env_name}'. Looked in standard location, parsed env list, and checked project dir.")
                           print_warning(f"Falling back to standard path guess: {standard_env_path}")
                           env_path = standard_env_path # Might not exist yet if creation failed

            # Determine python executable within the found env_path
            if is_windows:
                py_exe = env_path / "python.exe"
            else:
                py_exe = env_path / "bin" / "python"

            if py_exe.exists():
                python_exe_path = py_exe
            else:
                 print_warning(f"Python executable not found at expected Conda location: {py_exe}")

        except Exception as e:
            print_warning(f"Error determining Conda environment path: {e}. Attempting fallback structure.")
            # Fallback based on expected base structure if info commands fail
            conda_prefix_env_var = os.environ.get("CONDA_PREFIX")
            conda_base = Path(conda_prefix_env_var).parent.parent if conda_prefix_env_var else Path.home() / "miniconda3" # Very rough guess
            env_path = conda_base / "envs" / env_name
            if is_windows:
                 python_exe_path = env_path / "python.exe"
            else:
                 python_exe_path = env_path / "bin" / "python"


    elif env_manager == "pyenv":
         # pyenv virtualenvs are typically located in $(pyenv root)/versions/<env_name>
         try:
            pyenv_root_result = run_command(['pyenv', 'root'], capture_output=True, text=True, check=True, shell=is_windows)
            pyenv_root = Path(pyenv_root_result.stdout.strip())
            env_path = pyenv_root / "versions" / env_name

            if is_windows:
                # pyenv-win structure might place python directly in env path or Scripts
                py_exe_scripts = env_path / "Scripts" / "python.exe"
                py_exe_direct = env_path / "python.exe"
                if py_exe_scripts.exists():
                    python_exe_path = py_exe_scripts
                elif py_exe_direct.exists():
                     python_exe_path = py_exe_direct
                else:
                     print_warning(f"Python executable not found at expected pyenv-win locations: {py_exe_scripts} or {py_exe_direct}")
            else:
                py_exe = env_path / "bin" / "python"
                if py_exe.exists():
                    python_exe_path = py_exe
                else:
                     print_warning(f"Python executable not found at expected pyenv location: {py_exe}")

         except Exception as e:
            print_warning(f"Could not determine pyenv root or structure: {e}. Assuming standard structure.")
            # Fallback structure guess
            pyenv_root_default_unix = Path.home() / ".pyenv"
            pyenv_root_default_windows = Path.home() / ".pyenv" / "pyenv-win" # Common for pyenv-win
            pyenv_root = pyenv_root_default_windows if is_windows else pyenv_root_default_unix
            
            env_path = pyenv_root / "versions" / env_name
            if is_windows:
                 python_exe_path = env_path / "Scripts" / "python.exe" # Assume Scripts dir
            else:
                 python_exe_path = env_path / "bin" / "python"

    elif env_manager in ["venv", "uv"]:
        # env_base_path *is* the environment directory for these managers
        # Ensure env_base_path itself exists before checking inside it
        if not env_base_path or not env_base_path.is_dir():
             print_warning(f"Environment directory not found or is not a directory: {env_base_path}")
             return None # Cannot find python if env dir doesn't exist

        if is_windows:
            py_exe = env_base_path / "Scripts" / "python.exe"
        else:
            py_exe = env_base_path / "bin" / "python"

        if py_exe.exists():
            python_exe_path = py_exe
        else:
             print_warning(f"Python executable not found at expected venv/uv location: {py_exe}")


    if python_exe_path and python_exe_path.exists():
        print(f"  Python executable identified: {python_exe_path}")
        return python_exe_path.resolve() # Return resolved absolute path
    else:
        print_error(f"Could not find Python executable for environment '{env_name}' using {env_manager}.\n"
                    f"Expected location based on detection: {python_exe_path if python_exe_path else 'unknown'}\n"
                    "Please check if the environment was created successfully and the path is correct.",
                    exit_code=None) # Let main function handle exit
        return None


# --- Main Installation Logic ---

def main():
    """Main function orchestrating the installation process."""
    global ENV_NAME # Allow modifying the global ENV_NAME
    
    # Determine the Python version of the current interpreter
    current_python_major = sys.version_info.major
    current_python_minor = sys.version_info.minor
    TARGET_PYTHON_VERSION = f"{current_python_major}.{current_python_minor}"

    print_notice("Starting LoLLMs WebUI Installer")
    print(f"Installer running with Python: {sys.version.split()[0]} (Targeting this version: {TARGET_PYTHON_VERSION}) at {sys.executable}")
    print(f"Operating System: {platform.system()} ({platform.release()})")


    # 1. Prerequisites Check
    print_notice("Checking Prerequisites")
    if not check_command_exists("git"):
        print_error("Git is not installed or not found in PATH. Please install Git and ensure it's accessible from your terminal.")

    # 2. User Input
    print_notice("Getting Installation Paths")
    default_install_dir = Path.cwd() / "lollms-webui"
    lollms_webui_path = get_user_path(
        "Enter the directory to install lollms-webui into (will be created if needed)",
        default=str(default_install_dir),
        create_if_not_exist=False # Let git clone create the final dir, but check parent write access
    )

    # Check write access in parent of install dir BEFORE proceeding
    if not os.access(lollms_webui_path.parent, os.W_OK):
         print_error(f"No write permission in the parent directory: {lollms_webui_path.parent}. Cannot clone/install here.")

    default_personal_path = Path.home() / "lollms_data"
    lollms_personal_path = get_user_path(
        "Enter the directory for your personal LoLLMs data (models, configs, db, etc.)",
        default=str(default_personal_path),
        create_if_not_exist=True # Create this directory if it doesn't exist
    )

    print_notice("Choosing Python Environment Manager")
    managers = ["conda", "pyenv", "venv", "uv"]
    print("Select the Python environment manager to use:")
    for i, manager in enumerate(managers):
        print(f"  {i+1}. {manager}")

    env_manager = None
    while env_manager not in managers:
        try:
            choice_str = input(f"Enter selection (1-{len(managers)}): ")
            if not choice_str:
                print_warning("Please make a selection.")
                continue
            choice = int(choice_str) - 1
            if 0 <= choice < len(managers):
                # Check if chosen manager command exists
                if check_command_exists(managers[choice]):
                    env_manager = managers[choice]
                else:
                     print_warning(f"{managers[choice]} command not found. Please install it or choose a different manager.")
            else:
                print_warning("Invalid choice number.")
        except ValueError:
            print_warning("Please enter a number.")

    print(f"Selected environment manager: {env_manager}")
    # Make environment name specific to the manager and installation directory base name
    ENV_NAME = f"lollms_{lollms_webui_path.name}_{env_manager}_py{TARGET_PYTHON_VERSION.replace('.', '')}_env"


    # 3. Environment Setup
    print_notice(f"Setting up Python {TARGET_PYTHON_VERSION} environment '{ENV_NAME}' using {env_manager}")

    env_dir_location = None 
    python_exe_path = None
    activation_commands = { 
        "Windows": [],
        "Linux": [],
        "Darwin": [] 
    }
    is_windows = platform.system() == "Windows"

    if env_manager == "conda":
        print(f"> Checking if Conda environment '{ENV_NAME}' exists...")
        try:
            result = run_command(['conda', 'env', 'list', '--json'], capture_output=True, text=True, check=True, shell=is_windows)
            import json
            envs_info = json.loads(result.stdout)
            env_exists = any(Path(p).name == ENV_NAME for p in envs_info.get('envs', []))
        except Exception as e:
            print_warning(f"Could not accurately check if conda env '{ENV_NAME}' exists: {e}. Proceeding with creation attempt.")
            env_exists = False 

        if not env_exists:
            print(f"> Creating Conda environment '{ENV_NAME}' with Python {TARGET_PYTHON_VERSION}...")
            run_command(['conda', 'create', '-n', ENV_NAME, f'python={TARGET_PYTHON_VERSION}', '-y'], shell=is_windows, check=True)
        else:
            print(f"  Conda environment '{ENV_NAME}' already exists. Verifying Python version...")
            temp_python_path = get_python_executable_path(None, env_manager, lollms_webui_path, ENV_NAME)
            if temp_python_path:
                try:
                    version_result = run_command([str(temp_python_path), '--version'], capture_output=True, text=True, check=True)
                    output = version_result.stdout + version_result.stderr 
                    if f"Python {TARGET_PYTHON_VERSION}" not in output:
                         print_warning(f"Existing env '{ENV_NAME}' has Python {output.split()[1]}, not {TARGET_PYTHON_VERSION}.")
                    else:
                        print(f"  Python version {TARGET_PYTHON_VERSION} confirmed.")
                except Exception as e:
                    print_warning(f"Could not verify Python version in existing env '{ENV_NAME}': {e}")
            else:
                 print_warning(f"Could not get Python path for existing env '{ENV_NAME}' to verify version.")

        python_exe_path = get_python_executable_path(None, env_manager, lollms_webui_path, ENV_NAME)
        if python_exe_path: # env_dir_location is the directory *containing* the python executable
            env_dir_path_for_conda = python_exe_path.parent 
            if not is_windows: # for non-windows, python is in env_dir/bin/python
                env_dir_path_for_conda = env_dir_path_for_conda.parent
            env_dir_location = env_dir_path_for_conda


        activation_commands["Windows"] = [f"conda activate {ENV_NAME}"]
        conda_base_path_str = ""
        try:
            conda_base_result = run_command(['conda', 'info', '--base'], capture_output=True, text=True, check=True, shell=is_windows)
            conda_base_path_str = conda_base_result.stdout.strip()
        except Exception: pass 

        if not is_windows and conda_base_path_str:
             conda_activate_script = Path(conda_base_path_str) / "bin" / "activate"
             activation_commands["Linux"] = [f"source \"{conda_activate_script}\" {ENV_NAME}"]
             activation_commands["Darwin"] = [f"source \"{conda_activate_script}\" {ENV_NAME}"]
        elif not is_windows: 
             activation_commands["Linux"] = [f"conda activate {ENV_NAME} # May require conda init in shell profile"]
             activation_commands["Darwin"] = [f"conda activate {ENV_NAME} # May require conda init in shell profile"]


    elif env_manager == "pyenv":
        if is_windows:
             print_warning("pyenv support on native Windows (pyenv-win) can be experimental. Ensure it's correctly set up.")

        print(f"> Checking available pyenv Python versions for {TARGET_PYTHON_VERSION}...")
        try:
            result = run_command(['pyenv', 'versions', '--bare'], capture_output=True, text=True, check=True, shell=is_windows)
            installed_pythons = [v.strip() for v in result.stdout.strip().split('\n') if v.strip()]
        except Exception as e:
             print_error(f"Failed to list pyenv versions: {e}. Is pyenv installed and configured?")

        target_python_base_version = next((v for v in installed_pythons if v.startswith(TARGET_PYTHON_VERSION)), None)

        if not target_python_base_version:
            print(f"! No installed pyenv Python found matching {TARGET_PYTHON_VERSION}.x.")
            print(f"  Attempting to find and install the latest Python {TARGET_PYTHON_VERSION} via pyenv...")
            try:
                install_list_cmd = ['pyenv', 'install', '--list']
                install_list_result = run_command(install_list_cmd, capture_output=True, text=True, check=True, shell=is_windows)
                available_versions = [line.strip() for line in install_list_result.stdout.splitlines() if line.strip().startswith(TARGET_PYTHON_VERSION)]
                stable_versions = [v for v in available_versions if not any(tag in v for tag in ['dev', 'rc', 'a', 'b'])]
                version_to_install = stable_versions[-1] if stable_versions else (available_versions[-1] if available_versions else None)

                if not version_to_install:
                    print_error(f"Could not find any suitable {TARGET_PYTHON_VERSION}.x version to install with 'pyenv install --list'.")

                print(f"  Found '{version_to_install}' as candidate. Attempting installation (this may take a while)...")
                run_command(['pyenv', 'install', version_to_install], shell=is_windows, check=True) 
                target_python_base_version = version_to_install 
            except Exception as e:
                 print_error(f"pyenv install failed: {e}.\nPlease install Python {TARGET_PYTHON_VERSION}.x manually using 'pyenv install <version>' first.")

        print(f"  Using pyenv Python base version: {target_python_base_version}")

        print(f"> Checking if pyenv virtualenv '{ENV_NAME}' (based on {target_python_base_version}) exists...")
        try:
            result = run_command(['pyenv', 'versions', '--bare'], capture_output=True, text=True, check=True, shell=is_windows)
            installed_pythons_and_venvs = [v.strip() for v in result.stdout.strip().split('\n') if v.strip()]
        except Exception as e:
            print_error(f"Failed to list pyenv versions after install check: {e}.")

        if ENV_NAME not in installed_pythons_and_venvs:
            print(f"> Creating pyenv virtualenv '{ENV_NAME}' based on {target_python_base_version}...")
            run_command(['pyenv', 'virtualenv', target_python_base_version, ENV_NAME], shell=is_windows, check=True)
        else:
             print(f"  pyenv virtualenv '{ENV_NAME}' already exists. Skipping creation.")

        python_exe_path = get_python_executable_path(None, env_manager, lollms_webui_path, ENV_NAME)
        if python_exe_path: # env_dir_location is the directory *containing* the python executable
             env_dir_path_for_pyenv = python_exe_path.parent 
             if not is_windows: # for non-windows, python is in env_dir/bin/python
                 env_dir_path_for_pyenv = env_dir_path_for_pyenv.parent
             env_dir_location = env_dir_path_for_pyenv

        activation_commands["Windows"] = [f"pyenv activate {ENV_NAME} # May require pyenv-win shell integration"]
        pyenv_init_lines = [
            'export PYENV_ROOT="$HOME/.pyenv"',
            'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"',
            'eval "$(pyenv init -)"',
            'eval "$(pyenv virtualenv-init -)"'
        ]
        activation_commands["Linux"] = pyenv_init_lines + [f"pyenv activate {ENV_NAME}"]
        activation_commands["Darwin"] = pyenv_init_lines + [f"pyenv activate {ENV_NAME}"]


    elif env_manager in ["venv", "uv"]:
        env_dir_location = lollms_webui_path / ".venv" 
        env_exists = env_dir_location.is_dir() and (env_dir_location / "pyvenv.cfg").exists()

        if not env_exists:
            print(f"> Creating {env_manager} virtual environment at: {env_dir_location}")
            env_dir_location.parent.mkdir(parents=True, exist_ok=True)

            if env_manager == "venv":
                 print(f"> Using current Python interpreter ({sys.executable}, version {TARGET_PYTHON_VERSION}) to create venv.")
                 # sys.executable is the python running this script.
                 # Using it directly ensures the venv uses this Python version.
                 run_command([sys.executable, '-m', 'venv', str(env_dir_location)], check=True)

            elif env_manager == "uv":
                 try:
                      run_command(['uv', 'venv', str(env_dir_location), '--python', TARGET_PYTHON_VERSION], check=True)
                 except subprocess.CalledProcessError as e:
                      stderr_lower = (e.stderr or "").lower()
                      stdout_lower = (e.stdout or "").lower()
                      if "could not find python interpreter" in stderr_lower or \
                         "failed to find python" in stderr_lower or \
                         "could not find python interpreter" in stdout_lower or \
                         "failed to find python" in stdout_lower:
                           print_warning(f"uv could not automatically find Python {TARGET_PYTHON_VERSION}.")
                           print_warning("Attempting to create uv venv using uv's default/system Python.")
                           print_warning(f"The resulting environment might not use Python {TARGET_PYTHON_VERSION}.")
                           try:
                               run_command(['uv', 'venv', str(env_dir_location)], check=True)
                           except Exception as inner_e:
                                print_error(f"Failed to create uv venv even with default Python: {inner_e}")
                      else:
                            print_error(f"uv venv creation failed: {e.stderr or e.stdout or e}")

        else:
            print(f"  {env_manager} virtual environment already exists at: {env_dir_location}. Checking Python version...")
            # For venv/uv, env_dir_location *is* the env_base_path
            temp_python_path = get_python_executable_path(env_dir_location, env_manager, lollms_webui_path, env_dir_location.name) 
            if temp_python_path:
                 try:
                    version_result = run_command([str(temp_python_path), '--version'], capture_output=True, text=True, check=True)
                    output = version_result.stdout + version_result.stderr
                    if f"Python {TARGET_PYTHON_VERSION}" not in output:
                         print_warning(f"Existing env '{env_dir_location.name}' has Python {output.split()[1]}, not {TARGET_PYTHON_VERSION}.")
                    else:
                        print(f"  Python version {TARGET_PYTHON_VERSION} confirmed.")
                 except Exception as e:
                     print_warning(f"Could not verify Python version in existing env '{env_dir_location.name}': {e}")
            else:
                print_warning("Could not get Python path for existing env to verify version.")
        
        # For venv/uv, env_dir_location is the base path of the environment.
        python_exe_path = get_python_executable_path(env_dir_location, env_manager, lollms_webui_path, env_dir_location.name)

        if is_windows:
            activate_script = env_dir_location / "Scripts" / "activate.bat"
            activation_commands["Windows"] = [f'CALL "{activate_script}"']
        else:
            activate_script = env_dir_location / "bin" / "activate"
            activation_commands["Linux"] = [f'source "{activate_script}"']
            activation_commands["Darwin"] = [f'source "{activate_script}"']

    if not python_exe_path or not Path(python_exe_path).exists():
         print_error(f"Failed to create or locate the Python executable for environment '{ENV_NAME}'. Installation cannot proceed.")
    if not env_dir_location or not Path(env_dir_location).exists():
         print_warning(f"Environment directory location ({env_dir_location}) seems invalid after setup attempt. This might be okay if '{env_manager}' manages envs globally.")


    # 4. Repository Handling
    print_notice("Handling LoLLMs WebUI Repository")
    lollms_webui_path.parent.mkdir(parents=True, exist_ok=True) 

    git_dir = lollms_webui_path / ".git"
    if not git_dir.is_dir(): 
        if lollms_webui_path.exists() and any(lollms_webui_path.iterdir()):
            print_warning(f"Target directory '{lollms_webui_path}' exists and is not empty, but is not a git repository.")
            if input("  Clone into this directory anyway? (Existing files might conflict) [y/N]: ").lower().strip() != 'y':
                print_error("Installation aborted. Please choose an empty directory or a valid git repository.", exit_code=0)

        print(f"> Cloning LoLLMs WebUI from {REPO_URL} into {lollms_webui_path}...")
        run_command(['git', 'clone', '--recurse-submodules', REPO_URL, str(lollms_webui_path)], check=True)
    else:
        print(f"> Repository already exists at {lollms_webui_path}.")
        update_choice = input("  Do you want to attempt to update it? (git pull & submodule update --remote) [y/N]: ").lower().strip()
        if update_choice == 'y':
            print("> Stashing local changes (if any)...")
            run_command(['git', 'stash', 'push', '-m', 'lollms-installer-stash'], cwd=lollms_webui_path, check=False, success_codes=(0,1)) 

            print("> Pulling latest changes from origin...")
            run_command(['git', 'pull'], cwd=lollms_webui_path, check=True) 

            print("> Updating submodules (fetching remote changes)...")
            run_command(['git', 'submodule', 'update', '--init', '--recursive', '--remote'], cwd=lollms_webui_path, check=True)

            print("> Restoring stashed changes (if any)...")
            stash_apply_result = run_command(['git', 'stash', 'pop'], cwd=lollms_webui_path, check=False) 
            if stash_apply_result.returncode != 0:
                 print_warning("Could not automatically apply stashed changes. You may need to resolve conflicts manually in git.")
                 print_warning("Run 'git stash list' and 'git stash apply' in the repo directory.")
        else:
            print("> Ensuring submodules are initialized and updated (without fetching remote)...")
            run_command(['git', 'submodule', 'update', '--init', '--recursive'], cwd=lollms_webui_path, check=True)


    # 5. Dependency Installation within the environment
    print_notice(f"Installing Dependencies into '{ENV_NAME}' environment")
    requirements_file = lollms_webui_path / "requirements.txt"
    lollms_core_dir = lollms_webui_path / "lollms_core"

    if not requirements_file.is_file():
        print_error(f"requirements.txt not found in {lollms_webui_path}. Repository clone or update likely failed.")
    if not lollms_core_dir.is_dir() or not (lollms_core_dir / "setup.py").is_file():
         print_error(f"lollms_core submodule directory or its setup.py not found in {lollms_webui_path}. Submodule handling likely failed.")

    print(f"> Installing base packages from requirements.txt using {python_exe_path}...")
    pip_cmd_base = [str(python_exe_path), '-m', 'pip', 'install', '--upgrade'] 
    
    # Check if 'uv' command exists and if we are using 'uv' as the env_manager
    # This check_command_exists will print its own status messages
    uv_is_available_for_pip = env_manager == "uv" and check_command_exists("uv")
    
    uv_cmd_base = ['uv', 'pip', 'install'] 
    # If using uv, we need to specify the python interpreter for uv pip install if not activated
    # However, if python_exe_path points to uv's python, this might not be strictly needed by uv,
    # but it's safer to be explicit if uv supports a --python flag for its pip subcommand.
    # Assuming uv pip install can use the environment context if python_exe_path is the env's python.
    # If python_exe_path is correctly set up by uv env, then `str(python_exe_path) -m pip install` should work.
    # If we want to use `uv pip install`, we should ensure it targets the correct environment.
    # The `uv venv` command creates an env, then `uv pip install -p <path_to_python>` can target it.
    # Or, if the env is activated, `uv pip install` might just work.
    # For simplicity and robustness with python_exe_path:
    
    install_cmd_base = pip_cmd_base # Default to python -m pip
    if uv_is_available_for_pip:
        print("> 'uv' is available, will attempt to use 'uv pip install'.")
        # Ensure uv targets the correct Python environment.
        # If python_exe_path is from a uv-managed venv, uv might auto-detect or use it.
        # Explicitly: 'uv pip install --python <path_to_python_in_uv_env>'
        install_cmd_base = ['uv', 'pip', 'install', '--python', str(python_exe_path)]
        # If --python is not supported by uv pip install or causes issues,
        # one might need to ensure the environment is "active" for uv,
        # or stick to `python_exe_path -m pip install`.
        # Given `uv venv --python <version>` was used, this python_exe_path should be the target.


    req_install_cmd = install_cmd_base + ['-r', str(requirements_file)]
    print(f"  Using command: {' '.join(req_install_cmd)}")
    run_command(req_install_cmd, cwd=lollms_webui_path, check=True) 


    print(f"> Installing lollms_core submodule in editable mode using {python_exe_path}...")
    core_install_cmd = install_cmd_base + ['-e', str(lollms_core_dir)]
    print(f"  Using command: {' '.join(core_install_cmd)}")
    run_command(core_install_cmd, cwd=lollms_webui_path, check=True) 


    # 6. Configuration File Generation
    print_notice("Creating Configuration File")
    lollms_core_lollms_path = lollms_core_dir / "lollms"
    if not lollms_core_lollms_path.is_dir():
        print_error(f"Could not find the core lollms library directory expected at: {lollms_core_lollms_path}")

    config_data = {
        "lollms_path": str(lollms_core_lollms_path.resolve()).replace("\\", "/"),
        "lollms_personal_path": str(lollms_personal_path.resolve()).replace("\\", "/")
    }
    config_file_path = lollms_webui_path / "global_paths_cfg.yaml"

    print(f"> Writing configuration to: {config_file_path}")
    print(f"  lollms_path: {config_data['lollms_path']}")
    print(f"  lollms_personal_path: {config_data['lollms_personal_path']}")

    try:
        with open(config_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print_success("Configuration file 'global_paths_cfg.yaml' created.")
    except Exception as e:
        print_error(f"Failed to write configuration file '{config_file_path}': {e}")


    # 7. Starter Script Creation
    print_notice("Creating Starter Script")
    current_system_os = platform.system() 
    starter_content = ""
    script_name = ""
    app_script_path = lollms_webui_path / "app.py"

    current_os_activation_lines = activation_commands.get(current_system_os, [])
    if not current_os_activation_lines:
        print_warning(f"Could not determine specific activation commands for {current_system_os}.")
        fallback_info = f"# Please manually activate the '{ENV_NAME}' {env_manager} environment before running 'python app.py'"
        if is_windows:
             fallback_info = f"REM Please manually activate the '{ENV_NAME}' {env_manager} environment before running 'python app.py'"
        current_os_activation_lines = [fallback_info]


    if current_system_os == "Windows":
        script_name = "start_lollms.bat"
        starter_content = f"""@echo off
REM LoLLMs WebUI Starter Script - Generated by lollms-installer
echo Activating Python environment '{ENV_NAME}' (Python {TARGET_PYTHON_VERSION}) using {env_manager}...
{os.linesep.join(current_os_activation_lines)}

echo Starting LoLLMs WebUI...
cd /D "%~dp0"
echo Current directory: %CD%
echo Running: "{python_exe_path}" "{app_script_path}" %*

"{python_exe_path}" "{app_script_path}" %*

echo.
echo LoLLMs WebUI stopped.
if [%1]==[] (
    echo Press any key to exit.
    pause > nul
)
"""
    else: 
        script_name = "start_lollms.sh"
        quoted_python_exe = f'"{python_exe_path}"'
        quoted_app_script = f'"{app_script_path}"'
        quoted_webui_path = f'"{lollms_webui_path}"'

        starter_content = f"""#!/bin/bash
# LoLLMs WebUI Starter Script - Generated by lollms-installer

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

echo "Activating Python environment '{ENV_NAME}' (Python {TARGET_PYTHON_VERSION}) using {env_manager}..."
{os.linesep.join(current_os_activation_lines)} || {{ echo "Activation failed, proceeding might not work."; }}

echo "Starting LoLLMs WebUI from {quoted_webui_path}..."
cd "{quoted_webui_path}" || {{ echo "ERROR: Failed to change directory to {quoted_webui_path}"; exit 1; }}

echo "Current directory: $(pwd)"
echo "Running: {quoted_python_exe} {quoted_app_script} \"$@\""

{quoted_python_exe} {quoted_app_script} "$@"

echo "LoLLMs WebUI stopped."
exit 0
"""

    starter_script_path = lollms_webui_path / script_name
    try:
        with open(starter_script_path, 'w', encoding='utf-8', newline='') as f: 
            f.write(starter_content)

        if current_system_os != "Windows":
            os.chmod(starter_script_path, 0o755)

        print_success(f"Starter script created: {starter_script_path}")
    except Exception as e:
        print_error(f"Failed to create starter script '{starter_script_path}': {e}")


    # 8. Final Instructions
    print_notice("Installation Complete!")
    print(f"LoLLMs WebUI is installed/configured in: {lollms_webui_path}")
    print(f"Your personal data directory is set to: {lollms_personal_path}")
    env_loc_display = str(env_dir_location) if env_dir_location else f"Managed by {env_manager} (e.g., check `conda env list` or `pyenv versions`)"
    print(f"The Python environment '{ENV_NAME}' ({env_manager}, targeting Python {TARGET_PYTHON_VERSION}) is located at: {env_loc_display}")
    print(f"  Using Python executable: {python_exe_path}")
    print("\n--- How to Start LoLLMs WebUI ---")
    print(f"1. Open your terminal or command prompt.")
    print(f"2. Navigate to the installation directory:")
    print(f"   cd \"{lollms_webui_path}\"")
    print(f"3. Run the generated starter script:")
    if current_system_os == "Windows":
        print(f"   .\\{script_name}")
    else:
        print(f"   ./{script_name}")
    print("-" * 30)
    print("\nIf the starter script fails (especially with activation):")
    print("  1. Manually activate the environment:")
    for line in current_os_activation_lines:
        print(f"     {line}")
    print(f"  2. Once activated, run the application directly from '{lollms_webui_path}':")
    print(f"     python app.py")

    print("\nEnjoy using LoLLMs!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation aborted by user.")
        sys.exit(0) 
    except SystemExit as e: # Make sure SystemExit from print_error is handled cleanly
        sys.exit(e.code)
    except Exception as e:
        print_error(f"A critical unexpected error occurred during installation: {e}", exit_code=None) # Don't exit from here directly
        import traceback
        traceback.print_exc()
        sys.exit(1) # Exit with error code after printing traceback