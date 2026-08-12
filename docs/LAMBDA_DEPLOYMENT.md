# AWS Lambda Serverless Deployment Guide

Deploy CareCircle as a fully serverless API on AWS Lambda + API Gateway.

## Architecture

```
Client (Browser/Mobile/API)
        │
        ▼
┌─────────────────────┐
│  Amazon API Gateway  │  (HTTPS endpoint)
│  (HTTP API)          │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   AWS Lambda         │  (CareCircle FastAPI via Mangum)
│   - Risk Assessment  │
│   - Screening Sched  │
│   - Care Plans       │
│   - Education        │
│   - Notifications    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Amazon Bedrock      │  (Claude - for AI chat)
│  (Optional)          │
└─────────────────────┘
```

## Prerequisites

1. **AWS Account** with appropriate permissions
2. **AWS CLI** installed and configured (`aws configure`)
3. **AWS SAM CLI** installed (`pip install aws-sam-cli`)
4. **Python 3.11+**

## Deployment Steps

### Option 1: SAM CLI (Recommended)

```bash
# 1. Build the Lambda package
sam build

# 2. Deploy (first time - guided mode)
sam deploy --guided

# 3. Subsequent deploys
sam deploy
```

During guided deployment, you'll be asked:
- **Stack Name**: `carecircle-serverless`
- **Region**: `us-east-1` (or your preferred region)
- **Confirm changeset**: Yes
- **Allow SAM CLI IAM role creation**: Yes

### Option 2: Using the deploy script

```bash
# Linux/Mac
chmod +x deploy/lambda_deploy.sh
./deploy/lambda_deploy.sh

# Windows
deploy\lambda_deploy.bat
```

### Option 3: Manual CloudFormation

```bash
aws cloudformation deploy \
  --template-file template.yaml \
  --stack-name carecircle-serverless \
  --capabilities CAPABILITY_IAM \
  --region us-east-1
```

## After Deployment

Once deployed, you'll get an API Gateway URL like:
```
https://abc123def.execute-api.us-east-1.amazonaws.com/prod/
```

### Test your deployment:

```bash
# Health check
curl https://YOUR_API_URL/health

# Risk Assessment
curl -X POST https://YOUR_API_URL/api/risk-assessment \
  -H "Content-Type: application/json" \
  -d '{
    "age": 52,
    "family_history": true,
    "breast_density": "heterogeneous",
    "bmi": 27.5
  }'

# Get education content
curl https://YOUR_API_URL/api/education/mammogram_overview

# Interactive docs
# Open in browser: https://YOUR_API_URL/docs
```

## Configuration

### Environment Variables (set in Lambda console or template.yaml)

| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_REGION_NAME` | AWS region for Bedrock | us-east-1 |
| `BEDROCK_MODEL_ID` | Bedrock model ID | us.anthropic.claude-sonnet-4-20250514 |

### IAM Permissions Required

The SAM template automatically creates an IAM role with:
- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`

## Costs

With AWS Lambda free tier:
- **1 million** free requests per month
- **400,000 GB-seconds** of compute per month
- API Gateway: **1 million** HTTP API calls free per month

For typical usage (1000 risk assessments/day), estimated cost: **< $5/month**

## Updating

Push changes to GitHub, then:
```bash
sam build && sam deploy
```

## Removing

```bash
sam delete --stack-name carecircle-serverless
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| SAM build fails | Ensure Python 3.11 is available |
| Deploy permission error | Run `aws configure` with appropriate credentials |
| Lambda timeout | Increase `Timeout` in template.yaml (default: 30s) |
| Import errors | Check that all dependencies are in lambda_app/requirements.txt |
