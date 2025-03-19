FROM ghcr.io/georg-wolflein/toolarena-runtime:latest
# FROM toolarena-runtime:latest

ENV HOST=0.0.0.0
ENV PORT=8000

RUN mkdir -p /toolarena_runtime
COPY install.sh /toolarena_runtime/install.sh
COPY .env /toolarena_runtime/.env

# Run the install script (using environment variables)
RUN chmod +x /toolarena_runtime/install.sh && \
    export $(grep -v '^#' /toolarena_runtime/.env | xargs) && \
    /toolarena_runtime/install.sh

COPY task.yaml /toolarena_runtime/task.yaml
COPY implementation.py /toolarena_runtime/implementation.py

CMD /toolarena/.venv/bin/uvicorn --app-dir /toolarena --host ${HOST} --port ${PORT} toolarena.server:app