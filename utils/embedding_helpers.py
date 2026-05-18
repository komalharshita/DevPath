import os
import numpy as np
from google import genai
from google.genai import types

def get_embedding(text: str) -> list:
    """
    Generates a 768-dimensional text embedding vector using the Gemini API.

    Args:
        text (str): The context string to be vectorized.

    Returns:
        list: A list of floats representing the embedding vector.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Missing GEMINI_API_KEY environment variable.")

    client = genai.Client(api_key=api_key)

    response = client.models.embed_content(
        model="text-embedding-004",
        contents=text,
        config=types.EmbedContentConfig(output_dimensionality=768)
    )

    # Extract the vector matrix from the response
    return response.embeddings[0].values

def calculate_cosine_similarity(vector_a: list, vector_b: list) -> float:
    """
    Calculates the cosine similarity score between two vector arrays.

    Args:
        vector_a (list): First vector array.
        vector_b (list): Second vector array.

    Returns:
        float: Normalized score between -1.0 and 1.0 (where 1.0 means identical meaning).
    """
    a = np.array(vector_a)
    b = np.array(vector_b)

    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return float(dot_product / (norm_a * norm_b))