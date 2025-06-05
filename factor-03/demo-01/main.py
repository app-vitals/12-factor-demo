#!/usr/bin/env python
"""
Token Cost Calculator

This script calculates the token count and cost for different LLM models.
"""

import sys
import os
from llm_context import (
    calculate_costs_for_all_models,
    run_test_example
)

def display_menu():
    """Display the main menu options."""
    print("\n===== LLM Token and Cost Calculator =====")
    print("1. Calculate prompt tokens and cost")
    print("2. Calculate total conversation cost (prompt + completion)")
    print("3. Exit")
    try:
        return input("Enter your choice (1-3): ")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting program.")
        sys.exit(0)

def calculate_prompt_costs():
    """Calculate prompt tokens and cost for all models."""
    try:
        prompt = input("\nEnter your prompt: ")
        
        print("\n----- Results for All Models -----")
        prompt_results = calculate_costs_for_all_models(prompt)
        
        if not prompt_results:
            print("No supported models found.")
            return
            
        for result in prompt_results:
            print(f"\nModel: {result['model_display_name']}")
            print(f"Tokens: {result['tokens']}")
            print(f"Prompt Cost (USD): ${result['cost_usd']:.6f}")
    except Exception as e:
        print(f"Error calculating prompt costs: {e}")

def calculate_conversation_costs():
    """Calculate total conversation cost for all models."""
    try:
        prompt = input("\nEnter your prompt: ")
        completion = input("Enter the completion text: ")
        
        print("\n----- Results for All Models -----")
        total_results = calculate_costs_for_all_models(prompt, completion)
        
        if not total_results:
            print("No supported models found.")
            return
            
        for result in total_results:
            print(f"\nModel: {result['model_display_name']}")
            print(f"Prompt Tokens: {result['prompt_tokens']}")
            print(f"Completion Tokens: {result['completion_tokens']}")
            print(f"Total Tokens: {result['total_tokens']}")
            print(f"Prompt Cost (USD): ${result['prompt_cost_usd']:.6f}")
            print(f"Completion Cost (USD): ${result['completion_cost_usd']:.6f}")
            print(f"Total Cost (USD): ${result['total_cost_usd']:.6f}")
    except Exception as e:
        print(f"Error calculating conversation costs: {e}")

def interactive_mode():
    """Run the program in interactive mode with menu."""
    print("Welcome to the LLM Token and Cost Calculator!")
    print("This tool calculates token counts and costs for multiple LLM models.")
    
    try:
        while True:
            choice = display_menu()
            
            if choice == "1":
                calculate_prompt_costs()
            elif choice == "2":
                calculate_conversation_costs()
            elif choice == "3":
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