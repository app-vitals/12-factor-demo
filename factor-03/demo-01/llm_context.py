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
        ModelChoice.GPT_4O: "gpt-4o"
    }
    return model_map[choice]

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
        "prompt_tokens": prompt_result["tokens"],
        "completion_tokens": completion_result["tokens"],
        "total_tokens": prompt_result["tokens"] + completion_result["tokens"],
        "prompt_cost_usd": prompt_result["cost_usd"],
        "completion_cost_usd": completion_result["cost_usd"],
        "total_cost_usd": prompt_result["cost_usd"] + completion_result["cost_usd"]
    }

# Example usage
def run_test_example():
    """Run a non-interactive example to test functionality."""
    prompt = "What is the capital of France?"
    completion = "The capital of France is Paris."
    
    # Calculate for GPT-3.5-Turbo
    print("Token and cost calculation for OpenAI (GPT-3.5-Turbo):")
    print("Prompt only:")
    try:
        gpt35_prompt_result = calculate_prompt_tokens_and_cost(ModelChoice.GPT_35_TURBO, prompt)
        print(f"Model: {gpt35_prompt_result['model']}")
        print(f"Tokens: {gpt35_prompt_result['tokens']}")
        print(f"Prompt Cost (USD): {gpt35_prompt_result['cost_usd']:.6f}")
        
        print("\nTotal cost (prompt + completion):")
        gpt35_total = calculate_total_cost(ModelChoice.GPT_35_TURBO, prompt, completion)
        print(f"Model: {gpt35_total['model']}")
        print(f"Prompt Tokens: {gpt35_total['prompt_tokens']}")
        print(f"Completion Tokens: {gpt35_total['completion_tokens']}")
        print(f"Total Tokens: {gpt35_total['total_tokens']}")
        print(f"Prompt Cost (USD): {gpt35_total['prompt_cost_usd']:.6f}")
        print(f"Completion Cost (USD): {gpt35_total['completion_cost_usd']:.6f}")
        print(f"Total Cost (USD): {gpt35_total['total_cost_usd']:.6f}")
    except Exception as e:
        print(f"Error with GPT-3.5-Turbo model calculations: {e}")
    
    # Calculate for GPT-4o
    print("\nToken and cost calculation for OpenAI (GPT-4o):")
    print("Prompt only:")
    try:
        gpt4o_prompt_result = calculate_prompt_tokens_and_cost(ModelChoice.GPT_4O, prompt)
        print(f"Model: {gpt4o_prompt_result['model']}")
        print(f"Tokens: {gpt4o_prompt_result['tokens']}")
        print(f"Prompt Cost (USD): {gpt4o_prompt_result['cost_usd']:.6f}")
        
        print("\nTotal cost (prompt + completion):")
        gpt4o_total = calculate_total_cost(ModelChoice.GPT_4O, prompt, completion)
        print(f"Model: {gpt4o_total['model']}")
        print(f"Prompt Tokens: {gpt4o_total['prompt_tokens']}")
        print(f"Completion Tokens: {gpt4o_total['completion_tokens']}")
        print(f"Total Tokens: {gpt4o_total['total_tokens']}")
        print(f"Prompt Cost (USD): {gpt4o_total['prompt_cost_usd']:.6f}")
        print(f"Completion Cost (USD): {gpt4o_total['completion_cost_usd']:.6f}")
        print(f"Total Cost (USD): {gpt4o_total['total_cost_usd']:.6f}")
    except Exception as e:
        print(f"Error with GPT-4o model calculations: {e}")

def main():
    """Main function that can be called to run examples."""
    run_test_example()

if __name__ == "__main__":
    main()