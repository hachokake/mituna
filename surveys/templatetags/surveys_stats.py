from django import template
from surveys.models import Survey, Question, Response

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Filtre pour récupérer un élément d'un dictionnaire par sa clé"""
    if dictionary is None:
        return None
    return dictionary.get(key)

@register.simple_tag
def total_surveys():
    """Retourne le nombre total de sondages"""
    return Survey.objects.count()

@register.simple_tag
def total_responses():
    """Retourne le nombre total de réponses"""
    return Response.objects.count()

@register.simple_tag
def total_questions():
    """Retourne le nombre total de questions"""
    return Question.objects.count()

@register.simple_tag
def active_surveys():
    """Retourne le nombre de sondages actifs"""
    return Survey.objects.filter(is_active=True).count()

@register.inclusion_tag('admin/dashboard_stats.html')
def dashboard_stats():
    """Template tag pour afficher les statistiques du dashboard"""
    return {
        'total_surveys': Survey.objects.count(),
        'total_responses': Response.objects.count(),
        'total_questions': Question.objects.count(),
        'active_surveys': Survey.objects.filter(is_active=True).count(),
    }
