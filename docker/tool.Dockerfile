FROM ghcr.io/georg-wolflein/toolarena:main

ENV HOST=0.0.0.0
ENV PORT=8000
ENV WORKSPACE_DIR=/workspace

WORKDIR /workspace
COPY install.sh .env ./

# Run the install script (using environment variables)
RUN chmod +x install.sh && \
    . .env && \
    install.sh

COPY task.yaml implementation.py .

CMD /toolarena/.venv/bin/uvicorn --app-dir /toolarena --host ${HOST} --port ${PORT} toolarena.server:app