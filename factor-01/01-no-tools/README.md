# No-Tools: Direct Command Execution

This directory contains the simplest implementation of the Factor 1 approach - directly using an LLM to generate shell commands from user requests.

## Overview

The `simple_prompt.py` script demonstrates a basic approach where an LLM directly generates executable commands without any structured validation or constraints. This represents the most basic implementation but highlights the potential security and reliability concerns of this approach.

## How It Works

1. The user provides a natural language description of the shell command they want to run
2. The LLM (Claude) generates a shell command based on the description
3. The command is shown to the user for confirmation
4. If confirmed, the command is executed and the output is displayed

## Features

- Minimal implementation with few lines of code
- Direct command generation from natural language
- Command execution confirmation to prevent unintended actions
- Token usage and cost tracking

## Security Considerations

This approach has significant security implications:

- The LLM can generate any arbitrary shell command
- No validation or sanitization of the generated commands
- Relies entirely on the LLM's understanding of safe commands
- No constraints on what resources or actions can be performed

## Usage

1. Follow the installation steps in the [parent directory README](../README.md#getting-started)
2. Run the script:
   ```bash
   python simple_prompt.py
   ```
3. Enter a natural language description of the command you want to run
4. Review the generated command and confirm whether to execute it

## Example Prompts

- "List all files in the current directory"
- "Show me the top 5 CPU-consuming processes"
- "Create a new directory called 'test' and add an empty file inside it"

## Limitations

- No structured validation of commands
- No constraints on command generation
- No handling of complex workflows
- Limited error handling
- No context from previous interactions