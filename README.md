# ferd.ai
An AI-powered file explorer, allowing users to transform file management, searching, and organization with the help of machine learning to make intelligent categorization, retrieval, and automation possible. Includes features enhancing productivity, enabling convenient access, and achieving hassle-free file management across all platforms for all non-technical backgrounds.

### MAIN INSTRUCTIONS 

Download conda (https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
Then run    `conda env create -f environment.yml`
and         `conda activate llama-env`

As you find more python packages, add to `environment.yml` under pip.

Set a default model (Using 3.2-1b-fp16 1 billion params ~1 GB of ram):

For MacOS: `export INFERENCE_MODEL=llama3.2:1b-instruct-fp16`

For Windows: `$env:INFERENCE_MODEL="llama3.2:1b-instruct-fp16"`

Running the ollama server 
`docker run -d --name ollama -p 11434:11434 -v ollama:/root/.ollama ollama/ollama`

Then pull the model onto the server
`docker exec -it ollama bash`


#### To use the query_interpretation folder:

Run `download.py` to use the model using command: `python3 download.py`
