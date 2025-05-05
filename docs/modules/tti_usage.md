Okay, here is the documentation on how to use an available Lollms TTI binding instance within your Lollms code (e.g., inside a Personality, Service, or extension).

## Using the Lollms TTI Service (`self.lollms.tti`)

This documentation assumes you are working within a Lollms component (like a Personality class) where you have access to the main Lollms application instance, typically via `self.lollms`, and the currently selected and configured Text-to-Image service is available as `self.lollms.tti`.

`self.lollms.tti` is an instance of a class derived from `LollmsTTI` (e.g., `LollmsGoogleGemini`, `LollmsAutomatic1111`, etc.). It provides a standardized interface to generate images, regardless of the underlying backend service.

---

### Prerequisites

1.  **TTI Service Enabled:** The user must have selected and enabled a TTI service in the Lollms settings.
2.  **TTI Service Configured:** The selected TTI service must be properly configured (e.g., with necessary API keys, model paths, URLs).
3.  **Accessibility:** Your code must have access to the Lollms application object, commonly referred to as `self.lollms` or `self.app` depending on the context, which in turn provides access to the TTI service via `.tti`.

---

### Core Methods

The `self.lollms.tti` object exposes two primary methods for image generation:

1.  **`paint(...)`**: For standard Text-to-Image generation.
2.  **`paint_from_images(...)`**: For Image-to-Image, variations, or editing based on input images.

---

#### 1. `paint(...)` - Text-to-Image Generation

This method generates images based purely on textual prompts and parameters.

```python
paint(
    positive_prompt: str,
    negative_prompt: str = "", # Handled based on backend capabilities
    sampler_name: str = "Default", # Often ignored by non-Stable Diffusion backends
    seed: Optional[int] = None,   # Often ignored by API backends
    scale: Optional[float] = None, # Guidance Scale - Often ignored by API backends
    steps: Optional[int] = None,   # Often ignored by API backends
    width: Optional[int] = None,   # May be derived from aspect ratio or ignored
    height: Optional[int] = None,  # May be derived from aspect ratio or ignored
    output_folder: Optional[str | Path] = None, # Override default save location
    output_file_name: Optional[str] = None # Suggest a base filename (without extension)
) -> Tuple[Path | None, Dict | None]
```

**Parameters:**

*   `positive_prompt` (str): **Required.** A description of the image you want to generate.
*   `negative_prompt` (str): A description of elements or styles to avoid in the image.
    *   *Note:* How effectively this is used depends heavily on the backend TTI service. Some APIs might blend it with the positive prompt, others might have limited support, and some might ignore it. The binding attempts to handle it appropriately for its backend.
*   `sampler_name`, `seed`, `scale`, `steps`: These are parameters common in Stable Diffusion workflows.
    *   **Important:** Many TTI backends (especially commercial APIs like DALL-E, Midjourney, Google Imagen) **do not support** these parameters directly. The specific `LollmsTTI` binding you are using might ignore them. Consult the specific binding's documentation or configuration if precise control over these is needed and seems ineffective.
*   `width`, `height`: Desired image dimensions.
    *   *Note:* Some backends might enforce specific aspect ratios or resolutions. The binding might use configuration settings (like `aspect_ratio` in the Gemini example) or default values if these are not supported or provided.
*   `output_folder` (Optional[str | Path]): If specified, the generated image will be saved here instead of the binding's default output folder.
*   `output_file_name` (Optional[str]): If specified, the binding will use this as the base name for the saved file (e.g., "my_image" -> "my_image.png"). If omitted, the binding generates a unique filename (e.g., `service_img_0001.png`).

**Returns:**

*   `Tuple[Path | None, Dict | None]`: A tuple containing:
    *   The `Path` object pointing to the first successfully generated and saved image file.
    *   A `Dict` containing metadata about the generation process (prompts, model used, etc.).
*   **On Failure:**
    *   Returns `(None, error_dict)` where `error_dict` is a dictionary containing an `'error'` key with a description of the failure (API error, configuration issue, network problem, content filtering, etc.).
    *   You should always check if the first element of the returned tuple is `None` to determine if the generation was successful. Check Lollms logs (`self.app.error(...)` or in the console/log file) for more details on failures.

**Example Usage:**

```python
# Assuming 'self.app.tti' is available and configured (or self.tti if inside a class with it)

positive = "A photorealistic painting of a red panda coding on a laptop in a bamboo forest, vibrant colors, detailed fur."
negative = "blurry, low quality, cartoon, text, watermark, signature, deformed paws"

try:
    # Call paint, expecting a tuple
    image_path, metadata_or_error = self.app.tti.paint(
        positive_prompt=positive,
        negative_prompt=negative,
        # Optional: Specify a filename base
        # output_file_name="red_panda_coder"
        # Optional: Specify dimensions if you know the backend supports it
        # width=1024,
        # height=1024
    )

    # Check if image_path is valid (not None)
    if image_path:
        self.app.print_message(f"Image generated successfully: {image_path}")
        # You can now use the image_path, e.g., display it, process it further.
        # print(f"Metadata: {metadata_or_error}") # Contains generation info
    else:
        # Generation failed, metadata_or_error contains the error details
        error_message = metadata_or_error.get('error', 'Unknown TTI error')
        self.app.print_message(f"TTI service failed to generate the image: {error_message}")
        self.app.error(f"TTI Failure Details: {metadata_or_error}") # Log the full error dict
        # Handle the failure case

except Exception as e:
    self.app.print_message(f"An unexpected error occurred while calling paint: {e}")
    # Log the exception details if needed
    trace_exception(e) # Assuming trace_exception is available
```

---

#### 2. `paint_from_images(...)` - Image-to-Image Generation

This method generates images based on textual prompts *and* one or more input images. Use cases include image variation, style transfer, or guided editing.

**Important:** Not all TTI backends support image inputs. Check if the currently selected binding (`self.app.tti`) implements this functionality. If not, it will likely return `(None, error_dict)`.

```python
paint_from_images(
    positive_prompt: str,
    images: List[str], # List of input image file paths
    negative_prompt: str = "",
    sampler_name="Default", # Often ignored
    seed=None, # Often ignored
    scale=None, # Often ignored
    steps=None, # Often ignored
    width=None, # Often ignored or derived from input
    height=None, # Often ignored or derived from input
    output_folder=None,
    output_file_name=None
) -> Tuple[Path | None, Dict | None]
```

**Parameters:**

*   `positive_prompt` (str): **Required.** Description of the desired output or modification.
*   `images` (List[str]): **Required.** A list containing the file paths to the input image(s).
    *   *Note:* Many backends only support *one* input image. The binding will typically use `images[0]` in such cases and might issue a warning if more than one path is provided.
*   `negative_prompt` (str): Description of elements to avoid. Same caveats as in `paint`.
*   `sampler_name`, `seed`, `scale`, `steps`, `width`, `height`: Same caveats as in `paint`. Dimensions might often be derived from the input image.
*   `output_folder`, `output_file_name`: Same behavior as in `paint`.

**Returns:**

*   `Tuple[Path | None, Dict | None]`: Same format as `paint`. Returns the path to the first successfully generated output image and its metadata. The metadata might also include information about the input image(s) used.
*   **On Failure:** Returns `(None, error_dict)` if the generation fails or if the backend doesn't support image-to-image.

**Example Usage:**

```python
# Assuming 'self.app.tti' is available, configured, and supports img2img
# Assuming 'input_image_path' is the path to a valid image file

input_image_path = "/path/to/your/input/image.jpg" # Replace with actual path

if not Path(input_image_path).exists():
     self.app.print_message(f"Input image not found: {input_image_path}")
else:
    positive = "Make this image look like a Van Gogh painting."
    negative = "photorealistic, modern, blurry"

    try:
        # Call paint_from_images, expecting a tuple
        image_path, metadata_or_error = self.app.tti.paint_from_images(
            positive_prompt=positive,
            images=[input_image_path], # Pass as a list
            negative_prompt=negative,
            output_file_name="van_gogh_style"
        )

        # Check if image_path is valid
        if image_path:
            self.app.print_message(f"Image generated from image: {image_path}")
            # print(f"Metadata: {metadata_or_error}")
        else:
            # Generation failed
            error_message = metadata_or_error.get('error', 'Unknown img2img error')
            self.app.print_message(f"TTI service failed to generate from image: {error_message}")
            self.app.error(f"Img2Img Failure Details: {metadata_or_error}") # Log the full error dict
            # Handle the failure case

    except Exception as e:
        self.app.print_message(f"An unexpected error occurred while calling paint_from_images: {e}")
        trace_exception(e) # Assuming trace_exception is available
```

---

### Important Considerations

*   **Backend Variability:** The core strength of `LollmsTTI` is abstraction, but remember that the underlying backends have different capabilities. Don't rely on parameters like `seed`, `steps`, or precise `width`/`height` control unless you know the specific active binding supports them.
*   **Configuration:** The behavior of `self.lollms.tti` (e.g., which model is used, quality settings, aspect ratio) is determined by the user's configuration for that specific TTI service in Lollms settings. Your code uses these settings implicitly.
*   **Error Handling:** Always check if the returned list is empty (`if results:`). Consult Lollms logs for detailed error messages from the binding (e.g., API key errors, network issues, content filters, unsupported requests).
*   **Asynchronous Execution:** Depending on the backend and how Lollms integrates it, these calls might block execution until the image is generated. For complex UIs or long-running tasks, consider running these calls in separate threads or using asynchronous patterns if available within your Lollms component context.