#!/usr/bin/env python
"""
Token Cost Calculator

This script calculates the token count and cost for different LLM models.
"""

import sys
import os
from llm_context import (
    ModelChoice,
    calculate_prompt_tokens_and_cost,
    calculate_completion_tokens_and_cost, 
    calculate_total_cost,
    run_test_example
)

def display_menu():
    """Display the main menu options."""
    print("\n===== LLM Token and Cost Calculator =====")
    print("1. Calculate prompt tokens and cost")
    print("2. Calculate completion tokens and cost")
    print("3. Calculate total conversation cost")
    print("4. Exit")
    try:
        return input("Enter your choice (1-4): ")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting program.")
        sys.exit(0)

def select_model():
    """Let the user select a model."""
    print("\nSelect a model:")
    print(f"1. GPT-3.5-Turbo ({ModelChoice.GPT_35_TURBO.name})")
    print(f"2. GPT-4o ({ModelChoice.GPT_4O.name})")
    
    try:
        choice = input("Enter your choice (1-2): ")
        if choice == "1":
            return ModelChoice.GPT_35_TURBO
        elif choice == "2":
            return ModelChoice.GPT_4O
        else:
            print("Invalid choice. Defaulting to GPT-3.5-Turbo.")
            return ModelChoice.GPT_35_TURBO
    except (EOFError, KeyboardInterrupt):
        print("\nExiting program.")
        sys.exit(0)

def calculate_prompt():
    """Calculate prompt tokens and cost."""
    try:
        model = select_model()
        prompt = input("\nEnter your prompt: ")
        
        result = calculate_prompt_tokens_and_cost(model, prompt)
        
        print("\n----- Results -----")
        print(f"Model: {result['model']}")
        print(f"Tokens: {result['tokens']}")
        print(f"Cost (USD): ${result['cost_usd']:.6f}")
    except Exception as e:
        print(f"Error calculating prompt cost: {e}")

def calculate_completion():
    """Calculate completion tokens and cost."""
    try:
        model = select_model()
        completion = input("\nEnter the completion text: ")
        
        result = calculate_completion_tokens_and_cost(model, completion)
        
        print("\n----- Results -----")
        print(f"Model: {result['model']}")
        print(f"Tokens: {result['tokens']}")
        print(f"Cost (USD): ${result['cost_usd']:.6f}")
    except Exception as e:
        print(f"Error calculating completion cost: {e}")

def calculate_conversation():
    """Calculate total conversation cost."""
    try:
        model = select_model()
        prompt = input("\nEnter your prompt: ")
        completion = input("Enter the completion text: ")
        
        result = calculate_total_cost(model, prompt, completion)
        
        print("\n----- Results -----")
        print(f"Model: {result['model']}")
        print(f"Prompt Tokens: {result['prompt_tokens']}")
        print(f"Completion Tokens: {result['completion_tokens']}")
        print(f"Total Tokens: {result['total_tokens']}")
        print(f"Prompt Cost (USD): ${result['prompt_cost_usd']:.6f}")
        print(f"Completion Cost (USD): ${result['completion_cost_usd']:.6f}")
        print(f"Total Cost (USD): ${result['total_cost_usd']:.6f}")
    except Exception as e:
        print(f"Error calculating conversation cost: {e}")

def interactive_mode():
    """Run the program in interactive mode with menu."""
    print("Welcome to the LLM Token and Cost Calculator!")
    print("This tool calculates token counts and costs for different LLM models.")
    
    try:
        while True:
            choice = display_menu()
            
            if choice == "1":
                calculate_prompt()
            elif choice == "2":
                calculate_completion()
            elif choice == "3":
                calculate_conversation()
            elif choice == "4":
                print("\nThank you for using the LLM Token and Cost Calculator. Goodbye!")
                break
            else:
                print("\nInvalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

def main():
    """Main program entry point."""
    # Check if "test" argument is provided
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        print("Running in test mode...")
        run_test_example()
    else:
        # Run in interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()