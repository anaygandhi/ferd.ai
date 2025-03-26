from llama_cpp import Llama

# Loading model
llm = Llama(model_path="models/Meta-Llama-3-8B-Instruct.Q4_0.gguf")

# Test
output = llm("What is the capital of France? Answer in one word, nothing beyond that.", max_tokens=50)

print("\nModel Output:\n", output['choices'][0]['text'])
