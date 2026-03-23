"""
Script pour créer des données de démonstration
Exécuter avec: python create_sample_data.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sondage_project.settings')
django.setup()

from surveys.models import Survey, Question, Choice
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

def create_sample_surveys():
    print("Création des sondages de démonstration...")
    
    # Obtenir ou créer un utilisateur admin
    user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        user.set_password('admin123')
        user.save()
        print(f"✓ Utilisateur admin créé (username: admin, password: admin123)")
    
    # Sondage 1: Satisfaction Client
    survey1 = Survey.objects.create(
        title="Enquête de Satisfaction Client 2026",
        description="Aidez-nous à améliorer nos services en partageant votre expérience. Vos réponses sont précieuses pour nous!",
        created_by=user,
        is_active=True,
        allow_multiple_submissions=False,
        show_results=True,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=30)
    )
    
    q1 = Question.objects.create(
        survey=survey1,
        text="Comment évaluez-vous votre expérience globale avec nos services ?",
        question_type='rating',
        is_required=True,
        order=1
    )
    
    q2 = Question.objects.create(
        survey=survey1,
        text="Quel est votre niveau de satisfaction concernant la qualité de nos produits ?",
        question_type='single',
        is_required=True,
        order=2
    )
    Choice.objects.create(question=q2, text="Très satisfait", order=1)
    Choice.objects.create(question=q2, text="Satisfait", order=2)
    Choice.objects.create(question=q2, text="Neutre", order=3)
    Choice.objects.create(question=q2, text="Insatisfait", order=4)
    Choice.objects.create(question=q2, text="Très insatisfait", order=5)
    
    q3 = Question.objects.create(
        survey=survey1,
        text="Quels aspects de notre service appréciez-vous le plus ? (plusieurs choix possibles)",
        question_type='multiple',
        is_required=False,
        order=3
    )
    Choice.objects.create(question=q3, text="Qualité du produit", order=1)
    Choice.objects.create(question=q3, text="Service client", order=2)
    Choice.objects.create(question=q3, text="Rapidité de livraison", order=3)
    Choice.objects.create(question=q3, text="Prix compétitifs", order=4)
    Choice.objects.create(question=q3, text="Facilité d'utilisation", order=5)
    
    q4 = Question.objects.create(
        survey=survey1,
        text="Avez-vous des suggestions pour améliorer nos services ?",
        question_type='text',
        is_required=False,
        order=4
    )
    
    print(f"✓ Sondage créé: {survey1.title}")
    
    # Sondage 2: Préférences Alimentaires
    survey2 = Survey.objects.create(
        title="Sondage sur les Habitudes Alimentaires",
        description="Participez à notre étude sur les préférences et habitudes alimentaires de la population.",
        created_by=user,
        is_active=True,
        allow_multiple_submissions=False,
        show_results=True,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=60)
    )
    
    q5 = Question.objects.create(
        survey=survey2,
        text="Combien de fois par semaine mangez-vous des fruits et légumes ?",
        question_type='single',
        is_required=True,
        order=1
    )
    Choice.objects.create(question=q5, text="Tous les jours", order=1)
    Choice.objects.create(question=q5, text="5-6 fois par semaine", order=2)
    Choice.objects.create(question=q5, text="3-4 fois par semaine", order=3)
    Choice.objects.create(question=q5, text="1-2 fois par semaine", order=4)
    Choice.objects.create(question=q5, text="Rarement ou jamais", order=5)
    
    q6 = Question.objects.create(
        survey=survey2,
        text="Suivez-vous un régime alimentaire particulier ?",
        question_type='multiple',
        is_required=False,
        order=2
    )
    Choice.objects.create(question=q6, text="Végétarien", order=1)
    Choice.objects.create(question=q6, text="Végétalien", order=2)
    Choice.objects.create(question=q6, text="Sans gluten", order=3)
    Choice.objects.create(question=q6, text="Faible en glucides", order=4)
    Choice.objects.create(question=q6, text="Aucun régime spécifique", order=5)
    
    q7 = Question.objects.create(
        survey=survey2,
        text="Dans quelle mesure la santé influence-t-elle vos choix alimentaires ?",
        question_type='rating',
        is_required=True,
        order=3
    )
    
    q8 = Question.objects.create(
        survey=survey2,
        text="Quels sont vos principaux obstacles à une alimentation saine ?",
        question_type='text',
        is_required=False,
        order=4
    )
    
    print(f"✓ Sondage créé: {survey2.title}")
    
    # Sondage 3: Technologie et Télétravail
    survey3 = Survey.objects.create(
        title="Enquête sur le Télétravail et les Outils Numériques",
        description="Partagez votre expérience du télétravail et l'utilisation des outils numériques dans votre quotidien professionnel.",
        created_by=user,
        is_active=True,
        allow_multiple_submissions=True,
        show_results=True,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=45)
    )
    
    q9 = Question.objects.create(
        survey=survey3,
        text="À quelle fréquence travaillez-vous à distance ?",
        question_type='single',
        is_required=True,
        order=1
    )
    Choice.objects.create(question=q9, text="100% télétravail", order=1)
    Choice.objects.create(question=q9, text="3-4 jours par semaine", order=2)
    Choice.objects.create(question=q9, text="1-2 jours par semaine", order=3)
    Choice.objects.create(question=q9, text="Occasionnellement", order=4)
    Choice.objects.create(question=q9, text="Jamais", order=5)
    
    q10 = Question.objects.create(
        survey=survey3,
        text="Quels outils utilisez-vous pour le télétravail ? (plusieurs réponses possibles)",
        question_type='multiple',
        is_required=True,
        order=2
    )
    Choice.objects.create(question=q10, text="Zoom / Teams / Meet", order=1)
    Choice.objects.create(question=q10, text="Slack / Discord", order=2)
    Choice.objects.create(question=q10, text="Trello / Asana", order=3)
    Choice.objects.create(question=q10, text="Google Workspace", order=4)
    Choice.objects.create(question=q10, text="Microsoft 365", order=5)
    
    q11 = Question.objects.create(
        survey=survey3,
        text="Comment évaluez-vous votre productivité en télétravail ?",
        question_type='rating',
        is_required=True,
        order=3
    )
    
    q12 = Question.objects.create(
        survey=survey3,
        text="Quels sont les principaux défis du télétravail pour vous ?",
        question_type='text',
        is_required=False,
        order=4
    )
    
    print(f"✓ Sondage créé: {survey3.title}")
    
    print("\n" + "="*60)
    print("✓ Données de démonstration créées avec succès!")
    print("="*60)
    print(f"\nTrois sondages ont été créés:")
    print(f"1. {survey1.title}")
    print(f"2. {survey2.title}")
    print(f"3. {survey3.title}")
    print(f"\nVous pouvez maintenant:")
    print("- Visiter http://127.0.0.1:8000/ pour voir les sondages")
    print("- Vous connecter à http://127.0.0.1:8000/admin/ avec:")
    print("  Username: admin")
    print("  Password: admin123")

if __name__ == '__main__':
    # Supprimer les données existantes (optionnel)
    Survey.objects.all().delete()
    print("Anciennes données supprimées.\n")
    
    # Créer les nouvelles données
    create_sample_surveys()
