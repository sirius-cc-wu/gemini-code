"""
Tool implementations for Gemini CLI.
"""

from .file_tools import ViewTool, EditTool, ListTool, GrepTool, GlobTool
from .system_tools import BashTool
from .web_tools import WebFetchTool

# Register all available tools
AVAILABLE_TOOLS = {
    "view": ViewTool,
    "edit": EditTool,
    "ls": ListTool,
    "grep": GrepTool,
    "glob": GlobTool,
    "bash": BashTool,
    "web": WebFetchTool,
}

def get_tool(tool_name):
    """Get a tool instance by name."""
    tool_class = AVAILABLE_TOOLS.get(tool_name)
    if not tool_class:
        raise ValueError(f"Unknown tool: {tool_name}")
    
    return tool_class()

def get_tools_description():
    """Get a description of all available tools."""
    descriptions = []
    
    for name, tool_class in AVAILABLE_TOOLS.items():
        descriptions.append(f"- `/{name}`: {tool_class.description}")
    
    return "\n".join(descriptions)