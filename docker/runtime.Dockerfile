FROM python:3.12

WORKDIR /toolarena

COPY pyproject.toml uv.lock ./

RUN python -m pip install uv && \
    uv venv && \
    uv sync

COPY toolarena ./toolarena

RUN python -m pip install uv && \
    uv venv && \
    uv sync

RUN mkdir -p /workspace
WORKDIR /workspace

COPY docker/subprocess_utils.py /toolarena/subprocess_utils.py
COPY docker/function_runner.py /toolarena/function_runner.py

# For backwards compatibility with the old toolmaker runtime
RUN mkdir -p /toolmaker && ln -s /toolarena/subprocess_utils.py /toolmaker/subprocess_utils.py

VOLUME /mount/input
VOLUME /mount/output

RUN mkdir -p /toolarena_runtime
ENV TOOLARENA_RUNTIME_DIR=/toolarena_runtime