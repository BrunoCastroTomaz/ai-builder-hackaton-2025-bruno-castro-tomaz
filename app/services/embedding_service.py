"""
EmbeddingService
Gera embeddings usando o modelo text-embedding-3-small.
Retorna lista de np.array(float32) para compatibilidade com FAISS.
"""

import os
import openai
import numpy as np
from typing import List

class EmbeddingService:
    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set in environment")
        openai.api_key = self.api_key
        self.model = model

    def embed(self, texts: str | List[str]):
        """
        texts: str or list[str]
        Retorna: lista de numpy arrays dtype float32
        """
        if isinstance(texts, str):
            inputs = [texts]
        else:
            inputs = texts

        try:
            resp = openai.Embedding.create(model=self.model, input=inputs)
            embeddings = [item["embedding"] for item in resp["data"]]
            # converter para numpy arrays float32
            return [np.array(e, dtype=np.float32) for e in embeddings]
        except Exception as e:
            print("Embedding error:", e)
            # fallback: embeddings zero (não ideal, apenas para não quebrar flow em dev)
            dims = 1536  
            if isinstance(texts, str):
                return [np.zeros(dims, dtype=np.float32)]
            else:
                return [np.zeros(dims, dtype=np.float32) for _ in texts]
