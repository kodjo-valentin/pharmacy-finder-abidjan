# Emplacement EXACT : backend/Dockerfile
# (le workflow CI build avec le contexte ./backend, donc ce Dockerfile
#  doit vivre dans backend/, au meme niveau que requirements.txt)
#
# Principes appliques :
# - Multi-stage : les outils de compilation ne restent pas dans l'image finale
# - Utilisateur non-root : un compromis du conteneur ne donne pas les droits root
# - Image "slim" : moins de paquets systeme = moins de surface d'attaque (Trivy)
# - Aucun secret copie dans l'image : GEMINI_API_KEY, DATABASE_URL, DB_PASSWORD
#   restent des variables d'environnement injectees a l'execution
#   (Render > Environment, ou "docker run -e ..."). Ton .env n'est jamais COPY.

# ---------- STAGE 1 : installation des dependances ----------
FROM python:3.13-slim AS builder

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# ---------- STAGE 2 : image finale minimale ----------
FROM python:3.13-slim

RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# On recupere uniquement les paquets Python installes, pas pip/gcc/etc.
COPY --from=builder /root/.local /home/appuser/.local

# Copie le contenu de backend/ (app/, runtime.txt, etc.)
COPY . .

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# main.py est dans backend/app/, donc le module est "app.main"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
