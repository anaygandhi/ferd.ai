# This script downloads a model file from a specified URL and saves it to a local directory.
# It ensures the target directory exists before attempting to download the file.
# The script uses the `curl` command-line tool to perform the download.
# After the download is complete, it prints a confirmation message.
# Note: Ensure you have curl installed on your system for this script to work.

import os

model_url = "https://huggingface.co/QuantFactory/Meta-Llama-3-8B-Instruct-GGUF/resolve/main/Meta-Llama-3-8B-Instruct.Q4_0.gguf?download=true"
model_path = "models/Meta-Llama-3-8B-Instruct.Q4_0.gguf"

# Ensure the models directory exists
os.makedirs("models", exist_ok=True)

# Download the model using curl
os.system(f'curl -L -o {model_path} "{model_url}"')

print("Download complete.")

