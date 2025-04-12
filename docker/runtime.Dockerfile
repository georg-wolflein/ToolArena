# This image is published to ghcr.io/georg-wolflein/toolarena-runtime
FROM python:3.12

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.6 /uv /uvx /bin/

WORKDIR /toolarena

COPY pyproject.toml uv.lock README.md ./

RUN uv sync

COPY toolarena ./toolarena

RUN mkdir -p /workspace
WORKDIR /workspace

COPY docker/subprocess_utils.py /toolarena/subprocess_utils.py
COPY docker/function_runner.py /toolarena/function_runner.py

# For backwards compatibility with the old toolmaker runtime
RUN mkdir -p /toolmaker && ln -s /toolarena/subprocess_utils.py /toolmaker/subprocess_utils.py

VOLUME /mount/input
VOLUME /mount/output

ENV WORKSPACE_DIR=/workspace
ENV HOST=0.0.0.0
ENV PORT=8000

CMD /toolarena/.venv/bin/uvicorn --app-dir /toolarena --host ${HOST} --port ${PORT} toolarena.server:app