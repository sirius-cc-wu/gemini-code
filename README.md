# Gemini Code

A powerful AI coding assistant for your terminal, powered by Gemini 2.5 Pro with support for other LLM models.

## Features

- Interactive chat sessions in your terminal
- Multiple model support (currently Gemini 2.5 Pro, more coming soon)
- Intelligent context management with auto-compaction warnings and the `/compact` command
- Markdown rendering in the terminal
- Automatic tool usage by the assistant:
  - File operations (view, edit, list, grep, glob)
  - System commands (bash)
  - Web content fetching

## Installation

```bash
# Clone the repository
git clone https://github.com/raizamartin/gemini-code.git
cd gemini-code

# Install the package
pip install -e .
```

## Setup

Before using Gemini CLI, you need to set up your API keys:

```bash
# Set up Google API key for Gemini models
gemini setup YOUR_GOOGLE_API_KEY
```

## Usage

```bash
# Start an interactive session with the default model
gemini

# Start a session with a specific model
gemini --model gemini-2.5-pro

# Set default model
gemini set-default-model gemini-2.5-pro
```

## Interactive Commands

During an interactive session, you can use these commands:

- `/exit` - Exit the chat session
- `/help` - Display help information
- `/compact` - Summarize the conversation to reduce token usage

## How It Works

### Tool Usage

Unlike direct command-line tools, the Gemini CLI's tools are used automatically by the assistant to help answer your questions. For example:

1. You ask: "What files are in the current directory?"
2. The assistant uses the `ls` tool behind the scenes
3. The assistant provides you with a formatted response

This approach makes the interaction more natural and similar to how Claude Code works.

### Context Management

Gemini CLI intelligently manages the conversation context:

1. **Warning Threshold (80%)**: When you reach 80% of the token limit, you'll see a warning panel suggesting to use `/compact`
2. **Auto-Compact Prompt (95%)**: At 95% of the limit, the CLI will ask if you want to automatically compact the conversation
3. **Manual Compaction**: You can use `/compact` at any time to summarize the conversation and reduce token usage

The summarization process preserves important context while significantly reducing token count, allowing for virtually unlimited conversation length.

## Development

This project is under active development. More models and features will be added soon!

## License

MIT