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
uv pip install crewai langchain-openai python-dotenv

# Or using regular pip with virtualenv
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
pip install -e .
pip install crewai langchain-openai python-dotenv
```

### Configuration

Add your OpenAI API key to the `.env` file or set it as an environment variable:

```
# Set in .env file
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o  # or any other OpenAI model you prefer

# Or set as environment variable
export OPENAI_API_KEY=your_openai_api_key_here
```

> **Important**: Ensure your OpenAI account has sufficient quota for the model you're using. If you encounter a "RateLimitError: OpenAIException - You exceeded your current quota" error, you may need to:
> 1. Check your [OpenAI usage dashboard](https://platform.openai.com/usage) to verify your current usage
> 2. Add a payment method to your OpenAI account if using a free tier
> 3. Consider using a less expensive model like `gpt-3.5-turbo` by setting `OPENAI_MODEL=gpt-3.5-turbo` in your `.env` file

## Running the DevOps Knowledge Assistant

You can run the DevOps Knowledge Assistant in multiple ways:

### Using the crewai run command

```bash
# Run with default question
crewai run

# Set a custom question via environment variable
DEVOPS_QUESTION="What is Kubernetes?" crewai run

# Enable debugging output
DEVOPS_DEBUG=true crewai run
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

The assistant uses information from markdown files located in the `knowledge/` directory at the root of your project. This location is required by crewAI - it automatically looks for knowledge files in this specific directory.

You can:

1. Add new markdown files to expand the knowledge base
2. Update existing files to improve or correct information
3. Remove files you don't need

After modifying the knowledge base:

1. Update the list of files in `src/chatbot/crew.py` for both agents:
   ```python
   knowledge_files = TextFileKnowledgeSource(
       file_paths=[
           "your-new-file.md",
           "existing-file.md",
           # Add or remove files as needed
       ]
   )
   ```

2. Use relative file paths (no leading slash), as these are relative to the `knowledge/` directory
3. Ensure your files exist in the `knowledge/` directory, not elsewhere

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
