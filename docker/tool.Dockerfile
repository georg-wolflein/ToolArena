FROM ghcr.io/georg-wolflein/toolarena:main

COPY install.sh .env ./

# Run the install script (using environment variables)
RUN chmod +x install.sh && . .env && install.sh

COPY task.yaml implementation.py .
