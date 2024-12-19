import os
import re

# Define a list of file extensions to process
file_extensions = [".js", ".vue", ".html"]

# Regular expressions to match lines where semicolons can be added
javascript_pattern = (
    r"\b(?:(?<!if|else|while|for|switch|catch|return|function)\s*[^;]*$|^\s*{)"
)
vue_pattern = r"\b(?:data|computed|methods|watch|beforeCreate|created|beforeMount|mounted|beforeUpdate|updated|beforeDestroy|destroyed)\s*:[^;]*$"
html_pattern = r"<[^>]*>$"


# Function to add semicolons to the end of lines in a file
def add_semicolons_to_file(file_path):
    try:
        with open(file_path, "r") as file:
            lines = file.readlines()

        with open(file_path, "w") as file:
            for line in lines:
                if file_path.endswith(".js") and re.search(
                    javascript_pattern, line.strip()
                ):
                    line = line.rstrip() + ";"
                elif file_path.endswith(".vue") and re.search(
                    vue_pattern, line.strip()
                ):
                    line = line.rstrip() + ";"
                elif file_path.endswith(".html") and re.search(
                    html_pattern, line.strip()
                ):
                    line = line.rstrip() + ";"
                file.write(line)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


# Specify the path to the directory containing your JavaScript, Vue.js, or HTML files
directory_path = "/path/to/your/files"

# Iterate through files in the directory and add semicolons
for root, _, files in os.walk(directory_path):
    for file_name in files:
        if any(file_name.endswith(ext) for ext in file_extensions):
            file_path = os.path.join(root, file_name)
            add_semicolons_to_file(file_path)

print("Semicolons added successfully.")
