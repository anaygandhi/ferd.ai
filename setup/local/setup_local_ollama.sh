#!/bin/bash

set -e

# Arguments
MODEL_NAME="$1"                         # Model name is the first argument to the script
ENV_NAME="llama-env"                    # Conda env name (static) 
ENVIRONMENT_YML="../environment.yml"    # Path to the environment.yml file (static)
REQUIREMENTS_TXT="../requirements.txt"  # Path to the requirements.txt file (static)
OLLAMA_INSTALL_URI="https://ollama.com/install.sh"  # URL for installing the ollama cli utils (static)

# Check if a model name is given
if [ -z "$MODEL_NAME" ]; then
  echo "Usage: $0 <model-name>"
  exit 1
fi

# --- 1. Conda setup ---
# Create the conda environment (or recreate it if it already exists)
echo "Initializing conda environment: $ENV_NAME"

# Init conda in this shell
source "$(conda info --base)/etc/profile.d/conda.sh"

# Remove the environment if it exists
if conda info --envs | grep -q "$ENV_NAME"; then
  echo "Removing existing conda environment: $ENV_NAME"
  conda env remove -n "$ENV_NAME" --yes
fi

# Create the environment
echo "Creating conda environment from: $ENVIRONMENT_YML"
conda env create -n "$ENV_NAME" -f "$ENVIRONMENT_YML"

# Activate the conda environment
conda activate $ENV_NAME

# --- 2. Pip requirements ---
# Install the python requirements in the conda env 
echo "Installing Python dependencies"
pip install -r $REQUIREMENTS_TXT

# --- 3. Install Ollama ---
echo "Installing Ollama"

# Check if the OS is macOS or Linux
OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then
  echo "Detected macOS, using Homebrew to install Ollama"
  brew install ollama
elif [ "$OS" = "Linux" ]; then
  curl -fsSL $OLLAMA_INSTALL_URI | sh
else
  echo "Unsupported OS: $OS"
  exit 1
fi

# --- 4. Start Ollama Server ---
# Start the ollama server
echo "Starting Ollama server (not as daemon)"
ollama serve &

# Wait a few seconds for the server to start
sleep 5

# --- 5. Pull Model ---
# Pull the model 
echo "Pulling model: $MODEL_NAME"
ollama pull "$MODEL_NAME"

# DONE 
echo "Local setup complete. Ollama is running (in this shell) and model '$MODEL_NAME' is pulled.\n"
