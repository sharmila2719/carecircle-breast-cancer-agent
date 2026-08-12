#!/bin/bash
# CareCircle - AWS Lambda Serverless Deployment Script
# Prerequisites: AWS SAM CLI installed, AWS credentials configured

set -e

echo "🩺 CareCircle - Serverless Lambda Deployment"
echo "=============================================="

# Check prerequisites
if ! command -v sam &> /dev/null; then
    echo "❌ AWS SAM CLI not found. Install it:"
    echo "   pip install aws-sam-cli"
    echo "   OR"
    echo "   https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html"
    exit 1
fi

if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Install it:"
    echo "   https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html"
    exit 1
fi

echo ""
echo "📦 Step 1: Building Lambda package..."
sam build

echo ""
echo "🚀 Step 2: Deploying to AWS..."
sam deploy --guided

echo ""
echo "=============================================="
echo "✅ Deployment complete!"
echo ""
echo "Your API is now live at the URL shown above."
echo "Try these endpoints:"
echo "  GET  /          - API info"
echo "  GET  /health    - Health check"
echo "  GET  /docs      - Interactive API documentation"
echo "  POST /api/risk-assessment  - Risk assessment"
echo "  POST /api/screening/schedule  - Schedule screening"
echo "  POST /api/care-plan/generate  - Generate care plan"
echo "  GET  /api/education/{topic}   - Educational content"
echo ""
