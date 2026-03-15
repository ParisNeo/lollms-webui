import pipmaster as pm
if pm.is_installed("python-nmap"):
    pm.install("python-nmap")
import nmap
import random
from lollms.personality import APScript, AIPersonality
from lollms.client_session import Client
from lollms.helpers import ASCIIColors
from lollms.config import TypedConfig, BaseConfig, ConfigTemplate
from lollms.personality import APScript, AIPersonality

class Processor(APScript):
    def __init__(self, personality: AIPersonality, callback: callable = None) -> None:
       
        self.callback = callback
        
        # Configuration entry examples and types description:
        # Supported types: int, float, str, string (same as str, for back compatibility), text (multiline str),
        # btn (button for special actions), bool, list, dict.
        # An 'options' entry can be added for types like string, to provide a dropdown of possible values.
        personality_config_template = ConfigTemplate(
            [
                # Target configuration
                {"name":"target_hosts", "type":"str", "value":"192.168.1.0/24", 
                "help":"Target hosts to scan (e.g., '127.0.0.1', '192.168.1.0/24', '10.0.0.1-50')"},
                                
                # Host Discovery
                {"name":"enable_host_discovery", "type":"bool", "value":False, 
                "help":"Enable basic host discovery scan to find live hosts on the network"},
                
                # Port Scanning
                {"name":"enable_port_scan", "type":"bool", "value":False, 
                "help":"Enable TCP port scanning to identify open ports on target hosts"},
                
                # OS Detection
                {"name":"enable_os_detection", "type":"bool", "value":False, 
                "help":"Enable operating system detection to identify target system OS"},
                
                # Version Detection
                {"name":"enable_version_detection", "type":"bool", "value":False, 
                "help":"Enable service version detection on open ports"},
                
                # Script Scanning
                {"name":"enable_script_scan", "type":"bool", "value":False, 
                "help":"Enable NSE script scanning for additional information gathering"},
                
                # Vulnerability Scanning
                {"name":"enable_vulnerability_scan", "type":"bool", "value":False, 
                "help":"Enable vulnerability scanning using NSE scripts"},
                
                # Firewall/IDS Evasion
                {"name":"enable_firewall_evasion", "type":"bool", "value":False, 
                "help":"Enable firewall/IDS evasion techniques during scanning"},
                
                # Spoofing and Decoy
                {"name":"enable_spoofing", "type":"bool", "value":False, 
                "help":"Enable MAC address spoofing and decoy scanning techniques"},
                
                # TCP/IP Fingerprinting
                {"name":"enable_tcp_fingerprint", "type":"bool", "value":False, 
                "help":"Enable TCP/IP stack fingerprinting for OS detection"},
                
                # RPC Scanning
                {"name":"enable_rpc_scan", "type":"bool", "value":False, 
                "help":"Enable RPC service scanning and enumeration"},
                
                # UDP Scanning
                {"name":"enable_udp_scan", "type":"bool", "value":False, 
                "help":"Enable UDP port scanning to identify UDP services"},
                
                # SCTP Scanning
                {"name":"enable_sctp_scan", "type":"bool", "value":False, 
                "help":"Enable SCTP protocol scanning"},
                
                # IP Protocol Scanning
                {"name":"enable_ip_protocol", "type":"bool", "value":False, 
                "help":"Enable IP protocol scanning to identify supported protocols"}
            ])

        
        personality_config_vals = BaseConfig.from_template(personality_config_template)

        personality_config = TypedConfig(
            personality_config_template,
            personality_config_vals
        )
        
        super().__init__(
                            personality,
                            personality_config,
                            states_list=[
                                {
                                    "name": "idle",
                                    "commands": {
                                        "help": self.help, # Command triggering the help method
                                        "start_scanning": self.start_scanning
                                    },
                                    "default": None
                                },  
                                {
                                    "name": "script_scanning",
                                    "default": None
                                },  
                                                         
                            ],
                            callback=callback
                        )

    def mounted(self):
        print("Network Monitor mounted")

    def selected(self):
        print("Network Monitor selected")

    def install(self):
        print("Network Monitor installed")

    def help(self, prompt="", full_context=""):
        return "Network Monitor help"

    def run_workflow(self, context_details: dict = None, client: Client = None, callback: callable = None):
        self.callback = callback
        full_prompt = self.build_prompt_from_context_details(context_details)
        if self.yes_no("Is the user asking to start scanning the network?", context_details.prompt):
            self.start_scanning(from_discussion=True)
        else:
            self.set_message_content(self.generate(full_prompt))


    def scan_network(self, hosts, config):
        """
        Perform network scanning based on configuration settings
        Args:
            hosts: Target hosts to scan
            config: Configuration object containing boolean flags for each scan type
        """
        out = ""

        self.step_start(f"Loading NMAP")
        self.nmap = nmap.PortScanner()
        self.step_end(f"Loading NMAP")

        # Host Discovery
        if config.enable_host_discovery:
            self.step_start(f"Discovering hosts ...")
            try:
                self.nmap.scan(hosts=hosts, arguments='-sP')
                hosts_list = [(x, self.nmap[x]['status']['state']) for x in self.nmap.all_hosts()]
                out += "Hosts:\n"
                for host in hosts_list:
                    out += f"{host[0]} {host[1]}\n"
                self.step_end(f"Discovering hosts ...")
            except Exception as e:
                out += f"Host Discovery failed: {str(e)}\n"
                self.step_end(f"Discovering hosts ...", False)

        # Port Scanning
        if config.enable_port_scan:
            self.step_start(f"Scanning ports ...")
            try:
                self.nmap.scan(hosts=hosts, arguments='-sT')
                ports_list = [(x, self.nmap[x]['tcp'][x]['state']) for x in self.nmap.all_hosts() for x in self.nmap[x]['tcp']]
                out += "\nPorts:\n"
                for port in ports_list:
                    out += f"{port[0]} {port[1]}\n"
                self.step_end(f"Scanning ports ...")
            except Exception as e:
                out += f"Port Scanning failed: {str(e)}\n"
                self.step_end(f"Scanning ports ...", False)

        # OS Detection
        if config.enable_os_detection:
            self.step_start(f"Detecting os ...")
            try:
                self.nmap.scan(hosts=hosts, arguments='-O')
                os_list = [(x, self.nmap[x]['osmatch'][0]['name']) for x in self.nmap.all_hosts()]
                out += "\nOS:\n"
                for os in os_list:
                    out += f"{os[0]} {os[1]}\n"
                self.step_end(f"Detecting os ...")
            except Exception as e:
                out += f"OS Detection failed: {str(e)}\n"
                self.step_end(f"Detecting os ...", False)

        # Version Detection
        if config.enable_version_detection:
            try:
                self.step_start(f"Detecting version ...")
                self.nmap.scan(hosts=hosts, arguments='-sV')
                version_list = [(x, self.nmap[x]['version'][x]['version']) for x in self.nmap.all_hosts() for x in self.nmap[x]['version']]
                out += "\nVersions:\n"
                for version in version_list:
                    out += f"{version[0]} {version[1]}\n"
                self.step_end(f"Detecting version ...")
            except Exception as e:
                out += f"Version Detection failed: {str(e)}\n"
                self.step_end(f"Detecting version ...", False)


            # Script Scanning
            if config.enable_script_scan:
                self.step_start(f"Script scanning ...")
                try:
                    self.nmap.scan(hosts=hosts, arguments='--script=vuln')
                    script_list = [(x, self.nmap[x]['scripts'][x]['output']) for x in self.nmap.all_hosts() for x in self.nmap[x]['scripts']]
                    out += "\nScripts:\n"
                    for script in script_list:
                        out += f"{script[0]} {script[1]}\n"
                    self.step_end(f"Script scanning ...")
                except Exception as e:
                    out += f"Script Scanning failed: {str(e)}\n"
                    self.step_end(f"Script scanning ...", False)

            # Vulnerability Scanning
            if config.enable_vulnerability_scan:
                self.step_start(f"Vulnerability scanning ...")
                try:
                    self.nmap.scan(hosts=hosts, arguments='--script=vuln')
                    vuln_list = [(x, self.nmap[x]['scripts'][x]['output']) for x in self.nmap.all_hosts() for x in self.nmap[x]['scripts']]
                    out += "\nVulnerabilities:\n"
                    for vuln in vuln_list:
                        out += f"{vuln[0]} {vuln[1]}\n"
                    self.step_end(f"Vulnerability scanning ...")
                except Exception as e:
                    out += f"Vulnerability Scanning failed: {str(e)}\n"
                    self.step_end(f"Vulnerability scanning ...", False)

            # Firewall/IDS Evasion
            if config.enable_firewall_evasion:
                self.step_start(f"Firewall evasion scanning ...")
                try:
                    self.nmap.scan(hosts=hosts, arguments='--mtu 8')
                    evasion_list = [(x, self.nmap[x]['status']['state']) for x in self.nmap.all_hosts()]
                    out += "\nEvasion:\n"
                    for evasion in evasion_list:
                        out += f"{evasion[0]} {evasion[1]}\n"
                    self.step_end(f"Firewall evasion scanning ...")
                except Exception as e:
                    out += f"Firewall Evasion failed: {str(e)}\n"
                    self.step_end(f"Firewall evasion scanning ...", False)

            # Spoofing and Decoy Scanning
            if config.enable_spoofing:
                self.step_start(f"Spoofing scanning ...")
                try:
                    self.nmap.scan(hosts=hosts, arguments='--spoof-mac 00:11:22:33:44:55')
                    spoof_list = [(x, self.nmap[x]['status']['state']) for x in self.nmap.all_hosts()]
                    out += "\nSpoofing:\n"
                    for spoof in spoof_list:
                        out += f"{spoof[0]} {spoof[1]}\n"
                    self.step_end(f"Spoofing scanning ...")
                except Exception as e:
                    out += f"Spoofing Scan failed: {str(e)}\n"
                    self.step_end(f"Spoofing scanning ...", False)

            # TCP/IP Stack Fingerprinting
            if config.enable_tcp_fingerprint:
                self.step_start(f"TCP/IP fingerprinting ...")
                try:
                    self.nmap.scan(hosts=hosts, arguments='-O')
                    tcp_list = [(x, self.nmap[x]['osmatch'][0]['name']) for x in self.nmap.all_hosts()]
                    out += "\nTCP/IP:\n"
                    for tcp in tcp_list:
                        out += f"{tcp[0]} {tcp[1]}\n"
                    self.step_end(f"TCP/IP fingerprinting ...")
                except Exception as e:
                    out += f"TCP/IP Fingerprinting failed: {str(e)}\n"
                    self.step_end(f"TCP/IP fingerprinting ...", False)

            # RPC Scanning
            if config.enable_rpc_scan:
                self.step_start(f"RPC scanning ...")
                try:
                    self.nmap.scan(hosts=hosts, arguments='--script=rpcinfo')
                    rpc_list = [(x, self.nmap[x]['scripts'][x]['output']) for x in self.nmap.all_hosts() for x in self.nmap[x]['scripts']]
                    out += "\nRPC:\n"
                    for rpc in rpc_list:
                        out += f"{rpc[0]} {rpc[1]}\n"
                    self.step_end(f"RPC scanning ...")
                except Exception as e:
                    out += f"RPC Scanning failed: {str(e)}\n"
                    self.step_end(f"RPC scanning ...", False)

            # UDP Scanning
            if config.enable_udp_scan:
                self.step_start(f"UDP scanning ...")
                try:
                    self.nmap.scan(hosts=hosts, arguments='-sU')
                    udp_list = [(x, self.nmap[x]['udp'][x]['state']) for x in self.nmap.all_hosts() for x in self.nmap[x]['udp']]
                    out += "\nUDP:\n"
                    for udp in udp_list:
                        out += f"{udp[0]} {udp[1]}\n"
                    self.step_end(f"UDP scanning ...")
                except Exception as e:
                    out += f"UDP Scanning failed: {str(e)}\n"
                    self.step_end(f"UDP scanning ...", False)

            # SCTP Scanning
            if config.enable_sctp_scan:
                self.step_start(f"SCTP scanning ...")
                try:
                    self.nmap.scan(hosts=hosts, arguments='-sY')
                    sctp_list = [(x, self.nmap[x]['sctp'][x]['state']) for x in self.nmap.all_hosts() for x in self.nmap[x]['sctp']]
                    out += "\nSCTP:\n"
                    for sctp in sctp_list:
                        out += f"{sctp[0]} {sctp[1]}\n"
                    self.step_end(f"SCTP scanning ...")
                except Exception as e:
                    out += f"SCTP Scanning failed: {str(e)}\n"
                    self.step_end(f"SCTP scanning ...", False)

            # IP Protocol Scanning
            if config.enable_ip_protocol:
                self.step_start(f"IP protocol scanning ...")
                try:
                    self.nmap.scan(hosts=hosts, arguments='-sO')
                    ip_list = [(x, self.nmap[x]['ip'][x]['state']) for x in self.nmap.all_hosts() for x in self.nmap[x]['ip']]
                    out += "\nIP:\n"
                    for ip in ip_list:
                        out += f"{ip[0]} {ip[1]}\n"
                    self.step_end(f"IP protocol scanning ...")
                except Exception as e:
                    out += f"IP Protocol Scanning failed: {str(e)}\n"
                    self.step_end(f"IP protocol scanning ...", False)


        if out=="":
            out="No results found. Make sure you selected a scan mode and hosts in my configuration."
        return out

    def start_scanning(self, command="", full_context="", callback =None, context_state=None, client=None, from_discussion=False):
        if not from_discussion:
            self.new_message("")
        out = self.scan_network(self.personality_config.target_hosts, self.personality_config)
        self.set_message_content(out)