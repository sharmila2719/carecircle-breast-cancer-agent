#!/bin/bash
# CareCircle Deployment Script
# Deploys the application to AWS using CloudFormation + ECS

set -e

ENVIRONMENT=${1:-development}
REGION=${AWS_REGION:-us-east-1}
STACK_NAME="carecircle-${ENVIRONMENT}"

echo "🩺 Deploying CareCircle - ${ENVIRONMENT}"
echo "Region: ${REGION}"

# Deploy CloudFormation stack
echo "📦 Deploying infrastructure..."
aws cloudformation deploy \
  --template-file deploy/cloudformation.yaml \
  --stack-name ${STACK_NAME} \
  --parameter-overrides Environment=${ENVIRONMENT} \
  --capabilities CAPABILITY_NAMED_IAM \
  --region ${REGION}

echo "✅ Infrastructure deployed successfully!"
echo ""
echo "Next steps:"
echo "  1. Build Docker image: docker build -t carecircle ."
echo "  2. Push to ECR"
echo "  3. Update ECS task definition"
echo ""
echo "🩺 CareCircle deployment complete!"
