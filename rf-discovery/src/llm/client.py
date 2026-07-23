"""Client LLM à bascule de fournisseurs (§8).

Une seule fonction publique : ``complete(prompt, schema)``. L'ordre des fournisseurs est
lu dans ``config/llm.yaml`` ; aucun code métier ne connaît le fournisseur. Un fournisseur
sans clé d'API disponible est ignoré. Si aucun ne répond, ``complete`` lève
``LLMUnavailable`` — l'appelant doit se dégrader proprement (jamais faire échouer le run).
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class LLMUnavailable(RuntimeError):
    """Aucun fournisseur LLM disponible ou tous en échec."""


@dataclass
class Provider:
    name: str
    api_key_env: str
    base_url: str
    model: str


@dataclass
class LLMClient:
    providers: list[Provider]
    temperature: float = 0.0
    timeout_s: int = 60
    max_calls_per_run: int = 40
    _calls: int = 0

    @classmethod
    def from_config(cls, path: str | Path) -> LLMClient:
        cfg = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        providers = [Provider(p["name"], p["api_key_env"], p["base_url"], p["model"])
                     for p in cfg.get("providers", [])]
        return cls(providers=providers, temperature=float(cfg.get("temperature", 0.0)),
                   timeout_s=int(cfg.get("timeout_s", 60)),
                   max_calls_per_run=int(cfg.get("max_calls_per_run", 40)))

    def available(self) -> list[Provider]:
        return [p for p in self.providers if os.environ.get(p.api_key_env)]

    def complete(self, prompt: str, schema: dict | None = None) -> str:
        """Complète via le premier fournisseur disponible qui répond. Sinon LLMUnavailable."""
        if self._calls >= self.max_calls_per_run:
            raise LLMUnavailable("budget d'appels épuisé")
        providers = self.available()
        if not providers:
            raise LLMUnavailable("aucune clé de fournisseur en environnement")
        errors = []
        for p in providers:
            try:
                text = self._call(p, prompt, schema)
                self._calls += 1
                return text
            except Exception as exc:  # bascule au fournisseur suivant
                errors.append(f"{p.name}: {exc}")
        raise LLMUnavailable("; ".join(errors))

    def _call(self, provider: Provider, prompt: str, schema: dict | None) -> str:
        import requests  # import tardif : le module reste importable hors réseau

        payload: dict[str, Any] = {
            "model": provider.model,
            "temperature": self.temperature,
            "messages": [{"role": "user", "content": prompt}],
        }
        if schema is not None:
            payload["response_format"] = {"type": "json_object"}
        headers = {"Authorization": f"Bearer {os.environ[provider.api_key_env]}",
                   "Content-Type": "application/json"}
        resp = requests.post(provider.base_url, json=payload, headers=headers,
                             timeout=self.timeout_s)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


def parse_json(text: str) -> dict | None:
    """Parse une réponse JSON stricte ; renvoie ``None`` si invalide (dégradation)."""
    try:
        return json.loads(text)
    except (json.JSONDecodeError, TypeError):
        return None
