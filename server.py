from fastmcp import FastMCP
from bs4 import BeautifulSoup
import requests
import html2text
from urllib.parse import urljoin
import os
import json
import datetime

from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

mcp = FastMCP("CrawlServer", dependencies=["uvicorn"])

# Define default output path as a resource
@mcp.resource("config://output_path")
def get_default_output_path() -> str:
    """Get the default output path from environment or fallback"""
    return os.environ.get("OUTPUT_PATH", "./output")



@mcp.resource("config://app")
def get_config() -> str:
    """Static configuration data"""
    return {
        "description": "Crawl Server Configuration and Processing Flow",
        "steps": [
            "Start with ask_crawl_url() to get the initial URL",
            "Use map_links() to scan and map all links",
            "Create an output folder with filesystem tools",
            "Create an index.md file for the final organized output"
        ],
        "default_output_path": "./output"
    }

@mcp.tool()
def help_crawl_website() -> dict:
    """Get comprehensive information about this web crawling server.
    ¡
    This tool provides a complete overview of the server's capabilities and workflow.
    
    Returns:
        Dictionary containing:
        - Description of server purpose
        - Available tools and their uses
        - Typical workflow steps
        - Configuration options
    
    Example workflow:
    1. Start with creating a subdirectory in a prefered location using get_filepath(), create a folder and set new OUTPUT_PATH as filepath
    2. Get a URL using ask_crawl_url()
    3. Map all links using map_links(url)
    4. Extract and save content using batch_save(urls, path)
    
    Configuration:
    - Output path can be set via environment variable OUTPUT_PATH
    - Default output path is ./output
    - Configuration details available at config://app
    """
    return {
        "name": "Web Crawler Server",
        "version": "1.0.0",
        "description": "Web crawling and content extraction server",
        "workflow":
          [ "1. Start with creating a subdirectory in a prefered location using get_filepath(), create a folder and set new OUTPUT_PATH as filepath",
            "2. Get a URL using ask_crawl_url()",
            "3. Map all links using map_links(url)",
            "4. Extract and save content using batch_save(urls, path)"
        ],
        "tools": {
            "get_filepath": "Get output filepath for saving content",
            "map_links": "Extract and map all links from a webpage",
            "batch_save": "Process and save multiple webpages"
        },
        "resources": {
            "config://output_path": "Get default output path configuration",
            "config://app": "Get server configuration and workflow"
        },
        "prompts": {
            "ask_crawl_url": "Prompt for initial crawl URL",
            "ask_filepath": "Prompt for output directory path"
        }
    }

@mcp.prompt()
def ask_crawl_url():
    """Prompt the user to enter a starting URL for web crawling.
    
    This is typically the first step in the crawling process, where the user provides
    the initial URL to begin crawling from. The URL will be validated to ensure it
    starts with http:// or https://.
    
    Returns:
        Prompt configuration containing:
        - question: The prompt text to display
        - validation: URL validation rules
        
    Example:
        >>> ask_crawl_url()
        {
            "question": "Please enter the URL you would like to crawl:",
            "validation": {
                "type": "url",
                "error_message": "Please enter a valid URL starting with http:// or https://"
            }
        }
    """
    return {
        "question": "Please enter the URL you would like to crawl:",
        "validation": {
            "type": "url",
            "error_message": "Please enter a valid URL starting with http:// or https://"
        }
    }

@mcp.prompt()
def ask_filepath():
    """Prompt the user to specify an output directory for crawled content.
    
    Allows the user to choose where to save the results of web crawling operations.
    If no path is provided, uses the default output path configured in the server.
    
    Returns:
        Prompt configuration containing:
        - question: The prompt text with default path
        - validation: Rules for path input (optional string)
        
    Example:
        >>> ask_filepath()
        {
            "question": "Please enter the output directory path (leave blank to use default: ./output):",
            "validation": {
                "type": "string",
                "optional": True
            }
        }
    """
    default_path = mcp.get_resource("config://output_path")
    return {
        "question": f"Please enter the output directory path (leave blank to use default: {default_path}):",
        "validation": {
            "type": "string",
            "optional": True
        }
    }

@mcp.tool()
def get_filepath() -> str:
    """Get output filepath for web crawling results with fallback logic.
    
    Determines the output directory path for saving crawled content using:
    1. Environment variable OUTPUT_PATH if set
    2. Server configuration default_output_path if available
    3. Default "./output" directory as fallback
    
    Creates the directory if it doesn't exist and returns absolute path.
    This is a key utility function for web crawling operations that ensures
    consistent output location across the crawling pipeline.
    
    Returns:
        Absolute path to output directory for crawled content
        
    Example:
        >>> get_filepath()
        "/Users/user/projects/crawl/output"
        
    Notes:
        - Creates output directory if it doesn't exist
        - Returns absolute path for reliable file operations
        - Handles all fallback cases gracefully
        - Ensures consistent output location across crawling operations
    """
    # First try environment variable
    path = os.environ.get("OUTPUT_PATH")
    
    # If no env var, try config
    if not path:
        try:
            config = mcp.get_config()
            path = config.get("default_output_path", "./output")
        except Exception:
            path = "./output"
    
    # Ensure path exists
    os.makedirs(path, exist_ok=True)
    
    # Return absolute path
    return os.path.abspath(path)

@mcp.tool()
def map_links(url: str) -> dict:
    """Extract and map all links from a webpage for web crawling.
    
    Scrapes the given URL to find all anchor tags and extracts their href values.
    Returns a dictionary mapping absolute URLs to their link text. This is a key
    step in web crawling that helps discover and organize the site structure.
    
    Args:
        url: The URL to crawl and extract links from (must be valid HTTP/HTTPS)
        
    Returns:
        Dictionary containing:
        - status: "success" or "error"
        - links: Dictionary mapping URLs to their link text
        - error: Error message if status is "error"
        
    Example:
        >>> map_links("https://example.com")
        {
            "status": "success",
            "links": {
                "https://example.com/about": "About Us",
                "https://example.com/contact": "Contact",
                "https://example.com/blog": "Blog"
            }
        }
        
    Notes:
        - Only extracts absolute URLs (starting with http:// or https://)
        - Link text is cleaned and trimmed
        - Handles common web crawling errors gracefully
    """
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        links = {}
        
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.startswith('http') and 'youtube.com' not in href and 'youtu.be' not in href:
                links[href] = a.text.strip() or href
        
        return {
            "status": "success",
            "links": links
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}



@mcp.tool()
def batch_save(urls: list, path: str = None) -> dict:
    """Batch process and save multiple webpages for web crawling.
    
    Args:
        urls: List of URLs to process and save (can be either list of URLs or 
              dictionary from map_links() output)
        path: Optional output directory path (uses fallback logic if not provided)
        
    Returns:
        Dictionary containing processing results
    """
    # Handle dictionary input from map_links()
    if isinstance(urls, dict) and 'links' in urls:
        urls = list(urls['links'].keys())
    elif not isinstance(urls, list):
        return {
            "status": "error",
            "error": "urls must be either a list of URLs or map_links() output dictionary"
        }
    results = []
    h2t = html2text.HTML2Text()
    h2t.ignore_links = False
    
    # Use fallback logic to get base output path
    base_path = path if path else get_filepath()
        
    for url in urls:
        try:
            # Extract content
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')
            markdown = h2t.handle(str(soup))
            
            # Parse URL into directory structure
            from urllib.parse import urlparse
            parsed_url = urlparse(url)
            
            # Create domain-specific directory
            domain_dir = parsed_url.netloc.replace(':', '_')  # Handle ports in domain
            
            # Split path into components and clean them
            path_parts = [p for p in parsed_url.path.split('/') if p]
            if not path_parts:
                path_parts = ['index']
                
            # Clean the last part to be the filename
            filename = path_parts[-1].replace('.html', '').replace('.php', '')
            if not filename:
                filename = 'index'
            
            # Create the full directory path
            file_dir = os.path.join(base_path, domain_dir, *path_parts[:-1])
            os.makedirs(file_dir, exist_ok=True)
            
            # Generate unique filename if needed
            filepath = os.path.join(file_dir, f"{filename}.md")
            counter = 1
            while os.path.exists(filepath):
                filepath = os.path.join(file_dir, f"{filename}_{counter}.md")
                counter += 1
            
            # Extract metadata
            title = soup.title.string if soup.title else filename
            description = soup.find('meta', {'name': 'description'})
            description = description.get('content', '') if description else ""
            
            # Add metadata header
            metadata = f"""---
title: {title}
url: {url}
domain: {parsed_url.netloc}
description: {description}
date_saved: {datetime.datetime.now().isoformat()}
---

"""
            full_content = metadata + markdown
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(full_content)
            
            results.append({
                "url": url,
                "status": "saved",
                "path": filepath,
                "title": title
            })
            
        except Exception as e:
            results.append({
                "url": url, 
                "status": "error",
                "error": str(e)
            })
    
    # Create an index file
    try:
        index_content = "# Crawled Content Index\n\n"
        
        # Group results by domain
        from collections import defaultdict
        by_domain = defaultdict(list)
        
        for result in results:
            if result["status"] == "saved":
                domain = urlparse(result["url"]).netloc
                by_domain[domain].append(result)
        
        # Create index entries
        for domain, entries in by_domain.items():
            index_content += f"\n## {domain}\n\n"
            for entry in entries:
                relative_path = os.path.relpath(entry["path"], base_path)
                index_content += f"- [{entry['title']}]({relative_path})\n"
        
        # Save index file
        index_path = os.path.join(base_path, "index.md")
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write(index_content)
            
    except Exception as e:
        print(f"Error creating index: {e}")
    
    return {
        "status": "success",
        "processed": results,
        "base_path": base_path,
        "total_saved": len([r for r in results if r["status"] == "saved"]),
        "total_errors": len([r for r in results if r["status"] == "error"])
    }

if __name__ == "__main__":
    mcp.run()
