#!/usr/bin/env python3

import os
import subprocess
import sys
import anthropic

def main():
    # Check if ANTHROPIC_API_KEY is set
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        sys.exit(1)
    
    # Create Anthropic client
    client = anthropic.Anthropic()
    
    # Get user input
    user_prompt = input("Enter your prompt: ")
    
    # Send request to Anthropic API
    try:
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            temperature=0,
            system="You are a helpful assistant that provides shell commands. Give ONLY the command with no explanation or markdown formatting.",
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Get the response
        response = message.content[0].text
        
        # Get token usage
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        total_tokens = input_tokens + output_tokens
        
        # Print response
        print("\nClaude's response:")
        print(response)
        print(f"\nTokens used: {total_tokens} (Input: {input_tokens}, Output: {output_tokens})")
        
        # Ask if user wants to execute the command
        execute = input("\nDo you want to execute this command? (y/n): ").lower()
        
        if execute == 'y' or execute == 'yes':
            try:
                print("\nExecuting command...")
                result = subprocess.run(response, shell=True, check=True, text=True, 
                                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                print("\nCommand output:")
                print(result.stdout)
                if result.stderr:
                    print("\nErrors:")
                    print(result.stderr)
            except subprocess.CalledProcessError as e:
                print(f"\nCommand failed with exit code {e.returncode}")
                if e.stdout:
                    print("\nOutput:")
                    print(e.stdout)
                if e.stderr:
                    print("\nErrors:")
                    print(e.stderr)
        else:
            print("Command execution cancelled.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()