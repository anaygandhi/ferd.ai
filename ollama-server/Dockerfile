FROM python:3.12

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV INFERENCE_MODEL=llama3.2:1b-instruct-fp16
ENV OLLAMA_URL=http://ollama:11434

EXPOSE 8321

CMD ["python", "app.py"]
