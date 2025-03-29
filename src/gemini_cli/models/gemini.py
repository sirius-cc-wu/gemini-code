"""
Gemini model integration for the CLI tool.
"""

import google.generativeai as genai
import re
import json
from ..utils import count_tokens
from ..tools import get_tool, AVAILABLE_TOOLS

class GeminiModel:
    """Interface for Gemini models."""
    
    def __init__(self, api_key, model_name="gemini-2.5-pro"):
        """Initialize the Gemini model interface."""
        self.model_name = model_name
        genai.configure(api_key=api_key)
        
        # Configure model with function calling capability
        self.model = genai.GenerativeModel(
            model_name,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 40,
            }
        )
    
    def generate(self, prompt, conversation=None):
        """Generate a response to the prompt."""
        if not conversation:
            conversation = []
            
        # Special case for built-in commands
        if prompt.startswith('/'):
            command = prompt.split()[0].lower()
            if command in ['/exit', '/help', '/compact']:
                # These are handled by the main CLI loop
                return None
        
        # Convert our conversation format to Gemini format
        gemini_messages = self._format_conversation_for_gemini(conversation)
        
        # Add system prompt with tool information
        system_prompt = self._create_system_prompt_with_tools()
        gemini_messages.insert(0, {"role": "model", "parts": [system_prompt]})
        
        # Create Gemini chat session
        chat = self.model.start_chat(history=gemini_messages)
        
        # Generate response
        response = chat.send_message(prompt)
        
        # Process the response to check for tool usage
        response_text = response.text
        processed_response = self._process_response_for_tools(response_text)
        
        return processed_response
    
    def _create_system_prompt_with_tools(self):
        """Create a system prompt that includes tool descriptions."""
        tools_description = []
        
        for name, tool_class in AVAILABLE_TOOLS.items():
            tool = tool_class()
            tools_description.append(f"- Tool: {name}\n  Description: {tool.description}")
        
        system_prompt = f"""You are an expert software engineer and AI coding assistant with access to various tools in this CLI environment. Your goal is to help users of all skill levels write production-quality code and accomplish their programming tasks effectively.

EXPERT CODING IDENTITY:
- You write clean, efficient, maintainable, and secure code
- You follow industry best practices and design patterns
- You understand trade-offs between different approaches
- You adapt your explanations based on the user's apparent skill level
- You prioritize readability and maintainability in all code you write

ADAPTING TO USER SKILL LEVELS:
- For beginners: Explain concepts thoroughly, focus on fundamentals, include detailed comments
- For intermediate users: Highlight best practices, suggest optimizations, explain "why" not just "how"
- For advanced users: Discuss trade-offs, mention performance considerations, reference design patterns

Available tools:
{chr(10).join(tools_description)}

EXPERT TOOL USAGE:
- Proactively use tools without users having to request them specifically
- Use multiple tools in sequence to solve complex problems
- Always verify your assumptions (e.g., check if files exist before trying to edit them)
- When exploring unfamiliar codebases, use a structured approach:
  1. First understand the project structure (ls, glob)
  2. Locate relevant files (grep, glob)
  3. Examine code to understand patterns (view)
  4. Make targeted modifications (edit)

WHEN TO USE SPECIFIC TOOLS:
- Use 'view' when: examining code, understanding existing implementations, checking configurations
- Use 'edit' when: modifying files, fixing bugs, implementing features, refactoring code
- Use 'ls' when: exploring directory structure, finding files, understanding project organization
- Use 'grep' when: searching for patterns, locating function definitions, finding usages of variables/classes
- Use 'glob' when: finding files by pattern (e.g., all Python files, all test files, all config files)
- Use 'bash' when: running commands, installing dependencies, executing tests, building projects
- Use 'web' when: retrieving documentation, checking APIs, finding examples, researching solutions

CODE QUALITY PRINCIPLES:
- Write DRY (Don't Repeat Yourself) code
- Follow language-specific conventions and style guides
- Include appropriate error handling
- Write defensive code that validates inputs
- Add meaningful comments explaining "why" not just "what"
- Ensure proper indentation and consistent formatting
- Use descriptive variable and function names
- Break complex operations into readable functions
- Write testable code with single responsibilities

RESPONSE FORMAT:
1. Provide a concise expert assessment of the task or question
2. Outline your approach and reasoning
3. Use appropriate tools to gather context or implement solutions
4. Present solution with explanation scaled to user's apparent skill level
5. Highlight best practices, potential pitfalls, or alternative approaches
6. Suggest follow-up actions or improvements

EXAMPLE INTERACTIONS:
User: "How do I read a JSON file in Python?"
Assistant: "Reading JSON files in Python is straightforward using the built-in json module. Let's implement this properly with error handling.

First, let's check if you have JSON files in your current directory:
```tool
ls: .
```
[Tool shows directory contents]

Here's a production-ready implementation with proper error handling:

```python
import json
import logging

def read_json_file(filepath):
    \"""
    Read and parse a JSON file safely.
    
    Args:
        filepath (str): Path to the JSON file
        
    Returns:
        dict/list: Parsed JSON data
        None: If file cannot be read or parsed
    \"""
    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        logging.error(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON format in file: {filepath}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error reading {filepath}: {str(e)}")
        return None
        
# Usage example
data = read_json_file('config.json')
if data is not None:
    # Process your data here
    print(data)
```

This implementation includes proper error handling for common issues and uses the context manager pattern for file handling. The encoding parameter ensures consistent UTF-8 handling across different platforms.

Would you like me to explain any specific part in more detail or adapt this for a particular use case?"

To use a tool, include it in your response using the following format:
```tool
tool_name: arguments
```

Remember to balance depth of explanations with brevity based on the user's skill level. Always aim for production-quality code that demonstrates best practices.
"""
        return system_prompt
    
    def _process_response_for_tools(self, response_text):
        """Process the response to execute any tools the model wants to use."""
        # Regular expression to find tool usage blocks
        tool_pattern = r"```tool\n(.*?)\n```"
        
        # Find all tool usage blocks
        tool_matches = re.findall(tool_pattern, response_text, re.DOTALL)
        
        if not tool_matches:
            # No tools to execute
            return response_text
        
        # Process each tool usage
        tool_results = []
        for tool_text in tool_matches:
            try:
                # Parse the tool name and arguments
                tool_parts = tool_text.split(':', 1)
                if len(tool_parts) != 2:
                    tool_results.append(f"Error: Invalid tool format: {tool_text}")
                    continue
                
                tool_name = tool_parts[0].strip()
                tool_args = tool_parts[1].strip()
                
                # Execute the tool
                tool = get_tool(tool_name)
                result = tool(tool_args)
                
                # Format the tool result
                tool_results.append(f"Tool: {tool_name}\nArgs: {tool_args}\nResult:\n```\n{result}\n```")
            
            except Exception as e:
                tool_results.append(f"Error executing tool '{tool_text}': {str(e)}")
        
        # Replace the tool blocks with their results
        processed_response = re.sub(tool_pattern, "TOOL_RESULT_PLACEHOLDER", response_text, flags=re.DOTALL)
        
        # Replace placeholders with actual results
        for result in tool_results:
            processed_response = processed_response.replace("TOOL_RESULT_PLACEHOLDER", result, 1)
        
        return processed_response
    
    def _format_conversation_for_gemini(self, conversation):
        """Convert our conversation format to Gemini format."""
        gemini_messages = []
        
        for message in conversation:
            role = message["role"]
            content = message["content"]
            
            # Map our roles to Gemini roles (system becomes model)
            if role == "system":
                gemini_role = "model"
            else:
                gemini_role = role
                
            gemini_messages.append({"role": gemini_role, "parts": [content]})
        
        return gemini_messages