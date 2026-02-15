import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI

# Configure LlamaIndex to use DashScope via OpenAI compatible API
# Note: DashScope's OpenAI compatible API base is https://dashscope.aliyuncs.com/compatible-mode/v1
# We need to ensure the environment variables are set correctly for this.

def get_index():
    # Ensure API key is set (it should be from .env)
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = os.getenv("OPENAI_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    if not api_key:
        print("Warning: OPENAI_API_KEY not found in environment variables.")

    # Configure LLM
    llm = OpenAI(
        model="qwen-max",
        api_key=api_key,
        api_base=api_base,
        temperature=0
    )
    Settings.llm = llm

    # Configure Embedding
    # DashScope supports OpenAI compatible embedding API with model="text-embedding-v1"
    embed_model = OpenAIEmbedding(
        model="text-embedding-v1",
        api_key=api_key,
        api_base=api_base
    )
    Settings.embed_model = embed_model

    # Load documents
    # In a real app, this should be done once or cached
    # Check if data directory exists
    if not os.path.exists("./backend/app/data"):
        return None
        
    documents = SimpleDirectoryReader("./backend/app/data").load_data()
    
    # Create index
    index = VectorStoreIndex.from_documents(documents)
    return index

def query_index(query: str):
    index = get_index()
    if not index:
        return "Knowledge base not found."
    query_engine = index.as_query_engine()
    response = query_engine.query(query)
    return str(response)

def retrieve_documents(query: str):
    index = get_index()
    if not index:
        return []
    retriever = index.as_retriever()
    nodes = retriever.retrieve(query)
    return [node.text for node in nodes]
