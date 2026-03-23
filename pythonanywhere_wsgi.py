# Configuration WSGI pour PythonAnywhere
# Ce fichier doit être utilisé dans la configuration WSGI de PythonAnywhere

import os
import sys

# ⚠️ IMPORTANT: Remplacez 'votre-username' par votre vrai nom d'utilisateur PythonAnywhere
path = '/home/votre-username/mituna'
if path not in sys.path:
    sys.path.append(path)

# Définir le module de settings Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'sondage_project.settings'

# Charger l'application WSGI Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
