import git


def run_update_script(args=None):
    print("dir: " + os.listdir("."))
    update_script = Path(__file__).parent/"update_script.py"

    # Convert Namespace object to a dictionary
    if args:
        args_dict = vars(args)
    else:
        args_dict = {}
    # Filter out any key-value pairs where the value is None
    valid_args = {key: value for key, value in args_dict.items() if value is not None}

    # Save the arguments to a temporary file
    temp_file = Path(__file__).parent/"temp_args.txt"
    with open(temp_file, "w") as file:
        # Convert the valid_args dictionary to a string in the format "key1 value1 key2 value2 ..."
        arg_string = " ".join([f"--{key} {value}" for key, value in valid_args.items()])
        file.write(arg_string)

    os.system(f"python {update_script}")
    sys.exit(0)

def get_ip_address():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Connect to a remote host (doesn't matter which one)
        sock.connect(('8.8.8.8', 80))
        
        # Get the local IP address of the socket
        ip_address = sock.getsockname()[0]
        return ip_address
    except socket.error:
        return None
    finally:
        # Close the socket
        sock.close()


def check_update_(branch_name="main"):
    try:
        # Open the repository
        repo_path = str(Path(__file__).parent)
        ASCIIColors.yellow(f"Checking for updates from {repo_path}")
        repo = git.Repo(repo_path)
        
        # Fetch updates from the remote for the specified branch
        repo.remotes.origin.fetch(refspec=f"refs/heads/{branch_name}:refs/remotes/origin/{branch_name}")
        
        # Compare the local and remote commit IDs for the specified branch
        local_commit = repo.head.commit
        remote_commit = repo.remotes.origin.refs[branch_name].commit
        
        ASCIIColors.yellow(f"update availability: {local_commit != remote_commit}")
        # Return True if there are updates, False otherwise
        return local_commit != remote_commit
    except Exception as e:
        # Handle any errors that may occur during the fetch process
        # trace_exception(e)
        return False


def run_restart_script(args):
    restart_script = Path(__file__).parent/"restart_script.py"

    # Convert Namespace object to a dictionary
    args_dict = vars(args)

    # Filter out any key-value pairs where the value is None
    valid_args = {key: value for key, value in args_dict.items() if value is not None}

    # Save the arguments to a temporary file
    temp_file = Path(__file__).parent/"temp_args.txt"
    with open(temp_file, "w") as file:
        # Convert the valid_args dictionary to a string in the format "key1 value1 key2 value2 ..."
        arg_string = " ".join([f"--{key} {value}" for key, value in valid_args.items()])
        file.write(arg_string)

    os.system(f"python {restart_script}")
    sys.exit(0)

def sync_cfg(default_config, config):
    """Syncs a configuration with the default configuration

    Args:
        default_config (_type_): _description_
        config (_type_): _description_

    Returns:
        _type_: _description_
    """
    added_entries = []
    removed_entries = []

    # Ensure all fields from default_config exist in config
    for key, value in default_config.items():
        if key not in config:
            config[key] = value
            added_entries.append(key)

    # Remove fields from config that don't exist in default_config
    for key in list(config.config.keys()):
        if key not in default_config:
            del config.config[key]
            removed_entries.append(key)

    config["version"]=default_config["version"]
    
    return config, added_entries, removed_entries