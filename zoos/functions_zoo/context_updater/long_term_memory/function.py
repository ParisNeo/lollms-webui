import datetime
import json
from pathlib import Path
from lollms.app import LollmsApplication
from lollms.personality import AIPersonality
from lollms.function_call import FunctionCall, FunctionType
from lollms.client_session import Client
from lollms.prompting import LollmsContextDetails
from lollms.config import TypedConfig, ConfigTemplate, BaseConfig
from typing import List
from ascii_colors import ASCIIColors, trace_exception

class LongTermMemoryFunction(FunctionCall):
    def __init__(self, app: LollmsApplication, client: Client):
        static_parameters = TypedConfig(
            ConfigTemplate([
                {
                    "name": "memory_content",
                    "type": "text",
                    "value": '{"i":[],"b":{"id":"bond_001","c":"Initial bond state","imp":5,"ts":0},"n":[],"k":[],"sys":[],"s":[]}',
                    "help": "JSON string containing initial memory"
                },
                {
                    "name": "by_personality",
                    "type": "bool",
                    "value": False,
                    "help": "If true, each persona will have its own memory. If false, then all personalities share the same memory."
                },
            ])
        )
        
        super().__init__("long_term_memory", app, FunctionType.CONTEXT_UPDATE, client, static_parameters)
        self.model = app.model
        self.memory_path = Path.home() / "lollms_memory.json"
        if not self.memory_path.exists():
            self.memory_path.write_text(self.static_parameters.memory_content, encoding="utf8")
        else:
            self.static_parameters.memory_content = self.memory_path.read_text()

    def settings_updated(self):
        self.memory_path = Path.home() / "lollms_memory.json"
        self.memory_path.write_text(self.static_parameters.memory_content, encoding="utf8")
    
    def verify_and_fix_memory(self):
        """Verify JSON integrity, fix if broken"""
        self.personality.step_start("Verifying memory integrity")
        try:
            with open(self.memory_path, "r", encoding="utf-8") as f:
                memory_json = json.load(f)
            expected_keys = {"i", "b", "n", "k", "sys", "s"}
            if not isinstance(memory_json, dict) or not all(k in memory_json for k in expected_keys):
                raise ValueError("Invalid memory structure")
            if not isinstance(memory_json["b"], dict):
                memory_json["b"] = {"id":"bond_001","c":"Initial bond state","imp":5,"ts":0}
            self.personality.step_end("Verifying memory integrity")
            return memory_json
        except (json.JSONDecodeError, ValueError) as e:
            self.app.error(f"Memory corrupt: {e}")
            self.personality.step_start("Fixing corrupt memory")
            with open(self.memory_path, "r", encoding="utf-8") as f:
                corrupt_memory = f.read().strip() or '{"i":[],"b":{"id":"bond_001","c":"Initial bond state","imp":5,"ts":0},"n":[],"k":[],"sys":[],"s":[]}'
            
            fix_prompt = (
                f"Corrupt JSON memory detected:\n{corrupt_memory}\n\n"
                "Fix it to match this structure:\n"
                '{"i":[{"id":"int_001","c":"content","imp":8,"ts":3600}],"b":{"id":"bond_001","c":"bond info","imp":5,"ts":3600},"n":[...],"k":[...],"sys":[...],"s":[...]}\n'
                "Bond (b) is a single object with id (str), c (content str), imp (0-10), ts (int, seconds from 2025-03-24).\n"
                "Other sections are lists. Output a valid, condensed JSON string (no spaces, e.g., separators=',':')."
            )
            fixed_memory_str = self.app.personality.generate_code(fix_prompt, language="json")
            try:
                fixed_memory = json.loads(fixed_memory_str)
                with open(self.memory_path, "w", encoding="utf-8") as f:
                    json.dump(fixed_memory, f, separators=(',', ':'))
                self.personality.step_end("Fixing corrupt memory")
                return fixed_memory
            except json.JSONDecodeError as e:
                self.app.error(f"Failed to fix memory: {e}")
                self.personality.step_end("Fixing corrupt memory", False)
                return {"i":[],"b":{"id":"bond_001","c":"Initial bond state","imp":5,"ts":0},"n":[],"k":[],"sys":[],"s":[]}

    def update_context(self, context: LollmsContextDetails, constructed_context: List[str]):
        """Add long-term memory to context with dictionary"""
        try:
            memory_json = self.verify_and_fix_memory()
            memory_dict = (
                "Memory Dictionary:\n"
                "i: interactions - key past exchanges\n"
                "b: bond - single entry for emotional connection level\n"
                "n: notes - AI’s private observations\n"
                "k: knowledge - shared insights\n"
                "sys: system - AI’s core rules/persona\n"
                "s: skills - acquired abilities\n"
                "Each entry: id (str), c (content), imp (0-10), ts (seconds from 2025-03-24)"
            )
            memory_str = json.dumps(memory_json, separators=(',', ':'), ensure_ascii=False)
            constructed_context.append(
                "--------- Long Term Memory -------\n"
                "This memory persists across sessions, updated automatically.\n"
                f"{memory_dict}\n"
                f"Memory (last updated {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}):\n"
                f"{memory_str}\n"
                "----------------------"
            )
        except Exception as e:
            self.app.error(f"Error loading memory: {e}")
        
        return constructed_context

    def process_output(self, context: LollmsContextDetails, llm_output: str):
        """Process AI-generated update commands to modify memory"""
        try:
            self.personality.step_start("Updating long term memory")
            memory_json = self.verify_and_fix_memory()
            base_ts = 1711238400  # March 24, 2025, 00:00 UTC
            now_offset = int((datetime.datetime.utcnow() - datetime.datetime(2025, 3, 24)).total_seconds())
            memory_str = json.dumps(memory_json, separators=(',', ':'), ensure_ascii=False)
            
            update_prompt = (
                self.app.template.system_full_header + f"Act as a memory shaping assistant. Generate JSON update commands for the memory based on the current interaction.\n" +
                self.app.template.system_custom_header('Memory Dictionary') +
                "i: interactions - key past exchanges\n"
                "b: bond - single entry for emotional connection level\n"
                "n: notes - AI’s private observations\n"
                "k: knowledge - shared insights\n"
                "sys: system - AI’s core rules/persona\n"
                "s: skills - acquired abilities\n"
                "Each entry: id (str), c (content), imp (0-10), ts (seconds from 2025-03-24)\n\n" +
                self.app.template.system_custom_header('Existing Memory') +
                memory_str + "\n\n" +
                self.app.template.system_custom_header('New Interaction') +
                f"date:{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" +
                f"prompt:{context.prompt}\n" +
                f"response:{llm_output}\n\n" +
                self.app.template.system_custom_header('Instructions') +
                "Generate a JSON object with update commands:\n"
                '- "add": [{"section":"i","entry":{"id":"int_008","c":"new fact","imp":7,"ts":' + str(now_offset) + '}}]\n'
                '- "update": [{"section":"b","entry":{"id":"bond_001","c":"strong bond","imp":8,"ts":' + str(now_offset) + '}}]\n'
                '- "remove": [{"section":"i","id":"int_003"}]\n'
                f"1. Add new entries (facts, prefs, skills) w/ id, c, imp (0-10), ts ({now_offset})\n"
                f"2. Remove low-imp (<5) or old (ts < {now_offset-86400}) entries unless imp>8 (not for 'b')\n"
                "3. Update bond entry if relevant (always use id 'bond_001')\n"
                "4. Keep concise, only include changes\n"
                "5. Preserve core context (sys, high-imp items)\n"
                "6. Only add real important information\n"
                "Output ONLY the JSON update commands, condensed (no spaces).\n\n" +
                self.app.template.ai_custom_header('assistant')
            )
            update_commands_str = self.personality.generate_code(update_prompt, callback=self.personality.sink)
            update_commands = json.loads(update_commands_str)

            # Process commands with individual error handling
            for cmd in update_commands.get("add", []):
                try:
                    section = cmd["section"]
                    entry = cmd["entry"]
                    if section != "b":  # Bond is not a list
                        memory_json[section].append(entry)
                except Exception as e:
                    trace_exception(e)
                    self.app.error(f"Failed to add entry to {section}: {e}")

            for cmd in update_commands.get("update", []):
                try:
                    section = cmd["section"]
                    entry = cmd["entry"]
                    if section == "b":
                        memory_json["b"] = entry
                    else:
                        entry_id = entry["id"]
                        for i, existing in enumerate(memory_json[section]):
                            if existing["id"] == entry_id:
                                memory_json[section][i] = entry
                                break
                except Exception as e:
                    trace_exception(e)
                    self.app.error(f"Failed to update entry in {section}: {e}")

            for cmd in update_commands.get("remove", []):
                try:
                    section = cmd["section"]
                    if section != "b":  # Bond cannot be removed
                        entry_id = cmd["id"]
                        memory_json[section] = [e for e in memory_json[section] if e["id"] != entry_id]
                except Exception as e:
                    trace_exception(e)
                    self.app.error(f"Failed to remove entry from {section}: {e}")

            with open(self.memory_path, "w", encoding="utf-8") as f:
                json.dump(memory_json, f, separators=(',', ':'), ensure_ascii=False)
            self.personality.step_end("Updating long term memory")

        except Exception as e:
            trace_exception(e)
            self.app.error(f"Error updating memory: {e}")
            self.personality.step_end("Updating long term memory", False)

        return llm_output