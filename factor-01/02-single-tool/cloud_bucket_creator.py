#!/usr/bin/env python3

import os
import subprocess
import sys
import textwrap
import time

from anthropic import Anthropic
from dotenv import load_dotenv
from tokencost import calculate_cost_by_tokens

load_dotenv()

MODEL = "claude-3-7-sonnet-20250219"

def project_settings():
    """
    Read project settings from a markdown file.

    Returns:
        str: Content of the PROJECT.md file
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_md_path = os.path.join(script_dir, "PROJECT.md")
    with open(project_md_path, 'r') as file:
        return file.read()
    
def render_system_prompt():
    """
    Render the system prompt for the LLM.

    Returns:
        str: System prompt string
    """
    return textwrap.dedent(f"""\
    You are a cloud infrastructure assistant specialized in creating storage buckets. You help users provision cloud storage resources by executing commands through dedicated tools.

    {project_settings()}

    You have access to the following tools:

    1. create_aws_s3_bucket(bucket_name, region)
       Creates an S3 bucket in AWS with the specified name and region.

    2. create_gcs_bucket(bucket_name, region)
       Creates a Google Cloud Storage bucket with the specified name and region.

    When asked to create buckets:
    - Use the project settings as defaults, but prioritize any specific values provided by the user
    - Use the appropriate cloud provider tool based on user request or default provider
    - Check if the user's bucket name already contains the global prefix; if not, apply it
    - Apply the specified region for the selected provider or use the default from settings

    Remember that any setting in the configuration can be overridden by the user's explicit request.
    """)


def execute_command(command):
    """
    Execute a shell command and return the output.

    Args:
        command (str): The command to execute

    Returns:
        str: Output of the command execution
    """
    # Ask if user wants to execute the command
    print("\nGenerated command:")
    print(command)
    execute = input("\nDo you want to execute this command? (y/n): ").lower()
    
    output = ""
    if execute in ('y', 'yes'):
        output += f"\nExecuting: '{command}'\n"
        result = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            output += f"Command failed with exit code {result.returncode}\n"
        if result.stdout:
            output += f"Output:\n{result.stdout}\n"
        if result.stderr:
            output += f"Error:\n{result.stderr}\n"
    else:
        output += "Command execution cancelled.\n"
    return output


def create_aws_s3_bucket(bucket_name, region):
    """
    Create an S3 bucket in AWS with the specified name and region.

    Args:
        bucket_name (str): Name of the S3 bucket to create
        region (str): AWS region where the S3 bucket will be created

    Returns:
        str: Output of the command execution
    """
    if region == "us-east-1":
        command = f"aws s3api create-bucket --bucket {bucket_name} --region {region}"
    else:
        command = f"aws s3api create-bucket --bucket {bucket_name} --region {region} --create-bucket-configuration LocationConstraint={region}"
    return execute_command(command)    
        

def create_gcs_bucket(bucket_name, region):
    """
    Create a Google Cloud Storage bucket with the specified name and region.

    Args:
        bucket_name (str): Name of the GCS bucket to create
        region (str): Google Cloud region where the GCS bucket will be created

    Returns:
        str: Output of the command execution
    """
    return execute_command(f"gsutil mb -l {region} gs://{bucket_name} ")


TOOLS = {
    "create_aws_s3_bucket": {
        "name": "create_aws_s3_bucket",
        "function": create_aws_s3_bucket,
        "description": "Creates an S3 bucket in AWS with the specified name and region",
        "parameters": {
            "bucket_name": {
                "description": "The name of the S3 bucket to create",
                "type": "string",
            },
            "region": {
                "description": "The AWS region where the S3 bucket will be created",
                "type": "string",
            },
        },
    },
    "create_gcs_bucket": {
        "name": "create_gcs_bucket",
        "function": create_gcs_bucket,
        "description": "Creates a Google Cloud Storage bucket with the specified name and region",
        "parameters": {
            "bucket_name": {
                "description": "The name of the GCS bucket to create",
                "type": "string",
            },
            "region": {
                "name": "region",
                "description": "The Google Cloud region where the GCS bucket will be created",
                "type": "string",
            },
        },
    },
}


def get_tool_descriptions():
    """Get descriptions of available tools in a format suitable for LLM tool calling.

    Returns:
        List of tool descriptions compatible with LLM tool calling format
    """
    tool_descriptions = []
    for tool_name, tool_info in TOOLS.items():
        properties = {
            param_name: {
                "type": param_info["type"],
                "description": param_info["description"],
            }
            for param_name, param_info in tool_info["parameters"].items()
        }
        tool_descriptions.append(
            {
                "type": "custom",
                "name": tool_name,
                "description": tool_info["description"],
                "input_schema": {
                    "type": "object",
                    "properties": properties,
                    "required": list(tool_info["parameters"].keys()),
                },
            }
        )
    return tool_descriptions


def main():
    # Check if ANTHROPIC_API_KEY is set
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        sys.exit(1)
    
    # Create Anthropic client
    client = Anthropic()
    
    # Get user input
    user_prompt = input("Enter your cloud storage bucket request: ")
    print("\nProcessing your request...")

    # Send request to Anthropic API
    start = time.time()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        temperature=0,
        system=render_system_prompt(),
        tools=get_tool_descriptions(),
        tool_choice={"type": "any"},
        messages=[{"role": "user", "content": user_prompt}],
    )
    end = time.time()
    
    # Get usage
    input_tokens = response.usage.input_tokens
    input_cost = calculate_cost_by_tokens(input_tokens, MODEL, "input")
    output_tokens = response.usage.output_tokens
    output_cost = calculate_cost_by_tokens(output_tokens, MODEL, "output")
    print(f"Tokens: {input_tokens} sent, {output_tokens} recv, Cost: ${input_cost + output_cost:.4f}, Time: {end - start:.2f}s")

    # Get the tool
    result = ""
    for content in response.content:
        if content.type == "tool_use":
            result = TOOLS[content.name]["function"](**content.input)
            break

    print(result)

if __name__ == "__main__":
    main()
