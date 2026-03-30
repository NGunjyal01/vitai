# Sentence transformer embeddings
from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Load model at module level (384-dim vectors)
logger.info("Loading sentence-transformers model: all-MiniLM-L6-v2")
model = SentenceTransformer("all-MiniLM-L6-v2")
logger.info("Sentence-transformers model loaded successfully")


def get_embedding(text: str) -> list[float]:
    """Get 384-dim embedding for a single text."""
    if not text or not text.strip():
        raise ValueError("Cannot embed empty text")
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def get_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """Get embeddings for a batch of texts."""
    if not texts:
        return []
    for i, t in enumerate(texts):
        if not t or not t.strip():
            raise ValueError(f"Cannot embed empty text at index {i}")
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.tolist()
