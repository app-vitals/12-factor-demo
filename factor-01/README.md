# Factor 1: Natural Language to Tool Calls

This directory contains implementations of Factor 1 from the 12-Factor Agents methodology, which focuses on properly translating natural language requests into structured tool calls.

## Overview

Factor 1 demonstrates the evolution of translating natural language commands into structured, validated tool calls. This progression is essential for building reliable AI agent systems that can effectively interact with backend services and APIs.

## Example Implementations

The examples in this directory showcase different approaches to handling natural language requests:

1. **01-no-tools/** - LLM directly generates executable commands without structure or validation
2. **02-single-tool/** - Cloud Bucket Creator with constraints and configuration management
3. **03-workflow/** - AWS Tools with multi-step workflow and validation checks

## Examples

### 01-no-tools

The basic implementation where an LLM generates shell commands directly from user requests. This represents the simplest implementation but has significant security and reliability concerns.

### 02-single-tool (Cloud Bucket Creator)

A more structured approach where the LLM is constrained to use specific tools to create cloud storage buckets. Includes configuration management via markdown files.

### 03-workflow (AWS Tools)

Advanced implementation that demonstrates a workflow with validation checks, using AWS S3 bucket creation as the example use case.

## Requirements

All examples share the same requirements:

```
anthropic==0.51.0
boto3==1.38.11
python-dotenv==1.1.0
tokencost==0.1.20
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

3. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   ```

4. Run the example of your choice:
   ```bash
   # For example:
   python 01-no-tools/simple_prompt.py
   ```

See each subdirectory's README for specific instructions on running each example.