# MD MCP Webcrawler Project

A Python-based MCP (https://modelcontextprotocol.io/introduction) web crawler for extracting and saving website content. 

## Features
- Extract website content and save as markdown files
- Map website structure and links
- Batch processing of multiple URLs
- Configurable output directory

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/webcrawler.git
cd webcrawler
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Optional: Configure environment variables:
```bash
export OUTPUT_PATH=./output  # Set your preferred output directory
```

## Output
Crawled content is saved in markdown format in the specified output directory.

## Configuration
The server can be configured through environment variables:

- `OUTPUT_PATH`: Default output directory for saved files
- `MAX_CONCURRENT_REQUESTS`: Maximum parallel requests (default: 5)
- `REQUEST_TIMEOUT`: Request timeout in seconds (default: 30)

## Claude Set-Up
Install with FastMCP 
``` fastmcp install server.py ```

or user custom settings to run with fastmcp directly

````
"Crawl Server": {
      "command": "fastmcp",
      "args": [
        "run",
        "/Users/mm22/Dev_Projekte/servers-main/src/Webcrawler/server.py"
      ],
      "env": {
        "OUTPUT_PATH": "/Users/user/Webcrawl"
      }
```` 



## Development

### Live Development
```bash
fastmcp dev server.py --with-editable .
```
### Debug 
It helps to use https://modelcontextprotocol.io/docs/tools/inspector for debugging

## Examples

### Example 1: Extract and Save Content
```bash
mcp call extract_content --url "https://example.com" --output_path "example.md"
```

### Example 2: Create Content Index
```bash
mcp call scan_linked_content --url "https://example.com" | \
  mcp call create_index --content_map - --output_path "index.md"
```

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

Distributed under the MIT License. See `LICENSE` for more information.

## Requirements

- Python 3.7+
- FastMCP (uv pip install fastmcp)
- Dependencies listed in requirements.txt
