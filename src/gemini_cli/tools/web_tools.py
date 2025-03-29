"""
Web access tools.
"""

import requests
from urllib.parse import urlparse
import html2text
from .base import BaseTool

class WebFetchTool(BaseTool):
    """Tool to fetch web content."""
    
    name = "web"
    description = "Fetch content from a website"
    
    # Cache for recently accessed URLs
    _cache = {}
    
    def execute(self, url, prompt=None):
        """
        Fetch content from a website.
        
        Args:
            url: The URL to fetch
            prompt: Optional prompt to process the content
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return "Error: Invalid URL. Please provide a complete URL with scheme (http:// or https://)."
            
            # Use https by default
            if parsed_url.scheme == 'http':
                url = 'https://' + url[7:]
            
            # Check cache
            if url in self._cache:
                content = self._cache[url]
            else:
                # Fetch the content
                headers = {
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
                }
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                
                # Convert HTML to markdown
                h = html2text.HTML2Text()
                h.ignore_links = False
                h.ignore_images = True
                h.escape_all = False
                content = h.handle(response.text)
                
                # Cache the result
                self._cache[url] = content
            
            # Truncate if too long
            if len(content) > 10000:
                content = content[:10000] + "...\n[Content truncated due to length]"
            
            # Add prompt handling here if needed
            if prompt:
                return f"Content from {url}:\n\n{content}\n\nPrompt: {prompt}\n\n[Note: In a production version, the content would be processed with the provided prompt using an AI model]"
            
            return f"Content from {url}:\n\n{content}"
        
        except requests.exceptions.RequestException as e:
            return f"Error fetching URL: {str(e)}"
        except Exception as e:
            return f"Error processing content: {str(e)}"