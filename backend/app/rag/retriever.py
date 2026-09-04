from sqlalchemy.orm import Session

from app.rag.embeddings import (
    build_vocabulary,
    cosine_similarity,
    embed_text,
)
from app.rag.ingestion import ingest_policies


def retrieve_policies(
    db: Session,
    query: str,
    top_k: int = 3,
) -> list[dict]:

    documents = ingest_policies(db)

    if not documents:
        return []

    vocabulary = build_vocabulary(
        [
            document["text"]
            for document in documents
        ]
    )

    query_embedding = embed_text(
        query,
        vocabulary,
    )

    results = []

    for document in documents:

        score = cosine_similarity(
            query_embedding,
            document["embedding"],
        )

        result = {
            key: value
            for key, value in document.items()
            if key != "embedding"
        }

        result["similarity_score"] = round(
            score,
            4,
        )

        results.append(result)

    results.sort(
        key=lambda item: item["similarity_score"],
        reverse=True,
    )

    return results[:top_k]