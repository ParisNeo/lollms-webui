import argparse
import csv


# Define a function to split text into blocks
def split_text_into_blocks(text):
    return text.split("\n")


# Define the main function
def process_text_file(input_file, output_file=None):
    # If output_file is not provided, generate a default output file name based on the input file name
    output_file = output_file or input_file.split(".")[0] + ".csv"

    # Read the text from the input file
    with open(input_file, "r", encoding="utf-8") as input_file:
        text_content = input_file.read()

    # Split the text into blocks
    blocks = split_text_into_blocks(text_content)

    # Create a list of dictionaries with id and text for each block
    data = [{"id": i, "text": block} for i, block in enumerate(blocks)]

    # Write the data to a CSV file
    with open(output_file, "w", newline="", encoding="utf-8") as output_file:
        fieldnames = ["id", "text"]
        writer = csv.DictWriter(output_file, fieldnames=fieldnames)

        # Write the header row
        writer.writeheader()

        # Write the data rows
        writer.writerows(data)

    print(f'CSV file "{output_file}" has been created.')


# Check if the script is being run as a standalone program
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Split text from a file into blocks and create a CSV file."
    )

    # Add arguments for input and output file names
    parser.add_argument("input_file", help="Input text file name")
    parser.add_argument("-o", "--output_file", help="Output CSV file name")

    # Parse the command-line arguments
    args = parser.parse_args()

    # Call the main processing function
    process_text_file(args.input_file, args.output_file)
