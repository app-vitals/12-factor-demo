#!/usr/bin/env python
import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv()

# Get API keys from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

# Configure OpenAI model
def get_openai_llm():
    """
    Returns a configured OpenAI LLM instance
    """
    if not OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY environment variable is not set")
    
    return ChatOpenAI(
        model=MODEL,
        temperature=0.7
    )