"""
Script pour réinitialiser les migrations et recréer la base de données
"""
import os
import django
import shutil

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sondage_project.settings')
django.setup()

from surveys.models import Response

print("=" * 50)
print("Réinitialisation de la base de données")
print("=" * 50)

# 1. Supprimer les anciennes réponses
print("\n1. Suppression des réponses existantes...")
count = Response.objects.count()
if count > 0:
    Response.objects.all().delete()
    print(f"   ✓ {count} réponse(s) supprimée(s)")
else:
    print("   ✓ Aucune réponse à supprimer")

# 2. Supprimer les migrations
print("\n2. Suppression des anciens fichiers de migration...")
migrations_dir = "surveys/migrations"
if os.path.exists(migrations_dir):
    for file in os.listdir(migrations_dir):
        if file.endswith('.py') and file != '__init__.py':
            file_path = os.path.join(migrations_dir, file)
            os.remove(file_path)
            print(f"   ✓ Supprimé: {file}")
else:
    print("   ℹ Dossier migrations n'existe pas")

# 3. Supprimer la base de données
print("\n3. Suppression de la base de données...")
if os.path.exists('db.sqlite3'):
    os.remove('db.sqlite3')
    print("   ✓ db.sqlite3 supprimée")
else:
    print("   ℹ db.sqlite3 n'existe pas")

print("\n" + "=" * 50)
print("✓ Réinitialisation terminée!")
print("=" * 50)
print("\nMaintenant, exécutez:")
print("  1. python manage.py makemigrations")
print("  2. python manage.py migrate")
print("  3. python manage.py createsuperuser (optionnel)")
print("  4. python manage.py runserver")
