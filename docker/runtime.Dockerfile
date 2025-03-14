FROM python:3.12

RUN mkdir -p /toolarena
COPY pyproject.toml /toolarena/pyproject.toml
COPY uv.lock /toolarena/uv.lock
COPY toolarena /toolarena/toolarena
COPY docker/subprocess_utils.py /toolarena/subprocess_utils.py
COPY docker/function_runner.py /toolarena/function_runner.py

# For backwards compatibility with the old toolmaker runtime
RUN mkdir -p /toolmaker && ln -s /toolarena/subprocess_utils.py /toolmaker/subprocess_utils.py

RUN python -m pip install uv && \
    cd /toolarena && \
    uv venv && \
    uv sync

RUN mkdir -p /workspace
WORKDIR /workspace

VOLUME /mount/input
VOLUME /mount/output

RUN mkdir -p /toolarena_runtime
ENV TOOLARENA_RUNTIME_DIR=/toolarena_runtime