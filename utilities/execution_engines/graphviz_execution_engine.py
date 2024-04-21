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
from lollms.client_session import Client
from lollms.utilities import discussion_path_2_url


lollmsElfServer:LOLLMSWebUI = LOLLMSWebUI.get_instance()          

def build_graphviz_output(code, ifram_name="unnamed"):
    """
    This function creates an HTML5 iframe with the given HTML content and iframe name.

    Args:
    html (str): The HTML content to be displayed in the iframe.
    ifram_name (str, optional): The name of the iframe. Defaults to "unnamed".

    Returns:
    str: The HTML string for the iframe.
    """
    # Start the timer.
    start_time = time.time()    
    rendered =  "\n".join([
        '<div style="width: 100%; margin: 0 auto;">',
        f'<iframe id="{ifram_name}" srcdoc=\'',
        '<style>',
        'iframe {',
        'width: 100%;',
        'height: 100%;',
        'border: none;',
        '}',        
        '.graph {',
        'background-color: transparent;',
        'padding: 20px;',
        'border-radius: 10px;',
        'display: flex;',
        'justify-content: center;',
        'align-items: center;',
        'height: 100%;',
        '}',
        '</style>',
        '<div id="graph" class="graph"></div>',
        '<script src="https://github.com/mdaines/viz-js/releases/download/release-viz-3.2.4/viz-standalone.js"></script>',
        '<script>',
        '// Initialize the mermaid library and render our diagram',
        'Viz.instance().then(function(viz) {',
        'var svg = viz.renderSVGElement(`',
        "\n".join([c.replace("'","\"") for c in code.split("\n") if c.strip()!=""]),
        '`);',
        'document.getElementById("graph").appendChild(svg);',
        '});',
        '</script>',
        '<div style="text-align: center;">',
        '</div>',
        '\' style="width: 100%; height: 600px; border: none;"></iframe>',
        '</div>'
        ]
    )
    execution_time = time.time() - start_time
    return {"output": rendered, "execution_time": execution_time}

def execute_graphviz(code, client:Client, message_id, build_file=False):
    if build_file:
        # Start the timer.
        start_time = time.time()
        if not "http" in lollmsElfServer.config.host and not "https" in lollmsElfServer.config.host:
            host = "http://"+lollmsElfServer.config.host
        else:
            host = lollmsElfServer.config.host

        # Create a temporary file.
        root_folder = client.discussion.discussion_folder
        root_folder.mkdir(parents=True,exist_ok=True)
        tmp_file = root_folder/f"ai_code_{message_id}.html"
        with open(tmp_file,"w",encoding="utf8") as f:
            f.write(build_graphviz_output(code))
        link = f"{host}:{lollmsElfServer.config.port}/{discussion_path_2_url(tmp_file)}"
        output_json = {"output": f'<b>Page built successfully</b><br><a href="{link}" target="_blank">Press here to view the page</a>', "execution_time": execution_time}
        return output_json
    else:
        return build_graphviz_output(code)
