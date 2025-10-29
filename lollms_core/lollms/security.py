from fastapi import HTTPException
from ascii_colors import ASCIIColors
import pipmaster as pm
pm.ensure_packages(["lxml","defusedxml"])
import defusedxml.ElementTree as ET
from defusedxml import ElementTree as ET
from io import StringIO

from urllib.parse import urlparse
import socket
from pathlib import Path
from typing import List
import os
import re
import platform
import string
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from fastapi import Request
import asyncio
import pipmaster as pm

pm.ensure_packages({"lxml":""})

import lxml.etree as ET


class NotLocalhostError(Exception):
    """Custom exception raised when an event is triggered from a non-localhost IP."""
    def __init__(self, message="This event can only be triggered from localhost.", sid=None, ip_address=None):
        super().__init__(message)
        self.sid = sid
        self.ip_address = ip_address

    def __str__(self):
        base_message = super().__str__()
        details = []
        if self.sid:
            details.append(f"SID: {self.sid}")
        if self.ip_address:
            details.append(f"IP: {self.ip_address}")
        if details:
            return f"{base_message} ({', '.join(details)})"
        return base_message
import socketio # For type hinting, actual sio instance passed in
import functools
import inspect

def _get_client_ip_from_environ(environ: dict) -> str | None:
    """
    Extracts the client IP address from the Socket.IO environment.
    Returns the IP string or None if not found.
    """
    if not environ:
        return None

    remote_ip = None
    # 1. aiohttp
    if 'aiohttp.request' in environ:
        aio_request = environ['aiohttp.request']
        if aio_request.transport:
            peername = aio_request.transport.get_extra_info('peername')
            if peername:
                remote_ip = peername[0]
        if not remote_ip:
            remote_ip = aio_request.remote
    # 2. WSGI (Flask, etc.)
    elif 'REMOTE_ADDR' in environ:
        remote_ip = environ['REMOTE_ADDR']
    # 3. ASGI (FastAPI/Uvicorn)
    elif 'asgi.scope' in environ:
        scope = environ['asgi.scope']
        if 'client' in scope and scope['client']:
            remote_ip = scope['client'][0]
    
    return remote_ip

def require_localhost(sio_instance: socketio.AsyncServer | socketio.Server):
    """
    Decorator for Socket.IO event handlers to restrict access to localhost.

    Args:
        sio_instance: The Socket.IO server instance (AsyncServer or Server).

    Raises:
        NotLocalhostError: If the event is triggered from a non-localhost IP,
                           or if the IP cannot be determined.
    """
    def decorator(event_handler_func):
        is_async_handler = inspect.iscoroutinefunction(event_handler_func)

        @functools.wraps(event_handler_func)
        async def async_wrapper(sid, *args, **kwargs):
            environ = sio_instance.get_environ(sid)
            client_ip = _get_client_ip_from_environ(environ)
            
            allowed_ips = ['127.0.0.1', '::1']
            env_allowed_ip = os.environ.get("ALLOWED_CLIENT_IP")
            # Check for wildcard first
            if env_allowed_ip == "*":
                print(f"ALLOWED_CLIENT_IP is '*', allowing request from {client_ip} without further IP checks.")
                return await event_handler_func(sid, *args, **kwargs)
            if env_allowed_ip:
                allowed_ips.append(env_allowed_ip)
                print(f"Dynamically added {env_allowed_ip} to allowed hosts from environment variable.")

            event_name = event_handler_func.__name__ # Or could try to get from sio.handlers

            if client_ip is None:
                print(f"DENIED (IP Undetermined): Event '{event_name}' from SID {sid}.")
                raise NotLocalhostError(
                    f"Access to '{event_name}' denied: Could not determine client IP.",
                    sid=sid
                )

            if client_ip not in allowed_ips:
                print(f"DENIED (Not Localhost): Event '{event_name}' from SID {sid}, IP: {client_ip}.")
                raise NotLocalhostError(
                    f"Access to '{event_name}' denied: Event restricted to localhost.",
                    sid=sid,
                    ip_address=client_ip
                )
            
            # If IP is allowed, proceed with the original handler
            # print(f"ALLOWED (Localhost): Event '{event_name}' for SID {sid}, IP: {client_ip}.")
            return await event_handler_func(sid, *args, **kwargs)

        @functools.wraps(event_handler_func)
        def sync_wrapper(sid, *args, **kwargs):
            environ = sio_instance.get_environ(sid)
            client_ip = _get_client_ip_from_environ(environ)

            allowed_ips = ['127.0.0.1', '::1']
            event_name = event_handler_func.__name__

            if client_ip is None:
                print(f"DENIED (IP Undetermined): Event '{event_name}' from SID {sid}.")
                raise NotLocalhostError(
                    f"Access to '{event_name}' denied: Could not determine client IP.",
                    sid=sid
                )

            if client_ip not in allowed_ips:
                print(f"DENIED (Not Localhost): Event '{event_name}' from SID {sid}, IP: {client_ip}.")
                raise NotLocalhostError(
                    f"Access to '{event_name}' denied: Event restricted to localhost.",
                    sid=sid,
                    ip_address=client_ip
                )
            
            # print(f"ALLOWED (Localhost): Event '{event_name}' for SID {sid}, IP: {client_ip}.")
            return event_handler_func(sid, *args, **kwargs)

        return async_wrapper if is_async_handler else sync_wrapper
    return decorator

def check_access(lollmsElfServer, client_id):
    client = lollmsElfServer.session.get_client(client_id)
    if not client:
        raise HTTPException(status_code=400, detail=f"Not accessible without id")
    return client


def sanitize_based_on_separators(line):
    """
    Sanitizes a line of code based on common command separators.

    Parameters:
    - line (str): The line of code to be sanitized.

    Returns:
    - str: The sanitized line of code.
    """
    separators = ['&', '|', ';']
    for sep in separators:
        if sep in line:
            line = line.split(sep)[0]  # Keep only the first command before the separator
            break
    return line.strip()

def sanitize_after_whitelisted_command(line, command):
    """
    Sanitizes the line after a whitelisted command, removing any following commands
    if a command separator is present.

    Parameters:
    - line (str): The line of code containing the whitelisted command.
    - command (str): The whitelisted command.

    Returns:
    - str: The sanitized line of code, ensuring only the whitelisted command is executed.
    """
    # Find the end of the whitelisted command in the line
    command_end_index = line.find(command) + len(command)
    # Extract the rest of the line after the whitelisted command
    rest_of_line = line[command_end_index:]
    # Sanitize the rest of the line based on separators
    sanitized_rest = sanitize_based_on_separators(rest_of_line)
    # If anything malicious was removed, sanitized_rest will be empty, so only return the whitelisted command part
    if not sanitized_rest:
        return line[:command_end_index].strip()
    else:
        # If rest_of_line starts directly with separators followed by malicious commands, sanitized_rest will be empty
        # This means we should only return the part up to the whitelisted command
        return line[:command_end_index + len(sanitized_rest)].strip()


def sanitize_svg(svg_content):
    try:
        # Use defusedxml's fromstring function 
        root = ET.fromstring(svg_content)

        # Define a list of allowed elements
        allowed_elements = {
            'svg', 'g', 'path', 'circle', 'rect', 'line', 'polyline', 'polygon',
            'text', 'tspan', 'defs', 'filter', 'feGaussianBlur', 'feMerge',
            'feMergeNode', 'linearGradient', 'radialGradient', 'stop'
        }

        # Define a list of allowed attributes
        allowed_attributes = {
            'id', 'class', 'style', 'fill', 'stroke', 'stroke-width', 'cx', 'cy',
            'r', 'x', 'y', 'width', 'height', 'd', 'transform', 'viewBox',
            'xmlns', 'xmlns:xlink', 'version', 'stdDeviation', 'result', 'in',
            'x1', 'y1', 'x2', 'y2', 'offset', 'stop-color', 'stop-opacity'
        }

        # Remove any disallowed elements
        for element in root.iter():
            if element.tag.split('}')[-1] not in allowed_elements:
                parent = element.getparent()
                if parent is not None:
                    parent.remove(element)

        # Remove any disallowed attributes
        for element in root.iter():
            for attr in list(element.attrib):
                if attr not in allowed_attributes:
                    del element.attrib[attr]

        # Convert the tree back to an SVG string
        sanitized_svg = ET.tostring(root, encoding='unicode', method='xml')
        return sanitized_svg
    except ET.ParseError as e:
        raise ValueError("Invalid SVG content") from e



def sanitize_shell_code(code, whitelist=None):
    """
    Securely sanitizes a block of code by allowing commands from a provided whitelist,
    but only up to the first command separator if followed by other commands.
    Sanitizes based on common command separators if no whitelist is provided.

    Parameters:
    - code (str): The input code to be sanitized.
    - whitelist (list): Optional. A list of whitelisted commands that are allowed.

    Returns:
    - str: The securely sanitized code.
    """
    
    # Split the code by newline characters
    lines = code.split('\n')
    
    # Initialize the sanitized code variable
    sanitized_code = ""
    
    for line in lines:
        if line.strip():  # Check if the line is not empty
            if whitelist:
                for command in whitelist:
                    if line.strip().startswith(command):
                        # Check for command separators after the whitelisted command
                        sanitized_code = sanitize_after_whitelisted_command(line, command)
                        break
            else:
                # Sanitize based on separators if no whitelist is provided
                sanitized_code = sanitize_based_on_separators(line)
            break  # Only process the first non-empty line
    
    return sanitized_code


class InvalidFilePathError(Exception):
    pass


def sanitize_path(path: str, allow_absolute_path: bool = False, allow_current_folder=False, error_text="Absolute database path detected", exception_text="Detected an attempt of path traversal or command injection. Are you kidding me?"):
    """
    Sanitize a given file path by checking for potentially dangerous patterns and unauthorized characters.

    Args:
    -----
    path (str): The file path to sanitize.
    allow_absolute_path (bool, optional): Whether to allow absolute paths. Default is False.
    error_text (str, optional): The error message to display if an absolute path is detected. Default is "Absolute database path detected".
    exception_text (str, optional): The exception message to display if a path traversal, command injection, or unauthorized character is detected. Default is "Detected an attempt of path traversal or command injection. Are you kidding me?".

    Raises:
    ------
    HTTPException: If an absolute path, path traversal, command injection, or unauthorized character is detected.

    Returns:
    -------
    str: The sanitized file path.

    Note:
    -----
    This function checks for patterns like "....", multiple forward slashes, and command injection attempts like $(whoami). It also checks for unauthorized punctuation characters, excluding the dot (.) character.
    """    
    if path is None:
        return path

    if not allow_absolute_path:
        # Normalize path to use forward slashes
        path = path.replace('\\', '/')
    path = path.strip()

    if not allow_current_folder and path=="./":
        raise HTTPException(status_code=400, detail="current folder paths is disallowed for this endpoint!")

    if not allow_absolute_path and (path.startswith("/") or (len(path) == 2 and path[1] == ':')):
        raise HTTPException(status_code=400, detail=exception_text)


    # Regular expression to detect patterns like "....", multiple forward slashes, and command injection attempts like $(whoami)
    suspicious_patterns = re.compile(r'(\.\.+)|(/+/)|(\$\(.*\))')

    if suspicious_patterns.search(str(path)) or ((not allow_absolute_path) and Path(path).is_absolute()):
        ASCIIColors.error(error_text)
        raise HTTPException(status_code=400, detail=exception_text)

    # Detect if any unauthorized characters, excluding the dot character, are present in the path
    unauthorized_chars = set('!"#$%&\'()*+,;<=>?@[]^`{|}~')
    if any(char in unauthorized_chars for char in path):
        raise HTTPException(status_code=400, detail=exception_text)

    if not allow_absolute_path:
        path = path.lstrip('/')

    return path

    
def sanitize_path_from_endpoint(path: str, error_text: str = "A suspected LFI attack detected. The path sent to the server has suspicious elements in it!", exception_text: str = "Invalid path!") -> str:
    """
    Sanitize a given file path from an endpoint by checking for potentially dangerous patterns and unauthorized characters,
    and standardizing path separators to prevent directory traversal attacks.

    Args:
    -----
    path (str): The file path to sanitize.
    error_text (str, optional): Error message to display if a path traversal or unauthorized character is detected. Default is a warning about a suspected LFI attack.
    exception_text (str, optional): Exception message to display if an absolute path or invalid character is detected. Default is "Invalid path!".

    Raises:
    ------
    HTTPException: If an absolute path, path traversal, or unauthorized character is detected.

    Returns:
    -------
    str: The sanitized file path.
    """

    if path is None:
        return path

    # Normalize path to use forward slashes
    path = path.replace('\\', '/')

    if path.strip().startswith("/"):
        raise HTTPException(status_code=400, detail=exception_text)

    # Regular expression to detect patterns like "...." and multiple forward slashes
    suspicious_patterns = re.compile(r'(\.\.+)|(/+/)')

    # Detect if any unauthorized characters, excluding the dot character, are present in the path
    unauthorized_chars = set('!"#$%&\'()*+,;<=>?@[]^`{|}~')
    if any(char in unauthorized_chars for char in path):
        raise HTTPException(status_code=400, detail=exception_text)

    if suspicious_patterns.search(path) or Path(path).is_absolute():
        raise HTTPException(status_code=400, detail=error_text)

    path = path.lstrip('/')
    return path



def forbid_remote_access(lollmsElfServer, exception_text = "This functionality is forbidden if the server is exposed"):
    if not lollmsElfServer.config.force_accept_remote_access and lollmsElfServer.config.host!="localhost" and lollmsElfServer.config.host!="127.0.0.1":
        raise Exception(exception_text)

def validate_path(path, allowed_paths:List[str|Path]):
    # Convert the path to an absolute path
    abs_path = os.path.realpath(str(path))

    # Iterate over the allowed paths
    for allowed_path in allowed_paths:
        # Convert the allowed path to an absolute path
        abs_allowed_path = os.path.realpath(allowed_path)

        # Check if the absolute path starts with the absolute allowed path
        if abs_path.startswith(abs_allowed_path):
            return True

    # If the path is not within any of the allowed paths, return False
    return False

def is_allowed_url(url):
    # Check if url is legit
    parsed_url = urlparse(url)        
    # Check if scheme is not http or https, return False
    if parsed_url.scheme not in ['http', 'https']:
        return False
    
    hostname = parsed_url.hostname
    
    try:
        ip_address = socket.gethostbyname(hostname)
    except socket.gaierror:
        return False
    
    return not ip_address.startswith('127.') or ip_address.startswith('192.168.') or ip_address.startswith('10.') or ip_address.startswith('172.')


if __name__=="__main__":
    test_cases = [
        # Unix-style paths
        ("valid/path/to/file.txt", False, False),
        ("../../etc/passwd", False, False),
        ("/absolute/path/file.txt", False, False),
        ("relative/path/file.txt", False, False),
        ("valid/path/with/..", False, False),
        ("valid/path/with/./file.txt", False, False),
        ("another/valid/path/file.txt", True, False),
        ("/absolute/path/allowed.txt", True, False),
        ("$(whoami)", False, False),
        ("path/with/unauthorized&chars", False, False),
        (None, False, False),

        # Windows-style paths
        (r"valid\path\to\file.txt", False, False),
        (r"..\..\etc\passwd", False, False),
        (r"C:\absolute\path\file.txt", False, False),
        (r"relative\path\file.txt", False, False),
        (r"valid\path\with\..", False, False),
        (r"valid\path\with\.\file.txt", False, False),
        (r"another\valid\path\file.txt", True, False),
        (r"C:\absolute\path\allowed.txt", True, False),
        (r"$(whoami)", False, False),
        (r"path\with\unauthorized&chars", False, False),

        # New test cases with C: drive
        (r"C:\valid\path\to\file.txt", False, False),
        (r"C:\another\valid\path\file.txt", True, False),
        (r"C:\..\etc\passwd", False, False),
        (r"C:\valid\path\with\..", False, False),
        (r"C:", False, False),
        (r"./", False, False),
    ]

    for path, allow_absolute, allow_current_folder in test_cases:
        try:
            sanitized = sanitize_path(path, allow_absolute, allow_current_folder)
            print(f"Original: {path}, Sanitized: {sanitized}")
        except HTTPException as e:
            print(f"Original: {path}, Exception: {e.detail}")
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from starlette.responses import JSONResponse
import re

class MultipartBoundaryCheck(BaseHTTPMiddleware):
    def __init__(self, app, max_boundary_length=70, max_trailing_boundary_length=100):
        super().__init__(app)
        self.max_boundary_length = max_boundary_length
        self.max_trailing_boundary_length = max_trailing_boundary_length

    async def dispatch(self, request: Request, call_next):
        if request.headers.get("content-type", "").startswith("multipart/form-data"):
            content_type = request.headers.get("content-type", "")
            boundary_start = content_type.find("boundary=")
            
            if boundary_start == -1:
                return JSONResponse(status_code=400, content={"detail": "Missing boundary in content-type header"})
            
            boundary = content_type[boundary_start + 9:]  # 9 is the length of "boundary="
            
            # Check header boundary
            if len(boundary) > self.max_boundary_length or not self.is_valid_boundary(boundary):
                return JSONResponse(status_code=400, content={"detail": "Invalid boundary in header"})
            
            # Check trailing boundary if it exists
            body = await request.body()
            trailing_boundary = b"--" + boundary.encode() + b"--"
            if trailing_boundary in body:
                trailing_content = body[body.rfind(trailing_boundary):]
                if len(trailing_content) > self.max_trailing_boundary_length:
                    return JSONResponse(status_code=400, content={"detail": "Trailing boundary too long"})
                
                # Check for multiple trailing boundaries
                if body.count(trailing_boundary) > 1:
                    return JSONResponse(status_code=400, content={"detail": "Multiple trailing boundaries detected"})
            
            # Note: We're not returning an error if there's no trailing boundary
            
        return await call_next(request)

    def is_valid_boundary(self, boundary):
        # RFC 2046 states that the boundary should only contain these characters
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'()+_,-./:=?")
        return all(char in valid_chars for char in boundary)
