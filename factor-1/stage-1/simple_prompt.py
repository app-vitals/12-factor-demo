#!/usr/bin/env python3

import os
import subprocess
import sys
import time

from anthropic import Anthropic
from dotenv import load_dotenv
from tokencost import calculate_cost_by_tokens

load_dotenv()

MODEL = "claude-3-7-sonnet-20250219"
SYSTEM_PROMPT = "You are a helpful assistant that provides shell commands. Give ONLY the command with no explanation or markdown formatting."

def main():
    # Check if ANTHROPIC_API_KEY is set
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        sys.exit(1)
    
    # Create Anthropic client
    client = Anthropic()
    
    # Get user input
    user_prompt = input("Describe the shell command that you want to run: ")
    
    # Send request to Anthropic API
    print("\nProcessing your request...")
    start = time.time()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        temperature=0,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )
    end = time.time()
    
    # Get usage
    input_tokens = response.usage.input_tokens
    input_cost = calculate_cost_by_tokens(input_tokens, MODEL, "input")
    output_tokens = response.usage.output_tokens
    output_cost = calculate_cost_by_tokens(output_tokens, MODEL, "output")
    
    # Print response
    print(f"Tokens: {input_tokens} sent, {output_tokens} recv, Cost: ${input_cost + output_cost:.4f}, Time: {end - start:.2f}s")
    
    # Get the command
    command = response.content[0].text
    print("\nClaude's response:")
    print(command)
    
    # Ask if user wants to execute the command
    execute = input("\nDo you want to execute this command? (y/n): ").lower()
    
    if execute in ('y', 'yes'):
        print(f"\nExecuting: '{command}'")
        result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            print(f"Command failed with exit code {result.returncode}")
        if result.stdout:
            print("Output:")
            print(result.stdout)
        if result.stderr:
            print("Error:")
            print(result.stderr)
    else:
        print("Command execution cancelled.")

if __name__ == "__main__":
    main()
