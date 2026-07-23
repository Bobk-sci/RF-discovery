# RF-Discovery

Ce dépôt héberge **RF-Discovery**, un pipeline autonome de découverte inter-domaines
reliant l'exposition aux champs électromagnétiques radiofréquences (CEM-RF) à des processus
neurodéveloppementaux et neurotoxiques. Le moteur de scoring est **déterministe et fondé sur
un graphe hétérogène** ; le LLM est strictement périphérique.

➡️ **Tout le projet est dans [`rf-discovery/`](rf-discovery/)** — voir son
[README](rf-discovery/README.md) pour l'architecture, le démarrage et l'automatisation.

## Démarrage rapide

```bash
cd rf-discovery
uv venv --python 3.11 .venv && . .venv/bin/activate
uv pip install -e ".[dev]"
pytest -q                    # suite déterministe (fixtures, aucun réseau)
python -m run --synthetic    # démo bout-en-bout : scoring + gate + digest + dashboard
```

## Automatisation (GitHub Actions)

Les workflows sont à la racine (`.github/workflows/rf-discovery-*.yml`) car GitHub Actions
n'exécute que les workflows situés à la racine du dépôt :

- `rf-discovery-weekly` — collecte (Europe PMC + PubTator) → graphe → scoring → gate →
  digest → Issue `weekly-digest`.
- `rf-discovery-validate` — lint + tests + gate à chaque PR touchant `rf-discovery/**`.
- `rf-discovery-pages` — publie le dashboard sur GitHub Pages.
