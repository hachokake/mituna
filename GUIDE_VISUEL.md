# 🚀 Guide de Démarrage Visuel - Sondages Pro

## 📋 Checklist d'Installation

- [ ] Python 3.8+ installé
- [ ] Environnement virtuel créé
- [ ] Dépendances installées
- [ ] Migrations effectuées
- [ ] Super utilisateur créé
- [ ] Serveur démarré

## 🎯 Étapes Rapides

### 1️⃣ Installation (PowerShell)

```powershell
# Aller dans le dossier du projet
cd "c:\Users\Ir. HACHOKAKE\Desktop\sondage"

# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

### 2️⃣ Configuration de la Base de Données

```powershell
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate
```

### 3️⃣ Créer un Administrateur

```powershell
python manage.py createsuperuser
```

Vous serez invité à saisir :
- **Nom d'utilisateur** : admin (ou votre choix)
- **Email** : votre@email.com
- **Mot de passe** : (minimum 8 caractères)
- **Confirmation** : (répéter le mot de passe)

### 4️⃣ (Optionnel) Charger des Données de Démonstration

```powershell
python create_sample_data.py
```

Cela créera :
- ✅ 3 sondages prêts à l'emploi
- ✅ Questions variées (texte, choix, étoiles)
- ✅ Choix de réponse configurés

### 5️⃣ Démarrer le Serveur

```powershell
python manage.py runserver
```

Vous verrez :
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

## 🌐 Accès à l'Application

⚠️ **IMPORTANT** : Utilisez toujours **HTTP** (et non HTTPS) pour le serveur de développement !

### Site Public
**URL** : http://127.0.0.1:8000/

❌ **N'utilisez PAS** : ~~https://127.0.0.1:8000/~~

**Fonctionnalités** :
- 📊 Voir tous les sondages actifs
- ✍️ Répondre aux sondages
- 📈 Consulter les résultats

### Administration
**URL** : http://127.0.0.1:8000/admin/

**Fonctionnalités** :
- 🎨 Interface moderne et personnalisée
- 📊 Tableau de bord avec statistiques
- ➕ Créer/Modifier des sondages
- 👥 Gérer les réponses
- 📈 Analyser les données

**Premier login** :
1. Aller à http://127.0.0.1:8000/admin/
2. Saisir le nom d'utilisateur créé
3. Saisir le mot de passe
4. Cliquer sur "Se connecter"

## 📝 Créer Votre Premier Sondage

### Via l'Administration

1. **Connectez-vous** à http://127.0.0.1:8000/admin/
2. Cliquez sur **"+ Nouveau Sondage"** (action rapide)
3. **Remplissez les champs** :
   ```
   Titre : "Satisfaction Client 2026"
   Description : "Aidez-nous à améliorer nos services"
   ☑ Actif
   ☑ Afficher les résultats
   ```
4. **Ajoutez des questions** (section en bas) :
   
   **Question 1** :
   - Texte : "Comment évaluez-vous notre service ?"
   - Type : Évaluation (1-5)
   - ☑ Obligatoire
   - Ordre : 1
   
   **Question 2** :
   - Texte : "Quel est votre niveau de satisfaction ?"
   - Type : Choix unique
   - ☑ Obligatoire
   - Ordre : 2
   - **Choix** :
     - Très satisfait
     - Satisfait
     - Neutre
     - Insatisfait
   
   **Question 3** :
   - Texte : "Vos suggestions d'amélioration ?"
   - Type : Texte libre
   - ☐ Obligatoire (optionnel)
   - Ordre : 3

5. **Enregistrer** et voilà ! 🎉

## 🧪 Tester Votre Sondage

1. Ouvrez http://127.0.0.1:8000/
2. Vous verrez votre sondage dans la liste
3. Cliquez sur **"Répondre au sondage"**
4. Remplissez toutes les questions
5. Cliquez sur **"Soumettre mes réponses"**
6. Consultez les **résultats** immédiatement

## 📊 Voir les Statistiques

Dans l'administration, vous verrez sur le tableau de bord :

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   📊 Sondages   │  │   👥 Réponses   │  │  ❓ Questions   │  │ ✅ Actifs       │
│                 │  │                 │  │                 │  │                 │
│       3         │  │       15        │  │       12        │  │       2         │
│                 │  │                 │  │                 │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘  └─────────────────┘
```

## 🎨 Personnalisation

### Changer le Nom

**Fichier** : `templates/base.html` (ligne ~149)
```html
<span>Mon Entreprise</span>
```

**Fichier** : `templates/admin/base_site.html` (section branding)
```html
<span>Mon Entreprise</span>
```

### Changer les Couleurs

**Fichier** : `templates/base.html` (section `<style>`)
```css
:root {
    --primary-color: #votre-couleur;
}
```

## ⚠️ Problèmes Courants

### ❌ "python n'est pas reconnu"
**Solution** : Installer Python depuis https://www.python.org/

### ❌ "Execution of scripts is disabled"
**Solution** : 
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### ❌ "No module named 'django'"
**Solution** : 
```powershell
pip install -r requirements.txt
```

### ❌ "Table doesn't exist"
**Solution** : 
```powershell
python manage.py migrate
```

## 📚 Ressources

- 📖 [README.md](README.md) - Documentation complète
- 🎨 [ADMIN_README.md](ADMIN_README.md) - Guide de l'administration
- 🚀 [DEMARRAGE_RAPIDE.md](DEMARRAGE_RAPIDE.md) - Guide rapide

## 💡 Conseils Pro

1. **Sauvegardez régulièrement** votre base de données `db.sqlite3`
2. **Testez sur mobile** pour vérifier la responsivité
3. **Utilisez les filtres** dans l'admin pour trouver rapidement
4. **Exportez les données** avant de faire des modifications importantes
5. **Changez la SECRET_KEY** avant de déployer en production

## 🎉 Prêt à Commencer !

Vous êtes maintenant prêt à créer des sondages professionnels !

**Commandes essentielles** :
```powershell
# Démarrer le serveur
python manage.py runserver

# Créer un super utilisateur
python manage.py createsuperuser

# Charger les exemples
python create_sample_data.py

# Réinitialiser la base de données
python manage.py flush
```

---

**Besoin d'aide ?** Consultez la documentation complète dans README.md

**Bon sondage ! 🚀**
