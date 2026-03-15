# -*- coding: utf-8 -*-
"""
=========================================================================
 Lollms Function Call: Folder Structure to Text
=========================================================================
Developed by: ParisNeo
Creation Date: 2025-03-03
Last Update: 2024-05-24 # Added option to save output to discussion folder
Version: 1.6.0
Description:
  Takes a folder path and generates a Markdown-formatted text representation.
  First, it displays the folder structure as a tree view (`|-`, `L-`).
  Second, it lists each included text file with its relative path and
  full content within Markdown code blocks. Allows specifying files/folders
  to exclude using:
  1. Base default exclusions.
  2. Predefined project type presets (Python, Node.js, etc.).
  3. Custom static exclusions (folders, extensions, patterns) if 'Custom' preset is selected.
  4. Dynamic exclusions via arguments (wildcard patterns).
  Optionally saves a copy of the generated Markdown to the current discussion folder.
=========================================================================
"""
import fnmatch
import datetime
from pathlib import Path
from typing import List, Set, Tuple, Optional, Dict # Added Dict
import re # Import re for filename sanitization

# Use Lollms imports
from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from ascii_colors import ASCIIColors, trace_exception

# --- Configuration Constants ---
DEFAULT_EXCLUDED_FOLDERS: Set[str] = {
    ".git", "__pycache__", "node_modules", "target", "dist", "build", "venv",
    ".vscode", ".idea", "logs", "temp", "tmp", "bin", "obj",
    "coverage", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".hypothesis"
}
DEFAULT_EXCLUDED_EXTENSIONS: Set[str] = {
    ".pyc", ".pyo", ".o", ".obj", ".class", ".dll", ".so", ".exe", ".bin",
    ".zip", ".tar", ".gz", ".rar", ".7z", ".jar", ".war",
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".svg",
    ".mp3", ".wav", ".ogg", ".mp4", ".avi", ".mov", ".webm",
    ".db", ".sqlite", ".sqlite3", ".lock",
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".ods", ".odp",
    ".ttf", ".otf", ".woff", ".woff2",
    ".DS_Store", ".ipynb_checkpoints",
}
ALLOWED_TEXT_EXTENSIONS: Set[str] = {
    ".txt", ".md", ".markdown", ".rst", ".adoc", ".asciidoc",
    ".py", ".java", ".js", ".ts", ".jsx", ".tsx", ".html", ".htm", ".css", ".scss", ".sass", ".less",
    ".c", ".cpp", ".h", ".hpp", ".cs", ".go", ".rs", ".swift", ".kt", ".kts",
    ".php", ".rb", ".pl", ".pm", ".lua", ".sh", ".bash", ".zsh", ".bat", ".ps1", ".psm1",
    ".sql", ".r", ".dart", ".groovy", ".scala", ".clj", ".cljs", ".cljc", ".edn",
    ".vb", ".vbs", ".f", ".for", ".f90", ".f95",
    ".json", ".yaml", ".yml", ".xml", ".toml", ".ini", ".cfg", ".conf", ".properties",
    ".csv", ".tsv", ".env",
    ".dockerfile", "dockerfile", ".tf", ".tfvars", ".hcl",
    ".gradle", ".pom", ".csproj", ".vbproj", ".sln",
    ".gitignore", ".gitattributes", ".npmrc", ".yarnrc", ".editorconfig",
    ".babelrc", ".eslintrc", ".prettierrc", ".stylelintrc",
    ".makefile", "makefile", "Makefile", "CMakeLists.txt",
    ".tex", ".bib", ".sty",
    ".graphql", ".gql", ".vue", ".svelte", ".astro", ".liquid", ".njk", ".jinja", ".jinja2",
    ".patch", ".diff",
}
TREE_BRANCH = "├─ "
TREE_LAST = "└─ "
TREE_VLINE = "│  "
TREE_SPACE = "   "
FOLDER_ICON = "📁"
FILE_ICON = "📄"
MAX_FILE_SIZE_MB = 1 # Limit file size to avoid overwhelming context

# --- Preset Definitions ---
PRESET_EXCLUSIONS: Dict[str, List[str]] = {
    "Python Project": [
        "*.pyc", "*.pyo", "*.pyd", # Compiled Python
        "__pycache__/", "venv/", ".venv/", "env/", ".env/", # Virtual environments
        ".pytest_cache/", ".mypy_cache/", ".ruff_cache/", ".hypothesis/", # Caching
        "build/", "dist/", "*.egg-info/", # Packaging
        "htmlcov/", ".coverage", # Coverage reports
        "instance/", # Flask specific
        "*.sqlite3", "*.db", # Common local databases
    ],
    "Node.js Project": [
        "node_modules/",      # Dependencies
        "npm-debug.log*", "yarn-debug.log*", "yarn-error.log*", # Logs
        ".npm", ".yarn",      # Cache/config
        "dist/", "build/",    # Build output
        ".env", "*.local",    # Environment files (often sensitive)
        "coverage/",          # Coverage reports
        ".DS_Store",          # macOS specific
    ],
    "C/C++ Project": [
        "*.o", "*.obj", "*.a", "*.lib", "*.so", "*.dylib", "*.dll", "*.exe", # Compiled objects/libs/executables
        "build/", "bin/", "obj/", "Debug/", "Release/", # Common build output directories
        "*.out",                # Common executable name
        "*.gch",                # Precompiled headers
        "*.stackdump",          # Crash dumps
        ".vscode/", ".ccls-cache/", ".cache/", # Editor/tooling cache
        "CMakeCache.txt", "CMakeFiles/", "cmake_install.cmake", "CTestTestfile.cmake", # CMake generated
        "compile_commands.json" # Compilation database (can be large)
    ],
    "Rust Project": [
        "target/",           # Build directory
        "Cargo.lock",       # Usually included, but can be excluded if needed for context focus
        "*.rlib", "*.so", "*.dylib", "*.dll", "*.a", "*.exe", # Compiled artifacts
    ],
    "Java Project": [
        "*.class",             # Compiled bytecode
        "*.jar", "*.war", "*.ear", # Archives
        "target/", "build/", "bin/", "out/", # Build output directories (Maven, Gradle, Eclipse, IntelliJ)
        ".gradle/", ".mvn/",     # Build tool caches/wrappers
        "hs_err_pid*.log",      # HotSpot crash logs
        ".project", ".classpath", ".settings/", # Eclipse specific
        "*.iml", ".idea/",        # IntelliJ specific
    ],
    # Add more presets as needed (e.g., Go, PHP, Ruby)
}
PRESET_OPTIONS = ["None/Defaults", "Custom"] + sorted(PRESET_EXCLUSIONS.keys())
# --- End Constants ---


class FolderStructureToText(FunctionCall):
    """
    (Class Docstring serves as the 'header' in the code)
    =========================================================================
     Lollms Function Call: Folder Structure to Text
    =========================================================================
    Developed by: ParisNeo
    Creation Date: 2025-03-03
    Last Update: 2024-05-24 # Added option to save output to discussion folder
    Version: 1.6.0
    Description:
      Takes a folder path and generates a Markdown-formatted text representation.
      First, it displays the folder structure as a tree view (`|-`, `L-`).
      Second, it lists each included text file with its relative path and
      full content within Markdown code blocks. Allows specifying files/folders
      to exclude using:
      1. Base default exclusions.
      2. Predefined project type presets (Python, Node.js, etc.).
      3. Custom static exclusions (folders, extensions, patterns) if 'Custom' preset is selected.
      4. Dynamic exclusions via arguments (wildcard patterns).
      Optionally saves a copy of the generated Markdown to the current discussion folder.
    =========================================================================
    """
    BASE_EXCLUDED_FOLDERS = DEFAULT_EXCLUDED_FOLDERS
    BASE_EXCLUDED_EXTENSIONS = DEFAULT_EXCLUDED_EXTENSIONS
    ALLOWED_TEXT_EXTENSIONS = ALLOWED_TEXT_EXTENSIONS
    PRESET_EXCLUSIONS = PRESET_EXCLUSIONS # Make presets accessible within the class

    def __init__(self, app: LollmsApplication, client: Client):
        # --- Define Static Parameters ---
        config_template = ConfigTemplate([
            {
                "name": "exclusion_preset",
                "type": "str",
                "value": "None/Defaults", # Default to no preset
                "options": PRESET_OPTIONS, # Use the generated list
                "help": "Select a preset for common project types to automatically apply typical exclusion patterns. Select 'Custom' to use the custom static fields below. 'None/Defaults' uses only base exclusions and dynamic arguments."
            },
            {
                "name": "custom_static_exclude_folders", # Renamed for clarity
                "type": "str",
                "value": "",
                "help": "**Only used if 'Exclusion Preset' is 'Custom'.** Comma-separated list of folder names to always exclude (case-insensitive). Example: 'docs,examples,tests'"
            },
            {
                "name": "custom_static_exclude_extensions", # Renamed for clarity
                "type": "str",
                "value": "",
                "help": "**Only used if 'Exclusion Preset' is 'Custom'.** Comma-separated list of file extensions to always exclude (including dot, case-insensitive). Example: '.log,.tmp,.bak'"
            },
            {
                "name": "custom_static_exclude_patterns", # Renamed for clarity
                "type": "str",
                "value": "",
                "help": "**Only used if 'Exclusion Preset' is 'Custom'.** Comma-separated list of wildcard patterns (*, ?) to exclude files/folders. Example: '*.log,temp_*,cache_*/'"
            },
            {
                "name": "max_file_size_mb",
                "type": "float",
                "value": MAX_FILE_SIZE_MB,
                "min":0.01,
                "max":100,
                "help": "Maximum size (in MB) for individual files to include content. Files larger than this will have their content omitted."
            },
            { # New Parameter
                "name": "save_to_discussion_folder",
                "type": "bool",
                "value": True,
                "help": "If checked, save a copy of the generated Markdown output to a file named 'textraction_<foldername>.md' in the current Lollms discussion folder."
            },
        ])
        static_parameters = TypedConfig(config_template, BaseConfig(config={}))
        # --- End Static Parameters ---

        super().__init__(
            function_name="folder_structure_to_text",
            app=app,
            function_type=FunctionType.CLASSIC,
            client=client, # Ensure client is passed to parent
            static_parameters=static_parameters # Pass static parameters to parent
        )

        # Initialize attributes for parsed exclusions
        self._static_folders_set: Set[str] = set()
        self._static_exts_set: Set[str] = set()
        self._static_patterns_list: List[str] = []
        self._max_file_size_bytes: int = int(MAX_FILE_SIZE_MB * 1024 * 1024)

        # Parse initial exclusions based on config
        self._parse_static_exclusions()


    def _parse_static_exclusions(self):
        """
        Parses the static exclusion parameters from the configuration,
        prioritizing presets over custom settings unless 'Custom' is selected.
        Also parses the max file size. (Save option is handled in execute).
        """
        try:
            # Reset current static exclusions
            self._static_folders_set = set()
            self._static_exts_set = set()
            self._static_patterns_list = []

            # Get config values
            preset_name = self.static_parameters.config.get("exclusion_preset", "None/Defaults")
            custom_folders_str = self.static_parameters.config.get("custom_static_exclude_folders", "")
            custom_exts_str = self.static_parameters.config.get("custom_static_exclude_extensions", "")
            custom_patterns_str = self.static_parameters.config.get("custom_static_exclude_patterns", "")
            max_size_mb = self.static_parameters.config.get("max_file_size_mb", MAX_FILE_SIZE_MB)
            # Note: save_to_discussion_folder is checked in execute, not parsed here

            self._max_file_size_bytes = int(max(0.01, max_size_mb) * 1024 * 1024)

            active_preset_patterns = []

            if preset_name == "Custom":
                # Use the custom fields
                self.app.info(f"{self.function_name}: Using 'Custom' static exclusions.")
                self._static_folders_set = {f.strip().lower() for f in custom_folders_str.split(',') if f.strip()}
                self._static_exts_set = {e.strip().lower() for e in custom_exts_str.split(',') if e.strip() and e.strip().startswith('.')}
                self._static_patterns_list = [p.strip() for p in custom_patterns_str.split(',') if p.strip()]

            elif preset_name in self.PRESET_EXCLUSIONS:
                # Use the selected preset's patterns
                self.app.info(f"{self.function_name}: Using preset '{preset_name}' exclusions.")
                active_preset_patterns = self.PRESET_EXCLUSIONS.get(preset_name, [])
                # Presets primarily use patterns; folders/extensions are not parsed from custom fields here.
                self._static_patterns_list = active_preset_patterns # Assign preset patterns

            elif preset_name == "None/Defaults":
                self.app.info(f"{self.function_name}: Using only base defaults and dynamic exclusions (Preset: None/Defaults).")
                # All static lists/sets remain empty

            else:
                self.app.warning(f"{self.function_name}: Unknown preset '{preset_name}' selected. Falling back to None/Defaults.")
                # All static lists/sets remain empty

            # Log the final active static exclusions
            ASCIIColors.debug(f"  - Active Static Folders: {self._static_folders_set if self._static_folders_set else 'None'}")
            ASCIIColors.debug(f"  - Active Static Extensions: {self._static_exts_set if self._static_exts_set else 'None'}")
            ASCIIColors.debug(f"  - Active Static Patterns: {self._static_patterns_list if self._static_patterns_list else 'None'}")
            ASCIIColors.debug(f"  - Max file size: {max_size_mb} MB ({self._max_file_size_bytes} bytes)")


        except Exception as e:
            self.app.error(f"Error parsing static exclusion parameters for {self.function_name}: {e}", exc_info=True)
            # Reset to safe defaults on error
            self._static_folders_set = set()
            self._static_exts_set = set()
            self._static_patterns_list = []
            self._max_file_size_bytes = int(MAX_FILE_SIZE_MB * 1024 * 1024)

    def update_context(
        self,
        context: LollmsContextDetails,
        constructed_context: List[str]
    ) -> List[str]:
        """ Optional context update (no-op here). """
        return constructed_context

    def _is_excluded(self, item: Path, dynamic_exclude_patterns: List[str]) -> bool:
        """
        Checks if an item should be excluded based on base defaults,
        active static configuration (preset or custom), and dynamic arguments.
        The static configuration is determined by _parse_static_exclusions.
        """
        item_name_lower = item.name.lower()
        item_suffix_lower = item.suffix.lower() if item.is_file() else ""

        # 1. Check Base Exclusions (Folders & Extensions) - These always apply
        if item.is_dir():
            # Use fnmatch for base folders too, allowing patterns like '.git' to match '.github' if needed, though exact match is typical
            if any(fnmatch.fnmatchcase(item.name, pattern) for pattern in self.BASE_EXCLUDED_FOLDERS):
                 return True
            # Also check the lowercase set for direct name match
            if item_name_lower in self.BASE_EXCLUDED_FOLDERS:
                return True
        if item.is_file() and item_suffix_lower in self.BASE_EXCLUDED_EXTENSIONS:
            return True

        # 2. Check Active Static Exclusions (parsed from config - could be Custom or Preset)
        # These checks depend on whether the 'Custom' preset was selected.
        # If a preset was selected, _static_folders_set and _static_exts_set will be empty.
        if item.is_dir() and item_name_lower in self._static_folders_set: # Only has effect if preset is 'Custom'
            return True
        if item.is_file() and item_suffix_lower in self._static_exts_set: # Only has effect if preset is 'Custom'
            return True
        # Patterns apply for both 'Custom' and selected presets
        for pattern in self._static_patterns_list:
            # Use fnmatchcase for pattern consistency across OS for case sensitivity
            # Patterns can match file names ('*.log') or relative paths ('build/')
            # For folder patterns like 'build/', match directory names directly
            if item.is_dir():
                # Match pattern against folder name, potentially with trailing slash
                 if fnmatch.fnmatchcase(item.name, pattern.rstrip('/')):
                     return True
                 if pattern.endswith('/') and fnmatch.fnmatchcase(item.name, pattern[:-1]):
                     return True
            # Match pattern against file name
            if fnmatch.fnmatchcase(item.name, pattern):
                return True

        # 3. Check Dynamic Exclusions (from kwargs) - These always apply
        for pattern in dynamic_exclude_patterns:
            if fnmatch.fnmatchcase(item.name, pattern):
                return True

        return False

    def _is_text_file(self, file: Path) -> bool:
        """ Determines if file extension is in the allowed text list. """
        return file.suffix.lower() in self.ALLOWED_TEXT_EXTENSIONS

    def _read_file_content(self, file: Path) -> str:
        """ Reads file content, handling errors, encoding, and size limits. """
        try:
            file_size = file.stat().st_size
            if file_size > self._max_file_size_bytes:
                 # Get max size from current config
                 max_size_mb = self.static_parameters.config.get("max_file_size_mb", MAX_FILE_SIZE_MB)
                 return f"[File content omitted: Exceeds size limit ({max_size_mb}MB)]"
            if file_size == 0:
                return "[Empty file]"

            try:
                with open(file, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                self.app.info(f"File {file.name} not UTF-8, trying latin-1.")
                try:
                    with open(file, "r", encoding="latin-1") as f:
                        content = f.read()
                except Exception as read_err:
                    self.app.warning(f"Error reading file {file.name} with latin-1: {str(read_err)}")
                    return f"[Error reading file: Could not decode with UTF-8 or latin-1]"
            except Exception as read_err:
                self.app.warning(f"Error reading file {file.name}: {str(read_err)}")
                return f"[Error reading file: {str(read_err)}]"

            stripped_content = content.strip()
            return stripped_content if stripped_content else "[File contains only whitespace]"

        except OSError as os_err:
            self.app.warning(f"OS error accessing file {file.name}: {str(os_err)}")
            return f"[Error accessing file: {str(os_err)}]"
        except Exception as e:
            self.app.error(f"Unexpected error reading file {file.name}: {str(e)}")
            trace_exception(e) # Log traceback for unexpected errors
            return f"[Unexpected error reading file: {str(e)}]"

    def _build_tree_and_collect_files(
        self,
        folder: Path,
        dynamic_exclude_patterns: List[str], # Argument is only for dynamic patterns
        prefix: str = ""
    ) -> Tuple[List[str], List[Path]]:
        """
        Recursively builds the Markdown tree structure string and collects
        paths of text files to include. Uses the _is_excluded method which
        now considers base, static (preset or custom), and dynamic exclusions.
        """
        tree_lines = []
        found_files = []
        try:
            # Filter items using the consolidated _is_excluded method
            items = [
                item for item in folder.iterdir()
                if not self._is_excluded(item, dynamic_exclude_patterns) # Pass dynamic patterns here
            ]
            items.sort(key=lambda x: (x.is_file(), x.name.lower()))
        except PermissionError:
             tree_lines.append(f"{prefix}[Error listing directory: Permission denied]")
             return tree_lines, found_files
        except OSError as e:
            tree_lines.append(f"{prefix}[Error listing directory: {e}]")
            return tree_lines, found_files

        num_items = len(items)
        for i, item in enumerate(items):
            is_last = (i == num_items - 1)
            connector = TREE_LAST if is_last else TREE_BRANCH
            line_prefix = prefix + connector
            child_prefix = prefix + (TREE_SPACE if is_last else TREE_VLINE)

            if item.is_dir():
                tree_lines.append(f"{line_prefix}{FOLDER_ICON} {item.name}/")
                sub_tree_lines, sub_found_files = self._build_tree_and_collect_files(
                    item, dynamic_exclude_patterns, child_prefix # Pass dynamic patterns down
                )
                tree_lines.extend(sub_tree_lines)
                found_files.extend(sub_found_files)
            elif item.is_file():
                tree_lines.append(f"{line_prefix}{FILE_ICON} {item.name}")
                if self._is_text_file(item):
                    found_files.append(item)

        return tree_lines, found_files

    def _generate_file_contents_markdown(
        self,
        root_folder: Path,
        file_paths: List[Path]
    ) -> List[str]:
        """ Generates the Markdown section for displaying file contents. """
        content_lines = ["", "---", "", "## File Contents"]

        if not file_paths:
            content_lines.append("\n*No text files found or included based on filters and extensions.*")
            return content_lines

        file_paths.sort()

        for file_path in file_paths:
            try:
                relative_path = file_path.relative_to(root_folder)
            except ValueError:
                 relative_path = file_path.name
                 self.app.warning(f"Could not determine relative path for {file_path} against root {root_folder}. Using filename.")

            content_lines.append(f"\n### `{relative_path}`")
            file_content = self._read_file_content(file_path)
            lang = file_path.suffix[1:].lower() if file_path.suffix else "text"
            # Basic sanitization for language tag
            lang = "".join(c for c in lang if c.isalnum()) or "text"
            # Common aliases
            if lang == 'py': lang = 'python'
            if lang == 'js': lang = 'javascript'
            if lang == 'md': lang = 'markdown'
            if lang == 'sh': lang = 'bash'
            if lang == 'yml': lang = 'yaml'
            if lang == 'dockerfile': lang = 'docker'


            content_lines.append(f"```{lang}")
            if file_content.startswith("["): # Handle messages like size limit, read errors etc.
                 content_lines.append(file_content)
            else:
                # Ensure even empty files have a line inside the code block
                content_lines.extend(file_content.splitlines() or [""])
            content_lines.append("```")

        return content_lines

    def _sanitize_filename(self, filename: str) -> str:
        """ Removes or replaces characters invalid for filenames. """
        # Remove characters that are strictly disallowed or problematic in many filesystems
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', filename)
        # Optionally, replace multiple consecutive underscores with a single one
        sanitized = re.sub(r'_+', '_', sanitized)
        # Optionally, remove leading/trailing underscores/spaces
        sanitized = sanitized.strip(' _')
        # Limit length if necessary (though less common for this use case)
        # max_len = 100
        # if len(sanitized) > max_len:
        #     sanitized = sanitized[:max_len]
        return sanitized or "default_folder_name" # Ensure filename is not empty

    def execute(self, context: LollmsContextDetails, **kwargs) -> str:
        """
        Executes the function call. Generates a two-part Markdown output:
        1. Folder tree structure.
        2. Included text file contents with relative paths.
        Static exclusions are loaded based on the selected preset or custom settings.
        Dynamic exclusions are taken from kwargs.
        Optionally saves the output to the discussion folder.
        """
        self.app.info(f"Executing {self.function_name}...")

        # Re-parse static exclusions on each execution to reflect potential UI changes
        self._parse_static_exclusions()

        folder_path_str = kwargs.get("folder_path", "")
        dynamic_exclude_patterns = kwargs.get("exclude_patterns", [])
        save_copy = self.static_parameters.config.get("save_to_discussion_folder", True)

        # --- Parameter Validation ---
        if not folder_path_str:
            self.app.error("Parameter 'folder_path' is missing.")
            return "```error\nError: No folder path provided.\n```"
        if not isinstance(dynamic_exclude_patterns, list):
            self.app.warning(f"'exclude_patterns' parameter was not a list ({type(dynamic_exclude_patterns)}), using empty list for dynamic exclusions.")
            dynamic_exclude_patterns = []
        else:
            # Ensure dynamic patterns are strings
            dynamic_exclude_patterns = [str(p).strip() for p in dynamic_exclude_patterns if isinstance(p, (str, Path)) and str(p).strip()]

        try:
            # --- Path Resolution and Validation ---
            folder = Path(folder_path_str).resolve()
            if not folder.exists():
                self.app.error(f"Folder not found: {folder}")
                return f"```error\nError: Folder not found: {folder}\n```"
            if not folder.is_dir():
                self.app.error(f"Path is not a directory: {folder}")
                return f"```error\nError: The provided path is not a valid directory: {folder}\n```"

            # --- Generation ---
            self.app.info(f"Generating structure for: {folder}")
            self.app.info(f"Using dynamic exclude patterns: {dynamic_exclude_patterns if dynamic_exclude_patterns else 'None'}")


            # -- Part 1: Build Tree and Collect Files --
            # Pass only the *dynamic* exclude patterns here. Static/base ones are handled internally via _is_excluded.
            tree_lines, found_files = self._build_tree_and_collect_files(
                folder, dynamic_exclude_patterns, prefix=""
            )

            # Prepare structure output
            structure_output_lines = [
                f"# Folder Structure: {folder.name}",
                "",
                "```text",
                f"{FOLDER_ICON} {folder.name}/",
            ]
            structure_output_lines.extend(tree_lines)
            structure_output_lines.append("```")

            # -- Part 2: Generate File Contents --
            content_output_lines = self._generate_file_contents_markdown(
                folder, found_files
            )

            # -- Combine Outputs --
            full_output = "\n".join(structure_output_lines) + "\n" + "\n".join(content_output_lines)

            # -- Part 3: Optionally Save to Discussion Folder --
            if save_copy:
                discussion_folder: Optional[Path] = None
                if self.client and self.client.discussion and self.client.discussion.discussion_folder:
                    discussion_folder = self.client.discussion.discussion_folder

                if discussion_folder and discussion_folder.is_dir():
                    sanitized_folder_name = self._sanitize_filename(folder.name)
                    output_filename = f"textraction_{sanitized_folder_name}.md"
                    output_path = discussion_folder / output_filename
                    try:
                        output_path.write_text(full_output.strip(), encoding="utf-8")
                        self.app.info(f"Saved generated structure to discussion folder: {output_path}")
                    except OSError as e:
                        self.app.error(f"Failed to save output to discussion folder {output_path}: {e}")
                    except Exception as e:
                         self.app.error(f"Unexpected error saving output to discussion folder {output_path}: {e}")
                         trace_exception(e)
                elif save_copy: # Only warn if saving was intended but folder is invalid/missing
                     self.app.warning(f"Could not save output copy: Discussion folder not found or invalid ({discussion_folder}).")


            self.app.info(f"Folder structure and content generation complete for: {folder}")
            return full_output.strip()

        except PermissionError as pe:
             self.app.error(f"Permission error accessing path {folder_path_str}: {str(pe)}")
             trace_exception(pe)
             return f"```error\nError: Permission denied while accessing the folder or its contents: {str(pe)}\n```"
        except Exception as e:
            self.app.error(f"An unexpected error occurred during folder processing: {str(e)}", exc_info=True)
            trace_exception(e)
            return f"```error\nError: An unexpected error occurred: {str(e)}\n```"