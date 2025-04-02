#!/bin/bash

set -e

# Settings
IMAGE_NAME="ollama-conda"         # Name of the docker img to be created
CONTAINER_NAME="ollama-instance"  # Name of the docker container to be created

# Run from the setup/ root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"  # Dir that contains this script (dynamic from where the script is run)
ROOT_DIR="$(dirname "$SCRIPT_DIR")"                         # Dir that contains the environment.yml and requirements.txt files (one lvl up from script dir)

# Cd into the root dir
cd "$ROOT_DIR"

# Build the docker image
echo "Building Docker image: $IMAGE_NAME"
docker build -t "$IMAGE_NAME" -f docker/Dockerfile .

# Remove the existing container if it exists
if docker ps -a --format '{{.Names}}' | grep -Eq "^${CONTAINER_NAME}\$"; then
  echo "Removing existing container: $CONTAINER_NAME"
  docker rm -f "$CONTAINER_NAME"
fi

# Run the docker container with log outputs in this shell
echo "Running Docker container: $CONTAINER_NAME"
docker run -it --name "$CONTAINER_NAME" -p 11434:11434 "$IMAGE_NAME"