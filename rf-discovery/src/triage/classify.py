"""Triage supervisé sur le corpus curé (§2, M7).

Régression logistique sur les embeddings de titre+résumé, entraînée sur le corpus curé
(``data/seeds/curated_214.csv``). Objectif M7 : F1 en validation croisée supérieur à la
baseline par mots-clés. Déterministe (``random_state`` fixé).
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict

from triage.specter import Embedder, HashingEmbedder


@dataclass
class TriageClassifier:
    embedder: Embedder
    seed: int = 0
    _clf: LogisticRegression | None = None

    @classmethod
    def default(cls, seed: int = 0) -> TriageClassifier:
        return cls(embedder=HashingEmbedder(), seed=seed)

    def fit(self, texts: Sequence[str], labels: Sequence[int]) -> TriageClassifier:
        x = self.embedder.encode(texts)
        self._clf = LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=self.seed
        ).fit(x, list(labels))
        return self

    def score(self, texts: Sequence[str]) -> np.ndarray:
        if self._clf is None:
            raise RuntimeError("classifieur non entraîné")
        return self._clf.predict_proba(self.embedder.encode(texts))[:, 1]

    def cross_val_f1(self, texts: Sequence[str], labels: Sequence[int], n_splits: int = 5
                     ) -> float:
        y = np.asarray(labels, dtype=int)
        x = self.embedder.encode(texts)
        splits = min(n_splits, int(y.sum()), int((y == 0).sum()))
        cv = StratifiedKFold(n_splits=max(2, splits), shuffle=True, random_state=self.seed)
        clf = LogisticRegression(max_iter=1000, class_weight="balanced", random_state=self.seed)
        pred = cross_val_predict(clf, x, y, cv=cv)
        return float(f1_score(y, pred))


def keyword_baseline_f1(texts: Sequence[str], labels: Sequence[int], keywords: Sequence[str]
                        ) -> float:
    """Baseline : positif si le texte contient au moins un mot-clé du domaine."""
    kw = [k.lower() for k in keywords]
    pred = np.array([1 if any(k in t.lower() for k in kw) else 0 for t in texts])
    return float(f1_score(np.asarray(labels, dtype=int), pred))
