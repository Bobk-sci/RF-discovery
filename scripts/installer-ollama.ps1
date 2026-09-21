# Installe Ollama sur Windows, range ses modèles sur E: et télécharge ceux qu'il faut
# pour la bibliothèque RF.
#
#   powershell -ExecutionPolicy Bypass -File installer-ollama.ps1
#
# Réglé pour 16 Go de mémoire vive : qwen2.5:7b (dialogue) + nomic-embed-text
# (empreintes pour Smart Connections). Environ 5 Go à télécharger.

param(
    [string]$ModelesOllama = "E:\ollama-models",
    [string]$ModeleDialogue = "qwen2.5:7b",
    [string]$ModeleEmpreintes = "nomic-embed-text"
)

$ErrorActionPreference = "Stop"
function Etape($texte) { Write-Host "`n=== $texte ===" -ForegroundColor Cyan }

Etape "Dossier des modèles : $ModelesOllama"
# À faire AVANT le premier téléchargement : sinon les modèles atterrissent dans
# C:\Users\<vous>\.ollama et il faut les déplacer à la main.
New-Item -ItemType Directory -Force -Path $ModelesOllama | Out-Null
[Environment]::SetEnvironmentVariable("OLLAMA_MODELS", $ModelesOllama, "User")
$env:OLLAMA_MODELS = $ModelesOllama      # pour la session en cours

Etape "Installation d'Ollama"
if (Get-Command ollama -ErrorAction SilentlyContinue) {
    Write-Host "Déjà installé : $((ollama --version) -join ' ')"
} elseif (Get-Command winget -ErrorAction SilentlyContinue) {
    winget install --id Ollama.Ollama --accept-source-agreements --accept-package-agreements
    # winget ne rafraîchit pas le PATH de la session courante.
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" +
                [Environment]::GetEnvironmentVariable("Path", "User")
} else {
    throw "winget est absent. Installez Ollama depuis https://ollama.com/download/windows puis relancez ce script."
}

if (-not (Get-Command ollama -ErrorAction SilentlyContinue)) {
    throw "Ollama installé mais introuvable dans le PATH. Fermez ce PowerShell, rouvrez-en un, et relancez ce script."
}

Etape "Redémarrage du service"
# Un serveur déjà lancé garde l'ancien OLLAMA_MODELS : `pull` s'adresse à LUI, pas à la
# variable qu'on vient d'écrire. Sans ce redémarrage, les modèles partent sur C:.
Get-Process "ollama*" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2
Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
# Le serveur met une ou deux secondes à écouter sur 11434.
$pret = $false
foreach ($essai in 1..15) {
    try {
        Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 | Out-Null
        $pret = $true; break
    } catch { Start-Sleep -Seconds 2 }
}
if (-not $pret) { throw "Ollama ne répond pas sur http://localhost:11434 après 30 s." }
Write-Host "Ollama répond sur http://localhost:11434"

Etape "Téléchargement des modèles (~5 Go)"
ollama pull $ModeleEmpreintes
ollama pull $ModeleDialogue

Etape "Vérification"
$installes = (ollama list | Out-String)
foreach ($m in @($ModeleEmpreintes, $ModeleDialogue)) {
    if ($installes -notmatch [regex]::Escape($m.Split(":")[0])) { throw "$m manquant après téléchargement." }
}
$reponse = ollama run $ModeleDialogue "Réponds par un seul mot : bonjour" 2>&1 | Out-String
Write-Host "Réponse du modèle : $($reponse.Trim())"

Etape "Terminé"
Write-Host @"
Modèles rangés dans : $ModelesOllama
Serveur             : http://localhost:11434

Dans Obsidian :
  Smart Connections -> fournisseur Ollama, modèle d'empreintes $ModeleEmpreintes
  Copilot (facultatif) -> http://localhost:11434/v1, modèle $ModeleDialogue
"@ -ForegroundColor Green
