from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.llms.llama_cpp import LlamaCPP
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

# Load documents
reader = SimpleDirectoryReader('test_dir/')
docs = reader.load_data()

# Transformer
embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load Model
llm = LlamaCPP(
    model_path="models/Meta-Llama-3-8B-Instruct.Q4_0.gguf",
    temperature=0.7,
    max_new_tokens=256,
    context_window=4096,
)


# Index for semantic search
index = VectorStoreIndex.from_documents(docs, embed_model=embed_model)

# Query engine
query_engine = index.as_query_engine(llm=llm)

# Run the query
query = "Find files related to syllabuses"
response = query_engine.query(query)
print(response)