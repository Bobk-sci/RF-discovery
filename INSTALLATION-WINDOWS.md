# Installation complète sur Windows — tout sur `E:\`

Résultat final :

```
E:\rf-library\rf-discovery\articles\      coffre Obsidian (1370 fiches)
E:\rf-library\rf-discovery\articles\bibliotheque-rf.ris   à importer dans EndNote
E:\rf-library\rf-discovery\pdf\           PDF en accès libre
E:\ollama-models\                         modèles locaux (plusieurs Go)
```

---

## 1. Les quatre logiciels à installer

Dans cet ordre. Tous s'installent sur `C:` (ce sont des programmes, quelques centaines de
mégaoctets) ; seules les **données** iront sur `E:`.

| Logiciel | Où | Remarque |
|---|---|---|
| **Python 3.11+** | [python.org](https://www.python.org/downloads/windows/) | cochez **« Add python.exe to PATH »** à l'installation |
| **Git pour Windows** | [git-scm.com](https://git-scm.com/downloads/win) | valeurs par défaut |
| **Ollama** | [ollama.com](https://ollama.com/download/windows) | pour les modèles locaux |
| **Obsidian** | [obsidian.md](https://obsidian.md/download) | gratuit pour un usage personnel |

Vérifiez dans un **PowerShell fraîchement ouvert** :

```powershell
python --version    # doit afficher 3.11 ou plus
git --version
```

Si `python` n'est pas reconnu, l'option « Add to PATH » a été oubliée : relancez
l'installateur Python et choisissez *Modify*.

---

## 2. Installer la bibliothèque (un seul script)

```powershell
cd E:\
git clone -b claude/rf-discovery-pipeline-035bd2 https://github.com/Bobk-sci/RF-discovery E:\rf-library
powershell -ExecutionPolicy Bypass -File E:\rf-library\scripts\installer-windows.ps1 -Email votre@adresse.fr
```

Le script crée l'environnement Python, télécharge les PDF en accès libre, produit le
fichier de références et déplace le dossier des modèles Ollama sur `E:`.

Comptez une trentaine de minutes, l'essentiel étant le téléchargement des PDF.

> `-ExecutionPolicy Bypass` ne vaut que pour cette exécution : Windows bloque par défaut
> les scripts téléchargés, et cette option lève le blocage sans changer vos réglages.

Options utiles :

```powershell
# sans les PDF (références seules, deux minutes)
... -Email votre@adresse.fr -SansPdf

# ailleurs que E:\rf-library
... -Email votre@adresse.fr -Racine "E:\Documents\veille-rf"
```

**Sur les PDF, sans détour :** environ la moitié du corpus est en accès libre et sera
téléchargée. L'autre moitié est sous abonnement et ne le sera pas — aucun script ne
contourne un péage. Pour ces articles-là, passez par l'accès de votre bibliothèque
universitaire.

---

## 3. Obsidian

*Ouvrir un dossier comme coffre* → `E:\rf-library\rf-discovery\articles`

Ouvrez `_cartes/Accueil.md` : c'est le point d'entrée vers une carte par modèle d'étude.
Le panneau des étiquettes donne le classement croisé (`modele/in_vivo`,
`theme/neurodeveloppement`, `annee/2019`).

### Recherche sémantique locale

Configuration retenue pour **16 Go de mémoire vive** :

```powershell
ollama pull nomic-embed-text     # empreintes, ~270 Mo
ollama pull qwen2.5:7b           # dialogue, ~4,7 Go
```

Redémarrez Ollama pour qu'il prenne en compte `E:\ollama-models`, puis dans Obsidian :
*Paramètres → Modules complémentaires → Parcourir* → **Smart Connections** → dans ses
réglages, choisissez **Ollama** et le modèle `nomic-embed-text`. L'indexation des
1 370 fiches prend une à deux minutes.

Pour dialoguer avec le corpus, ajoutez **Copilot for Obsidian** et pointez-le sur
`http://localhost:11434/v1`, modèle `qwen2.5:7b`.

Avec 16 Go, un modèle de 7 à 8 milliards de paramètres occupe 5 à 6 Go une fois chargé :
il reste de quoi faire tourner Obsidian et le reste du système. Un modèle de 14 milliards
tiendrait à peine et ferait pagaille dès qu'une autre application demande de la mémoire —
inutile d'essayer. Si `qwen2.5:7b` vous semble lourd, `llama3.2` (3 milliards, ~2 Go)
répond plus vite pour une qualité moindre.

Fermez Ollama quand vous ne l'utilisez pas : le modèle reste chargé en mémoire quelques
minutes après la dernière question.

---

## 4. EndNote

*File → Import → File* → `E:\rf-library\rf-discovery\articles\bibliotheque-rf.ris`,
type **Reference Manager (RIS)**.

Les champs `L1` contiennent le chemin des PDF téléchargés : EndNote attache les fichiers
aux références à l'import. Les étiquettes `modele:` et `theme:` arrivent dans les
*keywords*.

---

## 5. Claude Code (facultatif, payant)

Nécessite un abonnement Claude (Pro à 20 $/mois suffit). Dans PowerShell :

```powershell
irm https://claude.ai/install.ps1 | iex
```

Puis, pour l'utiliser dans VS Code : extension **Claude Code** depuis la vue Extensions,
ouvrez `E:\rf-library`, connectez-vous. Les commandes `/synthese`, `/contradictions`,
`/lacunes` et `/redaction` sont déjà dans le dépôt et prêtes à servir.

Sans abonnement, tout le reste fonctionne : collecte, classement, Obsidian, Ollama,
EndNote.

---

## 6. Mettre à jour plus tard

```powershell
powershell -ExecutionPolicy Bypass -File E:\rf-library\scripts\installer-windows.ps1 -Email votre@adresse.fr
```

Le script fait un `git pull` : vous récupérez les articles ajoutés par la collecte
hebdomadaire, et seuls les PDF manquants sont téléchargés.

---

## En cas de problème

| Message | Cause | Solution |
|---|---|---|
| `python n'est pas reconnu` | PATH | relancer l'installateur Python, *Modify*, cocher « Add to PATH », rouvrir PowerShell |
| `l'exécution de scripts est désactivée` | politique PowerShell | garder `-ExecutionPolicy Bypass` dans la commande |
| `fatal: destination path already exists` | dossier déjà présent | relancer le script sans le `git clone` : il fait le `pull` lui-même |
| Ollama écrit toujours sur `C:` | variable non prise en compte | quitter Ollama depuis la zone de notification et le relancer |
| Peu de PDF téléchargés | la moitié du corpus est sous abonnement | normal ; voir la section 2 |
