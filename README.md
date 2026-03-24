# 🌟 Mituna - La Voix de Vos Questions

**Mituna** (qui signifie "questions" en lingala) - Une plateforme de sondages moderne et professionnelle, fièrement développée en RDC 🇨🇩

> *"Votre Question, Notre Mission"*

Une application Django élégante pour créer, gérer et analyser des sondages en ligne. Mituna incarne notre volonté de donner une voix à chaque personne et de transformer chaque question en opportunité de compréhension.

## ✨ Fonctionnalités

- 🎨 **Design Moderne et Responsive** - Interface utilisateur élégante avec Bootstrap 5
- 🖥️ **Interface d'Administration Personnalisée** - Panneau d'admin Django avec design professionnel
- 📊 **Types de Questions Variés** 
  - Texte libre
  - Choix unique (radio)
  - Choix multiples (checkbox)
  - Évaluation par étoiles (1-5)
- 📈 **Résultats en Temps Réel** - Visualisation instantanée des résultats avec graphiques
- 📊 **Rapport Statistique Professionnel** - Module complet style document Word
  - Dashboard interactif avec aperçu complet
  - Statistiques détaillées (participants, fréquences, pourcentages)
  - Graphiques professionnels (barres, circulaires, notations)
  - Tableaux récapitulatifs structurés
  - Conclusion automatique intelligente
  - Export PDF haute qualité prêt à l'impression
  - Aperçu avant téléchargement
- 👥 **Gestion des Participants** - Suivi optionnel des informations des participants
- 🔒 **Administration Complète** - Interface d'administration Django pour gérer les sondages
- 📥 **Export de Données** - Export optimisé CSV/HTML pour jusqu'à 10 000+ réponses
- 🌐 **Interface Multilingue** - Support du français
- 📱 **Mobile-First** - Parfaitement adapté aux mobiles et tablettes

## 🚀 Installation Rapide

### Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

### Étapes d'Installation

1. **Cloner ou télécharger le projet**
   ```bash
   cd sondage
   ```

2. **Créer un environnement virtuel**
   ```powershell
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Créer la base de données**
   ```powershell
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Créer un super utilisateur pour l'administration**
   
   **Option 1 : Via l'interface web (Recommandé)**
   ```powershell
   python manage.py runserver
   ```
   Puis visitez http://127.0.0.1:8000/ et cliquez sur "Créer mon Compte Administrateur"
   
   **Option 2 : Via la ligne de commande**
   ```powershell
   python manage.py createsuperuser
   ```
   Suivez les instructions pour créer votre compte administrateur.

6. **Lancer le serveur de développement**
   ```powershell
   python manage.py runserver
   ```

7. **Accéder à l'application**
   - Interface publique : http://127.0.0.1:8000/
   - Interface d'administration : http://127.0.0.1:8000/admin/
   
   > 💡 **Astuce** : L'interface d'administration a été entièrement personnalisée avec un design professionnel ! Consultez [ADMIN_README.md](ADMIN_README.md) pour plus de détails.

## 📖 Guide d'Utilisation

### Créer un Sondage

1. Connectez-vous à l'interface d'administration : http://127.0.0.1:8000/admin/
2. Cliquez sur **"Sondages"** puis **"Ajouter un sondage"**
3. Remplissez les informations :
   - Titre du sondage
   - Description
   - Dates de début et de fin
   - Paramètres (autoriser plusieurs soumissions, afficher les résultats, etc.)
4. Ajoutez des questions en utilisant la section "Questions" en bas de la page
5. Pour chaque question :
   - Saisissez le texte de la question
   - Choisissez le type (texte, choix unique, choix multiples, évaluation)
   - Marquez comme obligatoire si nécessaire
   - Définissez l'ordre d'affichage
6. Pour les questions à choix, ajoutez les options de réponse
7. Cliquez sur **"Enregistrer"**

### Répondre à un Sondage

1. Visitez la page d'accueil : http://127.0.0.1:8000/
2. Parcourez les sondages actifs
3. Cliquez sur **"Répondre au sondage"**
4. Remplissez vos informations (optionnel)
5. Répondez à toutes les questions
6. Cliquez sur **"Soumettre mes réponses"**

### Consulter les Résultats

1. Depuis la page d'accueil, cliquez sur **"Voir les résultats"**
2. Les résultats sont affichés avec :
   - Graphiques en barres pour les choix multiples
   - Moyenne et étoiles pour les évaluations
   - Liste des réponses textuelles

## 🎨 Personnalisation

### Modifier les Couleurs

Éditez le fichier `templates/base.html` et modifiez les variables CSS dans la section `:root` :

```css
:root {
    --primary-color: #6366f1;      /* Couleur principale */
    --secondary-color: #8b5cf6;     /* Couleur secondaire */
    --success-color: #10b981;       /* Couleur de succès */
    /* ... autres couleurs ... */
}
```

### Ajouter un Logo

Remplacez l'icône dans la navbar par votre logo dans `templates/base.html` :

```html
<a class="navbar-brand" href="{% url 'home' %}">
    <img src="{% static 'images/logo.png' %}" alt="Logo" height="40">
    Votre Nom
</a>
```

## 📊 Structure du Projet

```
sondage/
├── manage.py                          # Script de gestion Django
├── requirements.txt                   # Dépendances Python
├── sondage_project/                   # Configuration du projet
│   ├── __init__.py
│   ├── settings.py                    # Paramètres Django
│   ├── urls.py                        # URLs principales
│   ├── wsgi.py
│   └── asgi.py
├── surveys/                           # Application de sondages
│   ├── models.py                      # Modèles de données
│   ├── views.py                       # Vues/Contrôleurs
│   ├── urls.py                        # URLs de l'app
│   ├── admin.py                       # Configuration admin
│   └── migrations/                    # Migrations de base de données
└── templates/                         # Templates HTML
    ├── base.html                      # Template de base
    └── surveys/
        ├── home.html                  # Page d'accueil
        ├── survey_detail.html         # Formulaire de sondage
        └── survey_results.html        # Résultats
```

## 🔧 Configuration Avancée

### Changer la Base de Données

Par défaut, le projet utilise SQLite. Pour utiliser PostgreSQL ou MySQL, modifiez `settings.py` :

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nom_base',
        'USER': 'utilisateur',
        'PASSWORD': 'mot_de_passe',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Envoyer des Emails

Configurez les paramètres SMTP dans `settings.py` pour envoyer des notifications par email.

## 🛡️ Sécurité pour la Production

Avant de déployer en production :

1. Changez la `SECRET_KEY` dans `settings.py`
2. Définissez `DEBUG = False`
3. Configurez `ALLOWED_HOSTS` avec votre domaine
4. Utilisez HTTPS
5. Configurez les fichiers statiques avec `collectstatic`

## 📝 Modèles de Données

### Survey (Sondage)
- Titre, description
- Dates de début et fin
- Paramètres (actif, multiple soumissions, affichage résultats)

### Question
- Texte de la question
- Type (texte, choix unique, choix multiples, évaluation)
- Obligatoire ou optionnel
- Ordre d'affichage

### Choice (Choix)
- Texte du choix
- Lié à une question

### Response (Réponse)
- Informations du participant
- Date de soumission
- Lié à un sondage

### Answer (Réponse à une question)
- Réponse à une question spécifique
- Peut être : choix, texte, ou évaluation

## 📚 Documentation Détaillée

- **[RAPPORT_STATISTIQUE_GUIDE.md](RAPPORT_STATISTIQUE_GUIDE.md)** - Guide complet du module statistique professionnel
- **[ADMIN_README.md](ADMIN_README.md)** - Documentation de l'interface d'administration
- **[PERFORMANCE_EXPORT.md](PERFORMANCE_EXPORT.md)** - Guide d'optimisation des exports (1500+ réponses)
- **[ABOUT_MITUNA.md](ABOUT_MITUNA.md)** - Histoire et vision de la plateforme Mituna
- **[GUIDE_VISUEL.md](GUIDE_VISUEL.md)** - Guide visuel d'utilisation

## 🤝 Support

Pour toute question ou problème :
- Consultez la documentation Django : https://docs.djangoproject.com/
- Vérifiez les logs d'erreur dans le terminal

## 📄 Licence

Ce projet est libre d'utilisation pour des projets personnels et commerciaux.

## 🎉 Profitez de votre Plateforme de Sondages !

Votre application est maintenant prête à l'emploi. Créez votre premier sondage et commencez à collecter des réponses !
