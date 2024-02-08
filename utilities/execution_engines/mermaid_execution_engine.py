"""
project: lollms_webui
file: shell_execution_engine.py 
author: ParisNeo
description: 
    This is a utility for executing python code

"""
from lollms_webui import LOLLMSWebUI
from ascii_colors import get_trace_exception, trace_exception
import time
import subprocess
import json

lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()          

def build_mermaid_output(code, ifram_name="unnamed"):
    """
    This function creates an HTML5 iframe with the given HTML content and iframe name.

    Args:
    code (str): The mermaid code
    ifram_name (str, optional): The name of the iframe. Defaults to "unnamed".

    Returns:
    str: The HTML string for the iframe.
    """
    # Start the timer.
    start_time = time.time()    
    rendered =  "\n".join([
        '<div style="width: 100%; margin: 0 auto;">',
        f'<iframe id="{ifram_name}" srcdoc="',
        '<style>',
        '.mermaid {',
        'background-color: transparent;',
        'padding: 20px;',
        'border-radius: 10px;',
        'display: flex;',
        'justify-content: center;',
        'align-items: center;',
        'height: 100%;',
        '}',
        '</style>',
        '<div class=\'mermaid\'>',
        "\n".join([c for c in code.split("\n") if c.strip()!=""]),
        '</div>',
        '<button onclick="saveSVG()">Save SVG</button>',
        '<script src=\'https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js\'></script>',
        '<script>',
        '// Initialize the mermaid library and render our diagram',
        'mermaid.initialize({ startOnLoad: true });',
        '// Function to save SVG content to a file',
        'function saveSVG() {',
        'var svg = document.querySelector(".mermaid > svg");',
        'var serializer = new XMLSerializer();',
        'var source = serializer.serializeToString(svg);',
        'var blob = new Blob([source], {type: "image/svg+xml;charset=utf-8"});',
        'var url = URL.createObjectURL(blob);',
        'var a = document.createElement("a");',
        'a.href = url;',
        'a.download = "diagram.svg";',
        'a.click();',
        '}',
        '</script>',
        '<div style=\'text-align: center;\'>',
        '</div>',
        '" style="width: 100%; height: 600px; border: none;"></iframe>',
        '</div>'
        ]
    )
    execution_time = time.time() - start_time
    return {"output": rendered, "execution_time": execution_time}


def execute_mermaid(code, discussion_id, message_id):

    return build_mermaid_output(code)