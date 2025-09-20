# PolicyEdgeAI
<<<<<<< HEAD

A powerful compliance automation platform for analyzing, mapping, and reporting on regulatory frameworks such as NIST 800-53, HIPAA, and more. It includes Zero Trust Architecture mapping, PDF-to-JSON conversion, compliance report generation, and AI-powered compliance guidance.

## Features

- **Document Ingestion**: Parse regulatory PDF documents into structured data
- **Cross-Framework Mapping**: Map controls between different regulatory frameworks
- **Zero Trust Architecture (ZTA) Mapping**: Map compliance controls to ZTA components
- **Compliance Reporting**: Generate detailed HTML and PDF compliance reports
- **LLM-powered Q&A**: Ask natural language questions about compliance requirements
- **Implementation Guidance**: Generate control-specific implementation guidance
- **Gap Analysis**: Identify and analyze gaps in compliance coverage
- **Enterprise Integrations**: Connect to IT management and security tools including:
  - ServiceNow CMDB and SAM Pro
  - Category Management Tools
  - BigFix and CrowdStrike
  - Splunk, Qualys, and Tenable
  - Jamf and Intune
  - Azure Active Directory
  - Axonius
- **Unified Data Taxonomy**: Structured data models for:
  - Assets, financial data, and contracts
  - Regulatory mappings and evidence
  - Compliance scoring and metrics
  - User feedback

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/policyedgeai.git
   cd policyedgeai
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your API keys:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   JWT_SECRET_KEY=your_jwt_secret_key_here
   ```

## Usage

### Running the API Server

```bash
python main.py api --host 0.0.0.0 --port 8000 --reload
```

This starts the API server. Access the interactive API documentation at http://localhost:8000/docs.

### Running the Streamlit Dashboard

```bash
streamlit run streamlit_app.py
```

This starts the Streamlit dashboard. Access it at http://localhost:8501.

### Converting PDF Documents

```bash
# Convert a single PDF file
python main.py convert --input /path/to/nist-800-53.pdf

# Convert all PDFs in a directory
python main.py convert --input /path/to/directory
```

### Working with ZTA Mappings

```bash
# Generate default NIST mappings
python main.py zta --generate-default

# Export mappings to CSV
python main.py zta --export mappings.csv

# Import mappings from CSV
python main.py zta --import mappings.csv
```

## Deployment

The application can be deployed using Docker and AWS ECS. The deployment is fully automated using GitHub Actions.

### Docker Deployment

1. Build the API container:
   ```bash
   docker build -f api.Dockerfile -t policyedgeai-api .
   ```

2. Build the Dashboard container:
   ```bash
   docker build -f dashboard.Dockerfile -t policyedgeai-dashboard .
   ```

3. Run the containers:
   ```bash
   docker run -d -p 8000:8000 --name api policyedgeai-api
   docker run -d -p 8501:8501 --name dashboard policyedgeai-dashboard
   ```

### AWS Deployment

The application can be deployed to AWS using the provided CloudFormation templates.

1. Set up the required AWS resources:
   ```bash
   cd aws
   ./deploy-production.sh
   ```

2. This will create:
   - VPC with public and private subnets
   - ECS Cluster with Fargate tasks
   - Application Load Balancer
   - Route53 DNS records
   - SSL/TLS certificates
   - ECR repositories
   - CloudWatch logs and dashboard
   - Parameter Store secrets
   - S3 bucket for file storage
   - DynamoDB tables for data storage

### CI/CD with GitHub Actions

The repository includes a GitHub Actions workflow for continuous integration and deployment:

1. On pull requests:
   - Run tests and code coverage

2. On merges to main:
   - Build Docker images for API and Dashboard
   - Push images to ECR
   - Deploy to ECS Fargate
   - Verify deployment
   - Create deployment tags

3. Setup requirements:
   - AWS IAM role with permissions for ECR, ECS, and SSM
   - GitHub repository secret: `AWS_ROLE_ARN`
   - (Optional) GitHub repository secret: `SLACK_WEBHOOK_URL` for notifications

## API Endpoints

### PDF Conversion

- `POST /api/convert/pdf`: Convert a regulatory PDF document
- `POST /api/convert/batch`: Batch convert PDFs in a directory

### Zero Trust Architecture Mapping

- `GET /api/zta/components`: Get all ZTA components
- `GET /api/zta/component/{component_id}`: Get a specific ZTA component
- `POST /api/zta/mapping`: Add a new ZTA mapping
- `GET /api/zta/mappings/control/{control_id}`: Get ZTA mappings for a control
- `GET /api/zta/coverage`: Generate ZTA coverage report

### Compliance Reporting

- `POST /api/reports/generate`: Generate a compliance report
- `GET /api/reports/{report_name}`: Download a report
- `GET /api/reports`: List available reports

### Compliance Q&A

- `POST /api/qa/question`: Ask a question about compliance
- `POST /api/qa/implementation`: Generate implementation guidance
- `POST /api/qa/mapping_explanation`: Explain control mapping
- `POST /api/qa/compliance_plan`: Generate compliance plan
- `POST /api/qa/gap_analysis`: Analyze compliance gaps

### Enterprise Integrations

- `GET /api/integrations/list`: List all available integrations
- `GET /api/integrations/cmdb/servicenow`: Get ServiceNow CMDB data
- Various other integration endpoints for different systems

### Dashboard & Taxonomy

- `GET /api/dashboard/assets`: Get asset data with optional filtering
- `GET /api/dashboard/financials`: Get financial data with optional filtering
- `GET /api/dashboard/regulatory`: Get regulatory mapping data with optional filtering
- `GET /api/dashboard/scores`: Get compliance score data with optional filtering
- `GET /api/dashboard/metrics`: Get scoring metric data with optional filtering

### AI & Scoring

- `GET /ai/license-metrics`: Get license metrics data
- `GET /ai/risk-ontology`: Get risk ontology data
- `GET /score/report`: Get compliance scoring report

## Project Structure

```
policyedgeai/
├── api/                     # API endpoints
│   ├── endpoints.py
│   ├── gpt_api.py           # GPT integration endpoints
│   ├── integrations.py      # Enterprise integrations
│   ├── scoring.py           # Scoring endpoints  
│   ├── upload.py            # File upload handling
│   └── dashboard.py         # Dashboard endpoints
├── converter/               # PDF-to-JSON conversion
│   └── pdf_converter.py
├── data/                    # Data storage
│   ├── converted/           # Converted JSON files
│   ├── dashboard/           # Dashboard data
│   ├── integrations/        # Integration configuration
│   ├── reports/             # Generated reports
│   ├── uploads/             # Uploaded PDF files
│   └── zta/                 # ZTA mapping data
├── frontend/                # Web UI
│   ├── static/
│   └── templates/
├── ingest/                  # Document ingestion
│   ├── nist_parser.py
│   └── hipaa_parser.py
├── models/                  # Data models
│   ├── compliance_model.py
│   └── taxonomy.py          # Unified data taxonomy
├── qa_module/               # LLM-powered Q&A
│   ├── __init__.py
│   ├── gpt_qa.py            # GPT integration
│   └── llm_qa.py
├── reporting/               # Report generation
│   └── report_generator.py
├── tests/                   # Unit tests
├── utils/                   # Utility functions
│   ├── __init__.py
│   ├── auth.py              # Authentication utilities
│   └── text_extraction.py
├── zta_mapping/             # Zero Trust mapping
│   └── zta_mapper.py
├── aws/                     # AWS deployment configurations
│   ├── cloudformation.yaml
│   ├── cloudformation-https.yaml
│   ├── cloudformation-production.yaml
│   ├── deploy.sh
│   ├── deploy-https.sh
│   └── deploy-production.sh
├── .github/                 # GitHub Actions workflows
│   └── workflows/
│       └── deploy.yml       # CI/CD workflow
├── api.Dockerfile           # API container configuration
├── dashboard.Dockerfile     # Dashboard container configuration
├── docker-entrypoint.sh     # Docker entrypoint script
├── app.py                   # FastAPI application
├── main.py                  # Application entry point
├── streamlit_app.py         # Streamlit dashboard
├── requirements.txt         # Dependencies
├── setup.sh                 # Setup script
└── README.md                # This file
```

## Requirements

- Python 3.9+
- OpenAI API key for GPT-powered features
- Anthropic API key for Claude-powered features (optional)
- wkhtmltopdf for PDF report generation

## Development

### Running Tests

```bash
pytest
```

### Adding New Features

1. Fork the repository
2. Create a feature branch
3. Add your code
4. Write tests
5. Submit a pull request

## License

[MIT License](LICENSE)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
=======
AI-powered compliance automation engine for Zero Trust, FISMA, GDPR, and enterprise security frameworks. Supports GPT-4 and Claude via API.
# PolicyEdge AI — Compliance Intelligence Automation Engine

**PolicyEdge AI** is a modular, AI-powered backend framework for compliance automation, built with FastAPI and integrated with OpenAI’s GPT-4 and Anthropic’s Claude. It is designed to streamline regulatory analysis, checklist generation, risk mapping, and Zero Trust maturity modeling across U.S. federal, enterprise, and international security frameworks.

This repository contains the **backend engine only**.  
> ⚠️ All proprietary compliance logic, prompt chains, regulatory datasets, and SaaS deployment layers are excluded from this public repository and remain privately licensed intellectual property.

---

## 🔧 Features

- ✅ **/gpt/generate-checklist**: Generate structured compliance checklists (FISMA, GDPR, Zero Trust, etc.)
- ✅ **Multi-provider AI integration**: Choose between GPT-4 and Claude
- ✅ **API-key secured environment** using `.env` config
- ✅ **Modular Core Loop architecture** for extending endpoints (e.g. alerts, risk mapping)
- ✅ **Continuous improvement ready**: Feedback, model comparison, logging (extensible)
- ✅ **Future-ready SaaS toggles** for licensing, authentication, and deployment control
- ✅ Built to integrate with: [NIST 800-53](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final), [FISMA](https://www.congress.gov/bill/113th-congress/house-bill/1163), GDPR, the EU AI Act, and other frameworks

---

## 🚀 Quick Start (Local Development)

```bash
git clone https://github.com/yourusername/policyedgeai.git
cd policyedgeai
pip install -r requirements.txt
touch .env
>>>>>>> 7fc4353ecac751cccf096c4c96e597d66677c5a9
