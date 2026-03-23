# 🚀 Guide de Déploiement sur PythonAnywhere

Ce guide vous explique comment héberger votre application de sondage Django sur PythonAnywhere.

---

## 📋 Prérequis

- Un compte PythonAnywhere (gratuit ou payant)
- Votre code sur GitHub : https://github.com/hachokake/mituna
- Les identifiants de votre compte PythonAnywhere

---

## 🎯 Étape 1 : Créer un compte PythonAnywhere

1. Allez sur **https://www.pythonanywhere.com**
2. Cliquez sur **"Pricing & signup"**
3. Créez un compte **gratuit** (Beginner) ou payant selon vos besoins
4. Confirmez votre email
5. Connectez-vous à votre compte

> **Note** : Le compte gratuit vous donne :
> - 1 application web
> - 512 MB d'espace disque
> - Accès aux consoles
> - Un domaine : `votre-username.pythonanywhere.com`

---

## 🔧 Étape 2 : Ouvrir une Console Bash

1. Une fois connecté, allez dans l'onglet **"Consoles"**
2. Cliquez sur **"Bash"** (sous "Start a new console")
3. Une console bash s'ouvre - vous êtes maintenant dans votre serveur Linux !

---

## 📥 Étape 3 : Cloner votre repository GitHub

Dans la console Bash, tapez les commandes suivantes :

```bash
# Cloner votre repository
git clone https://github.com/hachokake/mituna.git

# Aller dans le dossier
cd mituna

# Vérifier que tout est là
ls -la
```

Vous devriez voir tous vos fichiers listés.

---

## 🐍 Étape 4 : Créer un environnement virtuel Python

```bash
# Créer un environnement virtuel avec Python 3.10
mkvirtualenv --python=/usr/bin/python3.10 mituna-venv

# L'environnement virtuel est maintenant activé
# Vous verrez (mituna-venv) au début de votre prompt
```

---

## 📦 Étape 5 : Installer les dépendances

```bash
# Assurez-vous d'être dans le dossier mituna
cd ~/mituna

# Installer les dépendances
pip install -r requirements.txt

# Vérifier l'installation
pip list
```

---

## 🔐 Étape 6 : Configurer les variables d'environnement

```bash
# Créer un fichier .env
nano .env
```

Dans l'éditeur nano, copiez-collez :

```env
SECRET_KEY=votre-cle-secrete-super-longue-et-aleatoire-ici
DEBUG=False
ALLOWED_HOSTS=votre-username.pythonanywhere.com
```

Pour sauvegarder dans nano :
- Appuyez sur **Ctrl + O** (enregistrer)
- Appuyez sur **Entrée**
- Appuyez sur **Ctrl + X** (quitter)

> **Important** : Générez une vraie clé secrète sécurisée !
> Vous pouvez en générer une avec cette commande :

```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

---

## 🗄️ Étape 7 : Initialiser la base de données

```bash
# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur admin
python manage.py createsuperuser
# Suivez les instructions pour créer votre compte admin
```

---

## 📁 Étape 8 : Collecter les fichiers statiques

```bash
# Collecter tous les fichiers statiques (CSS, JS, images)
python manage.py collectstatic --noinput
```

---

## 🌐 Étape 9 : Configurer l'application Web sur PythonAnywhere

### 9.1 Créer une nouvelle Web App

1. Allez dans l'onglet **"Web"** en haut
2. Cliquez sur **"Add a new web app"**
3. Cliquez sur **"Next"** pour accepter le domaine gratuit
4. Sélectionnez **"Manual configuration"** (PAS Django !)
5. Sélectionnez **"Python 3.10"**
6. Cliquez sur **"Next"**

### 9.2 Configurer le Virtual Environment

Dans la section **"Virtualenv"** :

1. Dans le champ "Enter path to a virtualenv", tapez :
   ```
   /home/votre-username/.virtualenvs/mituna-venv
   ```
   ⚠️ Remplacez `votre-username` par votre vrai nom d'utilisateur PythonAnywhere

### 9.3 Configurer le fichier WSGI

1. Scrollez jusqu'à la section **"Code"**
2. Cliquez sur le fichier **"WSGI configuration file"** (lien bleu)
3. **SUPPRIMEZ TOUT** le contenu existant
4. Copiez-collez le code suivant :

```python
# +++++++++++ DJANGO +++++++++++
import os
import sys

# Ajouter le chemin de votre projet
path = '/home/votre-username/mituna'
if path not in sys.path:
    sys.path.append(path)

# Définir le module de settings Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'sondage_project.settings'

# Charger l'application WSGI Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

⚠️ **IMPORTANT** : Remplacez `votre-username` par votre vrai nom d'utilisateur !

5. Cliquez sur **"Save"** en haut à droite

### 9.4 Configurer les fichiers statiques

Retournez dans l'onglet **"Web"**, scrollez jusqu'à **"Static files"** :

1. Ajoutez une nouvelle entrée :
   - **URL** : `/static/`
   - **Directory** : `/home/votre-username/mituna/staticfiles`

2. Ajoutez une autre entrée :
   - **URL** : `/media/`
   - **Directory** : `/home/votre-username/mituna/media`

⚠️ Remplacez `votre-username` dans les deux chemins !

---

## ⚙️ Étape 10 : Mettre à jour settings.py pour la production

Retournez dans la console Bash :

```bash
cd ~/mituna
nano sondage_project/settings.py
```

Modifiez les lignes suivantes :

```python
# Remplacez :
DEBUG = True

# Par :
DEBUG = False

# Remplacez :
ALLOWED_HOSTS = []

# Par (remplacez votre-username) :
ALLOWED_HOSTS = ['votre-username.pythonanywhere.com']
```

Sauvegardez avec **Ctrl + O**, **Entrée**, puis **Ctrl + X**.

---

## 🎉 Étape 11 : Recharger l'application

1. Retournez dans l'onglet **"Web"**
2. Scrollez en haut de la page
3. Cliquez sur le gros bouton vert **"Reload votre-username.pythonanywhere.com"**
4. Attendez quelques secondes

---

## ✅ Étape 12 : Tester votre application

1. Cliquez sur le lien de votre site : **https://votre-username.pythonanywhere.com**
2. Votre application devrait s'afficher !
3. Testez la page d'accueil
4. Connectez-vous à l'interface admin : **https://votre-username.pythonanywhere.com/admin/**

---

## 🔄 Mettre à jour votre application (après des modifications)

Quand vous faites des changements dans votre code :

```bash
# 1. Dans la console Bash
cd ~/mituna

# 2. Récupérer les dernières modifications de GitHub
git pull origin main

# 3. Réactiver l'environnement virtuel si nécessaire
workon mituna-venv

# 4. Installer les nouvelles dépendances (si ajoutées)
pip install -r requirements.txt

# 5. Appliquer les migrations (si changements dans models.py)
python manage.py migrate

# 6. Collecter les nouveaux fichiers statiques
python manage.py collectstatic --noinput

# 7. Recharger l'application
# Allez dans l'onglet Web et cliquez sur "Reload"
```

---

## 🐛 Dépannage

### L'application ne se charge pas

1. Vérifiez les **logs d'erreur** :
   - Onglet **"Web"** → Section **"Log files"**
   - Regardez le **"Error log"**

2. Vérifiez que l'environnement virtuel est correct :
   ```bash
   workon mituna-venv
   python --version  # Doit afficher Python 3.10
   ```

3. Vérifiez les chemins dans le fichier WSGI

### Les fichiers statiques ne s'affichent pas

1. Vérifiez les chemins dans la section "Static files"
2. Re-collectez les fichiers statiques :
   ```bash
   python manage.py collectstatic --clear --noinput
   ```

### Erreur 500

1. Activez temporairement DEBUG :
   ```python
   DEBUG = True
   ```
2. Rechargez l'app pour voir l'erreur détaillée
3. **N'oubliez pas de remettre DEBUG = False après !**

### Problèmes de base de données

```bash
# Réinitialiser la base de données (⚠️ EFFACE TOUTES LES DONNÉES)
cd ~/mituna
rm db.sqlite3
python manage.py migrate
python manage.py createsuperuser
```

---

## 📊 Caractéristiques du compte gratuit

- **Domaine** : `votre-username.pythonanywhere.com`
- **CPU** : Limité (suffisant pour petits projets)
- **Trafic** : Illimité
- **Espace** : 512 MB
- **Base de données** : SQLite incluse
- **HTTPS** : Inclus automatiquement
- **Mise en veille** : Le site dort après 3 mois d'inactivité

---

## 💰 Passer à un compte payant (optionnel)

Avantages :
- Domaine personnalisé
- Plus d'espace disque
- Base de données MySQL/PostgreSQL
- Plus de CPU
- Pas de mise en veille

Prix : À partir de 5$ / mois

---

## 📝 Notes importantes

1. **Sécurité** :
   - Ne committez JAMAIS votre `.env` sur GitHub
   - Utilisez toujours `DEBUG = False` en production
   - Changez la `SECRET_KEY` en production

2. **Performance** :
   - SQLite est suffisant pour petits projets (<10,000 réponses)
   - Pour plus, considérez MySQL/PostgreSQL (compte payant)

3. **Sauvegardes** :
   - PythonAnywhere ne fait pas de sauvegardes automatiques
   - Sauvegardez régulièrement votre `db.sqlite3` :
     ```bash
     # Télécharger la base de données
     # Dans l'onglet "Files", naviguez vers ~/mituna/
     # Cliquez sur db.sqlite3 pour le télécharger
     ```

---

## 🎓 Ressources utiles

- **Documentation PythonAnywhere** : https://help.pythonanywhere.com/
- **Forum d'aide** : https://www.pythonanywhere.com/forums/
- **Django deployment** : https://docs.djangoproject.com/en/5.0/howto/deployment/

---

## 🆘 Besoin d'aide ?

Si vous rencontrez des problèmes :

1. Consultez les logs dans l'onglet "Web" → "Log files"
2. Vérifiez la console Bash pour les erreurs
3. Consultez le forum PythonAnywhere
4. Vérifiez que tous les chemins sont corrects (remplacez votre-username)

---

**Bonne chance avec votre déploiement ! 🚀**
