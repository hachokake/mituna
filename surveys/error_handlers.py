"""
Gestion globale des erreurs pour une expérience utilisateur professionnelle
Ce module capture toutes les exceptions et les transforme en réponses propres
"""

import logging
import traceback
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.conf import settings
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.http import Http404

# Configuration du logger
logger = logging.getLogger('surveys.errors')


class GlobalErrorHandlerMiddleware:
    """
    Middleware de gestion globale des erreurs
    Capture toutes les exceptions non gérées et les transforme en réponses utilisateur propres
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Gérer l'exception de manière globale
            return self.handle_exception(request, e)
    
    def handle_exception(self, request, exception):
        """Traite l'exception et retourne une réponse appropriée"""
        
        # Logger l'erreur avec le stack trace complet (côté serveur uniquement)
        error_info = {
            'url': request.path,
            'method': request.method,
            'user': request.user.username if request.user.is_authenticated else 'Anonymous',
            'ip': self.get_client_ip(request),
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'stack_trace': traceback.format_exc()
        }
        
        logger.error(
            f"Erreur non gérée: {error_info['exception_type']} - {error_info['exception_message']}\n"
            f"URL: {error_info['url']}\n"
            f"Utilisateur: {error_info['user']}\n"
            f"Stack trace:\n{error_info['stack_trace']}"
        )
        
        # Déterminer le type d'erreur et retourner la réponse appropriée
        if isinstance(exception, Http404):
            return self.handle_404(request)
        elif isinstance(exception, PermissionDenied):
            return self.handle_403(request)
        elif isinstance(exception, ObjectDoesNotExist):
            return self.handle_not_found(request)
        else:
            return self.handle_500(request, exception)
    
    def handle_404(self, request):
        """Gestion des erreurs 404 - Page non trouvée"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': True,
                'message': 'La ressource demandée n\'existe pas.'
            }, status=404)
        
        return render(request, 'errors/404.html', status=404)
    
    def handle_403(self, request):
        """Gestion des erreurs 403 - Accès refusé"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': True,
                'message': 'Vous n\'avez pas la permission d\'accéder à cette ressource.'
            }, status=403)
        
        return render(request, 'errors/403.html', status=403)
    
    def handle_not_found(self, request):
        """Gestion des objets non trouvés"""
        messages.error(request, "La ressource demandée n'existe plus ou a été supprimée.")
        return redirect('home')
    
    def handle_500(self, request, exception):
        """Gestion des erreurs serveur 500"""
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'error': True,
                'message': 'Une erreur est survenue. Veuillez réessayer ultérieurement.'
            }, status=500)
        
        # En production, ne jamais exposer les détails
        context = {}
        if settings.DEBUG:
            context['debug_info'] = {
                'exception': str(exception),
                'type': type(exception).__name__
            }
        
        return render(request, 'errors/500.html', context, status=500)
    
    def get_client_ip(self, request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def process_exception(self, request, exception):
        """
        Hook Django pour capturer les exceptions
        Appelé automatiquement quand une exception n'est pas gérée dans une vue
        """
        return self.handle_exception(request, exception)


def custom_404_handler(request, exception):
    """Handler personnalisé pour les erreurs 404"""
    logger.warning(f"404 Error: {request.path} - User: {request.user}")
    return render(request, 'errors/404.html', status=404)


def custom_403_handler(request, exception):
    """Handler personnalisé pour les erreurs 403"""
    logger.warning(f"403 Error: {request.path} - User: {request.user}")
    return render(request, 'errors/403.html', status=403)


def custom_500_handler(request):
    """Handler personnalisé pour les erreurs 500"""
    logger.error(f"500 Error: {request.path} - User: {request.user}")
    return render(request, 'errors/500.html', status=500)


class SafeViewMixin:
    """
    Mixin pour sécuriser les vues avec gestion d'erreurs automatique
    Utilisation: class MyView(SafeViewMixin, View)
    """
    
    def dispatch(self, request, *args, **kwargs):
        """Enveloppe le dispatch avec gestion d'erreurs"""
        try:
            return super().dispatch(request, *args, **kwargs)
        except ObjectDoesNotExist:
            messages.error(request, "L'élément demandé n'existe pas ou a été supprimé.")
            return redirect('home')
        except PermissionDenied:
            messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
            return redirect('home')
        except Exception as e:
            logger.error(f"Erreur dans {self.__class__.__name__}: {str(e)}\n{traceback.format_exc()}")
            messages.error(request, "Une erreur est survenue. Veuillez réessayer.")
            return redirect('home')


def safe_view_decorator(view_func):
    """
    Décorateur pour sécuriser les vues fonction avec gestion d'erreurs
    
    Usage:
    @safe_view_decorator
    def my_view(request):
        ...
    """
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except ObjectDoesNotExist:
            messages.error(request, "L'élément demandé n'existe pas ou a été supprimé.")
            return redirect('home')
        except PermissionDenied:
            messages.error(request, "Vous n'avez pas la permission d'effectuer cette action.")
            return redirect('home')
        except Http404:
            return render(request, 'errors/404.html', status=404)
        except Exception as e:
            logger.error(f"Erreur dans {view_func.__name__}: {str(e)}\n{traceback.format_exc()}")
            messages.error(request, "Une erreur est survenue. Veuillez réessayer.")
            return redirect('home')
    
    wrapper.__name__ = view_func.__name__
    wrapper.__doc__ = view_func.__doc__
    return wrapper
