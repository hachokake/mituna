# 🚀 GUIDE DE DÉMARRAGE RAPIDE

## Méthode 1: Installation Automatique (Recommandée)

### Windows PowerShell

1. Ouvrez PowerShell dans le dossier du projet
2. Exécutez le script d'installation:
   ```powershell
   .\setup.ps1
   ```
3. Suivez les instructions à l'écran
4. Démarrez le serveur:
   ```powershell
   python manage.py runserver
   ```

## Méthode 2: Installation Manuelle

### Étape 1: Créer l'environnement virtuel
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### Étape 2: Installer les dépendances
```powershell
pip install -r requirements.txt
```

### Étape 3: Configurer la base de données
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Étape 4: Créer un administrateur

**Option 1 : Via l'interface web (Recommandé)**
1. Démarrez le serveur : `python manage.py runserver`
2. Ouvrez http://127.0.0.1:8000/
3. Cliquez sur "Créer mon Compte Administrateur"
4. Remplissez le formulaire et validez

**Option 2 : Via la ligne de commande**
```powershell
python manage.py createsuperuser
```

### Étape 5: (Optionnel) Charger des données de démonstration
```powershell
python create_sample_data.py
```

### Étape 6: Lancer le serveur
```powershell
python manage.py runserver
```

## 🌐 Accéder à l'Application

⚠️ **IMPORTANT** : Toujours utiliser **HTTP** et non HTTPS !

- **Site public**: http://127.0.0.1:8000/
- **Administration**: http://127.0.0.1:8000/admin/

> ❌ **Erreur courante** : N'utilisez PAS `https://` - le serveur de développement ne supporte que `http://`

## 📝 Premiers Pas

### Créer votre premier sondage

1. Connectez-vous à l'administration
2. Cliquez sur "Sondages" → "Ajouter un sondage"
3. Remplissez le formulaire:
   - Titre: "Mon Premier Sondage"
   - Description: Description de votre sondage
   - Cochez "Actif"
   - Cochez "Afficher les résultats"
4. Dans la section "Questions", cliquez sur "Ajouter une autre Question"
5. Remplissez les détails de la question
6. Pour les questions à choix, descendez et ajoutez des "Choix"
7. Cliquez sur "Enregistrer"

### Tester votre sondage

1. Visitez http://127.0.0.1:8000/
2. Votre sondage devrait apparaître
3. Cliquez sur "Répondre au sondage"
4. Remplissez et soumettez
5. Consultez les résultats

## 🎨 Personnalisation

### Changer le nom de l'application
Éditez `templates/base.html` ligne ~149:
```html
<a class="navbar-brand" href="{% url 'home' %}">
    <i class="fas fa-poll-h me-2"></i>VOTRE NOM
</a>
```

### Modifier les couleurs
Éditez `templates/base.html` dans la section `<style>`, modifiez les variables CSS:
```css
:root {
    --primary-color: #6366f1;  /* Votre couleur */
}
```

## ⚠️ Résolution de Problèmes

### Erreur: "No module named 'django'"
```powershell
pip install -r requirements.txt
```

### Erreur: "Execution of scripts is disabled"
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### La base de données n'est pas à jour
```powershell
python manage.py makemigrations
python manage.py migrate
```

### Erreur "You're accessing the development server over HTTPS"
Le serveur de développement Django ne supporte que HTTP.

**Solution** : Utilisez `http://127.0.0.1:8000/` (et non `https://`)

Si votre navigateur redirige automatiquement vers HTTPS :
- Utilisez le mode navigation privée
- Ou videz le cache du navigateur (Ctrl+Shift+Delete)

## 📞 Besoin d'Aide?

Consultez le fichier `README.md` pour la documentation complète.

---

**Bon sondage! 🎉**
