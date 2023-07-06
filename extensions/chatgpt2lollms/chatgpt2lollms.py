import json
import argparse
from datetime import datetime

def convert_discussions(input_data, flatten=False):
    discussions = []

    for discussion in input_data:
        converted_discussion = {
            "id": discussion['id'],
            "messages": [],
            "title": discussion['title']
        }

        mapping = discussion['mapping']
        message_ids = list(mapping.keys())

        messages = [mapping[message_id]['message'] for message_id in message_ids if mapping[message_id]['message']]

        for i, message in enumerate(messages):
            created_at = ''
            create_time = message.get('create_time')

            if create_time is not None:
                created_at = datetime.fromtimestamp(create_time).strftime("%Y-%m-%d %H:%M:%S")

            content = message['content'].get('parts', [''])[0]
            if content:
                parent = i - 1 if flatten and i > 0 else mapping[message_ids[i]]['parent'] or -1

                converted_message = {
                    "binding": message['content'].get('binding', ''),
                    "content": content,
                    "created_at": created_at,
                    "finished_generating_at": '',
                    "model": '',
                    "parent": parent,
                    "personality": '',
                    "rank": 0,
                    "sender": message['author']['role'],
                    "type": 0
                }

                converted_discussion['messages'].append(converted_message)

        discussions.append(converted_discussion)

    return discussions

def convert_json(input_file, output_file, flatten=False):
    with open(input_file, 'r') as file:
        input_json = file.read()

    input_data = json.loads(input_json)
    converted_data = convert_discussions(input_data, flatten=flatten)

    with open(output_file, 'w') as file:
        json.dump(converted_data, file, indent=4)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Convert JSON files from the first format to the second format.')
    parser.add_argument('input_file', help='Input JSON file path')
    parser.add_argument('output_file', help='Output JSON file path')
    parser.add_argument('--flatten', action='store_true', help='Flatten the discussion hierarchy')

    args = parser.parse_args()
    convert_json(args.input_file, args.output_file, flatten=args.flatten)
