"""Embeddings de documents pour le triage (§2, étage triage).

Interface ``Embedder`` : par défaut, SPECTER2 (transformers) si disponible ; sinon repli
déterministe par hachage de caractères n-grammes (aucun réseau, reproductible — utilisé
par les tests). Le classifieur en aval ne connaît pas la provenance des vecteurs.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

import numpy as np
from sklearn.feature_extraction.text import HashingVectorizer


class Embedder(Protocol):
    def encode(self, texts: Sequence[str]) -> np.ndarray: ...


class HashingEmbedder:
    """Repli déterministe : TF-IDF haché sur n-grammes de caractères (coût nul, hors-ligne)."""

    def __init__(self, dim: int = 256) -> None:
        self._vec = HashingVectorizer(
            n_features=dim, analyzer="char_wb", ngram_range=(3, 5),
            alternate_sign=False, norm="l2",
        )

    def encode(self, texts: Sequence[str]) -> np.ndarray:
        return np.asarray(self._vec.transform(list(texts)).todense(), dtype=np.float64)


def load_specter2() -> Embedder:  # pragma: no cover - dépend d'un modèle téléchargé
    """Charge SPECTER2 si transformers/torch sont présents ; sinon repli par hachage."""
    try:
        from transformers import AutoModel, AutoTokenizer  # type: ignore

        tok = AutoTokenizer.from_pretrained("allenai/specter2_base")
        model = AutoModel.from_pretrained("allenai/specter2_base")

        class _S2:
            def encode(self, texts: Sequence[str]) -> np.ndarray:
                import torch

                enc = tok(list(texts), padding=True, truncation=True,
                          return_tensors="pt", max_length=512)
                with torch.no_grad():
                    out = model(**enc).last_hidden_state[:, 0, :]
                return out.cpu().numpy().astype(np.float64)

        return _S2()
    except Exception:
        return HashingEmbedder()
