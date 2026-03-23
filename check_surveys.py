"""
Script pour vérifier les sondages actifs
"""
import os
import sys
import django

# Configuration de Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sondage_project.settings')
django.setup()

from surveys.models import Survey
from django.utils import timezone
from django.db.models import Count, Q

def check_active_surveys():
    """Vérifie et affiche les sondages actifs"""
    print("=" * 60)
    print("VÉRIFICATION DES SONDAGES ACTIFS")
    print("=" * 60)
    print()
    
    # Tous les sondages
    all_surveys = Survey.objects.all()
    print(f"📊 Total de sondages dans la base: {all_surveys.count()}")
    print()
    
    if all_surveys.count() == 0:
        print("⚠️  Aucun sondage trouvé dans la base de données!")
        print("   Créez un sondage depuis l'interface admin.")
        return
    
    # Afficher tous les sondages
    print("Détails de tous les sondages:")
    print("-" * 60)
    for survey in all_surveys:
        print(f"\n📋 {survey.title}")
        print(f"   ID: {survey.id}")
        print(f"   Actif (is_active): {survey.is_active}")
        print(f"   Date de début: {survey.start_date}")
        print(f"   Date de fin: {survey.end_date if survey.end_date else 'Aucune'}")
        print(f"   Créé le: {survey.created_at}")
        print(f"   Méthode is_open(): {survey.is_open()}")
        print(f"   Réponses: {survey.responses.count()}")
    
    print("\n" + "=" * 60)
    
    # Sondages actifs selon la requête de la vue
    now = timezone.now()
    active_surveys = Survey.objects.filter(
        is_active=True,
        start_date__lte=now
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=now)
    ).annotate(
        response_count=Count('responses')
    )
    
    print(f"\n✅ Sondages actifs visibles sur la page d'accueil: {active_surveys.count()}")
    print()
    
    if active_surveys.count() == 0:
        print("⚠️  Aucun sondage actif trouvé!")
        print("\nPossibles raisons:")
        print("  1. Tous les sondages ont is_active=False")
        print("  2. Les dates de début sont dans le futur")
        print("  3. Les dates de fin sont dépassées")
        print("\nSolutions:")
        print("  - Connectez-vous à l'admin et vérifiez l'état des sondages")
        print("  - Assurez-vous qu'au moins un sondage a:")
        print("    • is_active = True")
        print("    • start_date <= maintenant")
        print("    • end_date = None OU end_date >= maintenant")
    else:
        print("Sondages actifs:")
        for survey in active_surveys:
            print(f"  ✓ {survey.title} ({survey.response_count} réponses)")
    
    print("\n" + "=" * 60)
    print(f"Date/heure actuelle du serveur: {now}")
    print("=" * 60)

if __name__ == "__main__":
    check_active_surveys()
