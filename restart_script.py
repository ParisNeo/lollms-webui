import os
import sys

def main():
    if len(sys.argv) != 1:
        print("Usage: python restart_script.py")
        sys.exit(1)

    # Reload the main script with the original arguments
    temp_file = "temp_args.txt"
    if os.path.exists(temp_file):
        with open(temp_file, "r") as file:
            args = file.read().split()
        main_script = "app.py"
        os.system(f"python {main_script} {' '.join(args)}")
        os.remove(temp_file)
    else:
        print("Error: Temporary arguments file not found.")
        sys.exit(1)

if __name__ == "__main__":
    main()
