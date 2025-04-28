# Cloud Bucket Creator

https://github.com/humanlayer/12-factor-agents/blob/main/content/factor-1-natural-language-to-tool-calls.md

Create a tool that uses natural language processing to create storage buckets in different cloud providers (AWS S3 or Google Cloud Storage) based on simple text requests.

## Features

- Create AWS S3 buckets with natural language commands
- Create Google Cloud Storage buckets with natural language commands
- Configurable defaults via PROJECT.md
- Color-coded terminal interface (color-blind friendly)
- Confirms command execution before running

## Requirements

- Python 3.6+
- Anthropic API key (set as environment variable)
- AWS CLI (for AWS S3 buckets)
- Google Cloud SDK (for GCP buckets)

## Installation

1. Clone this repository
2. Set your Anthropic API key:
   ```
   export ANTHROPIC_API_KEY=your_api_key_here
   ```
3. Make sure you have the appropriate cloud CLI tools configured for your providers

## Usage

Run the script:
```
./cloud_bucket_creator.py
```

Then enter your request in natural language:
```
Create a bucket named logs-archive in us-west-2
```

The script will:
1. Parse your request using Claude
2. Show you the exact command that will be executed
3. Ask for confirmation before running
4. Execute the command and show the result

## Configuration

The application uses `PROJECT.md` to store configuration defaults. This file is read every time the script runs, so you can modify it to change the defaults without editing code.

Example configuration:
```markdown
# Cloud Bucket Configuration

## Cloud Provider Settings

### Default Provider
- provider: AWS

## Bucket Settings

### Global Settings
- prefix: app-vitals-

### AWS S3 Settings
- region: us-east-1

### Google Cloud Storage Settings
- region: us-east2
```

## Examples

- "Create an S3 bucket named user-uploads"
- "Make a GCS bucket called analytics-data in us-central1"
- "Create a bucket for storing log files in the asia region"
