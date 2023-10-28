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
    else:
        # Handle code blocks enclosed within single backticks (` `)
        parts = line.split('`')
        if len(parts) > 1:
            if current_block:
                notion_blocks.append(current_block)
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
                    current_block['paragraph']['rich_text'].append({'type': 'text', 'text': {'content': part.strip() + " "}})
                else:
                    # Code part
                    current_block['paragraph']['rich_text'].append({'type': 'text', 'text': {'content': part.strip() + " "}, 'annotations': {'code': True}})
        else:
            if current_block:
                notion_blocks.append(current_block)
            current_block = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [],
                }
            }
            current_block['paragraph']['rich_text'].append({'type': 'text', 'text': {'content': line.strip()}})

# Append the last block
if current_block:
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
