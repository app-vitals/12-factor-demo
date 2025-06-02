# LLM Token and Cost Calculator

A utility for calculating token counts and costs for OpenAI models using the tokencost library.

## Features

- Calculate token counts and costs for prompts
- Calculate token counts and costs for completions
- Calculate total cost for a conversation (prompt + completion)
- Support for OpenAI models:
  - GPT-3.5-Turbo
  - GPT-4o

## How to Install and Run

### Prerequisites

- Python 3.8 or higher
- API keys for Anthropic and OpenAI (if you want to actually call the APIs)

### Installation

1. Ensure you have Python installed on your system.
2. Clone this repository to your local machine.
3. Navigate to the project directory.
4. Install the required dependencies using:
   ```bash
   pip install -r requirements.txt
   ```

### Environment Setup

1. Copy the `.env.example` file to a new file named `.env`:
   ```bash
   cp .env.example .env
   ```
2. Edit the `.env` file and add your actual API keys:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Running the Program

1. Run the program using:
   ```bash
   python main.py
   ```
   or
   ```bash
   ./main.py
   ```
2. Follow the prompts in the terminal to:
   - Select the calculation type (prompt, completion, or total conversation)
   - Select the model (Claude 3.7 Sonnet or GPT-4o)
   - Enter your prompt/completion text
   - View the token count and cost results

## Usage Examples

The program provides an interactive menu with the following options:

1. Calculate prompt tokens and cost
2. Calculate completion tokens and cost
3. Calculate total conversation cost
4. Exit

### Example Output

```
Token and cost calculation for Anthropic (Claude 3.7 Sonnet):
Model: claude-3-7-sonnet-20250213
Tokens: 7
Prompt Cost (USD): $0.000156

Total cost (prompt + completion):
Model: claude-3-7-sonnet-20250213
Prompt Tokens: 7
Completion Tokens: 8
Total Tokens: 15
Prompt Cost (USD): $0.000156
Completion Cost (USD): $0.000048
Total Cost (USD): $0.000204
```

## Library Usage

You can also use the functions directly in your own code:

```python
from llm_context import ModelChoice, calculate_prompt_tokens_and_cost

# Calculate tokens and cost for a prompt
result = calculate_prompt_tokens_and_cost(ModelChoice.CLAUDE_3_7_SONNET, "What is the capital of France?")
print(f"Tokens: {result['tokens']}")
print(f"Cost: ${result['cost_usd']:.6f}")
```

## License

This project is open source and available under the MIT License.