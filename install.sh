#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e
# Treat unset variables as an error when substituting.
set -u
# Pipe failure is an error
set -o pipefail

echo "Starting Lollms WebUI Installation Script"

# --- Configuration ---
PYTHON_CMD="python3" # Command to run python 3
VENV_NAME="venv"
REQUIREMENTS_FILE="requirements.txt"
LOLLA_CORE_SUBDIR="lollms_core"
LOLLA_CORE_APP_SUBDIR="lollms" # a.k.a lollms_core/lollms
SETUP_PY_FILE="setup.py"
GLOBAL_CONFIG_FILE="global_paths_cfg.yaml"
DEFAULT_PERSONAL_DATA_SUBDIR="personal_data"

# Get the absolute path of the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
VENV_DIR="$SCRIPT_DIR/$VENV_NAME"

# --- Helper Functions ---
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: Command '$1' not found. Please install it and ensure it's in your PATH."
        exit 1
    fi
}

# --- Pre-flight Checks ---
echo "Checking for Python 3..."
check_command "$PYTHON_CMD"
"$PYTHON_CMD" -c "import sys; sys.exit(0 if sys.version_info.major == 3 and sys.version_info.minor >= 7 else 1)" \
    || { echo "Error: Python 3.7+ is required. Found: $("$PYTHON_CMD" --version)"; exit 1; }
echo "Python 3 check passed."

echo "Checking for pip (will be ensured by venv)..."
# No explicit pip check here, as venv should provide it.

# --- Virtual Environment Setup ---
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating Python Virtual Environment in '$VENV_DIR'..."
    "$PYTHON_CMD" -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment. Please check your Python installation."
        exit 1
    fi
    echo "Virtual environment created."
else
    echo "Virtual environment '$VENV_DIR' already exists."
fi

echo "Activating virtual environment..."
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"
if [ $? -ne 0 ]; then
    echo "Failed to activate virtual environment."
    exit 1
fi
echo "Virtual environment activated. Python: $(which python), Pip: $(which pip)"

echo "Upgrading pip..."
pip install --upgrade pip > /dev/null
if [ $? -ne 0 ]; then
    echo "Failed to upgrade pip (attempt 1)."
    pip install --upgrade pip # Retry with output
    if [ $? -ne 0 ]; then
        echo "Pip upgrade still failed. Please check your internet connection and pip installation."
        exit 1
    fi
fi

# --- Install Dependencies ---
if [ -f "$SCRIPT_DIR/$REQUIREMENTS_FILE" ]; then
    echo "Installing Python Dependencies from '$REQUIREMENTS_FILE'..."
    pip install -r "$SCRIPT_DIR/$REQUIREMENTS_FILE"
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies from '$REQUIREMENTS_FILE'. Please check the file and your internet connection."
        exit 1
    fi
else
    echo "No root '$REQUIREMENTS_FILE' found. Skipping this step."
    echo "(Dependencies for $LOLLA_CORE_SUBDIR will be handled next if defined in its $SETUP_PY_FILE)"
fi

# --- Install lollms_core ---
LOLLA_CORE_PATH="$SCRIPT_DIR/$LOLLA_CORE_SUBDIR"
if [ -f "$LOLLA_CORE_PATH/$SETUP_PY_FILE" ]; then
    echo "Installing lollms-core package from '$LOLLA_CORE_PATH'..."
    pip install -e "$LOLLA_CORE_PATH"
    if [ $? -ne 0 ]; then
        echo "Failed to install lollms-core. Please check the '$LOLLA_CORE_PATH' subfolder and its '$SETUP_PY_FILE'."
        exit 1
    fi
    echo "lollms-core installed successfully."
else
    echo "Warning: '$LOLLA_CORE_PATH/$SETUP_PY_FILE' not found. Cannot install lollms-core."
    echo "The application might not work correctly."
    # Consider exiting here if lollms_core is mandatory: exit 1
fi

echo
echo "Configuring Lollms WebUI Paths..."

# --- Determine lollms_path ---
# Absolute path to lollms_core/lollms
# Using realpath to get a canonical absolute path
TARGET_LOLLA_CODE_PATH="$LOLLA_CORE_PATH/$LOLLA_CORE_APP_SUBDIR"
if [ -d "$TARGET_LOLLA_CODE_PATH" ]; then
    LOLLA_PATH_VAL_YAML="$(realpath "$TARGET_LOLLA_CODE_PATH")"
else
    # Fallback if the directory doesn't exist yet, construct it (less ideal)
    echo "Warning: '$TARGET_LOLLA_CODE_PATH' does not exist. Constructing path, but ensure it's correct."
    LOLLA_PATH_VAL_YAML="$(realpath "$LOLLA_CORE_PATH")/$LOLLA_CORE_APP_SUBDIR"
fi
echo "lollms_path will be set to: $LOLLA_PATH_VAL_YAML"

# --- Prompt for lollms_personal_path ---
DEFAULT_PERSONAL_PATH_ABS="$SCRIPT_DIR/$DEFAULT_PERSONAL_DATA_SUBDIR"
read -r -p "Enter Lollms personal data path [$DEFAULT_PERSONAL_PATH_ABS]: " personal_data_input
# Use default if input is empty
LOLLA_PERSONAL_PATH_VAL_RAW="${personal_data_input:-$DEFAULT_PERSONAL_PATH_ABS}"

# Get absolute canonical path for personal data. -m allows it to not exist yet.
LOLLA_PERSONAL_PATH_VAL_YAML="$(realpath -m "$LOLLA_PERSONAL_PATH_VAL_RAW")"

# Create personal_data directory if it doesn't exist
if [ ! -d "$LOLLA_PERSONAL_PATH_VAL_YAML" ]; then
    echo "Creating personal data directory: $LOLLA_PERSONAL_PATH_VAL_YAML"
    mkdir -p "$LOLLA_PERSONAL_PATH_VAL_YAML"
    if [ $? -ne 0 ]; then
        echo "Failed to create personal data directory. Please check permissions."
        # Not exiting, as the app might handle it, but it's a strong warning.
    fi
else
    echo "Personal data directory already exists: $LOLLA_PERSONAL_PATH_VAL_YAML"
fi

# --- Create global_paths_cfg.yaml ---
CONFIG_FILE_PATH="$SCRIPT_DIR/$GLOBAL_CONFIG_FILE"
echo "Writing configuration to '$CONFIG_FILE_PATH'..."
cat << EOF > "$CONFIG_FILE_PATH"
lollms_path: '$LOLLA_PATH_VAL_YAML'
lollms_personal_path: '$LOLLA_PERSONAL_PATH_VAL_YAML'
EOF

if [ -f "$CONFIG_FILE_PATH" ]; then
    echo "Configuration saved to '$CONFIG_FILE_PATH'"
else
    echo "Failed to write '$CONFIG_FILE_PATH'."
    exit 1
fi

echo
echo "Lollms WebUI Installation and Setup Complete."
echo
echo "To launch the application:"
echo "1. Ensure you are in the project directory:"
echo "   cd \"$SCRIPT_DIR\""
echo "2. Activate the virtual environment (if not already active in your current shell):"
echo "   source \"$VENV_DIR/bin/activate\""
echo "3. Run the application using its main script, for example:"
echo "   python app.py"
echo "   (Or use the provided run.sh or equivalent if available in the project)"
echo
echo "If a run.sh or similar script is provided with Lollms WebUI, you might be able to simply execute:"
echo "   ./run.sh  (or bash run.sh)"
echo

# Deactivation is usually not done in a script that sets up an environment
# but if you wanted to:
# deactivate

exit 0