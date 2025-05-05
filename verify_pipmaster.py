import subprocess
import sys
import importlib

package_name = "pipmaster"
version_spec = ">=0.7.2"
package_spec = f"{package_name}{version_spec}"
import_alias = "pm"

def install_and_import(pkg_spec, pkg_name, alias):
    """
    Attempts to install a package using pip and then import it.

    Args:
        pkg_spec (str): The package specification for pip (e.g., "requests>=2.0").
        pkg_name (str): The actual package name to import (e.g., "requests").
        alias (str): The alias to use when importing (e.g., "req").

    Returns:
        module: The imported module if successful, otherwise raises an exception.

    Raises:
        RuntimeError: If pip installation fails.
        ImportError: If the package cannot be imported after installation attempt.
    """
    try:
        print(f"Attempting to ensure {pkg_name} ({pkg_spec}) is installed...")
        # Use sys.executable to ensure pip is run for the correct Python environment
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_spec])
        print(f"Successfully installed or verified {pkg_name}.")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install {pkg_spec} using pip.")
        print(f"Command failed: {' '.join(e.cmd)}")
        print(f"Return code: {e.returncode}")
        # You might want to print e.output or e.stderr if available/captured
        raise RuntimeError(f"Failed to install {pkg_spec}") from e
    except Exception as e:
        print(f"ERROR: An unexpected error occurred during installation: {e}")
        raise RuntimeError(f"Unexpected error installing {pkg_spec}") from e

    try:
        print(f"Importing {pkg_name} as {alias}...")
        # Perform the import dynamically using importlib and assign to globals
        globals()[alias] = importlib.import_module(pkg_name)
        print(f"Successfully imported {pkg_name} as {alias}.")
        return globals()[alias]
    except ImportError as e:
        print(f"ERROR: Could not import {pkg_name} even after attempting installation.")
        raise ImportError(f"Could not import {pkg_name}") from e

# --- Main execution ---
try:
    # Call the function to install and import pipmaster as pm
    pm = install_and_import(package_spec, package_name, import_alias)

    # --- You can now use 'pm' ---
    print("\nInstallation and import successful.")
    print(f"Using {package_name} version: {pm.__version__}")

    # Example: Use a (hypothetical) function from pipmaster
    # try:
    #     print("Attempting to use a function from pipmaster...")
    #     # Replace with an actual function/attribute if you know one
    #     # For example, check its type
    #     print(f"Type of 'pm': {type(pm)}")
    # except AttributeError as e:
    #      print(f"Could not find an example attribute/function: {e}")

except (RuntimeError, ImportError) as e:
    print(f"\nScript failed: {e}")
    # Exit or handle the failure appropriately
    sys.exit(1)
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
    sys.exit(1)

# If the script reaches here, 'pm' is available.
# print("You can now use the 'pm' variable.")
# pm.some_pipmaster_function(...)
