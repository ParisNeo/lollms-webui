import argparse
import json
from pathlib import Path


def indent_json_file(input_file, output_file=None, indent=4):
    # Read the JSON file
    with open(input_file, "r") as file:
        data = json.load(file)

    # Determine the output file path
    if output_file is None:
        output_file = input_file.with_stem(
            input_file.stem + "_indented" + input_file.suffix
        )

    # Write the indented JSON to the output file
    with open(output_file, "w") as file:
        json.dump(data, file, indent=indent)


def main():
    parser = argparse.ArgumentParser(
        description="Indent a JSON file and save it to a new file."
    )
    parser.add_argument("input_file", type=Path, help="path to the input JSON file")
    parser.add_argument(
        "-o", "--output_file", type=Path, help="path to the output JSON file"
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=4,
        help="number of spaces for indentation (default: 4)",
    )

    args = parser.parse_args()

    input_file = args.input_file
    output_file = args.output_file
    indent = args.indent

    indent_json_file(input_file, output_file, indent)


if __name__ == "__main__":
    main()
