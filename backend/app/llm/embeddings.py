import numpy as np

def get_text_embedding(text: str, vector_dim: int = 128) -> list[float]:
    # Placeholder embedding generator returning deterministic normalized random vectors for semantic matching
    np.random.seed(abs(hash(text)) % (2**32))
    vec = np.random.randn(vector_dim)
    norm = np.linalg.norm(vec)
    return (vec / (norm if norm != 0 else 1.0)).tolist()
