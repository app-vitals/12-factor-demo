#!/usr/bin/env python
"""
Simple script to run the DevOps Knowledge Assistant directly.
"""
import sys
import os

# Add the src directory to the path so we can import the chatbot module
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from src.chatbot.main import process_command_line

if __name__ == "__main__":
    process_command_line()