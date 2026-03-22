from sentence_transformers import SentenceTransformer

_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading embedding model...")
        _model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Embedding model ready.")
    return _model

def get_embedding(text: str) -> list:
    return get_model().encode(text).tolist()