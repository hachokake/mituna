#!/bin/bash
# Script de déploiement pour PythonAnywhere
# Exécutez ce script dans la console Bash de PythonAnywhere après avoir cloné le repo

echo "🚀 Script de déploiement Mituna sur PythonAnywhere"
echo "=================================================="
echo ""

# 1. Vérifier qu'on est dans le bon dossier
if [ ! -f "manage.py" ]; then
    echo "❌ Erreur: Fichier manage.py non trouvé!"
    echo "   Assurez-vous d'être dans le dossier ~/mituna"
    exit 1
fi

echo "✅ Dossier du projet détecté"
echo ""

# 2. Créer l'environnement virtuel si nécessaire
echo "🐍 Vérification de l'environnement virtuel..."
if [ ! -d "$HOME/.virtualenvs/mituna-venv" ]; then
    echo "   Création de l'environnement virtuel..."
    mkvirtualenv --python=/usr/bin/python3.10 mituna-venv
else
    echo "   ✅ Environnement virtuel existant"
    workon mituna-venv
fi
echo ""

# 3. Installer les dépendances
echo "📦 Installation des dépendances..."
pip install -r requirements.txt
echo ""

# 4. Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo "⚠️  ATTENTION: Fichier .env non trouvé!"
    echo "   Créez le fichier .env avec vos variables d'environnement"
    echo "   Utilisez .env.pythonanywhere comme modèle"
    echo ""
    echo "   Commande: nano .env"
    echo ""
fi

# 5. Appliquer les migrations
echo "🗄️  Application des migrations..."
python manage.py migrate
echo ""

# 6. Collecter les fichiers statiques
echo "📁 Collection des fichiers statiques..."
python manage.py collectstatic --noinput
echo ""

# 7. Créer un superutilisateur (optionnel)
read -p "Voulez-vous créer un compte administrateur maintenant? (o/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Oo]$ ]]; then
    python manage.py createsuperuser
fi
echo ""

# 8. Afficher les instructions finales
echo "✅ Installation terminée!"
echo ""
echo "📋 Prochaines étapes:"
echo "   1. Assurez-vous que le fichier .env contient vos vraies valeurs"
echo "   2. Configurez l'application Web dans l'onglet 'Web' de PythonAnywhere"
echo "   3. Configurez le fichier WSGI (utilisez pythonanywhere_wsgi.py comme modèle)"
echo "   4. Configurez les chemins des fichiers statiques"
echo "   5. Cliquez sur 'Reload' pour démarrer l'application"
echo ""
echo "📖 Consultez DEPLOIEMENT_PYTHONANYWHERE.md pour les détails complets"
echo ""
echo "🎉 Bonne chance!"
