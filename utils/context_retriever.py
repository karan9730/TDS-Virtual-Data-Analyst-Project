import numpy as np
import os
from typing import List, Tuple
from utils.embed import get_query_embedding

# Load your course-only embedding database
npz_data = np.load("course_embeddings.npz", allow_pickle=True)
stored_chunks = npz_data["chunks"]
stored_ids = npz_data["ids"]
stored_embeddings = npz_data["embeddings"]

def cosine_similarity(vec1, vec2):
    """
    Computes cosine similarity between two vectors.
    """
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def get_top_k_chunks(query: str, k: int = 3) -> List[Tuple[str, str, float]]:
    """
    Given a query, return the top-k most relevant course content chunks.
    Returns a list of tuples: (id, chunk_text, similarity_score)
    """
    query_embedding = get_query_embedding(query)
    if not query_embedding:
        return []

    similarities = [
        cosine_similarity(query_embedding, stored_embeddings[i])
        for i in range(len(stored_chunks))
    ]

    # Get indices of top-k similarities
    top_k_indices = sorted(range(len(similarities)), key=lambda i: similarities[i], reverse=True)[:k]

    top_k_results = []
    for idx in top_k_indices:
        top_k_results.append((
            stored_ids[idx],
            stored_chunks[idx],
            similarities[idx]
        ))

    return top_k_results
