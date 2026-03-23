# Script PowerShell pour l'installation rapide du projet

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "  Installation de Sondages Pro" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Python est installé
Write-Host "[1/6] Vérification de Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ Python détecté: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python n'est pas installé ou n'est pas dans le PATH" -ForegroundColor Red
    Write-Host "Veuillez installer Python depuis https://www.python.org/" -ForegroundColor Red
    pause
    exit
}

Write-Host ""

# Créer l'environnement virtuel
Write-Host "[2/6] Création de l'environnement virtuel..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "! L'environnement virtuel existe déjà" -ForegroundColor Yellow
} else {
    python -m venv venv
    Write-Host "✓ Environnement virtuel créé" -ForegroundColor Green
}

Write-Host ""

# Activer l'environnement virtuel
Write-Host "[3/6] Activation de l'environnement virtuel..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Environnement virtuel activé" -ForegroundColor Green

Write-Host ""

# Installer les dépendances
Write-Host "[4/6] Installation des dépendances..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "✓ Dépendances installées" -ForegroundColor Green

Write-Host ""

# Créer les migrations
Write-Host "[5/6] Création de la base de données..." -ForegroundColor Yellow
python manage.py makemigrations
python manage.py migrate
Write-Host "✓ Base de données créée" -ForegroundColor Green

Write-Host ""

# Créer un superutilisateur
Write-Host "[6/6] Création du compte administrateur..." -ForegroundColor Yellow
Write-Host ""
Write-Host "Veuillez créer un compte administrateur:" -ForegroundColor Cyan
python manage.py createsuperuser

Write-Host ""
Write-Host "=========================================" -ForegroundColor Green
Write-Host "  Installation terminée avec succès!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Pour démarrer le serveur, exécutez:" -ForegroundColor Cyan
Write-Host "  python manage.py runserver" -ForegroundColor White
Write-Host ""
Write-Host "Puis ouvrez votre navigateur à:" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:8000/" -ForegroundColor White
Write-Host ""
Write-Host "Interface d'administration:" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:8000/admin/" -ForegroundColor White
Write-Host ""
pause
