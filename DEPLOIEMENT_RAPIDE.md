# 🚀 Guide Rapide de Déploiement PythonAnywhere

Guide condensé pour un déploiement rapide. Pour les détails complets, consultez [DEPLOIEMENT_PYTHONANYWHERE.md](DEPLOIEMENT_PYTHONANYWHERE.md).

---

## 📋 Résumé en 5 minutes

### 1️⃣ Créez un compte PythonAnywhere
- Allez sur https://www.pythonanywhere.com
- Créez un compte gratuit
- Votre domaine sera : `votre-username.pythonanywhere.com`

### 2️⃣ Dans la console Bash PythonAnywhere

```bash
# Cloner le projet
git clone https://github.com/hachokake/mituna.git
cd mituna

# Créer l'environnement virtuel
mkvirtualenv --python=/usr/bin/python3.10 mituna-venv

# Installer les dépendances
pip install -r requirements.txt

# Créer le fichier .env
nano .env
```

Contenu du .env :
```env
SECRET_KEY=votre-cle-secrete-a-generer
DEBUG=False
ALLOWED_HOSTS=votre-username.pythonanywhere.com
```

Générer une SECRET_KEY :
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

```bash
# Initialiser la base de données
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

### 3️⃣ Configurer l'application Web

Dans l'onglet **Web** de PythonAnywhere :

1. **Créer une Web App**
   - Add a new web app → Manual configuration → Python 3.10

2. **Virtual Environment**
   - Chemin : `/home/votre-username/.virtualenvs/mituna-venv`

3. **WSGI Configuration**
   - Cliquez sur le lien du fichier WSGI
   - Supprimez tout et collez (remplacez `votre-username`) :

```python
import os
import sys

path = '/home/votre-username/mituna'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'sondage_project.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4. **Static Files**
   - URL: `/static/` → Directory: `/home/votre-username/mituna/staticfiles`
   - URL: `/media/` → Directory: `/home/votre-username/mituna/media`

5. **Reload**
   - Cliquez sur le bouton vert "Reload"

### 4️⃣ C'est prêt ! 🎉

Votre site est accessible à : `https://votre-username.pythonanywhere.com`

---

## 🔄 Mises à jour

```bash
cd ~/mituna
workon mituna-venv
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
# Puis cliquez sur "Reload" dans l'onglet Web
```

---

## 🐛 Dépannage

**Site ne charge pas ?**
- Vérifiez les logs : Onglet Web → Log files → Error log
- Vérifiez que vous avez remplacé `votre-username` partout

**CSS ne charge pas ?**
- Vérifiez les chemins des Static files
- Réexécutez : `python manage.py collectstatic --clear --noinput`

**Erreur 500 ?**
- Regardez l'Error log
- Vérifiez le fichier .env
- Vérifiez ALLOWED_HOSTS

---

## 📚 Documentation complète

- [Guide détaillé de déploiement](DEPLOIEMENT_PYTHONANYWHERE.md) - Instructions complètes étape par étape
- [Checklist de déploiement](CHECKLIST_DEPLOIEMENT.md) - Liste de vérification complète
- [Configuration WSGI](pythonanywhere_wsgi.py) - Fichier WSGI prêt à l'emploi
- [Variables d'environnement](.env.pythonanywhere) - Template pour .env

---

## ⚠️ Points importants

1. ✅ Remplacez **TOUJOURS** `votre-username` par votre vrai nom d'utilisateur
2. ✅ Générez une vraie SECRET_KEY pour la production
3. ✅ Assurez-vous que DEBUG=False en production
4. ✅ Ne commitez JAMAIS votre fichier .env sur GitHub
5. ✅ Sauvegardez régulièrement votre base de données

---

## 💡 Conseils

- **Compte gratuit** : Suffisant pour débuter, 512 MB d'espace
- **SQLite** : Suffisant jusqu'à ~10,000 réponses
- **HTTPS** : Inclus automatiquement avec PythonAnywhere
- **Domaine personnalisé** : Nécessite un compte payant (à partir de 5$/mois)

---

## 🆘 Besoin d'aide ?

1. Consultez l'Error log dans l'onglet Web
2. Lisez le [guide détaillé](DEPLOIEMENT_PYTHONANYWHERE.md)
3. Vérifiez la [checklist](CHECKLIST_DEPLOIEMENT.md)
4. Forum PythonAnywhere : https://www.pythonanywhere.com/forums/

---

**Bonne chance ! 🚀**
