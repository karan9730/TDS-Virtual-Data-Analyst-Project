import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")

def get_query_embedding(text: str, model="text-embedding-3-small") -> list:
    """
    Returns a 1536-dimensional embedding for the input text using OpenAI's embedding model.
    """
    try:
        response = openai.embeddings.create(
            input=[text],
            model=model
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return []
