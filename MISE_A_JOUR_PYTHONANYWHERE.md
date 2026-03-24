# 🚀 MISE À JOUR SUR PYTHONANYWHERE

## Étapes Rapides (Ligne de commande)

### 1️⃣ Ouvrir le Console Bash sur PythonAnywhere
- Allez sur : https://www.pythonanywhere.com
- Cliquez sur **"Consoles"** dans le menu
- Ouvrez un **"Bash console"**

### 2️⃣ Aller dans votre dossier
```bash
cd ~/mituna
```

### 3️⃣ Récupérer les modifications depuis GitHub
```bash
git pull origin main
```

### 4️⃣ Recharger l'application web
- **Option A - Depuis le console Bash :**
```bash
touch /var/www/hachokake_pythonanywhere_com_wsgi.py
```

- **Option B - Depuis l'interface Web :**
  1. Allez dans l'onglet **"Web"**
  2. Cliquez sur le bouton vert **"Reload"** à côté de votre application

### ✅ C'est tout !

---

## 🎯 Commandes Complètes (Copier-Coller)

```bash
# Aller dans le dossier du projet
cd ~/mituna

# Récupérer les dernières modifications
git pull origin main

# Recharger l'application
touch /var/www/hachokake_pythonanywhere_com_wsgi.py
```

---

## 🔧 Si vous avez des nouveaux packages (requirements.txt modifié)

```bash
cd ~/mituna
git pull origin main
pip install --user -r requirements.txt
touch /var/www/hachokake_pythonanywhere_com_wsgi.py
```

---

## 🗄️ Si vous avez des modifications de base de données (models.py modifié)

```bash
cd ~/mituna
git pull origin main
python manage.py makemigrations
python manage.py migrate
touch /var/www/hachokake_pythonanywhere_com_wsgi.py
```

---

## 📋 Vérifier que tout fonctionne

Après la mise à jour, testez :

1. **Page d'accueil** : `https://hachokake.pythonanywhere.com/`
2. **Page de debug** : `https://hachokake.pythonanywhere.com/debug/`
3. **Connexion admin** : `https://hachokake.pythonanywhere.com/admin/`

---

## ⚠️ En cas de problème

### Voir les logs d'erreur :
- Onglet **"Web"** → Section **"Log files"**
- Cliquez sur **"Error log"**

### Vérifier les fichiers statiques :
```bash
cd ~/mituna
python manage.py collectstatic --noinput
```

### Vérifier l'état de Git :
```bash
cd ~/mituna
git status
git log --oneline -5
```

---

## 🎉 Ce qui a été mis à jour aujourd'hui

✅ Correction du problème de connexion admin sur smartphone
✅ Ajout de l'icône d'œil pour voir le mot de passe
✅ Correction de l'affichage des sondages sur mobile
✅ Ajout de la page de debug `/debug/`
✅ Amélioration du CSS responsive

---

## 💡 Astuce : Script de mise à jour automatique

Créez un fichier `update.sh` sur PythonAnywhere :

```bash
#!/bin/bash
cd ~/mituna
echo "📥 Récupération des modifications..."
git pull origin main
echo "🔄 Rechargement de l'application..."
touch /var/www/hachokake_pythonanywhere_com_wsgi.py
echo "✅ Mise à jour terminée !"
```

Rendez-le exécutable :
```bash
chmod +x update.sh
```

Utilisez-le :
```bash
./update.sh
```
