# Mise en place du pipeline CI/CD sécurité — pharmacy-finder-abidjan

Basé sur la structure réelle de ton repo (`backend/app/main.py`, Python 3.13).

## 1. Où déposer les fichiers

```
pharmacy-finder-abidjan/
├── .github/
│   └── workflows/
│       └── ci-security.yml   <- NOUVEAU, à la racine du repo
├── backend/
│   ├── Dockerfile             <- NOUVEAU, dans backend/ (pas a la racine)
│   ├── requirements.txt       <- déjà présent, inchangé
│   └── app/
│       └── main.py
├── frontend/
└── docs/
```

Le contexte du `docker build` est `./backend` (voir le workflow), donc le
Dockerfile doit être dans `backend/`, au même niveau que `requirements.txt`.

## 2. Pousser et observer

```bash
git checkout -b ci/security-pipeline
git add .github/workflows/ci-security.yml backend/Dockerfile
git commit -m "ci: pipeline securite (bandit, pip-audit, trivy)"
git push -u origin ci/security-pipeline
```

Ouvre une pull request (ou push direct sur `main` si tu es seul sur le
repo) puis va dans l'onglet **Actions**. Tu dois voir 3 jobs s'exécuter :
`sast-bandit`, `dependency-audit`, `docker-build-and-scan`.

**Point d'attention possible :** `geopandas`/`pandas` peuvent avoir besoin
de quelques minutes pour s'installer sur Python 3.13 slim. Si le job
`dependency-audit` échoue avec une erreur de compilation (pas une CVE),
ajoute dans le Dockerfile, stage `builder`, avant le `pip install` :
```dockerfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libgdal-dev && rm -rf /var/lib/apt/lists/*
```

## 3. Le livrable mesurable : prouver que le filet fonctionne

**Option A — dépendance vulnérable connue**
Dans `backend/requirements.txt`, ajoute temporairement :
```
requests==2.6.0
```
`pip-audit` doit faire échouer le job `dependency-audit` avec la CVE détectée.

**Option B — faille de code pour Bandit**
Dans `backend/app/tools/pharmacy_finder.py` (ou tout fichier de `app/`),
ajoute temporairement :
```python
import subprocess
subprocess.call(user_input, shell=True)  # Bandit : B602, severite high
```
Le job `sast-bandit` doit le détecter.

Dans les deux cas :
1. Commit + push sur une branche de test
2. Capture d'écran du job **en rouge** dans Actions, avec le message
   d'erreur précis (CVE ou ligne de code signalée)
3. Revert, repush, capture du job qui repasse au vert

C'est cette paire de captures (échec provoqué → détection → correction)
qui constitue la preuve attendue.

## 4. Badge "CI passing"

En haut de `README.md` :
```markdown
![CI](https://github.com/kodjo-valentin/pharmacy-finder-abidjan/actions/workflows/ci-security.yml/badge.svg)
```

## 5. À garder en tête pour la suite

- `backend/app/agent/claude_client.py` lève une erreur si `GEMINI_API_KEY`
  est absent **dès l'import du module**. Le pipeline actuel ne fait que
  builder l'image et la scanner (il ne lance jamais `uvicorn`), donc ça ne
  pose pas de problème aujourd'hui. Mais si tu ajoutes plus tard un job
  "smoke test" qui démarre vraiment l'API en CI, il faudra créer un secret
  GitHub (`Settings > Secrets and variables > Actions`) pour `GEMINI_API_KEY`.
- Tu peux protéger `main` dans `Settings > Branches` pour exiger que les
  3 checks CI passent avant tout merge de pull request.
- Une fois à l'aise, élargis `severity` du scan Trivy à
  `CRITICAL,HIGH,MEDIUM` pour un filet plus strict.
