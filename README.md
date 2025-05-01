# 12-Factor Agents Demo

This repository contains demo code and resources for the 12-Factor Agents methodology, a framework for building production-grade AI systems. It accompanies our YouTube series exploring each factor in detail.

## What is 12-Factor Agents?

The 12-Factor Agents methodology, created by Dex at Human Layer, provides architectural patterns for building reliable, secure, and scalable AI systems. Inspired by the original [12-Factor App](https://12factor.net/) methodology, it addresses the fundamental challenges of moving AI systems from impressive demos to robust production deployments.

## Repository Structure

This repository is organized by factors, with each directory containing:
- Example implementations demonstrating the factor
- Documentation and explanation
- Resources for the corresponding YouTube video

Currently implemented factors:

- **Factor 1: Natural Language to Tool Calls** - Converting natural language instructions into structured tool invocations
  - Cloud Bucket Creator implementation
  - Tool Evolution Framework with four stages of maturity
  - Security and production considerations

## Factor 1: Natural Language to Tool Calls

The first factor focuses on properly translating natural language requests into structured tool calls - the foundation of any AI agent system.

### The Tool Evolution Framework

We introduce a maturity model for AI agent implementations:

1. **Stage 1: Direct Command Execution** - LLM directly generates executable commands
2. **Stage 2: Natural Language Enhanced Commands** - Adds descriptions and constraints to prompts
3. **Stage 3: Structured Tool Calls** - LLM produces structured data with validation
4. **Stage 4: SDK Integration** - Bypasses shell commands for direct API usage

### Cloud Bucket Creator Example

The Factor 1 directory contains a complete implementation of the Cloud Bucket Creator tool, which demonstrates:

- Natural language processing to extract structured parameters
- Multiple validation layers
- Cross-provider support (AWS S3 and Google Cloud Storage)
- Markdown-based configuration

### Getting Started with Factor 1

```bash
cd factor-1
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export ANTHROPIC_API_KEY=your_api_key_here
python cloud_bucket_creator.py
```

See the factor-specific README.md for detailed setup and usage instructions.

## YouTube Series

This repository accompanies our YouTube series exploring the 12-Factor Agents methodology. Each video covers one factor in depth, with practical examples and implementations.

- Factor 1: Natural Language to Tool Calls - From Commands to Cloud: Building AI Agents That Actually Work

## Original Resources

This work is based on the [12-Factor Agents](https://github.com/humanlayer/12-factor-agents) methodology by Human Layer. Visit their repository for the complete methodology documentation.

## Contributing

We welcome contributions and feedback to improve these demonstrations! Feel free to open issues or pull requests with suggestions, improvements, or questions.

## License

This project is licensed under the MIT License - see the LICENSE file for details.