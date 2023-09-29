import argparse

parser = argparse.ArgumentParser(description="Start the chatbot Flask app.")

parser.add_argument(
    "-c", "--config", type=str, default="local_config", help="Sets the configuration file to be used."
)

parser.add_argument(
    "-p", "--personality", type=str, default=None, help="Selects the personality to be using."
)

parser.add_argument(
    "-s", "--seed", type=int, default=None, help="Force using a specific seed value."
)

parser.add_argument(
    "-m", "--model", type=str, default=None, help="Force using a specific model."
)
parser.add_argument(
    "--temp", type=float, default=None, help="Temperature parameter for the model."
)
parser.add_argument(
    "--n_predict",
    type=int,
    default=None,
    help="Number of tokens to predict at each step.",
)
parser.add_argument(
    "--n_threads",
    type=int,
    default=None,
    help="Number of threads to use.",
)
parser.add_argument(
    "--top_k", type=int, default=None, help="Value for the top-k sampling."
)
parser.add_argument(
    "--top_p", type=float, default=None, help="Value for the top-p sampling."
)
parser.add_argument(
    "--repeat_penalty", type=float, default=None, help="Penalty for repeated tokens."
)
parser.add_argument(
    "--repeat_last_n",
    type=int,
    default=None,
    help="Number of previous tokens to consider for the repeat penalty.",
)
parser.add_argument(
    "--ctx_size",
    type=int,
    default=None,#2048,
    help="Size of the context window for the model.",
)
parser.add_argument(
    "--debug",
    dest="debug",
    action="store_true",
    default=None,
    help="launch Flask server in debug mode",
)
parser.add_argument(
    "--host", type=str, default=None, help="the hostname to listen on"
)
parser.add_argument("--port", type=int, default=None, help="the port to listen on")
parser.add_argument(
    "--db_path", type=str, default=None, help="Database path"
)