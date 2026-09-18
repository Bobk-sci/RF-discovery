"""Cache disque des réponses brutes d'API + HTTP avec backoff (§10).

Un rerun ne doit jamais re-solliciter les sources : chaque réponse est mise en cache par
empreinte de (url, params). Le backoff exponentiel (2,4,8,16 s) respecte les rate limits.
La couche réseau est isolée ici pour que le reste soit testable hors-ligne.
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import Any


def _key(url: str, params: dict[str, Any]) -> str:
    blob = url + "?" + json.dumps(params, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()[:24]


def cache_path(cache_dir: str | Path, url: str, params: dict[str, Any]) -> Path:
    return Path(cache_dir) / f"{_key(url, params)}.json"


def load_cache(cache_dir: str | Path, url: str, params: dict[str, Any]) -> Any | None:
    path = cache_path(cache_dir, url, params)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return None


def save_cache(cache_dir: str | Path, url: str, params: dict[str, Any], data: Any) -> None:
    path = cache_path(cache_dir, url, params)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def _get(
    url: str,
    params: dict[str, Any],
    *,
    parse,
    cache_dir: str | Path,
    user_agent: str,
    max_retries: int,
    backoff_base_s: float,
    sleep,
) -> Any:  # pragma: no cover - couche réseau, exercée via fixtures ailleurs
    cached = load_cache(cache_dir, url, params)
    if cached is not None:
        return cached
    import requests

    last: Exception | None = None
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, headers={"User-Agent": user_agent},
                                timeout=30)
            resp.raise_for_status()
            data = parse(resp)
            save_cache(cache_dir, url, params, data)
            return data
        except Exception as exc:
            last = exc
            sleep(backoff_base_s * (2 ** attempt))
    raise RuntimeError(f"échec réseau après {max_retries} tentatives : {last}")


def get_json(
    url: str,
    params: dict[str, Any],
    *,
    cache_dir: str | Path = "data/cache",
    user_agent: str = "rf-discovery/0.1",
    max_retries: int = 3,
    backoff_base_s: float = 1.0,
    sleep=time.sleep,
) -> Any:  # pragma: no cover - couche réseau
    """GET JSON avec cache et backoff exponentiel. Import de requests tardif."""
    return _get(url, params, parse=lambda r: r.json(), cache_dir=cache_dir,
                user_agent=user_agent, max_retries=max_retries,
                backoff_base_s=backoff_base_s, sleep=sleep)


def get_text(
    url: str,
    params: dict[str, Any],
    *,
    cache_dir: str | Path = "data/cache",
    user_agent: str = "rf-discovery/0.1",
    max_retries: int = 3,
    backoff_base_s: float = 1.0,
    sleep=time.sleep,
) -> str:  # pragma: no cover - couche réseau
    """Idem ``get_json`` pour les réponses texte (XML PubMed, pages HTML)."""
    return str(_get(url, params, parse=lambda r: r.text, cache_dir=cache_dir,
                    user_agent=user_agent, max_retries=max_retries,
                    backoff_base_s=backoff_base_s, sleep=sleep))
