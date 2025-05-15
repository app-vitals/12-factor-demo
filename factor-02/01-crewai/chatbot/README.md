# DevOps Knowledge Assistant

Welcome to the DevOps Knowledge Assistant, powered by [crewAI](https://crewai.com). This AI-powered chatbot specializes in DevOps and engineering topics, providing helpful information based on a knowledge base of technical documentation and best practices.

## Features

- Interactive Q&A with a DevOps/Engineering knowledge assistant
- Access to knowledge base containing DevOps best practices, deployment strategies, and more
- Powered by Anthropic's Claude model via the crewAI framework
- Multi-agent system with a knowledge researcher and a response formulator

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling.

For detailed installation instructions, see [INSTALL.md](INSTALL.md).

Quick setup:

```bash
# Install dependencies (using uv)
uv pip install -e .
uv pip install crewai langchain-anthropic python-dotenv

# Or using regular pip with virtualenv
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install -e .
pip install crewai langchain-anthropic python-dotenv
```

### Configuration

Add your Anthropic API key to the `.env` file:

```
ANTHROPIC_API_KEY=your_api_key_here
MODEL=claude-3-5-sonnet-20240620
```

## Running the DevOps Knowledge Assistant

You can run the DevOps Knowledge Assistant in multiple ways:

### Using the crewai run command

```bash
# Run with default question
crewai run

# Set a custom question via environment variable
DEVOPS_QUESTION="What is Kubernetes?" crewai run
```

### Using the included run script

```bash
# Interactive mode
python run_chatbot.py

# Ask a single question
python run_chatbot.py -q "What is blue-green deployment?"
```

### Using Python directly

```bash
# Interactive mode
python -m src.chatbot.main

# Ask a single question
python -m src.chatbot.main -q "What is blue-green deployment?"
```

### If you've installed the package

```bash
# Using the devops-assistant command
devops-assistant

# Using the chatbot command
chatbot
```

## Example Questions

The assistant can answer questions like:

- "How does blue-green deployment work?"
- "What are the best practices for code reviews?"
- "What should I include in an error rate runbook?"
- "How do I set up a Kubernetes cluster?"
- "What deployment strategies are recommended for high-availability systems?"

## Customizing the Knowledge Base

The assistant uses information from markdown files located in the `knowledge/` directory. You can:

1. Add new markdown files to expand the knowledge base
2. Update existing files to improve or correct information
3. Remove files you don't need

After modifying the knowledge base, update the file paths in `src/chatbot/crew.py` to reflect your changes.

## How It Works

The DevOps Knowledge Assistant uses a multi-agent approach:

1. **Knowledge Researcher**: Searches the knowledge base to find relevant information
2. **DevOps Assistant**: Formulates clear, concise, and helpful answers based on the research

This approach allows the assistant to provide accurate information grounded in the knowledge base while presenting it in a helpful and accessible way.

## Support

For support, questions, or feedback:
- Visit the crewAI [documentation](https://docs.crewai.com)
- Reach out through the crewAI [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join the crewAI Discord](https://discord.com/invite/X4JWnZnxPb)
