# Installe ou met à jour la bibliothèque RF sur un disque Windows (par défaut E:\rf-library).
#
#   Première fois  : powershell -ExecutionPolicy Bypass -File installer-windows.ps1 -Email vous@exemple.fr
#   Mise à jour    : powershell -ExecutionPolicy Bypass -File installer-windows.ps1 -Email vous@exemple.fr -Rapide
#
# -Rapide synchronise le corpus et réexporte les références, sans retélécharger les PDF
# ni les textes intégraux (c'est ce qui prend des heures). À utiliser pour la mise à jour
# hebdomadaire ; la version complète sert à la première installation ou après un gros
# ajout d'articles.
#
# Le script s'arrête à la première erreur et dit laquelle : rien n'est supposé acquis.
# Prérequis : Git et Python 3.11+ installés (voir INSTALLATION-WINDOWS.md).

param(
    [string]$Racine = "E:\rf-library",
    [Parameter(Mandatory = $true)][string]$Email,
    [string]$Branche = "claude/rf-discovery-pipeline-035bd2",
    [switch]$Rapide,
    [switch]$SansPdf,
    [string]$ModelesOllama = "E:\ollama-models",
    [string]$Coffre = ""
)

$ErrorActionPreference = "Stop"
# PowerShell 5.1 n'interrompt pas le script quand une commande EXTERNE échoue : sans ce
# contrôle explicite, un git en échec laissait la suite s'exécuter comme si de rien n'était.
function Verifier($quoi) { if ($LASTEXITCODE -ne 0) { throw "$quoi a échoué (code $LASTEXITCODE)." } }

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
    try {
        # Ce dossier est un MIROIR du dépôt : on n'y attend aucun travail local. On aligne
        # donc sur la branche distante plutôt que de fusionner — un `pull --ff-only`
        # échoue dès que l'historique distant a été réécrit, ce qui bloquait tout.
        $sale = (git status --porcelain) | Where-Object { $_ -notmatch "^\?\?" }
        if ($sale) {
            throw "Des fichiers suivis ont été modifiés dans $Racine. Sauvegardez-les ou supprimez le dossier, puis relancez."
        }
        git fetch origin $Branche
        Verifier "git fetch"
        git reset --hard "origin/$Branche"
        Verifier "git reset"
    } finally { Pop-Location }
} else {
    git clone -b $Branche https://github.com/Bobk-sci/RF-discovery $Racine
    Verifier "git clone"
}

$projet = Join-Path $Racine "rf-discovery"
Push-Location $projet
try {
    Etape "Environnement Python"
    if (-not (Test-Path ".venv")) { python -m venv .venv; Verifier "python -m venv" }
    $py = Join-Path $projet ".venv\Scripts\python.exe"
    & $py -m pip install --quiet --upgrade pip
    & $py -m pip install --quiet -e .
    Verifier "pip install"

    if ($Rapide) {
        Write-Host "Mode rapide : PDF et textes intégraux conservés tels quels." -ForegroundColor DarkGray
    }
    else {
        if (-not $SansPdf) {
            Etape "Téléchargement des PDF en accès libre (Unpaywall)"
            Write-Host "Seuls les articles légalement gratuits sont récupérés." -ForegroundColor DarkGray
            & $py -m fetch_pdfs --email $Email --out (Join-Path $projet "pdf")
            Verifier "fetch_pdfs"
        }

        Etape "Texte intégral des articles en accès libre (Europe PMC)"
        Write-Host "Pour lire et analyser : plus utile qu'un PDF, et sans refus d'éditeur." -ForegroundColor DarkGray
        & $py -m fetch_fulltext
        Verifier "fetch_fulltext"
    }

    Etape "Export des références (RIS + BibTeX)"
    # Les chemins de PDF partent en URI file:// : c'est la seule forme que Zotero sache
    # résoudre pour attacher un fichier local.
    if ($SansPdf) { & $py -m export_refs }
    else { & $py -m export_refs --pdf-dir (Join-Path $projet "pdf") }
    Verifier "export_refs"

    Etape "État du corpus"
    $fiches  = (Get-ChildItem (Join-Path $projet "articles") -Recurse -Filter *.md |
                Where-Object { $_.FullName -notmatch "\\_" -and $_.Name -ne "README.md" }).Count
    $textes  = @(Get-ChildItem (Join-Path $projet "articles\_textes") -Filter *.md -ErrorAction SilentlyContinue).Count
    $pdfs    = @(Get-ChildItem (Join-Path $projet "pdf") -Filter *.pdf -ErrorAction SilentlyContinue).Count
    $notes   = @(Get-ChildItem (Join-Path $projet "articles\_syntheses") -Filter *.md -ErrorAction SilentlyContinue).Count
    Write-Host ("Fiches : {0}   Textes intégraux : {1}   PDF : {2}   Synthèses : {3}" -f $fiches, $textes, $pdfs, $notes)
} finally {
    Pop-Location
}

if ($Coffre) {
    Etape "Jonction vers le coffre Obsidian"
    # Obsidian ne suit pas un dossier hors du coffre : une jonction NTFS expose le corpus
    # de E: à l'intérieur du coffre, sans copie ni synchronisation.
    $cible = Join-Path $Coffre "rf-articles"
    if (Test-Path $cible) {
        Write-Host "$cible existe déjà, rien à faire." -ForegroundColor DarkGray
    } else {
        cmd /c mklink /J "`"$cible`"" "`"$(Join-Path $projet 'articles')`"" | Out-Null
        Verifier "mklink"
        Write-Host "Jonction créée : $cible"
    }
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
Synthèses et schéma: $projet\articles\_syntheses
Références Zotero  : $projet\articles\bibliotheque-rf.ris
PDF                : $projet\pdf

À faire après une grosse mise à jour :
  1. Obsidian : relancer l'indexation Smart Connections (le corpus a grossi).
  2. Zotero   : Fichier -> Importer -> bibliotheque-rf.ris, "nouvelle collection".

Mise à jour hebdomadaire : relancer ce script avec -Rapide.
"@ -ForegroundColor Green
