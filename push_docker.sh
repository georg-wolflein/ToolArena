docker build -t toolarena-runtime -f docker/runtime.Dockerfile .
docker tag toolarena-runtime ghcr.io/georg-wolflein/ToolArena:latest
docker push ghcr.io/georg-wolflein/ToolArena:latest
