FROM continuumio/miniconda3

ENV ENV_NAME=llama-env
ENV PATH=/opt/conda/envs/$ENV_NAME/bin:$PATH
ENV OLLAMA_HOST=0.0.0.0

RUN apt-get update && apt-get install -y curl

WORKDIR /app
COPY ../environment.yml .
COPY ../requirements.txt .

RUN conda update -n base -c defaults conda && \
    conda env remove -n $ENV_NAME || true && \
    conda env create -n $ENV_NAME -f environment.yml && \
    /bin/bash -c "source /opt/conda/etc/profile.d/conda.sh && conda activate $ENV_NAME && pip install -r requirements.txt"

RUN curl -fsSL https://ollama.com/install.sh | sh

EXPOSE 11434

CMD bash -c "ollama serve & sleep 5 && ollama pull llama3.2:1b-instruct-fp16 && tail -f /dev/null"

