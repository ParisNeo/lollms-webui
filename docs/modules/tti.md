## Lollms Text-to-Image (TTI) Module Documentation

**Objective:** To provide a standardized way to integrate various Text-to-Image generation services (APIs, local models, etc.) into the Lollms ecosystem.

**Core Idea:** Lollms uses a modular approach. Each specific TTI implementation (like Stable Diffusion via Automatic1111, ComfyUI, an online API like DALL-E, Midjourney, or Google Imagen) is contained within its own *binding* or *module*. These modules all inherit from a common base class, `LollmsTTI`, ensuring they provide a consistent interface for the main Lollms application.

---

### 1. The `LollmsTTI` Base Class

The `lollms.tti.LollmsTTI` class serves as the foundation for all TTI modules. It defines the essential methods and properties that Lollms expects any TTI service to provide.

*   **Inheritance:** `LollmsTTI` inherits from `lollms.service.LollmsSERVICE`. This is important because `LollmsSERVICE` provides the basic framework for any Lollms service, including:
    *   Access to the main `LollmsApplication` instance (`self.app`).
    *   Handling of configuration via `TypedConfig` (`self.service_config`).
    *   A unique `name` for the service.
    *   Standard logging methods via `self.app` (e.g., `self.app.info`, `self.app.error`).

*   **Key Purpose:** To define a contract. Any class inheriting from `LollmsTTI` *must* implement (or override) certain methods to be compatible with Lollms' image generation features.

*   **Initialization (`__init__`)**:
    *   `name: str`: A unique identifier for this specific TTI service (e.g., "google_gemini", "automatic1111", "comfyui").
    *   `app: LollmsApplication`: The main Lollms application instance, providing access to global settings, paths, logging, etc.
    *   `service_config: TypedConfig`: An object holding the specific configuration settings for *this* TTI service (e.g., API keys, model paths, default parameters). This is usually created from a `ConfigTemplate`.
    *   `output_folder: str | Path | None`: Specifies where generated images should be saved. If `None`, it defaults to a standard location within the Lollms personal outputs path (`lollms_paths.personal_outputs_path / name`). The constructor ensures this folder exists.

*   **Core Generation Methods:**
    *   `paint(...)`: The primary method for standard text-to-image generation.
        *   **Input:** `positive_prompt`, `negative_prompt`, and common Stable Diffusion-style parameters (`sampler_name`, `seed`, `scale`, `steps`, `width`, `height`). It also takes optional `output_folder` and `output_file_name` overrides.
        *   **Implementation Detail:** **Crucially, not all TTI backends support all these parameters.** A specific module (like `LollmsGoogleGemini`) might ignore parameters like `seed`, `steps`, `sampler_name`, or derive `width`/`height` from an `aspect_ratio` setting, as seen in the example. The implementation should handle the parameters relevant to its backend API or model.
        *   **Output:** `List[Dict[str, Any]]`. A list containing one dictionary per generated image. Each dictionary *must* have at least a `'path'` key pointing to the saved image file. It *should* also include a `'metadata'` key containing a dictionary of generation parameters (prompts, model used, seed, steps, etc.) for reproducibility and information.
    *   `paint_from_images(...)`: Intended for image-to-image, inpainting, or image variation tasks.
        *   **Input:** `positive_prompt`, a `List[str]` of input image file paths (`images`), `negative_prompt`, and the same optional parameters as `paint`.
        *   **Implementation Detail:** Similar to `paint`, the specific module must adapt this to its backend's capabilities. Some backends might only use the first image, others might support multiple. The `LollmsGoogleGemini` example shows using the first image with Gemini 2.0 for image+text prompting.
        *   **Output:** Same format as `paint`: `List[Dict[str, Any]]`.

*   **Static Utility Methods:** These methods are called by Lollms *before* an instance of the TTI module is necessarily created. They operate at the class level.
    *   `verify(app: LollmsApplication) -> bool`: Checks if the necessary prerequisites for this TTI module are met. This usually involves checking if required libraries are installed (e.g., `google-generativeai` for the Gemini example) or if essential configuration (like an API key placeholder) exists. It often uses helper libraries like `pipmaster` (`pm`) as shown. Should return `True` if usable, `False` otherwise.
    *   `install(app: LollmsApplication) -> bool`: Attempts to install any missing prerequisites identified by `verify`. Typically uses `pipmaster` (`pm.install_if_missing`). Should return `True` on success, `False` on failure.
    *   `get(app: LollmsApplication, config: Optional[dict]=None, lollms_paths: Optional[LollmsPaths]=None) -> 'LollmsTTI'`: A factory method. Lollms calls this static method to get an actual instance of the specific TTI class (e.g., `LollmsGoogleGemini`). It passes the `app` instance and potentially pre-loaded configuration (`config`) and paths (`lollms_paths`).

---

### 2. How TTI Modules are Used by Lollms

1.  **Discovery:** Lollms scans designated directories for bindings/modules.
2.  **Verification & Installation:** For each potential TTI module found, Lollms might call its static `verify` method. If verification fails and installation is requested or automatic, it calls the static `install` method.
3.  **Listing:** Verified modules are presented to the user as available TTI services.
4.  **Selection & Configuration:** The user selects a TTI service. Lollms loads its configuration template (`ConfigTemplate`) and presents the settings (like API key, model choice, etc.) to the user. User inputs are saved.
5.  **Instantiation:** When the user wants to generate an image using the selected service, Lollms calls the static `get` method of the chosen module's class, passing the `app` instance and the loaded service `config`. This returns an active instance (e.g., an instance of `LollmsGoogleGemini`).
6.  **Generation Request:** When the user provides prompts (and potentially other parameters or input images), Lollms calls the appropriate method on the instantiated object:
    *   For text-to-image: `instance.paint(...)`
    *   For image-to-image/variation: `instance.paint_from_images(...)`
7.  **Execution:** The module's `paint` or `paint_from_images` method executes:
    *   It potentially initializes its specific client or loads its model if not already done (as seen in `_initialize_client` in the example).
    *   It translates the Lollms parameters (prompts, dimensions, etc.) into the format required by its backend (API call parameters, model inference arguments). It may ignore unsupported Lollms parameters.
    *   It communicates with the backend (makes the API call, runs the inference).
    *   It receives the image data (e.g., bytes, base64).
    *   It saves the image data to a file in the designated output folder (using helpers like `find_next_available_filename` if no specific name is given). PIL (Pillow) is commonly used for saving.
    *   It constructs the metadata dictionary.
    *   It returns the list of dictionaries (`[{'path': ..., 'metadata': ...}]`) back to Lollms.
8.  **Display:** Lollms receives the list and displays the generated image(s) (using the `path`) and potentially the metadata to the user.

---

### 3. Developing a New TTI Module

Here’s a step-by-step guide based on the `LollmsGoogleGemini` example:

1.  **Create the Module File:** Create a Python file in the appropriate Lollms bindings directory (e.g., `bindings/google_gemini/binding.py`). Add header comments detailing the binding (Title, Author, Licence, Description, Requirements).

2.  **Import Necessary Libraries:** Import `LollmsTTI`, `LollmsApplication`, `Path`, `List`, `Dict`, `Optional`, configuration classes (`TypedConfig`, `ConfigTemplate`), utility functions (`find_next_available_filename`, `ASCIIColors`, `trace_exception`), and any libraries required for your specific TTI backend (e.g., `requests`, `google.generativeai`, `PIL`, `diffusers`, etc.).

3.  **Handle Dependencies:**
    *   Use a `try...except ImportError` block to check if the required backend libraries are installed.
    *   If missing, use `ASCIIColors.info` to inform the user and `pipmaster.install` (`pm.install`) to install them. Re-import after installation or raise an error if it fails. This ensures the binding doesn't crash Lollms if dependencies are missing initially.

4.  **Define the Class:** Create a class that inherits from `LollmsTTI`.
    ```python
    from lollms.tti import LollmsTTI
    # ... other imports

    class LollmsMyTTIService(LollmsTTI):
        # ... implementation ...
    ```

5.  **Implement `__init__`:**
    *   Define the `__init__` method accepting `app`, `service_config`, and optional `lollms_paths` (if needed beyond what `app` provides) or `config` dict.
    *   Define the `ConfigTemplate` for your service's settings (API keys, models, defaults).
    *   Create the `TypedConfig` instance: `service_config = TypedConfig(service_config_template, config or {})`.
    *   **Crucially, call the parent constructor:** `super().__init__("my_tti_service_name", app, service_config, output_folder)`. Ensure the `name` is unique. Handle the `output_folder` logic as in the base class or example.
    *   Initialize any state needed for your service (e.g., set API clients to `None`, load default values from `service_config`).
    *   Optionally, attempt to initialize the backend client immediately if configuration allows (like the Gemini example checking for an API key).

6.  **Implement `paint`:**
    *   Define the `paint` method with the standard signature.
    *   Add logic to ensure your backend client/model is initialized (call an internal `_initialize_client` or similar helper if needed). Handle initialization failures gracefully.
    *   Retrieve necessary parameters from `self.service_config` (e.g., model name, specific quality settings).
    *   Translate the input parameters (`positive_prompt`, `negative_prompt`, etc.) into the format expected by your backend API or model.
        *   **Handle unsupported parameters:** Log a warning (`self.app.warning` or `ASCIIColors.warning`) if parameters like `seed`, `steps`, `sampler_name` are provided but ignored by your backend.
        *   **Combine prompts:** Decide how to handle `negative_prompt` if your backend doesn't have a separate parameter (e.g., append it, ignore it, use specific syntax).
    *   Make the call to your TTI backend. Wrap this in a `try...except` block to catch potential API errors (authentication, rate limits, network issues, invalid arguments, content filtering) or model inference errors. Use `self.app.error` and `trace_exception` for logging.
    *   Process the response. Extract the image data (bytes, base64, etc.).
    *   Determine the output filename (use `output_file_name` if provided, otherwise generate one using `find_next_available_filename`).
    *   Save the image data to a file using `PIL` or another appropriate library. Ensure the output folder exists (`self._ensure_output_folder`).
    *   Create the `metadata` dictionary, including prompts, model info, relevant settings, generation time, etc.
    *   Append `{'path': str(file_path), 'metadata': metadata}` to a `results` list.
    *   Return the `results` list. Return an empty list `[]` on failure.

7.  **Implement `paint_from_images`:**
    *   Define the `paint_from_images` method with the standard signature.
    *   Check if your backend actually supports image inputs. If not, log an error and return `[]`.
    *   Load the input image(s) from the provided `images` paths (e.g., using `PIL`). Handle file-not-found errors. Decide how many input images your backend supports (often just the first one).
    *   Follow similar steps as `paint`: initialize client, translate parameters, make the backend call (providing the image data alongside the prompt), handle errors, process the response, save the output image(s), create metadata (include the input image filename), and return the `results` list.

8.  **Implement Static Methods:**
    *   `verify(app: LollmsApplication) -> bool`: Implement the check for dependencies (e.g., `return pm.install_if_missing("my_required_library")`).
    *   `install(app: LollmsApplication) -> bool`: Implement the installation command (e.g., `return pm.install_if_missing("my_required_library")`).
    *   `get(app: LollmsApplication, config: Optional[dict]=None, lollms_paths: Optional[LollmsPaths]=None) -> 'LollmsMyTTIService'`: Implement the factory method: `return LollmsMyTTIService(app=app, config=config, lollms_paths=lollms_paths)`.

9.  **Helper Methods (Optional but Recommended):**
    *   Create private helper methods like `_initialize_client`, `_ensure_output_folder`, etc., to keep `paint` and `paint_from_images` cleaner, as shown in the Gemini example.
    *   Consider a `settings_updated` method if client re-initialization is needed when settings (like API key) change via the UI.

10. **Testing:** Test thoroughly with different prompts, negative prompts, parameters (even unsupported ones to check warnings), and error conditions (invalid API key, network down).

---

By following this structure and inheriting from `LollmsTTI`, developers can seamlessly integrate diverse image generation capabilities into Lollms, providing users with a wide range of choices through a consistent interface. The `LollmsGoogleGemini` example serves as an excellent template for implementing API-based TTI services.