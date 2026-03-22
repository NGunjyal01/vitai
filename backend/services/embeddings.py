from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_embedding(text: str) -> list:
    # Use a simple hash-based embedding for now
    # This keeps deployment lightweight
    import hashlib
    import numpy as np
    
    # Create deterministic 384-dim embedding from text
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
    rng = np.random.RandomState(seed)
    embedding = rng.randn(384).tolist()
    
    # Normalize
    norm = sum(x**2 for x in embedding) ** 0.5
    return [x/norm for x in embedding]