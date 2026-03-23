from django.shortcuts import redirect
from django.contrib.auth.models import User


class AdminSetupMiddleware:
    """
    Middleware qui redirige vers la page d'inscription admin
    si aucun superutilisateur n'existe et qu'on tente d'accéder au dashboard
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # URLs qui ne nécessitent PAS de redirection (accessibles sans superutilisateur)
        exempt_paths = [
            '/admin/register/',
            '/admin/login/',
        ]
        
        # Si on est sur une page exemptée, ne rien faire
        if request.path in exempt_paths:
            response = self.get_response(request)
            return response
        
        # Pour toutes les autres pages /admin/*, vérifier si un superutilisateur existe
        if request.path.startswith('/admin'):
            if not User.objects.filter(is_superuser=True).exists():
                # Rediriger vers la page d'inscription
                return redirect('/admin/register/')
        
        response = self.get_response(request)
        return response
