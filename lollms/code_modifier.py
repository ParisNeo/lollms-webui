import os
import subprocess
from typing import Dict, Tuple
import re

class CodeModifier:
    def __init__(self, folder_path: str):
        self.folder_path = os.path.abspath(folder_path)
        self.init_git()

    def init_git(self):
        if not os.path.exists(os.path.join(self.folder_path, '.git')):
            subprocess.run(['git', 'init'], cwd=self.folder_path, check=True)

    def generate_llm_prompt(self, file_path: str, modification_instruction: str) -> str:
        with open(os.path.join(self.folder_path, file_path), 'r') as file:
            content = file.read()

        prompt = f"""
Task: Modify the following code according to the instructions.
File: {file_path}
Instructions: {modification_instruction}

Please provide your response in the following format:
1. A unified diff of the changes
2. A commit message for the changes

Current code:
{content}

Make sure to use the unified diff format for your changes, starting with '--- {file_path}' and '+++ {file_path}', followed by '@@ ... @@' for line numbers.
"""
        return prompt

    def parse_llm_response(self, response: str) -> Tuple[str, str]:
        diff_pattern = r'(---[\s\S]*?)(?=\nCommit message:|$)'
        commit_pattern = r'Commit message:([\s\S]*)'

        diff_match = re.search(diff_pattern, response)
        commit_match = re.search(commit_pattern, response)

        if not diff_match or not commit_match:
            raise ValueError("Invalid LLM response format")

        diff = diff_match.group(1).strip()
        commit_message = commit_match.group(1).strip()

        return diff, commit_message

    def apply_diff(self, file_path: str, diff: str) -> None:
        with open(os.path.join(self.folder_path, file_path), 'r') as file:
            lines = file.readlines()

        diff_lines = diff.split('\n')
        current_line = 0
        for line in diff_lines[2:]:  # Skip the first two lines (--- and +++)
            if line.startswith('@@'):
                match = re.match(r'@@ -\d+,?\d* \+(\d+),?\d* @@', line)
                if match:
                    current_line = int(match.group(1)) - 1
            elif line.startswith('-'):
                if lines[current_line].strip() == line[1:].strip():
                    lines.pop(current_line)
                else:
                    raise ValueError(f"Mismatch at line {current_line + 1}")
            elif line.startswith('+'):
                lines.insert(current_line, line[1:] + '\n')
                current_line += 1
            else:
                current_line += 1

        with open(os.path.join(self.folder_path, file_path), 'w') as file:
            file.writelines(lines)

    def commit_changes(self, file_path: str, commit_message: str) -> None:
        try:
            subprocess.run(['git', 'add', file_path], cwd=self.folder_path, check=True)
            subprocess.run(['git', 'commit', '-m', commit_message], cwd=self.folder_path, check=True)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to commit changes: {e}")

    def modify_code(self, file_path: str, modification_instruction: str, llm_function) -> Dict[str, str]:
        prompt = self.generate_llm_prompt(file_path, modification_instruction)
        llm_response = llm_function(prompt)

        try:
            diff, commit_message = self.parse_llm_response(llm_response)
            print("Generated diff:")
            print(diff)
            self.apply_diff(file_path, diff)
            self.commit_changes(file_path, commit_message)
            return {"status": "success", "message": "Code modified and committed successfully"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

# Example usage:
def mock_llm_function(prompt):
    # This is a mock function to simulate LLM response
    return """
--- example.py
+++ example.py
@@ -1,5 +1,6 @@
 def hello_world():
-    print("Hello, World!")
+    print("Hello, Universe!")
+    return "Greetings from the cosmos!"
 
 hello_world()

Commit message:
Update hello_world function to greet the universe and return a message
"""

if __name__=="__main__":
    # Usage
    modifier = CodeModifier(r"C:\Users\aloui\Documents\ai\test_code_modif")
    result = modifier.modify_code("example.py", "Change the greeting to 'Hello, Universe!' and make the function return a string", mock_llm_function)
    print(result)
