"""
project: lollms_webui
file: shell_execution_engine.py 
author: ParisNeo
description: 
    This is a utility for executing python code

"""

import json
import subprocess
import time

from ascii_colors import get_trace_exception, trace_exception
from lollms.client_session import Client
from lollms.utilities import discussion_path_to_url

from lollms_webui import LOLLMSWebUI

lollmsElfServer: LOLLMSWebUI = LOLLMSWebUI.get_instance()


def build_mermaid_output(code, ifram_name=None):
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
    if ifram_name is not None:
        rendered = "\n".join(
            [
                '<div style="width: 100%; margin: 0 auto;">',
                f'<iframe id="{ifram_name}" style="width: 100%" srcdoc="',
                "<style>",
                "iframe {",
                "width: 100%;",
                "height: 100%;",
                "border: none;",
                "}",
                ".mermaid {",
                "background-color: transparent;",
                "padding: 20px;",
                "border-radius: 10px;",
                "display: flex;",
                "justify-content: center;",
                "align-items: center;",
                "height: 100%;",
                "}",
                "</style>",
                "<div class='mermaid'>",
                "\n".join([c for c in code.split("\n") if c.strip() != ""]),
                "</div>",
                "<script src='https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js'></script>",
                "<script>",
                "// Initialize the mermaid library and render our diagram",
                "mermaid.initialize({ startOnLoad: true });",
                "// Function to save SVG content to a file",
                "function saveSVG() {",
                'var svg = document.querySelector(".mermaid > svg");',
                "var serializer = new XMLSerializer();",
                "var source = serializer.serializeToString(svg);",
                'var blob = new Blob([source], {type: "image/svg+xml;charset=utf-8"});',
                "var url = URL.createObjectURL(blob);",
                'var a = document.createElement("a");',
                "a.href = url;",
                'a.download = "diagram.svg";',
                "a.click();",
                "}",
                "</script>",
                "<div style='text-align: center;'>",
                "</div>",
                '<button onclick="saveSVG()">Save SVG</button>',
                '" style="width: 100%; height: 600px; border: none;"></iframe>',
                "</div>",
            ]
        )
    else:
        rendered = "\n".join(
            [
                '<div style="width: 100%; margin: 0 auto;">',
                "<style>",
                ".mermaid {",
                "background-color: transparent;",
                "padding: 20px;",
                "border-radius: 10px;",
                "display: flex;",
                "justify-content: center;",
                "align-items: center;",
                "height: 100%;",
                "}",
                "</style>",
                "<div class='mermaid'>",
                "\n".join([c for c in code.split("\n") if c.strip() != ""]),
                "</div>",
                "<script src='https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js'></script>",
                "<script>",
                "// Initialize the mermaid library and render our diagram",
                "mermaid.initialize({ startOnLoad: true });",
                "// Function to save SVG content to a file",
                "function saveSVG() {",
                'var svg = document.querySelector(".mermaid > svg");',
                "var serializer = new XMLSerializer();",
                "var source = serializer.serializeToString(svg);",
                'var blob = new Blob([source], {type: "image/svg+xml;charset=utf-8"});',
                "var url = URL.createObjectURL(blob);",
                'var a = document.createElement("a");',
                "a.href = url;",
                'a.download = "diagram.svg";',
                "a.click();",
                "}",
                "</script>",
                "<div style='text-align: center;'>",
                "</div>",
                '<button onclick="saveSVG()">Save SVG</button>',
                "</div>",
            ]
        )
    execution_time = time.time() - start_time
    return {"output": rendered, "execution_time": execution_time}


def execute_mermaid(code, client: Client, message_id, build_file=False):
    if build_file:
        # Start the timer.
        start_time = time.time()
        if (
            not "http" in lollmsElfServer.config.host
            and not "https" in lollmsElfServer.config.host
        ):
            host = "http://" + lollmsElfServer.config.host
        else:
            host = lollmsElfServer.config.host

        # Create a temporary file.
        root_folder = client.discussion.discussion_folder
        root_folder.mkdir(parents=True, exist_ok=True)
        tmp_file = root_folder / f"ai_code_{message_id}.html"
        with open(tmp_file, "w", encoding="utf8") as f:
            f.write(build_mermaid_output(code)["output"])
        link = f"{host}:{lollmsElfServer.config.port}{discussion_path_to_url(tmp_file)}"
        # Stop the timer.
        execution_time = time.time() - start_time
        output_json = {
            "output": f'<b>Page built successfully</b><br><a href="{link}" target="_blank">Press here to view the page</a>',
            "execution_time": execution_time,
        }
        return output_json
    else:
        return build_mermaid_output(code, "app_iframe")
