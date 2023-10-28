import requests

integration_token = 'secret_2xGbM0UEYFDZdPORu5uTIH8GNh7wjsqNDFaEZipv16T'
database_id = '167f275dfde646e79e562804592cb123'  # The Notion database where you want to create the page

# Read Markdown content from README.md
with open('README.md', 'r', encoding='utf-8') as file:
    markdown_lines = file.readlines()

# Function to categorize Markdown content by tag
def categorize_markdown(markdown_lines):
    notion_blocks = []
    current_block = None  # Initialize current_block as None

    for line in markdown_lines:
        if line.startswith('# '):  # Heading
            if current_block:
                notion_blocks.append(current_block)
            current_block = {
                'object': 'block',
                'type': 'heading_1',
                'heading_1': {
                    'rich_text': [
                        {
                            type: 'text',
                            'text': {
                                'content': line[2:].strip()
                            }, 
                            "annotations": {
                                "bold": False,
                                "italic": False,
                                "strikethrough": False,
                                "underline": False,
                                "code": False,
                                "color": "green"
                            },
                        }
                    ]
                }
            }
        elif line.startswith('## '):  # Sub-heading
            if current_block:
                notion_blocks.append(current_block)
            current_block = {
                'object': 'block',
                'type': 'heading_2',
                'heading_2': {
                    'text': [{'type': 'text', 'text': {'content': line[3:].strip()}}
                    ],
                }
            }
        elif line.startswith('```'):  # Code block
            if current_block:
                notion_blocks.append(current_block)
            code_content = [line]
            while not line.startswith('```'):
                line = markdown_lines.pop(0)
                code_content.append(line)
            current_block = {
                'object': 'block',
                'type': 'code',
                'code': {
                    'text': [{'type': 'text', 'text': {'content': ''.join(code_content[1:-1])}},
                    ],
                }
            }
        else:  # Paragraph
            if current_block is None or "paragraph" not in current_block:
                current_block = {
                    'object': 'block',
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [],
                    },
                }
            current_block['paragraph']['rich_text'].append({'type': 'text', 'text': {'content': line}})

    if current_block:
        notion_blocks.append(current_block)

    return notion_blocks

# Categorize Markdown content and create a new page in Notion
notion_blocks = categorize_markdown(markdown_lines)

url = 'https://api.notion.com/v1/pages'
headers = {
    'Authorization': f'Bearer {integration_token}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28',
}
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
    }
}

# 1. Create the Notion page
response = requests.post(url, headers=headers, json=data)
page_id = response.json()['id']  # Capture the ID of the created page

# 2. Append child blocks to the created page
append_blocks_url = f'https://api.notion.com/v1/blocks/{page_id}/children'
data = {'children': notion_blocks}
response = requests.patch(append_blocks_url, headers=headers, json=data)

# Check the response to ensure the child blocks were successfully appended
print(response.status_code)
print(response.json())
