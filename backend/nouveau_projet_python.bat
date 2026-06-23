@echo off
REM ===================================================================
REM Script de demarrage pour un nouveau projet Python
REM Usage : place ce fichier dans le dossier de ton nouveau projet,
REM puis double-clique dessus (ou lance-le depuis CMD)
REM ===================================================================

echo === Verification de la version Python installee ===
python --version
echo.

echo === Creation de l'environnement virtuel (venv) ===
python -m venv venv
echo.

echo === Activation du venv ===
call venv\Scripts\activate.bat
echo.

echo === Verification que le venv utilise la bonne version ===
python --version
echo.

echo === Mise a jour de pip ===
python -m pip install --upgrade pip
echo.

echo ===================================================================
echo  Venv cree et active avec succes.
echo  Prochaine etape : cree ton fichier requirements.txt
echo  puis lance : pip install -r requirements.txt
echo ===================================================================
echo.

pause
