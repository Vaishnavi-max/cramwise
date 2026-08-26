from sentence_transformers import SentenceTransformer


class EmbeddingService:
    """
    Converts academic text into dense vector embeddings
    using BGE-M3.

    Responsibility:
        text -> embedding vector

    This class does NOT:
        - store embeddings
        - use ChromaDB
        - perform syllabus mapping
        - call an LLM
    """

    MODEL_NAME = "BAAI/bge-m3"

    def __init__(self):
        print(f"Loading embedding model: {self.MODEL_NAME}")

        self.model = SentenceTransformer(
            self.MODEL_NAME
        )

        print("✓ Embedding model loaded.")

    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding for one piece of text.
        """

        if not text or not text.strip():
            raise ValueError(
                "Cannot generate embedding for empty text."
            )

        embedding = self.model.encode(
            text,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def embed_batch(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """

        if not texts:
            return []

        for text in texts:
            if not text or not text.strip():
                raise ValueError(
                    "Cannot generate embedding for empty text."
                )

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            batch_size=16,
            show_progress_bar=True,
        )

        return embeddings.tolist()