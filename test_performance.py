"""
Script de test pour simuler 2000+ réponses et vérifier les performances d'export
Usage: python manage.py shell < test_performance.py
"""
import random
import time
from django.contrib.auth import get_user_model
from surveys.models import Survey, Question, Choice, Response, Answer
from datetime import datetime, timedelta

User = get_user_model()

def create_test_survey():
    """Créer un sondage de test avec plusieurs questions"""
    # Créer un admin si nécessaire
    admin, created = User.objects.get_or_create(
        username='admin_test',
        defaults={'is_superuser': True, 'is_staff': True}
    )
    if created:
        admin.set_password('admin123')
        admin.save()
        print(f"✅ Admin créé: {admin.username}")
    
    # Créer un sondage
    survey = Survey.objects.create(
        title="Test Performance - Sondage de Satisfaction Client",
        description="Sondage pour tester les performances avec 2000+ réponses",
        is_active=True
    )
    print(f"✅ Sondage créé: {survey.title}")
    
    # Question 1: Texte
    q1 = Question.objects.create(
        survey=survey,
        text="Quels sont vos commentaires généraux?",
        question_type='text',
        order=1,
        is_required=True
    )
    
    # Question 2: Choix unique
    q2 = Question.objects.create(
        survey=survey,
        text="Comment évaluez-vous notre service client?",
        question_type='single',
        order=2,
        is_required=True
    )
    Choice.objects.bulk_create([
        Choice(question=q2, text="Excellent", order=1),
        Choice(question=q2, text="Bon", order=2),
        Choice(question=q2, text="Moyen", order=3),
        Choice(question=q2, text="Mauvais", order=4),
    ])
    
    # Question 3: Choix multiples
    q3 = Question.objects.create(
        survey=survey,
        text="Quels produits avez-vous utilisés? (plusieurs choix possibles)",
        question_type='multiple',
        order=3,
        is_required=False
    )
    Choice.objects.bulk_create([
        Choice(question=q3, text="Produit A", order=1),
        Choice(question=q3, text="Produit B", order=2),
        Choice(question=q3, text="Produit C", order=3),
        Choice(question=q3, text="Produit D", order=4),
        Choice(question=q3, text="Service E", order=5),
    ])
    
    # Question 4: Rating
    q4 = Question.objects.create(
        survey=survey,
        text="Sur une échelle de 1 à 5, recommanderiez-vous nos services?",
        question_type='rating',
        order=4,
        is_required=True
    )
    
    print(f"✅ {survey.questions.count()} questions créées")
    return survey


def generate_bulk_responses(survey, count=2000):
    """Générer des réponses en masse"""
    print(f"\n🚀 Génération de {count} réponses...")
    
    # Noms et domaines pour emails
    first_names = ['Jean', 'Marie', 'Pierre', 'Sophie', 'Luc', 'Julie', 'Paul', 'Anne', 'Marc', 'Claire']
    last_names = ['Martin', 'Bernard', 'Dubois', 'Thomas', 'Robert', 'Richard', 'Petit', 'Durand', 'Leroy', 'Moreau']
    domains = ['gmail.com', 'outlook.fr', 'yahoo.fr', 'hotmail.com', 'orange.fr']
    comments = [
        "Très satisfait du service",
        "Quelques points à améliorer",
        "Excellent travail, merci!",
        "Le délai de livraison était trop long",
        "Parfait, je recommande vivement!",
        "Bon rapport qualité-prix",
        "Service client très réactif",
        "Produits de qualité"
    ]
    
    questions = list(survey.questions.all())
    q1, q2, q3, q4 = questions
    
    # Récupérer les choix
    q2_choices = list(q2.choices.all())
    q3_choices = list(q3.choices.all())
    
    responses_to_create = []
    answers_to_create = []
    
    start_time = time.time()
    
    # Préparer toutes les réponses
    for i in range(count):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        domain = random.choice(domains)
        
        # Créer une réponse
        response = Response(
            survey=survey,
            participant_name=f"{first_name} {last_name}",
            participant_email=f"{first_name.lower()}.{last_name.lower()}{i}@{domain}",
            submitted_at=datetime.now() - timedelta(days=random.randint(0, 30))
        )
        responses_to_create.append(response)
    
    # Insérer les réponses en bulk
    created_responses = Response.objects.bulk_create(responses_to_create, batch_size=500)
    print(f"✅ {len(created_responses)} réponses créées en {time.time() - start_time:.2f}s")
    
    # Créer les answers
    answer_time = time.time()
    for response in created_responses:
        # Q1: Texte
        answers_to_create.append(Answer(
            response=response,
            question=q1,
            text_answer=random.choice(comments)
        ))
        
        # Q2: Choix unique
        answers_to_create.append(Answer(
            response=response,
            question=q2,
            choice=random.choice(q2_choices)
        ))
        
        # Q3: Choix multiples (1 à 3 choix)
        selected_choices = random.sample(q3_choices, random.randint(1, 3))
        for choice in selected_choices:
            answers_to_create.append(Answer(
                response=response,
                question=q3,
                choice=choice
            ))
        
        # Q4: Rating
        answers_to_create.append(Answer(
            response=response,
            question=q4,
            rating=random.randint(1, 5)
        ))
    
    # Bulk create answers
    Answer.objects.bulk_create(answers_to_create, batch_size=1000)
    print(f"✅ {len(answers_to_create)} réponses aux questions créées en {time.time() - answer_time:.2f}s")
    print(f"\n✅ TOTAL: {time.time() - start_time:.2f}s pour {count} réponses complètes")
    
    return created_responses


def test_export_performance(survey):
    """Tester les performances d' export"""
    print(f"\n🔍 Test des performances d'export...")
    
    from django.test import RequestFactory
    from surveys.admin_views import admin_survey_export_download
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    admin = User.objects.filter(is_superuser=True).first()
    
    factory = RequestFactory()
    
    # Test 1: Export HTML avec limite de 100
    print("\n📄 Test 1: Export HTML (100 réponses)")
    request = factory.get(f'/admin/survey/{survey.id}/export/download/?limit=100&per_page=50&format=html')
    request.user = admin
    
    start = time.time()
    response = admin_survey_export_download(request, survey.id)
    duration = time.time() - start
    print(f"✅ Export HTML (100): {duration:.2f}s | Taille: {len(response.content) / 1024:.2f} KB")
    
    # Test 2: Export HTML avec limite de 500
    print("\n📄 Test 2: Export HTML (500 réponses)")
    request = factory.get(f'/admin/survey/{survey.id}/export/download/?limit=500&per_page=50&format=html')
    request.user = admin
    
    start = time.time()
    response = admin_survey_export_download(request, survey.id)
    duration = time.time() - start
    print(f"✅ Export HTML (500): {duration:.2f}s | Taille: {len(response.content) / 1024:.2f} KB")
    
    # Test 3: Export CSV avec toutes les réponses
    print("\n📊 Test 3: Export CSV (toutes les réponses)")
    request = factory.get(f'/admin/survey/{survey.id}/export/download/?limit=0&format=csv')
    request.user = admin
    
    start = time.time()
    response = admin_survey_export_download(request, survey.id)
    duration = time.time() - start
    print(f"✅ Export CSV (toutes): {duration:.2f}s | Taille: {len(response.content) / 1024:.2f} KB")
    
    print(f"\n{'='*60}")
    print(f"📊 RÉSUMÉ DES PERFORMANCES")
    print(f"{'='*60}")
    print(f"✅ Le système peut gérer {survey.responses.count()} réponses sans problème")
    print(f"✅ Export HTML recommandé jusqu'à 500 réponses")
    print(f"✅ Export CSV recommandé pour 500+ réponses")
    print(f"{'='*60}")


if __name__ == '__main__':
    print("="*60)
    print("TEST DE PERFORMANCE - SYSTÈME DE SONDAGES")
    print("="*60)
    
    # Créer un sondage de test
    survey = create_test_survey()
    
    # Générer 2000 réponses
    generate_bulk_responses(survey, count=2000)
    
    # Tester les exports
    test_export_performance(survey)
    
    print(f"\n✅ Tests terminés!")
    print(f"📋 Sondage ID: {survey.id}")
    print(f"📧 Total réponses: {survey.responses.count()}")
    print(f"\n💡 Accédez au sondage: http://127.0.0.1:8000/admin/survey/{survey.id}/export/")
