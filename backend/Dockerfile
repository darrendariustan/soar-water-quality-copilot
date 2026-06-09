FROM public.ecr.aws/lambda/python:3.12

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /var/task

COPY pyproject.toml uv.lock ./

# Install deps into the Lambda task directory (no venv, directly into site-packages)
RUN uv pip install --system --no-cache -r pyproject.toml

COPY src/ src/

CMD ["src.lambda_handler.handler"]
