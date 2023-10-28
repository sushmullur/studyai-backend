import requests

integration_token = 'secret_2xGbM0UEYFDZdPORu5uTIH8GNh7wjsqNDFaEZipv16T'
database_id = '167f275dfde646e79e562804592cb123'  # The Notion database where you want to create the page
url = 'https://api.notion.com/v1/pages'
headers = {
    'Authorization': f'Bearer {integration_token}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28',
}

# Read Markdown content from README.md
with open('README.md', 'r', encoding='utf-8') as file:
    markdown_lines = file.readlines()

# Initialize the list to store blocks
notion_blocks = []
current_block = None
code_block = False
code_language = None

for line in markdown_lines:
    if line.startswith('# '):  # Line starts with a '#'
        if current_block:
            notion_blocks.append(current_block)
        heading_text = line[2:].strip()  # Extract the heading text
        current_block = {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": heading_text,
                        },
                    },
                ],
            }
        }
    elif line.startswith('## '):  # Line starts with '##'
        if current_block:
            notion_blocks.append(current_block)
        heading_text = line[3:].strip()  # Extract the heading text
        current_block = {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": heading_text,
                        },
                    },
                ],
            }
        }
    elif line.startswith('### '):  # Line starts with '###'
        if current_block:
            notion_blocks.append(current_block)
        heading_text = line[4:].strip()  # Extract the heading text
        current_block = {
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": heading_text,
                        },
                    },
                ],
            }
        }
    elif line.startswith('```'):  # Line starts with '```' (code block delimiter)
        if code_block:
            # Closing code block
            code_block = False
            code_language = None
        else:
            # Opening code block
            code_block = True
            parts = line.split(' ')
            line = line[3:].strip()
            if len(line) > 1:
                # Extract code language
                code_language = line
                current_block = {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [],
                        "language": code_language,
                    }
                }
            else:
                current_block = {
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [],
                    }
                }
    elif code_block:
        # Append the line to the code block
        current_block['code']['rich_text'].append({'type': 'text', 'text': {'content': line}})
    else:
        if current_block:
            if code_language:
                current_block['code']['language'] = code_language
            notion_blocks.append(current_block)
        # Handle code blocks enclosed within single backticks (` `)
        parts = line.split('`')
        if len(parts) > 1:
            current_block = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [],
                }
            }
            for i, part in enumerate(parts):
                if i % 2 == 0:
                    # Non-code part
                    current_block['paragraph']['rich_text'].append({'type': 'text', 'text': {'content': part + ""}})
                else:
                    # Code part
                    current_block['paragraph']['rich_text'].append({'type': 'text', 'text': {'content': part + ""}, 'annotations': {'code': True}})
        else:
            # Handle bold text enclosed within **
            parts = line.split('**')
            if len(parts) > 1:
                current_block = {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [],
                    }
                }
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        # Non-bold part
                        current_block['paragraph']['rich_text'].append({'type': 'text', 'text': {'content': part + " "}})
                    else:
                        # Bold part
                        current_block['paragraph']['rich_text'].append({'type': 'text', 'text': {'content': part}, 'annotations': {'bold': True}})
            else:
                current_block = {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [],
                    }
                }
                current_block['paragraph']['rich_text'].append({'type': 'text', 'text': {'content': line}})

# Append the last block
if current_block:
    if code_language:
        current_block['code']['language'] = code_language
    notion_blocks.append(current_block)

# Define the page properties with the title
data = {
    'parent': {
        'database_id': database_id,
    },
    'properties': {
        'title': {
            'type': 'title',
            'title': [
                {
                    'type': 'text',
                    'text': {
                        'content': 'Your Page Title',
                    },
                },
            ],
        },
    },
    'children': notion_blocks  # Include the list of blocks in the 'children' property
}

# 1. Create the Notion page with the blocks
response = requests.post(url, headers=headers, json=data)

# Check the response to ensure the page with the child blocks was successfully created
print(response.status_code)
print(response.json())
