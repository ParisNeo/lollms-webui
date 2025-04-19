#!/usr/bin/env python3
import os
import sys
import subprocess
import platform
import venv # venv is part of Python's standard library
import shutil # shutil is part of Python's standard library
from pathlib import Path # pathlib is part of Python's standard library
import time # time is part of Python's standard library
import importlib # For checking module availability without immediate import

# --- Bootstrap Dependencies ---
# Ensure PyYAML is installed for the installer itself.
# This block must be very early, before PyYAML is actually used.
_INSTALLER_DEPENDENCIES = ["PyYAML"]
_dependencies_installed_this_run = False

for dep in _INSTALLER_DEPENDENCIES:
    try:
        # PyYAML installs as 'yaml', requests installs as 'requests', etc.
        # We assume the package name is lowercase for importlib check.
        module_name = dep.lower()
        importlib.import_module(module_name)
    except ImportError:
        print(f"Installer dependency '{dep}' not found. Attempting to install...")
        try:
            # Use check_call to ensure pip command succeeds
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
            print(f"Successfully installed '{dep}'.")
            _dependencies_installed_this_run = True
        except subprocess.CalledProcessError as e:
            print(f"ERROR: Failed to install '{dep}' using pip.")
            print(f"Please try installing it manually:")
            print(f"  {sys.executable} -m pip install {dep}")
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
REQUIRED_PYTHON_VERSION = "3.11" # Major.Minor version requirement
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
            conda_base = Path(os.environ.get("CONDA_PREFIX", "")).parent if os.environ.get("CONDA_PREFIX") else Path.home() / "miniconda3" # Very rough guess
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
            pyenv_root = Path.home() / ".pyenv"
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
                    f"Expected location based on detection: {python_exe_path}\n"
                    "Please check if the environment was created successfully and the path is correct.",
                    exit_code=None) # Let main function handle exit
        return None


# --- Main Installation Logic ---

def main():
    """Main function orchestrating the installation process."""
    print_notice("Starting LoLLMs WebUI Installer")
    print(f"Installer running with Python: {sys.version.split()[0]} at {sys.executable}")
    print(f"Operating System: {platform.system()} ({platform.release()})")
    global ENV_NAME # Allow modifying the global ENV_NAME

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
                     # Optionally, allow retrying check_command_exists here if user claims to have fixed it.
            else:
                print_warning("Invalid choice number.")
        except ValueError:
            print_warning("Please enter a number.")

    print(f"Selected environment manager: {env_manager}")
    # Make environment name specific to the manager and installation directory base name
    ENV_NAME = f"lollms_{lollms_webui_path.name}_{env_manager}_env"


    # 3. Environment Setup
    print_notice(f"Setting up Python {REQUIRED_PYTHON_VERSION} environment '{ENV_NAME}' using {env_manager}")

    # Define where the environment directory itself will be located or managed from
    env_dir_location = None # Actual path to the venv/uv directory, or the conda/pyenv env dir
    python_exe_path = None
    activation_commands = { # Store commands for the starter script
        "Windows": [],
        "Linux": [],
        "Darwin": [] # macOS
    }
    is_windows = platform.system() == "Windows"

    if env_manager == "conda":
        # Conda named environments are usually managed centrally
        print(f"> Checking if Conda environment '{ENV_NAME}' exists...")
        try:
            result = run_command(['conda', 'env', 'list', '--json'], capture_output=True, text=True, check=True, shell=is_windows)
            import json
            envs_info = json.loads(result.stdout)
            env_exists = any(Path(p).name == ENV_NAME for p in envs_info.get('envs', []))
        except Exception as e:
            print_warning(f"Could not accurately check if conda env '{ENV_NAME}' exists: {e}. Proceeding with creation attempt.")
            env_exists = False # Assume it doesn't exist

        if not env_exists:
            print(f"> Creating Conda environment '{ENV_NAME}' with Python {REQUIRED_PYTHON_VERSION}...")
            # Using -n for named environment. Check=True ensures it exits if creation fails.
            run_command(['conda', 'create', '-n', ENV_NAME, f'python={REQUIRED_PYTHON_VERSION}', '-y'], shell=is_windows, check=True)
        else:
            print(f"  Conda environment '{ENV_NAME}' already exists. Verifying Python version...")
            # We need the python path first to verify
            temp_python_path = get_python_executable_path(None, env_manager, lollms_webui_path, ENV_NAME)
            if temp_python_path:
                try:
                    version_result = run_command([str(temp_python_path), '--version'], capture_output=True, text=True, check=True)
                    output = version_result.stdout + version_result.stderr # Version might be in stderr
                    if f"Python {REQUIRED_PYTHON_VERSION}" not in output:
                         print_warning(f"Existing env '{ENV_NAME}' has Python version {output.split()[1]}, not {REQUIRED_PYTHON_VERSION}.")
                         # Ask user? Or just proceed? For now, just warn.
                         # Consider adding option to remove/recreate env.
                    else:
                        print(f"  Python version {REQUIRED_PYTHON_VERSION} confirmed.")
                except Exception as e:
                    print_warning(f"Could not verify Python version in existing env '{ENV_NAME}': {e}")
            else:
                 print_warning(f"Could not get Python path for existing env '{ENV_NAME}' to verify version.")


        # Get the definitive python path AFTER potential creation/verification
        python_exe_path = get_python_executable_path(None, env_manager, lollms_webui_path, ENV_NAME)
        if python_exe_path:
            env_dir_location = python_exe_path.parents[1] if not is_windows else python_exe_path.parent # bin/ or Scripts/ parent

        # Activation commands for starter script
        activation_commands["Windows"] = [f"conda activate {ENV_NAME}"]
        conda_base_path = ""
        try:
            conda_base_result = run_command(['conda', 'info', '--base'], capture_output=True, text=True, check=True, shell=is_windows)
            conda_base_path = Path(conda_base_result.stdout.strip())
        except Exception: pass # Ignore if fails, fallback below

        if not is_windows:
            if conda_base_path:
                 conda_activate_script = conda_base_path / "bin" / "activate"
                 activation_commands["Linux"] = [f"source \"{conda_activate_script}\" {ENV_NAME}"]
                 activation_commands["Darwin"] = [f"source \"{conda_activate_script}\" {ENV_NAME}"]
            else: # Fallback if base couldn't be determined
                 activation_commands["Linux"] = [f"conda activate {ENV_NAME} # May require conda init in shell profile"]
                 activation_commands["Darwin"] = [f"conda activate {ENV_NAME} # May require conda init in shell profile"]


    elif env_manager == "pyenv":
        if is_windows:
             print_warning("pyenv support on native Windows (pyenv-win) can be experimental. Ensure it's correctly set up.")

        print(f"> Checking available pyenv Python versions for {REQUIRED_PYTHON_VERSION}...")
        try:
            result = run_command(['pyenv', 'versions', '--bare'], capture_output=True, text=True, check=True, shell=is_windows)
            installed_pythons = [v.strip() for v in result.stdout.strip().split('\n') if v.strip()]
        except Exception as e:
             print_error(f"Failed to list pyenv versions: {e}. Is pyenv installed and configured?")

        # Find an installed Python matching MAJOR.MINOR (e.g., 3.11.x)
        target_python_base_version = next((v for v in installed_pythons if v.startswith(REQUIRED_PYTHON_VERSION)), None)

        if not target_python_base_version:
            print(f"! No installed pyenv Python found matching {REQUIRED_PYTHON_VERSION}.x.")
            print(f"  Attempting to find and install the latest Python {REQUIRED_PYTHON_VERSION} via pyenv...")
            try:
                # List available versions for installation
                install_list_cmd = ['pyenv', 'install', '--list']
                install_list_result = run_command(install_list_cmd, capture_output=True, text=True, check=True, shell=is_windows)
                available_versions = [line.strip() for line in install_list_result.stdout.splitlines() if line.strip().startswith(REQUIRED_PYTHON_VERSION)]
                # Filter out dev, rc, alpha, beta versions if possible
                stable_versions = [v for v in available_versions if not any(tag in v for tag in ['dev', 'rc', 'a', 'b'])]
                version_to_install = stable_versions[-1] if stable_versions else (available_versions[-1] if available_versions else None)

                if not version_to_install:
                    print_error(f"Could not find any suitable {REQUIRED_PYTHON_VERSION}.x version to install with 'pyenv install --list'.")

                print(f"  Found '{version_to_install}' as candidate. Attempting installation (this may take a while)...")
                run_command(['pyenv', 'install', version_to_install], shell=is_windows, check=True) # Install it
                target_python_base_version = version_to_install # Use the newly installed version
            except Exception as e:
                 print_error(f"pyenv install failed: {e}.\nPlease install Python {REQUIRED_PYTHON_VERSION}.x manually using 'pyenv install <version>' first.")

        print(f"  Using pyenv Python base version: {target_python_base_version}")

        # Now check for the virtualenv based on this Python version
        print(f"> Checking if pyenv virtualenv '{ENV_NAME}' (based on {target_python_base_version}) exists...")
        try:
            # Re-fetch versions to see if virtualenv exists
            result = run_command(['pyenv', 'versions', '--bare'], capture_output=True, text=True, check=True, shell=is_windows)
            installed_pythons_and_venvs = [v.strip() for v in result.stdout.strip().split('\n') if v.strip()]
        except Exception as e:
            print_error(f"Failed to list pyenv versions after install check: {e}.")


        if ENV_NAME not in installed_pythons_and_venvs:
            print(f"> Creating pyenv virtualenv '{ENV_NAME}' based on {target_python_base_version}...")
            # Use check=True to catch errors during virtualenv creation
            run_command(['pyenv', 'virtualenv', target_python_base_version, ENV_NAME], shell=is_windows, check=True)
        else:
             print(f"  pyenv virtualenv '{ENV_NAME}' already exists. Skipping creation.")
             # Add version check here too? Similar to conda. For now, skip.

        python_exe_path = get_python_executable_path(None, env_manager, lollms_webui_path, ENV_NAME)
        if python_exe_path:
             env_dir_location = python_exe_path.parents[1] if not is_windows else python_exe_path.parent # bin/ or Scripts/ parent

        # Activation for pyenv is complex, often relies on shell init.
        # Using the direct python path in the starter script is more reliable.
        # The commands below are mostly for user info / manual activation.
        activation_commands["Windows"] = [f"pyenv activate {ENV_NAME} # May require pyenv-win shell integration"]
        # Linux/Mac need pyenv init and virtualenv-init eval'd in the shell environment
        pyenv_init_lines = [
            'export PYENV_ROOT="$HOME/.pyenv"',
            'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"',
            'eval "$(pyenv init -)"',
            'eval "$(pyenv virtualenv-init -)"'
        ]
        activation_commands["Linux"] = pyenv_init_lines + [f"pyenv activate {ENV_NAME}"]
        activation_commands["Darwin"] = pyenv_init_lines + [f"pyenv activate {ENV_NAME}"]


    elif env_manager in ["venv", "uv"]:
        # Place the environment inside the project directory for encapsulation
        env_dir_location = lollms_webui_path / ".venv" # Standard name
        env_exists = env_dir_location.is_dir() and (env_dir_location / "pyvenv.cfg").exists()

        if not env_exists:
            print(f"> Creating {env_manager} virtual environment at: {env_dir_location}")
            env_dir_location.parent.mkdir(parents=True, exist_ok=True) # Ensure parent exists

            if env_manager == "venv":
                 # Find a suitable Python 3.11 executable on the system
                 print(f"> Searching for system Python {REQUIRED_PYTHON_VERSION} executable...")
                 system_python_cmd = None
                 version_prefixes_to_try = [REQUIRED_PYTHON_VERSION, "3.11", "3", ""] # Try python3.11, python3, python
                 for suffix in version_prefixes_to_try:
                      potential_cmd = f"python{suffix}"
                      try:
                          # On Windows, 'python' often resolves correctly if in PATH
                          check_cmd_list = ['python', '--version'] if is_windows and not suffix else [potential_cmd, '--version']
                          result = subprocess.run(check_cmd_list, capture_output=True, text=True, check=True, timeout=5)
                          output = result.stdout + result.stderr
                          if f"Python {REQUIRED_PYTHON_VERSION}" in output:
                              system_python_cmd = potential_cmd if not (is_windows and not suffix) else 'python'
                              print(f"  Found suitable Python as '{system_python_cmd}' (version: {output.splitlines()[0].strip()})")
                              break
                      except (FileNotFoundError, subprocess.CalledProcessError, subprocess.TimeoutExpired):
                           continue # Try next suffix

                 if not system_python_cmd:
                      print_error(f"Python {REQUIRED_PYTHON_VERSION} executable not found in your PATH.\n"
                                  f"Please install Python {REQUIRED_PYTHON_VERSION} globally or use Conda/pyenv to manage Python versions.")

                 # Create venv using the found Python
                 run_command([system_python_cmd, '-m', 'venv', str(env_dir_location)], check=True)

            elif env_manager == "uv":
                 # uv can often find/download Python itself
                 try:
                      # Use --python flag to request specific version
                      run_command(['uv', 'venv', str(env_dir_location), '--python', REQUIRED_PYTHON_VERSION], check=True)
                 except subprocess.CalledProcessError as e:
                      # Check if error is due to Python not found
                      if "could not find python interpreter" in (e.stderr or "").lower() or \
                         "failed to find python" in (e.stderr or "").lower():
                           print_warning(f"uv could not automatically find Python {REQUIRED_PYTHON_VERSION}.")
                           print_warning("Attempting to create uv venv using uv's default/system Python.")
                           print_warning(f"The resulting environment might not use Python {REQUIRED_PYTHON_VERSION}.")
                           try:
                               # Try creating without specifying Python version
                               run_command(['uv', 'venv', str(env_dir_location)], check=True)
                           except Exception as inner_e:
                                print_error(f"Failed to create uv venv even with default Python: {inner_e}")
                      else:
                           # Re-raise other uv errors
                            print_error(f"uv venv creation failed: {e.stderr or e.stdout or e}")

        else:
            print(f"  {env_manager} virtual environment already exists at: {env_dir_location}. Checking Python version...")
            temp_python_path = get_python_executable_path(env_dir_location, env_manager, lollms_webui_path, ENV_NAME)
            if temp_python_path:
                 try:
                    version_result = run_command([str(temp_python_path), '--version'], capture_output=True, text=True, check=True)
                    output = version_result.stdout + version_result.stderr
                    if f"Python {REQUIRED_PYTHON_VERSION}" not in output:
                         print_warning(f"Existing env '{env_dir_location.name}' has Python {output.split()[1]}, not {REQUIRED_PYTHON_VERSION}.")
                         # Consider asking user to delete/recreate?
                    else:
                        print(f"  Python version {REQUIRED_PYTHON_VERSION} confirmed.")
                 except Exception as e:
                     print_warning(f"Could not verify Python version in existing env '{env_dir_location.name}': {e}")
            else:
                print_warning("Could not get Python path for existing env to verify version.")

        # Get definitive python path
        python_exe_path = get_python_executable_path(env_dir_location, env_manager, lollms_webui_path, ENV_NAME)

        # Activation commands (same for venv and uv)
        if is_windows:
            activate_script = env_dir_location / "Scripts" / "activate.bat"
            # Use CALL for .bat scripts within other .bat scripts
            activation_commands["Windows"] = [f'CALL "{activate_script}"']
        else:
            activate_script = env_dir_location / "bin" / "activate"
            # Use source for .sh scripts
            activation_commands["Linux"] = [f'source "{activate_script}"']
            activation_commands["Darwin"] = [f'source "{activate_script}"']

    # Final check after environment setup attempt
    if not python_exe_path or not Path(python_exe_path).exists():
         print_error(f"Failed to create or locate the Python executable for environment '{ENV_NAME}'. Installation cannot proceed.")
    if not env_dir_location or not Path(env_dir_location).exists():
         print_warning(f"Environment directory location ({env_dir_location}) seems invalid after setup attempt.")


    # 4. Repository Handling
    print_notice("Handling LoLLMs WebUI Repository")
    lollms_webui_path.parent.mkdir(parents=True, exist_ok=True) # Ensure parent dir exists

    git_dir = lollms_webui_path / ".git"
    if not git_dir.is_dir(): # Check if it's specifically a directory
        # Target path exists but is not a git repo OR target path doesn't exist
        if lollms_webui_path.exists() and any(lollms_webui_path.iterdir()):
            # If the directory exists and contains files/folders
            print_warning(f"Target directory '{lollms_webui_path}' exists and is not empty, but is not a git repository.")
            if input("  Clone into this directory anyway? (Existing files might conflict) [y/N]: ").lower().strip() != 'y':
                print_error("Installation aborted. Please choose an empty directory or a valid git repository.", exit_code=0)
            # If user agrees, git clone will likely fail if non-empty, but let it try.

        print(f"> Cloning LoLLMs WebUI from {REPO_URL} into {lollms_webui_path}...")
        # Clone with recursive submodules. Check=True ensures it fails if clone errors out.
        run_command(['git', 'clone', '--recurse-submodules', REPO_URL, str(lollms_webui_path)], check=True)
    else:
        # Target path is a git repository
        print(f"> Repository already exists at {lollms_webui_path}.")
        # Optional: Check remote URL matches? For now, assume it's the correct repo.
        # Stash local changes before pulling? Offer option? For now, keep it simple.
        update_choice = input("  Do you want to attempt to update it? (git pull & submodule update --remote) [y/N]: ").lower().strip()
        if update_choice == 'y':
            print("> Stashing local changes (if any)...")
            run_command(['git', 'stash', 'push', '-m', 'lollms-installer-stash'], cwd=lollms_webui_path, check=False) # Don't fail if nothing to stash (returns 1) success_codes=[0,1]

            print("> Pulling latest changes from origin...")
            run_command(['git', 'pull'], cwd=lollms_webui_path, check=True) # Fail if pull has issues

            print("> Updating submodules (fetching remote changes)...")
            # --init ensures new submodules are cloned, --recursive handles nested ones, --remote fetches latest commit from submodule's remote
            run_command(['git', 'submodule', 'update', '--init', '--recursive', '--remote'], cwd=lollms_webui_path, check=True)

            print("> Restoring stashed changes (if any)...")
            stash_apply_result = run_command(['git', 'stash', 'pop'], cwd=lollms_webui_path, check=False) # Don't fail script if stash pop conflicts
            if stash_apply_result.returncode != 0:
                 print_warning("Could not automatically apply stashed changes. You may need to resolve conflicts manually in git.")
                 print_warning("Run 'git stash list' and 'git stash apply' in the repo directory.")

        else:
            print("> Ensuring submodules are initialized and updated (without fetching remote)...")
            # Just make sure submodules are present and checked out according to the main repo's recorded commit
            run_command(['git', 'submodule', 'update', '--init', '--recursive'], cwd=lollms_webui_path, check=True)


    # 5. Dependency Installation within the environment
    print_notice(f"Installing Dependencies into '{ENV_NAME}' environment")
    requirements_file = lollms_webui_path / "requirements.txt"
    lollms_core_dir = lollms_webui_path / "lollms_core"

    # Validate crucial files exist after clone/update
    if not requirements_file.is_file():
        print_error(f"requirements.txt not found in {lollms_webui_path}. Repository clone or update likely failed.")
    if not lollms_core_dir.is_dir() or not (lollms_core_dir / "setup.py").is_file():
         print_error(f"lollms_core submodule directory or its setup.py not found in {lollms_webui_path}. Submodule handling likely failed.")

    print(f"> Installing base packages from requirements.txt using {python_exe_path}...")
    # Define pip/uv commands
    pip_cmd_base = [str(python_exe_path), '-m', 'pip', 'install', '--upgrade'] # Add --upgrade for pip itself and packages
    
    # Check if uv command exists *again* here in case it wasn't checked before
    uv_available = env_manager == "uv" and check_command_exists("uv")
    uv_cmd_base = ['uv', 'pip', 'install', '--python', str(python_exe_path)] if uv_available else None

    # Prefer uv if chosen and available, otherwise use pip
    install_cmd_base = uv_cmd_base if uv_cmd_base else pip_cmd_base

    # Install requirements.txt
    req_install_cmd = install_cmd_base + ['-r', str(requirements_file)]
    print(f"  Using command: {' '.join(req_install_cmd)}")
    run_command(req_install_cmd, cwd=lollms_webui_path, check=True) # Fail if reqs install fails


    print(f"> Installing lollms_core submodule in editable mode using {python_exe_path}...")
    # Install lollms_core editable
    core_install_cmd = install_cmd_base + ['-e', str(lollms_core_dir)]
    print(f"  Using command: {' '.join(core_install_cmd)}")
    run_command(core_install_cmd, cwd=lollms_webui_path, check=True) # Fail if core install fails


    # 6. Configuration File Generation
    print_notice("Creating Configuration File")
    lollms_core_lollms_path = lollms_core_dir / "lollms"
    # Check if the actual library directory exists within the submodule
    if not lollms_core_lollms_path.is_dir():
        print_error(f"Could not find the core lollms library directory expected at: {lollms_core_lollms_path}")

    # Prepare config data with resolved, absolute paths using POSIX slashes for consistency
    config_data = {
        "lollms_path": str(lollms_core_lollms_path.resolve()).replace("\\", "/"),
        "lollms_personal_path": str(lollms_personal_path.resolve()).replace("\\", "/")
    }
    config_file_path = lollms_webui_path / "global_paths_cfg.yaml"

    print(f"> Writing configuration to: {config_file_path}")
    print(f"  lollms_path: {config_data['lollms_path']}")
    print(f"  lollms_personal_path: {config_data['lollms_personal_path']}")

    try:
        # Write YAML file with UTF-8 encoding
        with open(config_file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print_success("Configuration file 'global_paths_cfg.yaml' created.")
    except Exception as e:
        print_error(f"Failed to write configuration file '{config_file_path}': {e}")


    # 7. Starter Script Creation
    print_notice("Creating Starter Script")
    current_system_os = platform.system() # Linux, Darwin, Windows
    starter_content = ""
    script_name = ""
    app_script_path = lollms_webui_path / "app.py"

    # Get the activation command lines for the current OS
    current_os_activation_lines = activation_commands.get(current_system_os, [])
    if not current_os_activation_lines:
        # Generate a fallback warning/instruction if no specific commands were determined
        print_warning(f"Could not determine specific activation commands for {current_system_os}.")
        fallback_info = f"# Please manually activate the '{ENV_NAME}' {env_manager} environment before running 'python app.py'"
        if is_windows:
             fallback_info = f"REM Please manually activate the '{ENV_NAME}' {env_manager} environment before running 'python app.py'"
        current_os_activation_lines = [fallback_info]


    if current_system_os == "Windows":
        script_name = "start_lollms.bat"
        # Use %~dp0 to get the directory of the batch script itself, making it more portable
        starter_content = f"""@echo off
REM LoLLMs WebUI Starter Script - Generated by lollms-installer
echo Activating Python environment '{ENV_NAME}' using {env_manager}...
{os.linesep.join(current_os_activation_lines)}

echo Starting LoLLMs WebUI...
REM Change directory to the script's location (%~dp0) then to the lollms-webui root
cd /D "%~dp0"
echo Current directory: %CD%
echo Running: "{python_exe_path}" "{app_script_path}" %*

REM Execute Python script, passing along any arguments given to the batch script (%*)
"{python_exe_path}" "{app_script_path}" %*

echo.
echo LoLLMs WebUI stopped.
REM Pause only if the script wasn't called with arguments (simple heuristic)
if [%1]==[] (
    echo Press any key to exit.
    pause > nul
)
"""
    else: # Linux and Darwin (macOS)
        script_name = "start_lollms.sh"
        # Use dirname "$0" to find the script's directory
        # Ensure paths are quoted properly for shell
        quoted_python_exe = f'"{python_exe_path}"'
        quoted_app_script = f'"{app_script_path}"'
        quoted_webui_path = f'"{lollms_webui_path}"'

        starter_content = f"""#!/bin/bash
# LoLLMs WebUI Starter Script - Generated by lollms-installer

# Get the directory where the script is located
SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)

echo "Activating Python environment '{ENV_NAME}' using {env_manager}..."
# Execute activation commands - handle potential errors?
{os.linesep.join(current_os_activation_lines)} || {{ echo "Activation failed, proceeding might not work."; }}

# Verify activation (optional debug)
# echo "Which python after activation: $(command -v python)"
# echo "Python version: $({quoted_python_exe} --version 2>&1)"


echo "Starting LoLLMs WebUI from {quoted_webui_path}..."
# Change to the LoLLMs WebUI root directory relative to the script
cd "{quoted_webui_path}" || {{ echo "ERROR: Failed to change directory to {quoted_webui_path}"; exit 1; }}

echo "Current directory: $(pwd)"
echo "Running: {quoted_python_exe} {quoted_app_script} \"$@\""

# Execute the python application, passing all script arguments ("$@")
{quoted_python_exe} {quoted_app_script} "$@"

echo "LoLLMs WebUI stopped."
exit 0
"""

    # Write the starter script to the root of the lollms-webui installation directory
    starter_script_path = lollms_webui_path / script_name
    try:
        with open(starter_script_path, 'w', encoding='utf-8', newline='') as f: # Use OS default line endings
            f.write(starter_content)

        if current_system_os != "Windows":
            # Make the script executable on Linux/macOS (owner rwx, group rx, others rx)
            os.chmod(starter_script_path, 0o755)

        print_success(f"Starter script created: {starter_script_path}")
    except Exception as e:
        print_error(f"Failed to create starter script '{starter_script_path}': {e}")


    # 8. Final Instructions
    print_notice("Installation Complete!")
    print(f"LoLLMs WebUI is installed/configured in: {lollms_webui_path}")
    print(f"Your personal data directory is set to: {lollms_personal_path}")
    print(f"The Python environment '{ENV_NAME}' ({env_manager}) is located at: {env_dir_location or 'Managed by '+env_manager}")
    print(f"  Using Python: {python_exe_path}")
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
    # Print the activation lines again for easy copy-paste
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
        sys.exit(0) # Exit code 0 for user-initiated abort
    except SystemExit as e:
        # Catch sys.exit calls from print_error and other parts of the script
        # The exit code should already be set correctly by print_error
        sys.exit(e.code)
    except Exception as e:
        # Catch any other unexpected errors during the main execution flow
        print_error(f"A critical unexpected error occurred during installation: {e}", exit_code=None)
        # Print the full traceback for debugging purposes
        import traceback
        traceback.print_exc()
        sys.exit(1) # General error exit code