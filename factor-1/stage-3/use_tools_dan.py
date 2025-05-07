#!/usr/bin/env python3

import os
import subprocess
import sys
import textwrap
import time

import boto3
from botocore.exceptions import ClientError
from anthropic import Anthropic
from dotenv import load_dotenv
from tokencost import calculate_cost_by_tokens

load_dotenv()

MODEL = "claude-3-7-sonnet-20250219"

def render_system_prompt():
    return textwrap.dedent(f"""\
    You are an AWS S3 bucket management assistant. You help users create and validate S3 buckets using specialized tools.

    You have access to the following tools:

    1. create_bucket(bucket_name, region)
       Creates an S3 bucket in AWS with the specified name and region.
       This action requires confirmation before execution.

    2. is_valid_region(region)
       Checks if the provided region is a valid AWS region.
       Returns true or false.

    3. bucket_exists(bucket_name, region)
       Checks if an S3 bucket exists in the specified region.
       Returns true if the bucket exists, false otherwise.

    When handling bucket requests:
    - Always validate regions using is_valid_region before attempting to create buckets
    - Check if a bucket already exists using bucket_exists before attempting to create it

    Guide users through the bucket creation process step by step, validating at each stage to prevent errors. If validation fails, explain specifically why and how to fix the issue.
    """)


def is_valid_region(region):
    """
    Validate if the provided region is a valid AWS region
    
    Args:
        region (str): AWS region to validate
        
    Returns:
        str: A string indicating whether the region is valid or not
    """
    try:
        # Basic sanity checks for region parameter
        if region is None or not isinstance(region, str) or region.strip() == "":
            return "unprocessable region name"
        
        # Get the list of available regions using boto3 session
        session = boto3.session.Session()
        valid_regions = session.get_available_regions('s3')
        
        # Check if the provided region is in the list of valid regions
        is_valid = region in valid_regions
        
        if is_valid:
            return "valid region name"
        else:
            return "invalid region name"
    except Exception as e:
        return f"error validating region: {e}"


def bucket_exists(bucket_name, region):
    """
    Check if an S3 bucket exists
    
    Args:
        bucket_name (str): Name of the S3 bucket to check
        region (str): AWS region where the bucket should exist
        
    Returns:
        str: A string indicating whether the bucket exists or not
    """
    try:
        # Basic sanity checks for bucket name
        if bucket_name is None or not isinstance(bucket_name, str) or bucket_name.strip() == "":
            return "invalid bucket name"
            
        # Create a boto3 client for S3 in the specified region
        s3_client = boto3.client('s3', region_name=region)
        
        # Check if the bucket exists by calling head_bucket
        s3_client.head_bucket(Bucket=bucket_name)
        return "bucket exists"
    except ClientError as e:
        error_code = e.response.get('Error', {}).get('Code', '')
        
        # 404 means bucket doesn't exist, which is fine
        if error_code == '404':
            return "bucket does not exist"
        return f"error checking bucket existence: {e}"
    except Exception as e:
        return f"error checking bucket existence: {e}"


def create_bucket(bucket_name, region):
    """
    Create an S3 bucket in AWS with the specified name and region.

    Args:
        bucket_name (str): Name of the S3 bucket to create
        region (str): AWS region where the S3 bucket will be created
    """
    # Create a boto3 client for S3 in the specified region
    s3_client = boto3.client('s3', region_name=region)
    
    # Create the S3 bucket
    if region == "us-east-1":
        s3_client.create_bucket(Bucket=bucket_name)
    else:
        s3_client.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={'LocationConstraint': region}
        )

TOOLS = {
    "create_bucket": {
        "name": "create_bucket",
        "function": create_bucket,
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
        "requires_confirmation": True,
    },
    "is_valid_region": {
        "name": "is_valid_region",
        "function": is_valid_region,
        "description": "Checks if the provided region is a valid AWS region",
        "parameters": {
            "region": {
                "description": "The AWS region to check",
                "type": "string",
            },
        },
        "requires_confirmation": False,
    },
    "bucket_exists": {
        "name": "bucket_exists",
        "function": bucket_exists,
        "description": "Checks if an S3 bucket exists in the specified region",
        "parameters": {
            "bucket_name": {
                "description": "The name of the S3 bucket to check",
                "type": "string",
            },
            "region": {
                "description": "The AWS region where the bucket should exist",
                "type": "string",
            },
        },
        "requires_confirmation": False,
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


def llm_request(messages):
    """
    Send a request to the Anthropic API and handle the response.

    Args:
        messages (list): List of messages to send to the LLM

    Returns:
        response: The response from the LLM
    """

    # Check if ANTHROPIC_API_KEY is set
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        sys.exit(1)
    
    # Create Anthropic client
    client = Anthropic()
    
    # Send request to Anthropic API
    start = time.time()
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        temperature=0,
        system=render_system_prompt(),
        tools=get_tool_descriptions(),
        tool_choice={"type": "auto"},
        messages=messages,
    )
    end = time.time()
    
    # Get usage
    input_tokens = response.usage.input_tokens
    input_cost = calculate_cost_by_tokens(input_tokens, MODEL, "input")
    output_tokens = response.usage.output_tokens
    output_cost = calculate_cost_by_tokens(output_tokens, MODEL, "output")
    print(f"Tokens: {input_tokens} sent, {output_tokens} recv, Cost: ${input_cost + output_cost:.4f}, Time: {end - start:.2f}s")

    return response


def main():
    user_prompt = input("Enter your cloud storage bucket request: ")
    messages = [{"role": "user", "content": user_prompt}]
    print("\nProcessing your request...")

    while True:
        response = llm_request(messages)
        messages.append({"role": "assistant", "content": response.content})

        if(response.stop_reason == "tool_use"):
            tool_results = []
            for content in response.content:
                if content.type == "tool_use":
                    tool = TOOLS[content.name]
                    formatted_input = ", ".join(
                        f"{k}='{v}'" for k, v in content.input.items()
                    )
                    formatted_tool = f"{content.name}({formatted_input})"
                    if tool["requires_confirmation"]:
                        confirmation = input(f"\nConfirm {formatted_tool}? (y/n): ").lower()
                        if confirmation not in ('y', 'yes'):
                            print("Tool execution cancelled.")
                            break
                    print(f"\nExecuting: {formatted_tool}")
                    result = tool["function"](**content.input)
                    tool_results.append({
                      "type": "tool_result",
                      "tool_use_id": content.id,
                      "content": str(result),
                    })
            if not tool_results:
                print("No tool results to process.")
                break
            messages.append({"role": "user", "content": tool_results})
            print("\nProcessing tool results...")
        else:
            print("\nResponse:")
            print(response.content[0].text)
            break

if __name__ == "__main__":
    main()
