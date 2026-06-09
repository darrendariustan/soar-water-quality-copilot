# Stage 1 — install runtime dependencies
# Lambda base image already has pip; fastapi/uvicorn excluded since the
# Lambda handler is invoked directly (not via HTTP).
FROM public.ecr.aws/lambda/python:3.12 AS builder

RUN pip install --no-cache-dir \
    "opencv-python-headless>=4.10.0" \
    "numpy>=2.0.0" \
    "pydantic>=2.8.0" \
    "boto3>=1.35.0"

# Stage 2 — lean runtime image (no build tools)
FROM public.ecr.aws/lambda/python:3.12

COPY --from=builder /var/lang/lib/python3.12/site-packages/ \
                    /var/lang/lib/python3.12/site-packages/

# Copy application source (cv module + handlers)
COPY src/ ${LAMBDA_TASK_ROOT}/src/

# Handler: src/lambda_handler.py :: handler()
CMD ["src.lambda_handler.handler"]
