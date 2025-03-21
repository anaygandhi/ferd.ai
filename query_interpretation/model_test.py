from llama_cpp import Llama

# Loading model
llm = Llama(model_path="models/Meta-Llama-3-8B-Instruct.Q6_K.gguf")

# Test
output = llm("What is the capital of France?", max_tokens=50)

print("\nModel Output:\n", output)
