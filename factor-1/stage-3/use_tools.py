#!/usr/bin/env python3

import os
import subprocess
import sys
import anthropic
import boto3
from botocore.exceptions import ClientError

def extract_region_code(region_str):
    """
    Helper function to extract AWS region code from a friendly region name
    
    Args:
        region_str (str): Region name or code
        
    Returns:
        str: AWS region code
    """
    region_name_map = {
        "us-east-1": "us-east-1",
        "northern virginia": "us-east-1",
        "n. virginia": "us-east-1",
        "virginia": "us-east-1",
        
        "us-east-2": "us-east-2",
        "ohio": "us-east-2",
        
        "us-west-1": "us-west-1",
        "northern california": "us-west-1",
        "n. california": "us-west-1",
        "california": "us-west-1",
        
        "us-west-2": "us-west-2",
        "oregon": "us-west-2",
        
        "ca-central-1": "ca-central-1",
        "canada": "ca-central-1",
        "central": "ca-central-1",
        "montreal": "ca-central-1",
        
        "eu-west-1": "eu-west-1",
        "ireland": "eu-west-1",
        "dublin": "eu-west-1",
        
        "eu-west-2": "eu-west-2",
        "london": "eu-west-2",
        "uk": "eu-west-2",
        
        "eu-west-3": "eu-west-3",
        "paris": "eu-west-3",
        "france": "eu-west-3",
        
        "eu-central-1": "eu-central-1",
        "frankfurt": "eu-central-1",
        "germany": "eu-central-1",
        
        "ap-northeast-1": "ap-northeast-1",
        "tokyo": "ap-northeast-1",
        "japan": "ap-northeast-1",
        
        "ap-northeast-2": "ap-northeast-2",
        "seoul": "ap-northeast-2",
        "korea": "ap-northeast-2",
        
        "ap-southeast-1": "ap-southeast-1",
        "singapore": "ap-southeast-1",
        
        "ap-southeast-2": "ap-southeast-2",
        "sydney": "ap-southeast-2",
        "australia": "ap-southeast-2",
        
        "ap-south-1": "ap-south-1",
        "mumbai": "ap-south-1",
        "india": "ap-south-1",
        
        "sa-east-1": "sa-east-1",
        "sao paulo": "sa-east-1",
        "brazil": "sa-east-1"
    }
    
    if not region_str:
        return region_str
    
    # Convert to lowercase for case-insensitive matching
    normalized_region = region_str.lower()
    
    # Return the mapped region code if available, otherwise return the original string
    return region_name_map.get(normalized_region, region_str)

def main():
    # Check if ANTHROPIC_API_KEY is set
    if "ANTHROPIC_API_KEY" not in os.environ:
        print("Error: ANTHROPIC_API_KEY environment variable is not set")
        sys.exit(1)
    
    # Create Anthropic client
    client = anthropic.Anthropic()
    
    # Get user input
    user_prompt = input("Enter your prompt: ")
    
    # Send request to Anthropic API
    try:
        message = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            max_tokens=1000,
            temperature=0,
            system="You are a helpful assistant that converts friendly names to AWS resources and checks AWS resources. When given a region name like 'Oregon', 'Ohio', or 'Northern Virginia', convert it to the corresponding AWS region code (e.g., 'Oregon' = 'us-west-2', 'Ohio' = 'us-east-2', 'Northern Virginia' = 'us-east-1') before using it in any tools. Always convert friendly region names to their AWS region code counterparts.",
            tools=[is_valid_region_tool, bucket_exists_tool],
            tool_choice={"type": "any"},
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        # Process the response
        response_text = ""
        for content in message.content:
            if content.type == "text":
                response_text = content.text
            elif content.type == "tool_use":
                tool_name = content.name
                tool_params = content.input
                print(f"Tool called: {tool_name} with params: {tool_params}")
                
                # Execute the appropriate tool function
                if tool_name == "is_valid_region":
                    region = tool_params["region"]
                    result = is_valid_region(region)
                    print(f"\nChecking if region '{region}' is valid: {result}")
                    response_text = f"Region '{region}' is {'valid' if result else 'not valid'}"
                
                elif tool_name == "bucket_exists":
                    try:
                        bucket_name = tool_params["bucket_name"]
                        region = tool_params["region"]
                    except KeyError as e:
                        response_text = f"Error: Missing required parameter: {e}"
                        continue
                    
                    print(f"\nProcessing bucket_exists tool with bucket_name='{bucket_name}' and region='{region}'")
                                       
                    # Check if the bucket exists
                    result = bucket_exists(bucket_name, region)
                    
                    if result:
                        print(f"Bucket exists. Setting response.")
                        response_text = f"Bucket '{bucket_name}' exists in region '{region}'"
                    else:
                        print(f"Bucket does not exist. Proceeding to generate AWS CLI command.")
                        # If bucket doesn't exist in a valid region, generate the AWS CLI command to create it
                        response_text = f"Bucket '{bucket_name}' does not exist in region '{region}'"
                        
                        # Create a new prompt to get the AWS CLI command for bucket creation
                        create_prompt = f"Generate the AWS CLI command to create an S3 bucket named '{bucket_name}' in the AWS region '{region}'. Only provide the command with no explanation."
                        
                        # Send request to Anthropic API for bucket creation command
                        create_message = client.messages.create(
                            model="claude-3-7-sonnet-20250219",
                            max_tokens=500,
                            temperature=0,
                            system="You are a helpful assistant that provides AWS CLI commands. Give ONLY the command with no explanation or markdown formatting.",
                            messages=[
                                {"role": "user", "content": create_prompt}
                            ]
                        )
                        
                        # Get the AWS CLI command
                        aws_command = create_message.content[0].text.strip()
                        print(f"\nAWS CLI command to create bucket:")
                        print(aws_command)
                        
                        # Ask if user wants to execute the command
                        execute = input("\nDo you want to execute this command to create the bucket? (y/n): ").lower()
                        
                        if execute == 'y' or execute == 'yes':
                            try:
                                print("\nExecuting command...")
                                result = subprocess.run(aws_command, shell=True, check=True, text=True, 
                                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                print("\nCommand output:")
                                print(result.stdout)
                                if result.stderr:
                                    print("\nErrors:")
                                    print(result.stderr)
                                
                                response_text += "\nBucket created successfully."
                            except subprocess.CalledProcessError as e:
                                print(f"\nCommand failed with exit code {e.returncode}")
                                if e.stdout:
                                    print("\nOutput:")
                                    print(e.stdout)
                                if e.stderr:
                                    print("\nErrors:")
                                    print(e.stderr)
                                
                                response_text += "\nBucket creation failed."
                        else:
                            response_text += "\nBucket creation cancelled."
        
        # Get token usage
        input_tokens = message.usage.input_tokens
        output_tokens = message.usage.output_tokens
        total_tokens = input_tokens + output_tokens
        
        # Print response
        print("\nClaude's response:")
        print(response_text)
        print(f"\nTokens used: {total_tokens} (Input: {input_tokens}, Output: {output_tokens})")
        
        # If response looks like a shell command and not a tool response, ask if user wants to execute it
        if not response_text.startswith("Region") and not response_text.startswith("Bucket"):
            execute = input("\nDo you want to execute this command? (y/n): ").lower()
            
            if execute == 'y' or execute == 'yes':
                try:
                    print("\nExecuting command...")
                    result = subprocess.run(response_text, shell=True, check=True, text=True, 
                                          stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    print("\nCommand output:")
                    print(result.stdout)
                    if result.stderr:
                        print("\nErrors:")
                        print(result.stderr)
                except subprocess.CalledProcessError as e:
                    print(f"\nCommand failed with exit code {e.returncode}")
                    if e.stdout:
                        print("\nOutput:")
                        print(e.stdout)
                    if e.stderr:
                        print("\nErrors:")
                        print(e.stderr)
            else:
                print("Command execution cancelled.")
    
    except Exception as e:
        print(f"Error: {e}")

# Tool definition for is_valid_region function
is_valid_region_tool = {
  "type": "custom",
  "name": "is_valid_region",
  "description": "Validates if the provided AWS region is valid",
  "input_schema": {
    "type": "object",
    "properties": {
      "region": {
        "type": "string",
        "description": "The AWS region to validate (e.g., 'us-east-1', 'eu-west-2', 'Ohio', 'Oregon', etc.)"
      }
    },
    "required": ["region"]
  }
}

bucket_exists_tool = {
  "type": "custom",
  "name": "bucket_exists",
  "description": "Checks if an S3 bucket exists, returning True if the bucket exists and false if it doesn't",
  "input_schema": {
    "type": "object", 
    "properties": {
      "bucket_name": {
        "type": "string",
        "description": "The name of the S3 bucket to check"
      },
      "region": {
        "type": "string",
        "description": "The AWS region to check in (e.g., 'us-east-1', 'eu-west-2', 'Ohio', 'Oregon', etc.)"
      }
    },
    "required": ["bucket_name", "region"]
  }
}

def is_valid_region(region):
    """
    Validate if the provided region is a valid AWS region
    
    Args:
        region (str): AWS region to validate
        
    Returns:
        bool: True if the region is valid, False otherwise
    """
    try:
        # Basic sanity checks for region parameter
        if region is None or not isinstance(region, str) or region.strip() == "":
            print(f"Invalid region format: '{region}'")
            return False
        
        # Use the extract_region_code helper function to get AWS region code
        mapped_region = extract_region_code(region)
        
        if mapped_region != region:
            print(f"Mapped region '{region}' to AWS region code '{mapped_region}'")
            region = mapped_region
        else:
            print(f"Using region as provided: '{region}'")
        
        # Get the list of available regions using boto3 session
        session = boto3.session.Session()
        valid_regions = session.get_available_regions('s3')
        
        # Check if the provided region is in the list of valid regions
        is_valid = region in valid_regions
        
        return is_valid
    except Exception as e:
        print(f"Error in region validation: {e}")
        # Return False if there's any error in region validation
        return False

def bucket_exists(bucket_name, region):
    """
    Check if an S3 bucket exists
    
    Args:
        bucket_name (str): Name of the S3 bucket to check
        region (str): AWS region where the bucket should exist
        
    Returns:
        bool: True if the bucket exists, False if it doesn't
    """
    try:
        # Basic sanity checks for bucket name
        if bucket_name is None or not isinstance(bucket_name, str) or bucket_name.strip() == "":
            print(f"Invalid bucket name: '{bucket_name}'")
            return False
        
        # Use the extract_region_code helper function to get AWS region code
        mapped_region = extract_region_code(region)
        
        if mapped_region != region:
            print(f"Mapped region '{region}' to AWS region code '{mapped_region}'")
            region = mapped_region
        else:
            print(f"Using region as provided: '{region}'")
            
        # Create a boto3 client for S3 in the specified region
        s3_client = boto3.client('s3', region_name=region)
        
        print(f"Checking if bucket '{bucket_name}' exists in region '{region}'...")
        
        # Check if the bucket exists by calling head_bucket
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            print(f"Bucket '{bucket_name}' exists in region '{region}'")
            return True
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            
            # 404 means bucket doesn't exist, which is fine
            if error_code == '404':
                print(f"Bucket '{bucket_name}' does not exist in region '{region}'")
                return False
            # 403 could mean bucket exists but is owned by someone else
            elif error_code == '403':
                print(f"Access denied to bucket '{bucket_name}' in region '{region}' (might exist but not accessible)")
                return False
            # Other errors should be raised
            else:
                print(f"Error checking bucket: {e}")
                raise
    except Exception as e:
        print(f"Error checking if bucket exists: {e}")
        # Return False for unexpected errors
        return False

if __name__ == "__main__":
    main()