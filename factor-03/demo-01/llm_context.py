from enum import IntEnum, auto
from tokencost import calculate_prompt_cost, calculate_completion_cost, count_string_tokens
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Verify API key is set
if not openai_api_key:
    raise ValueError("Missing OPENAI_API_KEY in .env file")

# Define enumerated constant for models
class ModelChoice(IntEnum):
    GPT_35_TURBO = 1
    GPT_4O = 2
    GPT_41 = 3
    O1_MINI = 4

# Function to get model name for tokencost
def get_model_name(choice: ModelChoice) -> str:
    model_map = {
        ModelChoice.GPT_35_TURBO: "gpt-3.5-turbo",
        ModelChoice.GPT_4O: "gpt-4o",
        ModelChoice.GPT_41: "gpt-4-1106-preview",  # This is the gpt-4-turbo 2023-11-06 model
        ModelChoice.O1_MINI: "gpt-3.5-turbo"  # Using gpt-3.5-turbo as fallback for Claude/o1-mini
    }
    return model_map.get(choice, "gpt-3.5-turbo")  # Default to gpt-3.5-turbo if model not found

# Function to get human-readable model name
def get_model_display_name(choice: ModelChoice) -> str:
    model_display_map = {
        ModelChoice.GPT_35_TURBO: "GPT-3.5-Turbo",
        ModelChoice.GPT_4O: "GPT-4o",
        ModelChoice.GPT_41: "GPT-4 Turbo",
        ModelChoice.O1_MINI: "Claude/Anthropic o1-mini (estimated with GPT-3.5-Turbo)"
    }
    return model_display_map.get(choice, str(choice))

# Function to check if a model is supported by tokencost
def is_model_supported(model_name: str) -> bool:
    """Check if a model is supported by the tokencost library."""
    try:
        # Just try counting tokens for a simple string
        count_string_tokens("test", model_name)
        return True
    except Exception as e:
        if "is not implemented" in str(e):
            return False
        # If it's some other error, we'll assume the model is supported
        return True

# Function to calculate token count and cost for a prompt
def calculate_prompt_tokens_and_cost(model_choice: ModelChoice, prompt: str) -> dict:
    model_name = get_model_name(model_choice)
    
    # Check if the model is supported
    if not is_model_supported(model_name):
        raise ValueError(f"Model {model_name} is not supported by the tokencost library.")
    
    # For chat models, we need to format the prompt as a message
    message_prompt = [{"role": "user", "content": prompt}]
    
    # Calculate tokens using the new API
    token_count = count_string_tokens(prompt, model_name)
    
    # Calculate cost using the new API
    cost = calculate_prompt_cost(message_prompt, model_name)
    
    return {
        "model": model_name,
        "tokens": token_count,
        "cost_usd": cost
    }

# Function to calculate token count and cost for a completion
def calculate_completion_tokens_and_cost(model_choice: ModelChoice, completion: str) -> dict:
    model_name = get_model_name(model_choice)
    
    # Check if the model is supported
    if not is_model_supported(model_name):
        raise ValueError(f"Model {model_name} is not supported by the tokencost library.")
    
    # Calculate tokens using the new API
    token_count = count_string_tokens(completion, model_name)
    
    # Calculate cost using the new API
    cost = calculate_completion_cost(completion, model_name)
    
    return {
        "model": model_name,
        "tokens": token_count,
        "cost_usd": cost
    }

# Function to calculate total cost for a conversation (prompt + completion)
def calculate_total_cost(model_choice: ModelChoice, prompt: str, completion: str) -> dict:
    prompt_result = calculate_prompt_tokens_and_cost(model_choice, prompt)
    completion_result = calculate_completion_tokens_and_cost(model_choice, completion)
    
    return {
        "model": prompt_result["model"],
        "model_display_name": get_model_display_name(model_choice),
        "prompt_tokens": prompt_result["tokens"],
        "completion_tokens": completion_result["tokens"],
        "total_tokens": prompt_result["tokens"] + completion_result["tokens"],
        "prompt_cost_usd": prompt_result["cost_usd"],
        "completion_cost_usd": completion_result["cost_usd"],
        "total_cost_usd": prompt_result["cost_usd"] + completion_result["cost_usd"]
    }

# Function to calculate costs for all models
def calculate_costs_for_all_models(prompt: str, completion: str = None) -> list:
    """Calculate token counts and costs for all models in the ModelChoice enum.
    
    Args:
        prompt: The user prompt
        completion: Optional completion response text
        
    Returns:
        A list of dictionaries with token counts and costs for each model
    """
    results = []
    
    # Loop through all models defined in the ModelChoice enum
    for model in ModelChoice:
        try:
            if completion:
                # Calculate total cost for prompt + completion
                model_result = calculate_total_cost(model, prompt, completion)
            else:
                # Calculate cost for prompt only
                model_result = calculate_prompt_tokens_and_cost(model, prompt)
                model_result["model_display_name"] = get_model_display_name(model)
            
            results.append(model_result)
        except Exception as e:
            # Skip models that are not supported or encounter errors
            print(f"Skipping {get_model_display_name(model)}: {e}")
            continue
    
    return results

# Example usage
def run_test_example():
    """Run a non-interactive example to test functionality."""
    prompt = "What is the capital of France?"
    completion = "The capital of France is Paris."
    
    print("=== Token and Cost Calculation for All Models ===")
    print("Prompt: " + prompt)
    
    # Calculate prompt-only costs for all models
    print("\n== Prompt Only Costs ==")
    prompt_results = calculate_costs_for_all_models(prompt)
    
    if not prompt_results:
        print("No supported models found.")
    else:
        for result in prompt_results:
            print(f"\nModel: {result['model_display_name']}")
            print(f"Tokens: {result['tokens']}")
            print(f"Prompt Cost (USD): ${result['cost_usd']:.6f}")
    
    # Calculate total costs (prompt + completion) for all models
    print("\n== Total Costs (Prompt + Completion) ==")
    print("Completion: " + completion)
    
    total_results = calculate_costs_for_all_models(prompt, completion)
    
    if not total_results:
        print("No supported models found.")
    else:
        for result in total_results:
            print(f"\nModel: {result['model_display_name']}")
            print(f"Prompt Tokens: {result['prompt_tokens']}")
            print(f"Completion Tokens: {result['completion_tokens']}")
            print(f"Total Tokens: {result['total_tokens']}")
            print(f"Prompt Cost (USD): ${result['prompt_cost_usd']:.6f}")
            print(f"Completion Cost (USD): ${result['completion_cost_usd']:.6f}")
            print(f"Total Cost (USD): ${result['total_cost_usd']:.6f}")

def main():
    """Main function that can be called to run examples."""
    run_test_example()

if __name__ == "__main__":
    main()