import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    """
    Convert text into normalized tokens.
    """
    return re.findall(
        r"[a-z0-9_]+",
        text.lower(),
    )


def build_vocabulary(texts: list[str]) -> list[str]:
    """
    Build a vocabulary from policy documents.
    """
    vocabulary = set()

    for text in texts:
        vocabulary.update(tokenize(text))

    return sorted(vocabulary)


def embed_text(
    text: str,
    vocabulary: list[str],
) -> list[float]:
    """
    Create a lightweight TF-IDF-style vector.

    This is intentionally local and deterministic so
    Phase 4 works without an external embedding API.
    """

    tokens = tokenize(text)
    counts = Counter(tokens)

    total = max(len(tokens), 1)

    vector = []

    for word in vocabulary:
        tf = counts[word] / total
        vector.append(float(tf))

    return vector


def cosine_similarity(
    a: list[float],
    b: list[float],
) -> float:

    if not a or not b:
        return 0.0

    dot_product = sum(
        x * y
        for x, y in zip(a, b)
    )

    magnitude_a = math.sqrt(
        sum(x * x for x in a)
    )

    magnitude_b = math.sqrt(
        sum(x * x for x in b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0

    return dot_product / (
        magnitude_a * magnitude_b
    )