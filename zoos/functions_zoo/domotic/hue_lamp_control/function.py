from lollms.function_call import FunctionCall, FunctionType
from lollms.app import LollmsApplication
from lollms.client_session import Client
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
import pipmaster as pm
if not pm.is_installed("phue"):
    pm.install("phue")
from phue import Bridge # You'll need to install the phue library first
import json
from ascii_colors import ASCIIColors

class HueLampControl(FunctionCall):

    def __init__(self, app: LollmsApplication, client: Client):
        
        static_parameters = TypedConfig(
            ConfigTemplate([
                {
                    "name": "bridge_ip_address",
                    "type": "str",
                    "value": "192.168.1.1",
                    "help": "Ip address of the bridge"
                },
            ]),
            BaseConfig(config={
            })
        )
        super().__init__("hue_lamp_control", app, FunctionType.CLASSIC, client, static_parameters)
        self.settings_updated()

    def settings_updated(self):
        # Initialize the Bridge (you'll need to set your bridge IP)
        pass
    def execute(self, context, *args, **kwargs):
        """
        Turn Philips Hue lamps on or off
        """
        try:
            self.bridge = Bridge(self.static_parameters.bridge_ip_address)
            # If this is the first time, you'll need to press the button on the bridge
            self.bridge.connect()
            # Get all lights
            lights = self.bridge.lights
            
            # Set the state for all lights
            for light in lights:
                light.on = kwargs.get("state")
                if kwargs.get("state"):
                    light.brightness = kwargs.get("brightness")
                    
            return f"Lights turned {'on' if kwargs.get('state') else 'off'}"
        except Exception as e:
            return str(e)