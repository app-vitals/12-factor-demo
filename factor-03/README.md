# Factor 3: Own Your Context Window

This directory contains implementations of Factor 3 from the 12-Factor Agents methodology, which focuses on structuring context for maximum AI performance.

## Overview

Factor 3 demonstrates the impact of context engineering on LLM performance. Since LLMs are stateless functions, better structured inputs lead to better outputs. This factor explores when sophisticated context formatting justifies the increased token costs.

## Demo

This directory contains a comprehensive demonstration of Factor 3 context engineering:

### factor3_test.py

Complete Factor 3 analysis that demonstrates the progression from standard message formats to Factor 3 optimized context engineering. Shows how adding context and restructuring messages affects LLM performance:

- **Baseline**: Standard message format (system + user)
- **Factor 3 formats**: XML structured, compressed, and JSON conversation history
- **5 diverse scenarios**: Loaded from scenarios.json
- **Quality measurement**: LLM-based evaluation of response quality
- **Cost-benefit analysis**: Whether Factor 3 improvements justify token costs
- **Statistical significance**: 60 total tests for reliable results

### scenarios.json

Test scenarios containing both standard message format and rich context data. Each scenario includes:
- Standard OpenAI-style messages (baseline)
- User profile and project context (for Factor 3 enhancement)
- Diverse engineering scenarios (deployment, security, performance, etc.)

## Requirements

```
anthropic==0.51.0
openai==1.55.3
google-generativeai==0.8.3
tokencost==0.1.20
python-dotenv==1.1.0
```

## Getting Started

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set your API keys:
   ```bash
   export ANTHROPIC_API_KEY=your_anthropic_key_here
   export OPENAI_API_KEY=your_openai_key_here
   export GOOGLE_API_KEY=your_google_key_here
   ```

4. Run the demo:
   ```bash
   python factor3_test.py
   ```

The demo will run comprehensive tests across multiple scenarios and models to definitively answer whether Factor 3 context engineering is worth the cost.