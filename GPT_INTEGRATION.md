# GPT Integration for PolicyEdgeAI

PolicyEdgeAI now includes powerful GPT capabilities for advanced compliance analysis, guidance, and planning. This document explains how to set up and use the GPT integration.

## Overview

The GPT integration provides enhanced capabilities for:

- Advanced compliance question answering
- Detailed implementation guidance generation
- Provider comparison between OpenAI and Anthropic models
- Comprehensive compliance roadmap generation
- Control documentation templates

## Setup

To use the GPT integration, you need to configure the necessary API keys:

1. **OpenAI API Key** - Required for GPT-4 integration
2. **Anthropic API Key** - Optional for Claude integration

Set these in your environment variables:

```bash
# Required for OpenAI GPT models
export OPENAI_API_KEY="your-openai-api-key"
export OPENAI_MODEL_NAME="gpt-4-turbo"  # Default, can be changed

# Optional for Anthropic Claude models
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export ANTHROPIC_MODEL_NAME="claude-3-opus-20240229"  # Default, can be changed

# Optional for Azure OpenAI
export OPENAI_API_BASE="https://your-azure-endpoint"
```

## API Endpoints

### Check Available Providers

```
GET /gpt/providers
```

Returns information about which LLM providers are available and their configured models.

### Ask a Compliance Question

```
POST /gpt/question
```

**Request Body:**
```json
{
  "question": "What are the key controls for access management in NIST 800-53?",
  "control_ids": ["AC-1", "AC-2"],  // Optional
  "provider": "openai"  // Optional: "openai" or "anthropic"
}
```

### Generate Implementation Guidance

```
POST /gpt/implementation
```

**Request Body:**
```json
{
  "control_id": "AC-1",
  "provider": "openai"  // Optional: "openai" or "anthropic"
}
```

### Compare Provider Responses

```
POST /gpt/compare
```

**Request Body:**
```json
{
  "question": "What is the difference between NIST 800-53 and ISO 27001?",
  "control_ids": [],  // Optional
}
```

### Generate Compliance Roadmap

```
POST /gpt/roadmap
```

**Request Body:**
```json
{
  "framework": "NIST 800-53",
  "organization_size": "medium",
  "industry": "healthcare",
  "timeframe": "12 months",
  "current_maturity": "low",
  "provider": "anthropic"  // Optional: "openai" or "anthropic"
}
```

### Generate Documentation Template

```
POST /gpt/documentation-template
```

**Request Body:**
```json
{
  "control_id": "AC-1",
  "provider": "openai"  // Optional: "openai" or "anthropic"
}
```

## GPT Models vs LLM-QA

PolicyEdgeAI includes two Q&A modules:

1. **Basic LLM-QA** (`/api/qa/*`): Original implementation using OpenAI
2. **Enhanced GPT-QA** (`/gpt/*`): New multi-provider implementation with advanced features

The enhanced GPT integration provides superior results and additional capabilities:

- Multiple provider support (OpenAI and Anthropic)
- Comparative analysis between providers
- Advanced roadmap generation
- Documentation template creation
- More detailed implementation guidance

## Example Code

```python
import requests
import json

API_URL = "http://localhost:8000"
TOKEN = "your-auth-token"  # If using authentication

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# Ask a compliance question using GPT
response = requests.post(
    f"{API_URL}/gpt/question",
    headers=headers,
    json={
        "question": "What are the main requirements for access control in HIPAA?",
        "provider": "openai"
    }
)

print(json.dumps(response.json(), indent=2))
```

## Adding New Capabilities

The GPT integration is designed to be extensible. To add new capabilities:

1. Add new methods to the `GPTComplianceQA` class in `qa_module/gpt_qa.py`
2. Create corresponding API endpoints in `api/gpt_api.py`
3. Update this documentation to reflect the new capabilities

## Performance Considerations

GPT API calls, especially to advanced models like GPT-4 and Claude, can be expensive and have latency. The system includes:

- Response caching to minimize duplicate API calls
- Retry logic for API failures
- Error handling for rate limiting

For production deployments, consider implementing additional caching layers or asynchronous processing for time-intensive operations.