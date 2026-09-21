# Installe la bibliothèque RF sur un disque Windows (par défaut E:\rf-library).
#
#   powershell -ExecutionPolicy Bypass -File installer-windows.ps1 -Email vous@exemple.fr
#
# Le script s'arrête à la première erreur et dit laquelle : rien n'est supposé acquis.
# Prérequis : Git et Python 3.11+ installés (voir INSTALLATION-WINDOWS.md).

param(
    [string]$Racine = "E:\rf-library",
    [Parameter(Mandatory = $true)][string]$Email,
    [string]$Branche = "claude/rf-discovery-pipeline-035bd2",
    [switch]$SansPdf,
    [string]$ModelesOllama = "E:\ollama-models"
)

$ErrorActionPreference = "Stop"

function Etape($texte) { Write-Host "`n=== $texte ===" -ForegroundColor Cyan }

Etape "Vérification des prérequis"
foreach ($outil in @("git", "python")) {
    if (-not (Get-Command $outil -ErrorAction SilentlyContinue)) {
        throw "$outil est introuvable. Installez-le puis rouvrez PowerShell."
    }
}
$version = (python --version) -replace "Python ", ""
Write-Host "Python $version, Git présent."

Etape "Récupération du dépôt dans $Racine"
if (Test-Path (Join-Path $Racine ".git")) {
    Push-Location $Racine
    git pull --ff-only origin $Branche
    Pop-Location
} else {
    git clone -b $Branche https://github.com/Bobk-sci/RF-discovery $Racine
}

$projet = Join-Path $Racine "rf-discovery"
Push-Location $projet
try {
    Etape "Environnement Python"
    if (-not (Test-Path ".venv")) { python -m venv .venv }
    $py = Join-Path $projet ".venv\Scripts\python.exe"
    & $py -m pip install --quiet --upgrade pip
    & $py -m pip install --quiet -e .

    if (-not $SansPdf) {
        Etape "Téléchargement des PDF en accès libre (Unpaywall)"
        Write-Host "Seuls les articles légalement gratuits sont récupérés." -ForegroundColor DarkGray
        & $py -m fetch_pdfs --email $Email --out (Join-Path $projet "pdf")
    }

    Etape "Export des références (RIS + BibTeX)"
    if ($SansPdf) { & $py -m export_refs }
    else { & $py -m export_refs --pdf-dir (Join-Path $projet "pdf") }
} finally {
    Pop-Location
}

Etape "Modèles Ollama sur le même disque"
# Par défaut Ollama écrit dans C:\Users\<vous>\.ollama : plusieurs gigaoctets sur le
# disque système. Cette variable les déplace sur E:. Redémarrez Ollama après coup.
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $ModelesOllama, "User")
New-Item -ItemType Directory -Force -Path $ModelesOllama | Out-Null
Write-Host "OLLAMA_MODELS = $ModelesOllama (prise en compte au prochain démarrage d'Ollama)"

Etape "Terminé"
Write-Host @"
Coffre Obsidian    : $projet\articles
Références EndNote : $projet\articles\bibliotheque-rf.ris
PDF                : $projet\pdf

Suite : ouvrir le coffre dans Obsidian, importer le RIS dans EndNote.
Mise à jour du corpus plus tard : relancer ce script (il fait un git pull).
"@ -ForegroundColor Green
