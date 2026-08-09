import numpy as np


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    """Calculate cosine similarity between two vectors."""

    array_a = np.asarray(vector_a, dtype=np.float32)
    array_b = np.asarray(vector_b, dtype=np.float32)

    if array_a.ndim != 1 or array_b.ndim != 1:
        raise ValueError("Both vectors must be one-dimensional.")

    if array_a.shape != array_b.shape:
        raise ValueError(
            "Both vectors must have the same number of dimensions."
        )

    denominator = np.linalg.norm(array_a) * np.linalg.norm(array_b)

    if denominator == 0:
        return 0.0

    return float(np.dot(array_a, array_b) / denominator)