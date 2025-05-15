#!/usr/bin/env python
import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic

# Load environment variables
load_dotenv()

# Get API keys from environment
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
MODEL = os.getenv("MODEL", "claude-3-5-sonnet-20240620")

# Configure Anthropic model
def get_anthropic_llm():
    """
    Returns a configured Anthropic LLM instance
    """
    if not ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
    
    return ChatAnthropic(
        model=MODEL,
        anthropic_api_key=ANTHROPIC_API_KEY,
        temperature=0.7
    )