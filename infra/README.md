# WaterForAll CV Infrastructure

AWS CDK (Python) stacks for the Computer Vision module.

## Stacks

| Stack | Resources |
|---|---|
| WaterForAllS3Stack | S3 bucket (encrypted, no public access, 30-day raw/ lifecycle) |
| WaterForAllDatabaseStack | RDS PostgreSQL 16 t3.micro + Secrets Manager credential |
| WaterForAllComputeStack | Lambda container image (ECR), IAM role, S3 event trigger |
| WaterForAllApiStack | API Gateway HTTP API — /cv/upload-url, /cv/process, /cv/results/{id} |

## Prerequisites

- AWS CLI configured (`aws configure`)
- Docker running (needed to build Lambda container image)
- CDK CLI: `npm install -g aws-cdk`
- Python 3.11+

## Setup

```bash
cd infra
python -m venv .venv
.venv/Scripts/activate     # Windows
pip install -r requirements.txt
```

## Deploy

```bash
# Set environment variables (copy from ../.env.example)
set CDK_DEFAULT_ACCOUNT=123456789012
set CDK_DEFAULT_REGION=ap-southeast-1

# Bootstrap CDK (first time only per account/region)
cdk bootstrap

# Deploy all stacks
cdk deploy --all --require-approval never
```

## Destroy (hackathon cleanup)

```bash
cdk destroy --all
```

## Database initialisation

After the DatabaseStack is deployed, run the schema migration once:

```bash
# Get the DB endpoint from the CDK output or AWS console
# Then connect and run:
psql -h <db-endpoint> -U cvadmin -d waterforall_cv -f sql/init.sql
```

The database password is stored in AWS Secrets Manager (see CDK output `DbSecretArn`).

## Tags on all resources

```
Project:    WaterForAll
Component:  ComputerVision
Environment: dev
Owner:      Member2
```

## Notes

- No public S3 access. Images are fetched by Lambda via IAM role only.
- No personal data stored by default. Location fields must be consent-based (handled by the agent layer).
- RDS is single-AZ with no backup retention to minimise hackathon cost.
- Lambda memory: 1024 MB, timeout: 30s.
