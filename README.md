# ferd.ai
An AI-powered file explorer, allowing users to transform file management, searching, and organization with the help of machine learning to make intelligent categorization, retrieval, and automation possible. Includes features enhancing productivity, enabling convenient access, and achieving hassle-free file management across all platforms for all non-technical backgrounds.

## MAIN INSTRUCTIONS 

### Linux/Unix/MacOS 

Instructions on setting up the Ollama model. There are two options: 

1. [Run the model locally](#option-1-local-setup) (simpler, recommended)
2. [Run the model in a Docker container](#option-2-docker-container) 

#### OPTION 1: local setup

This will run the Ollama model on your local machine without a docker container.

**Enter the [setup/local/](./setup/local/) directory**
```bash
cd setup/local/
```

**Run the [local setup script](./setup/local/setup_local_ollama.sh)**

This will: 
- Create a conda environment called "llama-env" 
- Install the ollama CLI utils 
- Start an ollama instance
- Pull an ollama model (note: specify model name as arg to the script)
- Run the ollama model (will be accessible at http://localhost:11434)

*Note: recommended Ollama model is "llama3.2:1b-instruct-fp16"*

```bash
chmod +x setup_local_ollama.sh
./setup_local_ollama.sh llama3.2:1b-instruct-fp16
```

**Test:**

Test that the model is running successfully via curl: 

```bash 
curl http://localhost:11434/api/generate   
    -H "Content-Type: application/json"   
    -d '{
        "model": "llama3.2:1b-instruct-fp16",
        "prompt": "Tell me a bedtime story."
    }'
```

**Future runs:**

To start the local model in the future, simply run: 

```bash
ollama start
```

This will run the ollama model at http://localhost:11434. 

Then to activate the conda environment, open a new terminal and use: 

```bash 
conda activate llama-env
```

This will activate the conda environment with the required python dependencies so you can run the other scripts. 

#### OPTION 2: Docker container

This will create and start a docker container to run the Ollama model. 

**Enter the [setup/docker/](./setup/docker/) directory**

```bash
cd setup/docker/
```

**Run the [create ollama container script](./setup/docker/create_ollama_container.sh)

```bash 
chmod +x create_ollama_container.sh
./create_ollama_container.sh
```

*Note: this creates a docker image called "ollama-conda" and container called "ollama-instance"*

**Test:**

Test that the model is running successfully via curl: 

```bash 
curl http://localhost:11434/api/generate   
    -H "Content-Type: application/json"   
    -d '{
        "model": "llama3.2:1b-instruct-fp16",
        "prompt": "Tell me a bedtime story."
    }'
```

**Future runs:**

To run the model after setup, simply start the docker container: 

```bash
# With docker log outputs to terminal: 
docker start -a ollama-instance

# Without docker log outputs to terminal (headless): 
docker start ollama-instance
```

This will run the ollama model at http://localhost:11434. 

Then to activate the conda environment, open a new terminal and use: 

```bash 
conda activate llama-env
```

This will activate the conda environment with the required python dependencies so you can run the other scripts. 

### To use the query_interpretation folder:

Run `download.py` to use the model using command: `python3 download.py`
