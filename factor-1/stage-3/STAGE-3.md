```python
    # dan's hack
    class AWSRegion(str, Enum):
        # US Regions
        US_EAST_1 = "us-east-1"       # N. Virginia
        US_EAST_2 = "us-east-2"       # Ohio
        US_WEST_1 = "us-west-1"       # N. California
        US_WEST_2 = "us-west-2"       # Oregon
    class CreateS3Bucket(BaseModel):
        bucket: str = Field(..., description="S3Uri of bucket to create")
        region: Optional[AWSRegion] = Field(None, description="AWS region for the bucket")
        profile: Optional[str] = Field(None, description="AWS profile to use")

    tools = [
        {
            "input_schema": CreateS3Bucket.model_json_schema(),
            "name": "create_bucket_tool",
            "description": "A tool to create cloud storage buckets.",
        }
    ]
    
    message = client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=1000,
        temperature=0,
        system=system_prompt,
        messages=[
            {"role": "user", "content": user_input}
        ],
        tools=tools,
    )
```
```python
# claude's hack
from typing import Dict, List, Optional, Union, Any, Literal
import json
import subprocess
from enum import Enum
from pydantic import BaseModel, Field

# Define AWS regions as enum
class AWSRegion(str, Enum):
    # US Regions
    US_EAST_1 = "us-east-1"       # N. Virginia
    US_EAST_2 = "us-east-2"       # Ohio
    US_WEST_1 = "us-west-1"       # N. California
    US_WEST_2 = "us-west-2"       # Oregon
    
    # Canada Regions
    CA_CENTRAL_1 = "ca-central-1" # Canada Central
    
    # South America Regions
    SA_EAST_1 = "sa-east-1"       # São Paulo
    
    # Europe Regions
    EU_WEST_1 = "eu-west-1"       # Ireland
    EU_WEST_2 = "eu-west-2"       # London
    EU_WEST_3 = "eu-west-3"       # Paris
    EU_CENTRAL_1 = "eu-central-1" # Frankfurt
    EU_NORTH_1 = "eu-north-1"     # Stockholm
    EU_SOUTH_1 = "eu-south-1"     # Milan
    
    # Asia Pacific Regions
    AP_EAST_1 = "ap-east-1"       # Hong Kong
    AP_SOUTH_1 = "ap-south-1"     # Mumbai
    AP_NORTHEAST_1 = "ap-northeast-1" # Tokyo
    AP_NORTHEAST_2 = "ap-northeast-2" # Seoul
    AP_NORTHEAST_3 = "ap-northeast-3" # Osaka
    AP_SOUTHEAST_1 = "ap-southeast-1" # Singapore
    AP_SOUTHEAST_2 = "ap-southeast-2" # Sydney
    
    # Middle East Regions
    ME_SOUTH_1 = "me-south-1"     # Bahrain
    
    # Africa Regions
    AF_SOUTH_1 = "af-south-1"     # Cape Town

class S3ACL(str, Enum):
    PRIVATE = "private"
    PUBLIC_READ = "public-read"
    PUBLIC_READ_WRITE = "public-read-write"
    AUTHENTICATED_READ = "authenticated-read"
    AWS_EXEC_READ = "aws-exec-read"
    BUCKET_OWNER_READ = "bucket-owner-read"
    BUCKET_OWNER_FULL_CONTROL = "bucket-owner-full-control"
    LOG_DELIVERY_WRITE = "log-delivery-write"

class S3StorageClass(str, Enum):
    STANDARD = "STANDARD"
    REDUCED_REDUNDANCY = "REDUCED_REDUNDANCY"
    STANDARD_IA = "STANDARD_IA"
    ONEZONE_IA = "ONEZONE_IA"
    INTELLIGENT_TIERING = "INTELLIGENT_TIERING"
    GLACIER = "GLACIER"
    DEEP_ARCHIVE = "DEEP_ARCHIVE"
    GLACIER_IR = "GLACIER_IR"

class S3SSE(str, Enum):
    AES256 = "AES256"
    AWS_KMS = "aws:kms"

# Define parameter types for each command
class S3ListParams(BaseModel):
    path: Optional[str] = Field(None, description="S3Uri or empty to list buckets")
    recursive: Optional[bool] = Field(None, description="List all objects recursively")
    human_readable: Optional[bool] = Field(None, description="Display sizes in human-readable format")
    summarize: Optional[bool] = Field(None, description="Show total objects/size")
    bucket_name_prefix: Optional[str] = Field(None, description="Filter buckets by name prefix")
    bucket_region: Optional[AWSRegion] = Field(None, description="Filter buckets by region")
    profile: Optional[str] = Field(None, description="AWS profile to use")
    region: Optional[AWSRegion] = Field(None, description="AWS region", default=AWSRegion.US_WEST_1)

class S3CreateBucketParams(BaseModel):
    bucket: str = Field(..., description="S3Uri of bucket to create")
    region: Optional[AWSRegion] = Field(None, description="AWS region for the bucket")
    profile: Optional[str] = Field(None, description="AWS profile to use")

class S3DeleteBucketParams(BaseModel):
    bucket: str = Field(..., description="S3Uri of bucket to delete")
    force: Optional[bool] = Field(None, description="Remove all contents before deleting bucket")
    profile: Optional[str] = Field(None, description="AWS profile to use")
    region: Optional[AWSRegion] = Field(None, description="AWS region")

class S3CopyParams(BaseModel):
    source: str = Field(..., description="Source path (local path or S3Uri)")
    destination: str = Field(..., description="Destination path (local path or S3Uri)")
    recursive: Optional[bool] = Field(None, description="Copy directories/prefixes recursively")
    acl: Optional[S3ACL] = Field(None, description="Set permissions (private, public-read, etc.)")
    sse: Optional[S3SSE] = Field(None, description="Server-side encryption (AES256, aws:kms)")
    storage_class: Optional[S3StorageClass] = Field(None, description="Storage tier (STANDARD, GLACIER, etc.)")
    include: Optional[str] = Field(None, description="Include files matching pattern")
    exclude: Optional[str] = Field(None, description="Exclude files matching pattern")
    metadata: Optional[Dict[str, str]] = Field(None, description="Metadata key-value pairs")
    grants: Optional[str] = Field(None, description="Grant permissions to specific users/groups")
    profile: Optional[str] = Field(None, description="AWS profile to use")
    region: Optional[AWSRegion] = Field(None, description="AWS region")

class S3MoveParams(BaseModel):
    source: str = Field(..., description="Source path (local path or S3Uri)")
    destination: str = Field(..., description="Destination path (local path or S3Uri)")
    recursive: Optional[bool] = Field(None, description="Move directories/prefixes recursively")
    acl: Optional[S3ACL] = Field(None, description="Set permissions (private, public-read, etc.)")
    sse: Optional[S3SSE] = Field(None, description="Server-side encryption (AES256, aws:kms)")
    storage_class: Optional[S3StorageClass] = Field(None, description="Storage tier (STANDARD, GLACIER, etc.)")
    include: Optional[str] = Field(None, description="Include files matching pattern")
    exclude: Optional[str] = Field(None, description="Exclude files matching pattern")
    metadata: Optional[Dict[str, str]] = Field(None, description="Metadata key-value pairs")
    grants: Optional[str] = Field(None, description="Grant permissions to specific users/groups")
    validate_same_s3_paths: Optional[bool] = Field(None, description="Prevent accidental deletion")
    profile: Optional[str] = Field(None, description="AWS profile to use")
    region: Optional[AWSRegion] = Field(None, description="AWS region")

class S3RemoveParams(BaseModel):
    path: str = Field(..., description="S3Uri of object to delete")
    recursive: Optional[bool] = Field(None, description="Remove directories/prefixes recursively")
    include: Optional[str] = Field(None, description="Include files matching pattern")
    exclude: Optional[str] = Field(None, description="Exclude files matching pattern")
    dryrun: Optional[bool] = Field(None, description="Show what would be deleted without deleting")
    profile: Optional[str] = Field(None, description="AWS profile to use")
    region: Optional[AWSRegion] = Field(None, description="AWS region")

class S3SyncParams(BaseModel):
    source: str = Field(..., description="Source path (local path or S3Uri)")
    destination: str = Field(..., description="Destination path (local path or S3Uri)")
    delete: Optional[bool] = Field(None, description="Remove files in destination not in source")
    size_only: Optional[bool] = Field(None, description="Compare by size only, not timestamp")
    exact_timestamps: Optional[bool] = Field(None, description="Use exact timestamp comparison")
    include: Optional[str] = Field(None, description="Include files matching pattern")
    exclude: Optional[str] = Field(None, description="Exclude files matching pattern")
    acl: Optional[S3ACL] = Field(None, description="Set permissions (private, public-read, etc.)")
    sse: Optional[S3SSE] = Field(None, description="Server-side encryption (AES256, aws:kms)")
    storage_class: Optional[S3StorageClass] = Field(None, description="Storage tier (STANDARD, GLACIER, etc.)")
    source_region: Optional[AWSRegion] = Field(None, description="Region of source bucket")
    profile: Optional[str] = Field(None, description="AWS profile to use")
    region: Optional[AWSRegion] = Field(None, description="AWS region")

class S3PresignParams(BaseModel):
    path: str = Field(..., description="S3Uri of object to create URL for")
    expires_in: Optional[int] = Field(None, description="URL validity in seconds (default: 3600, max: 604800)")
    profile: Optional[str] = Field(None, description="AWS profile to use")
    region: Optional[AWSRegion] = Field(None, description="AWS region")

class S3WebsiteParams(BaseModel):
    bucket: str = Field(..., description="S3Uri of bucket to configure")
    index_document: Optional[str] = Field(None, description="Default page (e.g., index.html)")
    error_document: Optional[str] = Field(None, description="Error page for 4XX errors")
    profile: Optional[str] = Field(None, description="AWS profile to use")
    region: Optional[AWSRegion] = Field(None, description="AWS region")

# Tool implementations
def s3_list_buckets(params: S3ListParams) -> Dict[str, Any]:
    cmd = ["aws", "s3", "ls"]
    
    if params.path:
        cmd.append(params.path)
    
    if params.recursive:
        cmd.append("--recursive")
    if params.human_readable:
        cmd.append("--human-readable")
    if params.summarize:
        cmd.append("--summarize")
    if params.bucket_name_prefix:
        cmd.extend(["--bucket-name-prefix", params.bucket_name_prefix])
    if params.bucket_region:
        cmd.extend(["--bucket-region", params.bucket_region.value])
    if params.profile:
        cmd.extend(["--profile", params.profile])
    if params.region:
        cmd.extend(["--region", params.region.value])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"output": result.stdout, "status": "success"}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr, "status": "error", "error_code": e.returncode}

def s3_create_bucket(params: S3CreateBucketParams) -> Dict[str, Any]:
    cmd = ["aws", "s3", "mb", params.bucket]
    
    if params.region:
        cmd.extend(["--region", params.region.value])
    if params.profile:
        cmd.extend(["--profile", params.profile])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"output": result.stdout, "status": "success"}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr, "status": "error", "error_code": e.returncode}

def s3_delete_bucket(params: S3DeleteBucketParams) -> Dict[str, Any]:
    cmd = ["aws", "s3", "rb", params.bucket]
    
    if params.force:
        cmd.append("--force")
    if params.profile:
        cmd.extend(["--profile", params.profile])
    if params.region:
        cmd.extend(["--region", params.region.value])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"output": result.stdout, "status": "success"}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr, "status": "error", "error_code": e.returncode}

def s3_copy(params: S3CopyParams) -> Dict[str, Any]:
    cmd = ["aws", "s3", "cp", params.source, params.destination]
    
    if params.recursive:
        cmd.append("--recursive")
    if params.acl:
        cmd.extend(["--acl", params.acl.value])
    if params.sse:
        cmd.extend(["--sse", params.sse.value])
    if params.storage_class:
        cmd.extend(["--storage-class", params.storage_class.value])
    if params.include:
        cmd.extend(["--include", params.include])
    if params.exclude:
        cmd.extend(["--exclude", params.exclude])
    if params.metadata:
        metadata_str = ",".join([f"{k}={v}" for k, v in params.metadata.items()])
        cmd.extend(["--metadata", metadata_str])
    if params.grants:
        cmd.extend(["--grants", params.grants])
    if params.profile:
        cmd.extend(["--profile", params.profile])
    if params.region:
        cmd.extend(["--region", params.region.value])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"output": result.stdout, "status": "success"}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr, "status": "error", "error_code": e.returncode}

def s3_move(params: S3MoveParams) -> Dict[str, Any]:
    cmd = ["aws", "s3", "mv", params.source, params.destination]
    
    if params.recursive:
        cmd.append("--recursive")
    if params.acl:
        cmd.extend(["--acl", params.acl.value])
    if params.sse:
        cmd.extend(["--sse", params.sse.value])
    if params.storage_class:
        cmd.extend(["--storage-class", params.storage_class.value])
    if params.include:
        cmd.extend(["--include", params.include])
    if params.exclude:
        cmd.extend(["--exclude", params.exclude])
    if params.metadata:
        metadata_str = ",".join([f"{k}={v}" for k, v in params.metadata.items()])
        cmd.extend(["--metadata", metadata_str])
    if params.grants:
        cmd.extend(["--grants", params.grants])
    if params.validate_same_s3_paths:
        cmd.append("--validate-same-s3-paths")
    if params.profile:
        cmd.extend(["--profile", params.profile])
    if params.region:
        cmd.extend(["--region", params.region.value])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"output": result.stdout, "status": "success"}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr, "status": "error", "error_code": e.returncode}

def s3_remove(params: S3RemoveParams) -> Dict[str, Any]:
    cmd = ["aws", "s3", "rm", params.path]
    
    if params.recursive:
        cmd.append("--recursive")
    if params.include:
        cmd.extend(["--include", params.include])
    if params.exclude:
        cmd.extend(["--exclude", params.exclude])
    if params.dryrun:
        cmd.append("--dryrun")
    if params.profile:
        cmd.extend(["--profile", params.profile])
    if params.region:
        cmd.extend(["--region", params.region.value])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"output": result.stdout, "status": "success"}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr, "status": "error", "error_code": e.returncode}

def s3_sync(params: S3SyncParams) -> Dict[str, Any]:
    cmd = ["aws", "s3", "sync", params.source, params.destination]
    
    if params.delete:
        cmd.append("--delete")
    if params.size_only:
        cmd.append("--size-only")
    if params.exact_timestamps:
        cmd.append("--exact-timestamps")
    if params.include:
        cmd.extend(["--include", params.include])
    if params.exclude:
        cmd.extend(["--exclude", params.exclude])
    if params.acl:
        cmd.extend(["--acl", params.acl.value])
    if params.sse:
        cmd.extend(["--sse", params.sse.value])
    if params.storage_class:
        cmd.extend(["--storage-class", params.storage_class.value])
    if params.source_region:
        cmd.extend(["--source-region", params.source_region.value])
    if params.profile:
        cmd.extend(["--profile", params.profile])
    if params.region:
        cmd.extend(["--region", params.region.value])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"output": result.stdout, "status": "success"}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr, "status": "error", "error_code": e.returncode}

def s3_presign(params: S3PresignParams) -> Dict[str, Any]:
    cmd = ["aws", "s3", "presign", params.path]
    
    if params.expires_in:
        cmd.extend(["--expires-in", str(params.expires_in)])
    if params.profile:
        cmd.extend(["--profile", params.profile])
    if params.region:
        cmd.extend(["--region", params.region.value])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"output": result.stdout, "status": "success"}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr, "status": "error", "error_code": e.returncode}

def s3_website(params: S3WebsiteParams) -> Dict[str, Any]:
    cmd = ["aws", "s3", "website", params.bucket]
    
    if params.index_document:
        cmd.extend(["--index-document", params.index_document])
    if params.error_document:
        cmd.extend(["--error-document", params.error_document])
    if params.profile:
        cmd.extend(["--profile", params.profile])
    if params.region:
        cmd.extend(["--region", params.region.value])
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return {"output": result.stdout, "status": "success"}
    except subprocess.CalledProcessError as e:
        return {"output": e.stderr, "status": "error", "error_code": e.returncode}

# Register the tools for LLM to use
tools = {
    "s3_list_buckets": {
        "function": s3_list_buckets,
        "description": "Lists all S3 buckets or objects in a specific bucket",
        "schema": S3ListParams.schema()
    },
    "s3_create_bucket": {
        "function": s3_create_bucket,
        "description": "Creates a new S3 bucket",
        "schema": S3CreateBucketParams.schema()
    },
    "s3_delete_bucket": {
        "function": s3_delete_bucket,
        "description": "Deletes an S3 bucket",
        "schema": S3DeleteBucketParams.schema()
    },
    "s3_copy": {
        "function": s3_copy,
        "description": "Copies files between local filesystem and S3, or within S3",
        "schema": S3CopyParams.schema()
    },
    "s3_move": {
        "function": s3_move,
        "description": "Moves files between local filesystem and S3, or within S3",
        "schema": S3MoveParams.schema()
    },
    "s3_remove": {
        "function": s3_remove,
        "description": "Deletes objects from S3",
        "schema": S3RemoveParams.schema()
    },
    "s3_sync": {
        "function": s3_sync,
        "description": "Syncs directories between local filesystem and S3, or within S3",
        "schema": S3SyncParams.schema()
    },
    "s3_presign": {
        "function": s3_presign,
        "description": "Generates a pre-signed URL for an S3 object",
        "schema": S3PresignParams.schema()
    },
    "s3_website": {
        "function": s3_website,
        "description": "Configures an S3 bucket for static website hosting",
        "schema": S3WebsiteParams.schema()
    }
}

# Example of wiring up to LLM prompt
def format_tools_for_llm():
    """Convert tool definitions to format usable in LLM system prompt"""
    tool_descriptions = []
    
    for tool_name, tool_info in tools.items():
        schema = tool_info["schema"]
        params = []
        
        for prop_name, prop_info in schema.get("properties", {}).items():
            required = prop_name in schema.get("required", [])
            
            # Handle enum types specially
            if prop_info.get("enum"):
                enum_values = prop_info.get("enum", [])
                param = {
                    "name": prop_name,
                    "type": "enum",
                    "description": prop_info.get("description", ""),
                    "required": required,
                    "enum_values": enum_values
                }
            else:
                param = {
                    "name": prop_name,
                    "type": prop_info.get("type", "string"),
                    "description": prop_info.get("description", ""),
                    "required": required
                }
            params.append(param)
        
        tool_descriptions.append({
            "name": tool_name,
            "description": tool_info["description"],
            "parameters": params
        })
    
    return json.dumps(tool_descriptions, indent=2)

def create_prompt(user_input):
    """Create a prompt for the LLM with tool definitions"""
    system_prompt = f"""
    You are an expert devops engineer configuring AWS S3 buckets. You have access to the following tools:
    
    When you need to use a tool, use the following format:
    
    <tool_call>
    <tool_name>TOOL_NAME</tool_name>
    <parameters>
    <parameter name="PARAM_NAME">PARAM_VALUE</parameter>
    ...
    </parameters>
    </tool_call>
    
    For parameters of type enum, use one of the allowed values. For example, AWS regions must be one of the standard AWS region codes like "us-east-1", "eu-west-2", etc.
    
    Analyze the user's request and respond with the appropriate S3 tool calls to complete the task.
    """
    
    return {
        "system": system_prompt,
        "user": user_input
    }

# Example of processing LLM response to execute tools
def process_llm_response(llm_response):
    """Process LLM response and execute any tool calls found"""
    # This is a simplified parser - a more robust implementation would be needed
    # to handle nested structures and edge cases
    results = []
    
    # Simple regex-based extraction could be used here
    # For simplicity, assuming a structured format like:
    # <tool_call>
    # <tool_name>s3_list_buckets</tool_name>
    # <parameters>
    # <parameter name="recursive">true</parameter>
    # </parameters>
    # </tool_call>
    
    import re
    tool_call_pattern = r'<tool_call>(.*?)</tool_call>'
    tool_calls = re.findall(tool_call_pattern, llm_response, re.DOTALL)
    
    for tool_call in tool_calls:
        # Extract tool name
        tool_name_match = re.search(r'<tool_name>(.*?)</tool_name>', tool_call, re.DOTALL)
        if not tool_name_match:
            continue
        
        tool_name = tool_name_match.group(1).strip()
        if tool_name not in tools:
            results.append(f"Unknown tool: {tool_name}")
            continue
        
        # Extract parameters
        params = {}
        param_pattern = r'<parameter name="([^"]+)">(.*?)</parameter>'
        param_matches = re.findall(param_pattern, tool_call, re.DOTALL)
        
        for param_name, param_value in param_matches:
            # Convert param value to the right type based on schema
            schema = tools[tool_name]["schema"]
            prop_info = schema.get("properties", {}).get(param_name, {})
            prop_type = prop_info.get("type", "string")
            
            if prop_type == "boolean":
                params[param_name] = param_value.lower() == "true"
            elif prop_type == "integer":
                params[param_name] = int(param_value)
            elif prop_type == "object":
                try:
                    params[param_name] = json.loads(param_value)
                except:
                    params[param_name] = param_value
            # Handle enums
            elif "enum" in prop_info:
                params[param_name] = param_value  # Enum validation happens in the Pydantic model
            else:
                params[param_name] = param_value
        
        # Execute the tool with parameters
        try:
            param_model = eval(f"{tool_name.capitalize()}Params")(**params)
            result = tools[tool_name]["function"](param_model)
            results.append({
                "tool": tool_name,
                "parameters": params,
                "result": result
            })
        except Exception as e:
            results.append({
                "tool": tool_name,
                "parameters": params,
                "error": str(e)
            })
    
    return results

# Example usage:
if __name__ == "__main__":
    user_input = "Please list all my S3 buckets and show me the contents of bucket-example in us-east-1 if it exists"
    
    # 1. Create prompt for LLM
    prompt = create_prompt(user_input)
    
    # 2. Send prompt to LLM (not implemented here)
    # llm_response = call_llm_api(prompt, tools=tools_for_llm())
    
    # Simulated LLM response for demonstration
    llm_response = """
    I'll help you list your S3 buckets and show the contents of bucket-example in us-east-1 if it exists.
    
    First, let's list all your S3 buckets:
    
    <tool_call>
    <tool_name>s3_list_buckets</tool_name>
    <parameters>
    </parameters>
    </tool_call>
    
    Now, let's check if the bucket-example exists in the results. If it does, I'll show its contents:
    
    <tool_call>
    <tool_name>s3_list_buckets</tool_name>
    <parameters>
    <parameter name="path">s3://bucket-example/</parameter>
    <parameter name="recursive">true</parameter>
    <parameter name="human_readable">true</parameter>
    <parameter name="region">us-east-1</parameter>
    </parameters>
    </tool_call>
    """
    
    # 3. Process LLM response and execute tools
    results = process_llm_response(llm_response)
    
    # 4. Use the results to create a response for the user
    print(json.dumps(results, indent=2))
```

