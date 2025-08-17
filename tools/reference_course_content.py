from utils.context_retriever import get_top_k_chunks

def get_course_tips(query: str, k: int = 3) -> str:
    """
    Retrieves top-k relevant course content chunks for a given query.
    """
    try:
        # Retrieve top-k course tips
        top_chunks = get_top_k_chunks(query, k=k)

        # Format tips as markdown-style bullet points with optional topic ID
        if top_chunks:
            tips_text = "\n".join(
                f"- [{chunk_id}] {' '.join(chunk_text.split()[:120])} ..."
                for chunk_id, chunk_text, _ in top_chunks
            )
        else:
            tips_text = "- No relevant tips found."

        return tips_text

    except Exception as e:
        return f"Error retrieving course tips: {str(e)}"