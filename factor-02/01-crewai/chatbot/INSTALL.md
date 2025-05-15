# Installation Guide

## Prerequisites

- Python 3.10 to 3.12
- [uv](https://docs.astral.sh/uv/) for dependency management (optional but recommended)

## Setting up the Environment

### Using uv (Recommended)

If you have uv installed, you can use it to set up everything:

```bash
# Install dependencies
uv pip install -e .

# Install extra development dependencies
uv pip install crewai langchain-anthropic python-dotenv
```

### Using pip with virtualenv

Alternatively, you can use pip with a virtual environment:

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`

# Install the package in development mode
pip install -e .

# Install required dependencies
pip install crewai langchain-anthropic python-dotenv
```

## Configuration

1. Create or update the `.env` file in the project root directory:

```
ANTHROPIC_API_KEY=your_api_key_here
MODEL=claude-3-5-sonnet-20240620
```

2. Make sure your Anthropic API key is valid. You can get an API key from [https://console.anthropic.com/](https://console.anthropic.com/).

## Verifying Installation

To verify that everything is set up correctly, run:

```bash
python run_chatbot.py -q "Hello, are you working?"
```

If you see a response from the assistant, the installation was successful!

## Troubleshooting

If you encounter errors related to missing modules:

1. Make sure you've activated the virtual environment
2. Check that all required dependencies are installed
3. If using a virtualenv, try reinstalling with:
   ```bash
   pip install -e .
   pip install crewai langchain-anthropic python-dotenv
   ```

If you see an error about ANTHROPIC_API_KEY not being set:

1. Check that your `.env` file is in the project root directory
2. Make sure the API key in the `.env` file is valid
3. Try setting the environment variable directly:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here  # On Windows, use `set ANTHROPIC_API_KEY=your_api_key_here`
   ```