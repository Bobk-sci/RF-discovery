"""Corps d'Issues GitHub (§10) : digest hebdomadaire et échec de pipeline.

Un échec silencieux est pire qu'un échec bruyant : toute exception non rattrapée doit
ouvrir une Issue ``pipeline-failure``.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass
class IssuePayload:
    title: str
    body: str
    labels: list[str]


def weekly_issue(run_date: date, digest_markdown: str) -> IssuePayload:
    return IssuePayload(
        title=f"Digest hebdomadaire RF-Discovery — {run_date.isoformat()}",
        body=digest_markdown,
        labels=["weekly-digest"],
    )


def failure_issue(run_date: date, error: str, traceback_text: str = "") -> IssuePayload:
    body = (f"Le run du {run_date.isoformat()} a échoué.\n\n"
            f"**Erreur** : {error}\n")
    if traceback_text:
        body += f"\n```\n{traceback_text.strip()}\n```\n"
    return IssuePayload(title=f"Échec du pipeline — {run_date.isoformat()}",
                        body=body, labels=["pipeline-failure"])
