import traceback
from ascii_colors import ASCIIColors
from enum import Enum
from urllib.parse import urlparse
import re # Optional: for more complex validation if needed


def is_valid_url(url_string: str) -> bool:
    """
    Checks if the given string represents a potentially valid HTTP or HTTPS URL.

    This performs a basic structural check using urllib.parse and ensures
    the scheme and network location are present. It doesn't guarantee
    the URL is reachable or exists.

    Args:
        url_string: The string to validate.

    Returns:
        True if the string appears to be a valid HTTP/HTTPS URL, False otherwise.
    """
    if not isinstance(url_string, str) or not url_string:
        return False
    try:
        # Parse the URL string
        parsed_url = urlparse(url_string)

        # Check for essential components:
        # 1. Scheme must be 'http' or 'https'.
        # 2. Network location (domain name or IP address) must be present.
        if parsed_url.scheme in ['http', 'https'] and parsed_url.netloc:
            # Optional additional check: ensure netloc looks like a domain/IP
            # This regex is basic and might not cover all edge cases (like IDNs)
            # but helps filter out things like 'http:///'
            # netloc_pattern = r"^[a-zA-Z0-9.-]+(?::\d+)?$" # Basic domain/IP + optional port
            # if re.match(netloc_pattern, parsed_url.netloc):
            #    return True
            return True # Keep it simple for now, scheme + netloc is usually sufficient

        return False
    except ValueError:
        # urlparse might raise ValueError for severely malformed strings
        # (though it's often lenient)
        return False
    except Exception as e:
        # Catch any unexpected errors during parsing
        # You might want to log this if it happens unexpectedly
        # print(f"Unexpected error validating URL '{url_string}': {e}")
        trace_exception(e) # Use existing helper if available
        return False


def get_trace_exception(ex):
    """
    Traces an exception (useful for debug) and returns the full trace of the exception
    """
    # Catch the exception and get the traceback as a list of strings
    traceback_lines = traceback.format_exception(type(ex), ex, ex.__traceback__)

    # Join the traceback lines into a single string
    traceback_text = ''.join(traceback_lines)        
    return traceback_text

def trace_exception(ex):
    """
    Traces an exception (useful for debug)
    """
    ASCIIColors.error(get_trace_exception(ex))

