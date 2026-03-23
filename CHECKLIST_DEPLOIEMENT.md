# ✅ Checklist de Déploiement PythonAnywhere

Utilisez cette checklist pour vous assurer que tout est configuré correctement.

---

## ⏰ Avant le déploiement (sur votre PC)

- [ ] Code poussé sur GitHub avec les dernières modifications
- [ ] `.gitignore` configuré correctement (db.sqlite3, .env, etc.)
- [ ] `requirements.txt` à jour
- [ ] Testé localement que tout fonctionne

---

## 🔧 Sur PythonAnywhere - Configuration initiale

### Compte et Console
- [ ] Compte PythonAnywhere créé et confirmé
- [ ] Console Bash ouverte

### Repository Git
- [ ] Repository cloné : `git clone https://github.com/hachokake/mituna.git`
- [ ] Entré dans le dossier : `cd mituna`

### Environnement Python
- [ ] Environnement virtuel créé : `mkvirtualenv --python=/usr/bin/python3.10 mituna-venv`
- [ ] Dépendances installées : `pip install -r requirements.txt`

### Configuration
- [ ] Fichier `.env` créé avec :
  - [ ] SECRET_KEY générée
  - [ ] DEBUG=False
  - [ ] ALLOWED_HOSTS avec votre domaine PythonAnywhere
- [ ] Variables d'environnement vérifiées

### Base de données
- [ ] Migrations appliquées : `python manage.py migrate`
- [ ] Superutilisateur créé : `python manage.py createsuperuser`
- [ ] Fichiers statiques collectés : `python manage.py collectstatic --noinput`

---

## 🌐 Configuration Web App

### Création de l'application
- [ ] Web App créée (onglet "Web" → "Add a new web app")
- [ ] "Manual configuration" sélectionné (PAS Django)
- [ ] Python 3.10 sélectionné

### Virtual Environment
- [ ] Chemin du virtualenv configuré : `/home/VOTRE-USERNAME/.virtualenvs/mituna-venv`
- [ ] ⚠️ Remplacé "VOTRE-USERNAME" par le vrai nom d'utilisateur

### Fichier WSGI
- [ ] Fichier WSGI ouvert (lien bleu dans section "Code")
- [ ] Tout le contenu ancien supprimé
- [ ] Nouveau contenu copié depuis `pythonanywhere_wsgi.py`
- [ ] ⚠️ Remplacé "VOTRE-USERNAME" dans le chemin
- [ ] Fichier sauvegardé

### Fichiers Statiques
- [ ] URL `/static/` configurée → Directory `/home/VOTRE-USERNAME/mituna/staticfiles`
- [ ] URL `/media/` configurée → Directory `/home/VOTRE-USERNAME/mituna/media`
- [ ] ⚠️ Remplacé "VOTRE-USERNAME" dans les deux chemins

---

## 🚀 Lancement

- [ ] Bouton "Reload" cliqué en haut de l'onglet Web
- [ ] Attendre quelques secondes
- [ ] Site visité : `https://VOTRE-USERNAME.pythonanywhere.com`
- [ ] Page d'accueil s'affiche correctement
- [ ] Connection à l'admin testée : `/admin/`

---

## 🧪 Tests post-déploiement

### Fonctionnalités de base
- [ ] Page d'accueil accessible
- [ ] Navigation entre les pages fonctionne
- [ ] Fichiers statiques (CSS, JS, images) chargent correctement

### Interface Admin
- [ ] Connection à `/admin/` réussie
- [ ] Dashboard administrateur s'affiche
- [ ] Création d'un sondage test
- [ ] Ajout de questions au sondage

### Sondages publics
- [ ] Affichage d'un sondage public
- [ ] Soumission d'une réponse
- [ ] Visualisation des résultats

### Export de réponses
- [ ] Page d'export accessible
- [ ] Sélection manuelle des réponses fonctionne
- [ ] Aperçu HTML fonctionne
- [ ] Téléchargement CSV fonctionne
- [ ] Téléchargement HTML fonctionne

---

## 🐛 En cas de problème

### Vérifications de base
- [ ] Error log consulté (onglet Web → Log files → Error log)
- [ ] Server log consulté (onglet Web → Log files → Server log)
- [ ] Tous les chemins vérifiés (username remplacé partout)

### Problèmes courants

#### Site ne charge pas
- [ ] Error log vérifié pour les détails
- [ ] Chemin dans WSGI correct
- [ ] Virtual environment path correct
- [ ] `DEBUG=True` temporairement pour voir l'erreur

#### CSS/JS ne chargent pas
- [ ] Chemins des fichiers statiques vérifiés dans l'onglet Web
- [ ] `python manage.py collectstatic --noinput` réexécuté
- [ ] Navigation forcée rafraîchie (Ctrl + F5)

#### Erreur 500
- [ ] Logs consultés
- [ ] `.env` vérifié (présent et correct)
- [ ] `ALLOWED_HOSTS` vérifié dans .env
- [ ] Migrations appliquées

#### Erreur de base de données
- [ ] Migrations vérifiées : `python manage.py showmigrations`
- [ ] Migrations réappliquées si nécessaire

---

## 🔄 Mises à jour futures

Quand vous faites des modifications :

- [ ] Code pushé sur GitHub : `git push origin main`
- [ ] Sur PythonAnywhere, dans la console :
  - [ ] `cd ~/mituna`
  - [ ] `workon mituna-venv`
  - [ ] `git pull origin main`
  - [ ] `pip install -r requirements.txt` (si dépendances changées)
  - [ ] `python manage.py migrate` (si models changés)
  - [ ] `python manage.py collectstatic --noinput` (si fichiers statiques changés)
- [ ] Bouton "Reload" cliqué dans l'onglet Web
- [ ] Site testé

---

## 📝 Notes importantes

### Sécurité
- [ ] `.env` JAMAIS commité sur GitHub
- [ ] `DEBUG=False` en production
- [ ] `SECRET_KEY` différente de celle de développement

### Performance
- [ ] SQLite suffisant pour <10,000 réponses
- [ ] Pour plus, considérer MySQL (compte payant)

### Sauvegardes
- [ ] Base de données sauvegardée régulièrement
- [ ] Fichiers media sauvegardés si nécessaire

---

## ✅ Déploiement réussi !

Si toutes les cases sont cochées, félicitations ! 🎉

Votre application est en ligne à : `https://VOTRE-USERNAME.pythonanywhere.com`

---

**Date de déploiement** : ________________

**Nom d'utilisateur PythonAnywhere** : ________________

**URL de l'application** : ________________

**Notes** : 
_____________________________________________
_____________________________________________
_____________________________________________
