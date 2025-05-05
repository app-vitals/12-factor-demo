#!/usr/bin/env python3
"""
Cloud Bucket Creator

A tool that uses natural language processing to create storage buckets in
different cloud providers (AWS S3, Google Cloud Storage, or Azure Blob Storage) based on user input.

Requirements:
- ANTHROPIC_API_KEY environment variable must be set
- AWS CLI, Google Cloud SDK, or Azure CLI must be installed depending on which provider you use
"""

import json
import os
import subprocess
import anthropic

# Color definitions - using color-blind friendly colors
# Using blue and orange which are distinguishable by most color-blind people
class Colors:
    BLUE = '\033[94m'      # Information/normal text
    ORANGE = '\033[38;5;208m'  # Commands/highlights
    BOLD = '\033[1m'       # Emphasis
    UNDERLINE = '\033[4m'  # Important items
    END = '\033[0m'        # Reset color

# These will be loaded from PROJECT.md at runtime
DEFAULT_CLOUD_PROVIDER = ""
DEFAULT_BUCKET_PREFIX = ""
AWS_DEFAULT_REGION = ""
GCP_DEFAULT_REGION = ""
AZURE_DEFAULT_REGION = ""
AZURE_DEFAULT_RESOURCE_GROUP = ""
AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE = ""

# Token usage tracking
input_tokens = 0
output_tokens = 0
total_tokens = 0

def load_defaults_from_project_file():
    """Load default settings from PROJECT.md file."""
    global DEFAULT_CLOUD_PROVIDER, DEFAULT_BUCKET_PREFIX, AWS_DEFAULT_REGION, GCP_DEFAULT_REGION
    global AZURE_DEFAULT_REGION, AZURE_DEFAULT_RESOURCE_GROUP, AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE
    
    try:
        project_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "PROJECT.md")
        with open(project_path, 'r') as file:
            content = file.read()
            
            # Parse using markdown section headers and bullet points pattern
            lines = content.split('\n')
            current_section = ""
            subsection = ""
            
            for line in lines:
                line = line.strip()
                
                # Skip empty lines
                if not line:
                    continue
                
                # Main sections (##)
                if line.startswith('## '):
                    current_section = line[3:].strip().lower()
                    subsection = ""
                # Subsections (###)
                elif line.startswith('### '):
                    subsection = line[4:].strip().lower()
                # Settings (bullet points)
                elif line.startswith('- '):
                    # Extract the key-value pair (format: "- key: value")
                    if ': ' in line:
                        key, value = [part.strip() for part in line[2:].split(':', 1)]
                        
                        # Map to the appropriate global variable based on section and key
                        if current_section == "cloud provider settings" and subsection == "default provider" and key == "provider":
                            DEFAULT_CLOUD_PROVIDER = value
                        elif current_section == "bucket settings":
                            if subsection == "global settings" and key == "prefix":
                                DEFAULT_BUCKET_PREFIX = value
                            elif subsection == "aws s3 settings" and key == "region":
                                AWS_DEFAULT_REGION = value
                            elif subsection == "google cloud storage settings" and key == "region":
                                GCP_DEFAULT_REGION = value
                            elif subsection == "azure blob storage settings":
                                if key == "region":
                                    AZURE_DEFAULT_REGION = value
                                elif key == "resource_group":
                                    AZURE_DEFAULT_RESOURCE_GROUP = value
                                elif key == "storage_account_type":
                                    AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE = value
            
            # Set fallbacks if any values are missing
            if not DEFAULT_CLOUD_PROVIDER:
                DEFAULT_CLOUD_PROVIDER = "AWS"
            if not AWS_DEFAULT_REGION:
                AWS_DEFAULT_REGION = "us-east-1"
            if not GCP_DEFAULT_REGION:
                GCP_DEFAULT_REGION = "us-east2"
            if not AZURE_DEFAULT_REGION:
                AZURE_DEFAULT_REGION = "eastus"
            if not AZURE_DEFAULT_RESOURCE_GROUP:
                AZURE_DEFAULT_RESOURCE_GROUP = "rg-app-vitals"
            if not AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE:
                AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE = "Standard_LRS"
            
        print(f"{Colors.BLUE}Loaded defaults from PROJECT.md:{Colors.END}")
        print(f"{Colors.BLUE}- Cloud Provider: {Colors.ORANGE}{DEFAULT_CLOUD_PROVIDER}{Colors.END}")
        print(f"{Colors.BLUE}- Bucket Prefix: {Colors.ORANGE}{DEFAULT_BUCKET_PREFIX}{Colors.END}")
        print(f"{Colors.BLUE}- AWS Region: {Colors.ORANGE}{AWS_DEFAULT_REGION}{Colors.END}")
        print(f"{Colors.BLUE}- GCP Region: {Colors.ORANGE}{GCP_DEFAULT_REGION}{Colors.END}")
        print(f"{Colors.BLUE}- Azure Region: {Colors.ORANGE}{AZURE_DEFAULT_REGION}{Colors.END}")
        print(f"{Colors.BLUE}- Azure Resource Group: {Colors.ORANGE}{AZURE_DEFAULT_RESOURCE_GROUP}{Colors.END}")
        print(f"{Colors.BLUE}- Azure Storage Account Type: {Colors.ORANGE}{AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE}{Colors.END}")
        print()
    except Exception as e:
        print(f"{Colors.ORANGE}Warning: Could not load defaults from PROJECT.md: {str(e)}{Colors.END}")
        print(f"{Colors.BLUE}Using fallback defaults.{Colors.END}")
        
        # Set fallback defaults
        if not DEFAULT_CLOUD_PROVIDER:
            DEFAULT_CLOUD_PROVIDER = "AWS"
        if not AWS_DEFAULT_REGION:
            AWS_DEFAULT_REGION = "us-east-1"
        if not GCP_DEFAULT_REGION:
            GCP_DEFAULT_REGION = "us-east2"
        if not AZURE_DEFAULT_REGION:
            AZURE_DEFAULT_REGION = "eastus" 
        if not AZURE_DEFAULT_RESOURCE_GROUP:
            AZURE_DEFAULT_RESOURCE_GROUP = "rg-app-vitals"
        if not AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE:
            AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE = "Standard_LRS"

# Initialize Anthropic client (using environment variable for API key)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def create_aws_s3_bucket(bucket_name, region=AWS_DEFAULT_REGION):
    """Create an AWS S3 bucket using AWS CLI."""
    try:
        # us-east-1 requires different syntax (no LocationConstraint)
        if region == "us-east-1":
            command = f"aws s3api create-bucket --bucket {bucket_name} --region {region}"
        else:
            command = f"aws s3api create-bucket --bucket {bucket_name} --region {region} --create-bucket-configuration LocationConstraint={region}"
        
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        
        return {
            "status": "success", 
            "message": f"AWS S3 bucket '{bucket_name}' created in region '{region}'",
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Command failed with code {e.returncode}",
            "error": e.stderr
        }

def create_gcs_bucket(bucket_name, region=GCP_DEFAULT_REGION):
    """Create a Google Cloud Storage bucket using gcloud CLI."""
    try:
        command = f"gcloud storage buckets create gs://{bucket_name} --location={region}"
        
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        
        return {
            "status": "success", 
            "message": f"Google Cloud Storage bucket '{bucket_name}' created in region '{region}'",
            "output": result.stdout
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Command failed with code {e.returncode}",
            "error": e.stderr
        }
        
def create_azure_storage_container(storage_account_name, container_name, region=AZURE_DEFAULT_REGION, 
                                   resource_group=AZURE_DEFAULT_RESOURCE_GROUP, 
                                   storage_account_type=AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE):
    """Create an Azure Blob Storage container using Azure CLI."""
    try:
        # First check if the storage account exists, if not create it
        check_account_cmd = f"az storage account show --name {storage_account_name} --resource-group {resource_group}"
        try:
            subprocess.run(check_account_cmd, shell=True, check=True, capture_output=True, text=True)
            storage_account_exists = True
        except subprocess.CalledProcessError:
            storage_account_exists = False
            
        # Create storage account if it doesn't exist
        if not storage_account_exists:
            create_acct_cmd = f"az storage account create --name {storage_account_name} --resource-group {resource_group} --location {region} --sku {storage_account_type}"
            create_result = subprocess.run(create_acct_cmd, shell=True, check=True, capture_output=True, text=True)
            account_creation_message = f"Storage account '{storage_account_name}' created in region '{region}'. "
        else:
            account_creation_message = f"Using existing storage account '{storage_account_name}'. "
        
        # Get storage account key for container creation
        key_cmd = f"az storage account keys list --account-name {storage_account_name} --resource-group {resource_group} --query '[0].value' -o tsv"
        key_result = subprocess.run(key_cmd, shell=True, check=True, capture_output=True, text=True)
        account_key = key_result.stdout.strip()
        
        # Create the blob container
        container_cmd = f"az storage container create --name {container_name} --account-name {storage_account_name} --account-key {account_key}"
        container_result = subprocess.run(container_cmd, shell=True, check=True, capture_output=True, text=True)
        
        return {
            "status": "success", 
            "message": f"{account_creation_message}Blob container '{container_name}' created in storage account '{storage_account_name}'",
            "output": container_result.stdout
        }
    except subprocess.CalledProcessError as e:
        return {
            "status": "error",
            "message": f"Command failed with code {e.returncode}",
            "error": e.stderr
        }

def get_storage_account_name_from_bucket(bucket_name):
    """Convert a bucket name to a valid Azure storage account name."""
    # Remove any hyphens and special characters
    name = ''.join(c for c in bucket_name if c.isalnum()).lower()
    # Ensure it's between 3 and 24 characters
    if len(name) < 3:
        name = name + 'storage'  # append 'storage' if too short
    if len(name) > 24:
        name = name[:24]  # truncate if too long
    return name

def process_natural_language(user_input):
    """Convert natural language to a tool call using LLM."""
    global DEFAULT_CLOUD_PROVIDER, DEFAULT_BUCKET_PREFIX, AWS_DEFAULT_REGION, GCP_DEFAULT_REGION, AZURE_DEFAULT_REGION
    global AZURE_DEFAULT_RESOURCE_GROUP, AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE, input_tokens, output_tokens, total_tokens
    
    # Initialize token counters
    input_tokens = 0
    output_tokens = 0
    total_tokens = 0
    
    system_prompt = f"""Convert the user request into a JSON object for creating a cloud storage bucket.
    
    If the request is for AWS S3, the JSON should have:
    - "tool" field set to "create_aws_s3_bucket"
    - "parameters" field with "bucket_name" and "region"
    - Default region: "{AWS_DEFAULT_REGION}" if not specified
    
    If the request is for Google Cloud Storage, the JSON should have:
    - "tool" field set to "create_gcs_bucket" 
    - "parameters" field with "bucket_name" and "region"
    - Default region: "{GCP_DEFAULT_REGION}" if not specified
    
    If the request is for Azure Blob Storage, the JSON should have:
    - "tool" field set to "create_azure_storage_container"
    - "parameters" field with "storage_account_name", "container_name", "region", "resource_group", and "storage_account_type"
    - Default region: "{AZURE_DEFAULT_REGION}" if not specified
    - Default resource group: "{AZURE_DEFAULT_RESOURCE_GROUP}" if not specified
    - Default storage account type: "{AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE}" if not specified
    - Storage account names must be between 3 and 24 characters in length and use only numbers and lowercase letters
    - Container names must be lowercase, between 3 and 63 characters
    
    If the cloud provider is not specified, assume {DEFAULT_CLOUD_PROVIDER} as the default cloud provider.
    
    IMPORTANT INSTRUCTIONS FOR UNDERSTANDING USER INTENT:
    1. When the user mentions "bucket" generically without specifying a provider, use the default provider ({DEFAULT_CLOUD_PROVIDER}).
    2. If the default provider is "AWS", interpret "bucket" as an S3 bucket.
    3. If the default provider is "Azure", interpret "bucket" as an Azure Blob Storage container.
    4. If the default provider is "Google", interpret "bucket" as a Google Cloud Storage bucket.
    
    IMPORTANT: If the bucket/container name doesn't already include the prefix "{DEFAULT_BUCKET_PREFIX}" and the user didn't 
    explicitly say to not use the prefix, automatically add the prefix "{DEFAULT_BUCKET_PREFIX}" to the beginning 
    of the bucket/container name. For Azure storage accounts, use a modified version of the prefix without hyphens 
    (remove any hyphens), as Azure storage account names cannot contain hyphens.
    
    Only return the JSON object, no additional text.
    """
    
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1000,
        temperature=0,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_input}
        ]
    )
    
    response_text = message.content[0].text
    
    # Get token usage information
    input_tokens = message.usage.input_tokens
    output_tokens = message.usage.output_tokens
    total_tokens = input_tokens + output_tokens
    
    # Extract JSON from response
    try:
        # Find JSON structure in the response
        json_start = response_text.find('{')
        json_end = response_text.rfind('}') + 1
        if json_start != -1 and json_end != -1:
            json_str = response_text[json_start:json_end]
            tool_call = json.loads(json_str)
            
            # Post-process to ensure default provider is respected
            if "tool" not in tool_call or not tool_call["tool"]:
                # If we couldn't determine a tool or provider was not specified,
                # force the default provider based on the request
                if DEFAULT_CLOUD_PROVIDER.upper() == "AZURE" and "bucket" in user_input.lower():
                    # Convert a generic bucket request to Azure blob storage
                    bucket_name = tool_call.get("parameters", {}).get("bucket_name", "default")
                    # Generate a storage account name based on the bucket name
                    storage_account_name = get_storage_account_name_from_bucket(bucket_name)
                    
                    return {
                        "tool": "create_azure_storage_container",
                        "parameters": {
                            "storage_account_name": storage_account_name,
                            "container_name": bucket_name,
                            "region": AZURE_DEFAULT_REGION,
                            "resource_group": AZURE_DEFAULT_RESOURCE_GROUP,
                            "storage_account_type": AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE
                        }
                    }
                elif DEFAULT_CLOUD_PROVIDER.upper() == "GOOGLE" and "bucket" in user_input.lower():
                    bucket_name = tool_call.get("parameters", {}).get("bucket_name", "default")
                    return {
                        "tool": "create_gcs_bucket",
                        "parameters": {
                            "bucket_name": bucket_name,
                            "region": GCP_DEFAULT_REGION
                        }
                    }
            
            return tool_call
        else:
            return {"error": "Could not extract JSON from response"}
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in response"}

def main():
    print(f"{Colors.BLUE}{Colors.BOLD}Cloud Bucket Creator{Colors.END}")
    user_input = input(f"{Colors.BLUE}Enter your cloud storage bucket request: {Colors.END}")
    print(f"{Colors.BLUE}Processing request: '{Colors.ORANGE}{user_input}{Colors.BLUE}'{Colors.END}")
    print(f"{Colors.BLUE}Default cloud provider: {Colors.ORANGE}{DEFAULT_CLOUD_PROVIDER}{Colors.END}")
    
    tool_call = process_natural_language(user_input)
    
    # Check for errors in the tool call
    if isinstance(tool_call, dict) and "error" in tool_call:
        print(f"{Colors.ORANGE}{Colors.BOLD}Error: {tool_call['error']}{Colors.END}")
        return
    
    if not isinstance(tool_call, dict) or "tool" not in tool_call:
        print(f"{Colors.ORANGE}{Colors.BOLD}Error: Could not understand the request. Please try again with more details.{Colors.END}")
        return
        
    # Override with default provider if "bucket" is mentioned but no specific provider
    if "bucket" in user_input.lower() and "aws" not in user_input.lower() and "s3" not in user_input.lower() and \
       "azure" not in user_input.lower() and "blob" not in user_input.lower() and \
       "google" not in user_input.lower() and "gcs" not in user_input.lower() and "gcp" not in user_input.lower():
        
        if DEFAULT_CLOUD_PROVIDER.upper() == "AZURE" and tool_call["tool"] != "create_azure_storage_container":
            # Extract bucket name from existing tool call
            bucket_name = None
            if tool_call["tool"] == "create_aws_s3_bucket" or tool_call["tool"] == "create_gcs_bucket":
                bucket_name = tool_call["parameters"].get("bucket_name", "default")
                
            if bucket_name:
                storage_account_name = get_storage_account_name_from_bucket(bucket_name)
                print(f"{Colors.BLUE}Overriding provider to {Colors.ORANGE}Azure{Colors.BLUE} (default provider){Colors.END}")
                tool_call = {
                    "tool": "create_azure_storage_container",
                    "parameters": {
                        "storage_account_name": storage_account_name,
                        "container_name": bucket_name,
                        "region": AZURE_DEFAULT_REGION,
                        "resource_group": AZURE_DEFAULT_RESOURCE_GROUP,
                        "storage_account_type": AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE
                    }
                }
        elif DEFAULT_CLOUD_PROVIDER.upper() == "GOOGLE" and tool_call["tool"] != "create_gcs_bucket":
            # Extract bucket name from existing tool call
            bucket_name = None
            if tool_call["tool"] == "create_aws_s3_bucket":
                bucket_name = tool_call["parameters"].get("bucket_name", "default")
            elif tool_call["tool"] == "create_azure_storage_container":
                bucket_name = tool_call["parameters"].get("container_name", "default")
                
            if bucket_name:
                print(f"{Colors.BLUE}Overriding provider to {Colors.ORANGE}Google Cloud{Colors.BLUE} (default provider){Colors.END}")
                tool_call = {
                    "tool": "create_gcs_bucket",
                    "parameters": {
                        "bucket_name": bucket_name,
                        "region": GCP_DEFAULT_REGION
                    }
                }
        elif DEFAULT_CLOUD_PROVIDER.upper() == "AWS" and tool_call["tool"] != "create_aws_s3_bucket":
            # Extract bucket name from existing tool call
            bucket_name = None
            if tool_call["tool"] == "create_gcs_bucket":
                bucket_name = tool_call["parameters"].get("bucket_name", "default")
            elif tool_call["tool"] == "create_azure_storage_container":
                bucket_name = tool_call["parameters"].get("container_name", "default")
                
            if bucket_name:
                print(f"{Colors.BLUE}Overriding provider to {Colors.ORANGE}AWS{Colors.BLUE} (default provider){Colors.END}")
                tool_call = {
                    "tool": "create_aws_s3_bucket",
                    "parameters": {
                        "bucket_name": bucket_name,
                        "region": AWS_DEFAULT_REGION
                    }
                }
    
    tool_type = tool_call.get("tool", "")
    
    if tool_type == "create_aws_s3_bucket":
        # AWS S3 bucket creation
        bucket_name = tool_call["parameters"]["bucket_name"]
        region = tool_call["parameters"].get("region", AWS_DEFAULT_REGION)
        
        # us-east-1 requires different syntax (no LocationConstraint)
        if region == "us-east-1":
            command = f"aws s3api create-bucket --bucket {bucket_name} --region {region}"
        else:
            command = f"aws s3api create-bucket --bucket {bucket_name} --region {region} --create-bucket-configuration LocationConstraint={region}"
        
        print(f"\n{Colors.BLUE}{Colors.BOLD}Command to be executed (AWS S3):{Colors.END}")
        print(f"{Colors.ORANGE}{command}{Colors.END}")
        print(f"{Colors.BLUE}Tokens used: {Colors.ORANGE}{total_tokens}{Colors.BLUE} (Input: {input_tokens}, Output: {output_tokens}){Colors.END}")
        confirmation = input(f"\n{Colors.BLUE}{Colors.BOLD}Do you want to proceed? (y/n): {Colors.END}").strip().lower()
        
        if confirmation == 'y':
            print(f"{Colors.BLUE}Executing AWS CLI command...{Colors.END}")
            result = create_aws_s3_bucket(bucket_name, region)
            
            if result["status"] == "success":
                print(f"{Colors.BLUE}{Colors.BOLD}Success:{Colors.END} {result['message']}")
                if result.get("output"):
                    print(f"{Colors.BLUE}Output:{Colors.END} {result['output']}")
            else:
                print(f"{Colors.ORANGE}{Colors.BOLD}Error:{Colors.END} {result['message']}")
                if result.get("error"):
                    print(f"{Colors.ORANGE}Details:{Colors.END} {result['error']}")
        else:
            print(f"{Colors.BLUE}Operation cancelled.{Colors.END}")
            
    elif tool_type == "create_gcs_bucket":
        # Google Cloud Storage bucket creation
        bucket_name = tool_call["parameters"]["bucket_name"]
        region = tool_call["parameters"].get("region", GCP_DEFAULT_REGION)
        
        command = f"gcloud storage buckets create gs://{bucket_name} --location={region}"
        
        print(f"\n{Colors.BLUE}{Colors.BOLD}Command to be executed (Google Cloud Storage):{Colors.END}")
        print(f"{Colors.ORANGE}{command}{Colors.END}")
        print(f"{Colors.BLUE}Tokens used: {Colors.ORANGE}{total_tokens}{Colors.BLUE} (Input: {input_tokens}, Output: {output_tokens}){Colors.END}")
        confirmation = input(f"\n{Colors.BLUE}{Colors.BOLD}Do you want to proceed? (y/n): {Colors.END}").strip().lower()
        
        if confirmation == 'y':
            print(f"{Colors.BLUE}Executing Google Cloud CLI command...{Colors.END}")
            result = create_gcs_bucket(bucket_name, region)
            
            if result["status"] == "success":
                print(f"{Colors.BLUE}{Colors.BOLD}Success:{Colors.END} {result['message']}")
                if result.get("output"):
                    print(f"{Colors.BLUE}Output:{Colors.END} {result['output']}")
            else:
                print(f"{Colors.ORANGE}{Colors.BOLD}Error:{Colors.END} {result['message']}")
                if result.get("error"):
                    print(f"{Colors.ORANGE}Details:{Colors.END} {result['error']}")
        else:
            print(f"{Colors.BLUE}Operation cancelled.{Colors.END}")
            
    elif tool_type == "create_azure_storage_container":
        # Azure Blob Storage container creation
        storage_account_name = tool_call["parameters"]["storage_account_name"]
        container_name = tool_call["parameters"]["container_name"]
        region = tool_call["parameters"].get("region", AZURE_DEFAULT_REGION)
        resource_group = tool_call["parameters"].get("resource_group", AZURE_DEFAULT_RESOURCE_GROUP)
        storage_account_type = tool_call["parameters"].get("storage_account_type", AZURE_DEFAULT_STORAGE_ACCOUNT_TYPE)
        
        # First display check account command
        check_account_cmd = f"az storage account show --name {storage_account_name} --resource-group {resource_group}"
        create_account_cmd = f"az storage account create --name {storage_account_name} --resource-group {resource_group} --location {region} --sku {storage_account_type}"
        container_cmd = f"az storage container create --name {container_name} --account-name {storage_account_name}"
        
        print(f"\n{Colors.BLUE}{Colors.BOLD}Commands to be executed (Azure Blob Storage):{Colors.END}")
        print(f"{Colors.ORANGE}1. Check if storage account exists: {check_account_cmd}{Colors.END}")
        print(f"{Colors.ORANGE}2. Create storage account if needed: {create_account_cmd}{Colors.END}")
        print(f"{Colors.ORANGE}3. Create container: {container_cmd}{Colors.END}")
        print(f"{Colors.BLUE}Tokens used: {Colors.ORANGE}{total_tokens}{Colors.BLUE} (Input: {input_tokens}, Output: {output_tokens}){Colors.END}")
        confirmation = input(f"\n{Colors.BLUE}{Colors.BOLD}Do you want to proceed? (y/n): {Colors.END}").strip().lower()
        
        if confirmation == 'y':
            print(f"{Colors.BLUE}Executing Azure CLI commands...{Colors.END}")
            result = create_azure_storage_container(storage_account_name, container_name, region, resource_group, storage_account_type)
            
            if result["status"] == "success":
                print(f"{Colors.BLUE}{Colors.BOLD}Success:{Colors.END} {result['message']}")
                if result.get("output"):
                    print(f"{Colors.BLUE}Output:{Colors.END} {result['output']}")
            else:
                print(f"{Colors.ORANGE}{Colors.BOLD}Error:{Colors.END} {result['message']}")
                if result.get("error"):
                    print(f"{Colors.ORANGE}Details:{Colors.END} {result['error']}")
        else:
            print(f"{Colors.BLUE}Operation cancelled.{Colors.END}")
    else:
        print(f"{Colors.ORANGE}{Colors.BOLD}Error: Unknown tool type '{tool_type}'.{Colors.END}")

if __name__ == "__main__":
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(f"{Colors.ORANGE}{Colors.BOLD}Error: ANTHROPIC_API_KEY environment variable not set{Colors.END}")
        print(f"{Colors.BLUE}Please set the environment variable with:{Colors.END}")
        print(f"{Colors.ORANGE}export ANTHROPIC_API_KEY=your_api_key{Colors.END}")
        exit(1)
    
    try:
        # Load defaults from PROJECT.md before running
        load_defaults_from_project_file()
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.BLUE}Operation cancelled by user.{Colors.END}")
    except Exception as e:
        print(f"\n{Colors.ORANGE}{Colors.BOLD}An unexpected error occurred: {str(e)}{Colors.END}")
        exit(1)