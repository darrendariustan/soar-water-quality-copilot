# Handover — WaterForAll CV Backend (Member 2)

**Date:** 2026-06-09  
**Owner:** Barry (Member 2 — Computer Vision & Test Kit Engineer)  
**Repo:** `darrendariustan/soar-water-quality-copilot`  
**Branch:** your working branch (not `main`)

---

## What Is Built

The entire CV backend is complete and deployed. It handles water quality test kit image analysis via three pipelines:

| Kit Type | Processor |
|---|---|
| Generic 16-in-1 test strip | `src/cv/engine.py` + `src/cv/aws_provider.py` |
| Heavy metals strip | `src/cv/heavy_metals_processor.py` |
| TDS meter (digital display) | `src/cv/tds_processor.py` |

All three routes through `src/cv/submission_handler.py` → `process_submission()`.

---

## File Map

```
backend/
├── src/
│   ├── main.py                        # FastAPI app + all endpoints
│   ├── db.py                          # DynamoDB read/write
│   ├── lambda_handler.py              # AWS Lambda entrypoint (S3 event → CV → DynamoDB)
│   ├── cv/
│   │   ├── models.py                  # Pydantic schemas (StripAnalysisResult, TDSResult, etc.)
│   │   ├── engine.py                  # OpenCV local strip analyser
│   │   ├── aws_provider.py            # Bedrock Claude Haiku strip + water sample analyser
│   │   ├── classifier.py              # Water sample classifier (local OpenCV)
│   │   ├── kit_classifier.py          # Kit type classifier (local heuristic + Bedrock)
│   │   ├── tds_processor.py           # TDS meter OCR (local=manual_review, aws=Bedrock)
│   │   ├── heavy_metals_processor.py  # Heavy metals strip (wraps engine.py)
│   │   ├── submission_handler.py      # Orchestrates multi-image submissions
│   │   └── reference_charts/
│   │       ├── generic_16_in_1.json   # Colour chart for 16-in-1 strips
│   │       ├── heavy_metals_strip.json
│   │       └── tds_thresholds.json    # TDS risk thresholds (WHO/EPA)
│   └── static/
│       └── index.html                 # Web UI (3 tabs: Submission, Test Strip, Water Sample)
├── tests/cv/                          # 73 passing tests
├── Dockerfile                         # Multi-stage Lambda container image
├── .env                               # Real AWS creds — DO NOT COMMIT
└── .env.example                       # Template for other devs
```

---

## AWS Infrastructure (all manual — CDK/CloudFormation is SCP-blocked)

| Resource | Name / ARN |
|---|---|
| S3 bucket | `waterforall-dev-cv-images` (us-east-1) |
| DynamoDB table | `waterforall-cv-submissions` (us-east-1, PK: `submission_id`) |
| ECR repository | `986682844768.dkr.ecr.us-east-1.amazonaws.com/waterforall-cv` |
| Lambda function | `waterforall-cv-processor` (us-east-1, 1024 MB, 30s timeout) |
| Lambda image tag | `:linux-amd64` (single-arch OCI — `:latest` is multi-arch and won't work with Lambda) |
| IAM role | `waterforall-cv-lambda-role` |
| S3 trigger | `ObjectCreated` on `raw/*` prefix → Lambda |

**Lambda env vars:**
```
CV_PROVIDER=aws
DYNAMODB_TABLE=waterforall-cv-submissions
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `POST` | `/cv/submissions` | Upload 1–3 images, get combined analysis |
| `GET` | `/cv/results/{submission_id}` | Fetch stored result from DynamoDB |
| `POST` | `/cv/upload-url` | Get pre-signed S3 PUT URL (AWS mode, for mobile) |
| `POST` | `/analyze/test-strip` | Legacy single-image strip analysis |
| `POST` | `/analyze/water-sample` | Legacy single-image water sample |
| `GET` | `/` | Serves `src/static/index.html` |

### `/cv/submissions` request format
```
Content-Type: multipart/form-data
files: [image1.jpg, image2.jpg, ...]          # 1–3 files
kit_types: '["generic_16_in_1", "tds_meter"]' # optional JSON array, same length as files
                                               # omit or use "auto" to trigger classifier
```

### S3 upload path (Lambda trigger)
```
s3://waterforall-dev-cv-images/raw/{kit_type}/{any-filename}.jpg
```
Kit type is inferred from the S3 key path segment.

---

## Running Locally

```powershell
cd backend

# Start server (CV_PROVIDER=aws uses Bedrock, local uses OpenCV heuristics)
uv run uvicorn src.main:app --reload --port 8000

# Open http://localhost:8000
```

Requires `.env` with:
```
CV_PROVIDER=aws
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
BEDROCK_MODEL_ID=us.anthropic.claude-haiku-4-5-20251001-v1:0
DYNAMODB_TABLE=waterforall-cv-submissions
S3_BUCKET=waterforall-dev-cv-images
```

---

## Running Tests

```powershell
cd backend
uv run pytest tests/cv/ -v
# 73 tests, all should pass
```

---

## Rebuilding & Redeploying Lambda (if code changes)

```powershell
# 1. ECR login (use Bash — PowerShell pipe breaks the token)
$token = aws ecr get-login-password --region us-east-1
docker login --username AWS --password "$token" 986682844768.dkr.ecr.us-east-1.amazonaws.com

# 2. Build
docker build -t waterforall-cv backend/

# 3. Push
docker tag waterforall-cv 986682844768.dkr.ecr.us-east-1.amazonaws.com/waterforall-cv:linux-amd64
docker push 986682844768.dkr.ecr.us-east-1.amazonaws.com/waterforall-cv:linux-amd64

# 4. Update Lambda
aws lambda update-function-code `
  --function-name waterforall-cv-processor `
  --image-uri 986682844768.dkr.ecr.us-east-1.amazonaws.com/waterforall-cv:linux-amd64 `
  --region us-east-1
```

> **Important:** Always push to `:linux-amd64`, not `:latest`. The `:latest` tag is a multi-arch index that Lambda rejects.

---

## Key Design Decisions

- **Bedrock, not Rekognition** — Rekognition is SCP-blocked in this AWS account.
- **Bedrock model** — `us.anthropic.claude-haiku-4-5-20251001-v1:0` (cross-region inference profile, requires `us-east-1`).
- **Markdown fence stripping** — Haiku sometimes wraps JSON in \`\`\`json...\`\`\` fences despite being told not to. All three Bedrock callers (`aws_provider.py`, `tds_processor.py`, `kit_classifier.py`) strip fences before `json.loads`.
- **Safety rule** — The module **never** says water is safe or unsafe to drink. It only outputs readings, confidence scores, boiling-resistant risk flags, and warnings. Final advice belongs to the Water Quality Agent.
- **Boiling-resistant params** — `nitrate`, `nitrite`, `iron`, `lead`, `mercury`, `copper`, `cadmium`, `chromium`. Any of these at warning/critical level generates a `BoilingRiskFlag`.

---

## Credentials Warning

The AWS credentials (`AKIA6LOXBMZQKTYE4AHE`) appeared in the conversation transcript. **Rotate them after the hackathon.**

---

## What's Left (optional improvements)

- [ ] Add `bedrock:InvokeModel` for the cross-region inference profile ARN (may need updating if Bedrock ARN format changes)
- [ ] Test Lambda end-to-end by uploading a real JPEG to S3 `raw/` prefix and checking CloudWatch logs
- [ ] Wire up `/cv/upload-url` in the frontend so mobile clients can upload directly to S3
