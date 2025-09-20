# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Lint/Test Commands

- **Run API server**: `python main.py api --reload`
- **Run with specific host/port**: `python main.py api --host 0.0.0.0 --port 8080 --reload`
- **Convert PDF file**: `python main.py convert --input /path/to/file.pdf`
- **Work with ZTA mappings**: `python main.py zta --generate-default`
- **Run tests**: `pytest`
- **Install dependencies**: `pip install -r requirements.txt`
- **Format code**: `black .`
- **Lint**: `flake8 .`
- **Type checking**: `mypy .`
- **Configure integrations**: Edit `.env` file based on `.env.example` template

## Code Style Guidelines

- **Imports**: Group standard library imports first, followed by third-party imports, then local imports
- **Formatting**: Follow PEP 8 standards
- **Typing**: Use type hints for function parameters and return values
- **Naming**:
  - Use snake_case for variables and functions
  - Use PascalCase for classes
  - Use UPPER_CASE for constants
- **Error handling**: Use try/except blocks with specific exceptions
- **Comments**: Document function purpose with docstrings
- **API Patterns**: Follow FastAPI RESTful conventions
- **Security**: Never commit API keys or credentials

## Project Structure

PolicyEdgeAI is a compliance automation platform with PDF-to-JSON conversion, Zero Trust mapping, compliance reporting, LLM-powered Q&A capabilities, and enterprise integrations. The codebase is organized into modules based on functionality, with a FastAPI interface and command-line tools.

## Integration Notes

The application supports integration with numerous enterprise IT and security tools:
- ServiceNow CMDB and SAM Pro for asset and software management
- Category Management Tools for federal procurement
- Security tools like BigFix, CrowdStrike, Splunk, Qualys, and Tenable
- Device management tools like Jamf and Intune
- Identity management via Azure AD
- Asset consolidation through Axonius

Integration configurations are loaded from environment variables or a JSON configuration file.

## Data Taxonomy

The platform uses a unified data taxonomy that connects:
- Asset data (hardware, software, network devices)
- Financial information (costs, vendors, licensing)
- Contract details (terms, renewals, expirations)
- Regulatory mappings (controls to assets, with evidence)
- Compliance scoring (metrics, calculations, trends)
- User feedback (feature satisfaction, improvement ideas)

This taxonomy powers the dashboard and provides a consistent data model for APIs.