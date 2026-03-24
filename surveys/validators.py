"""
Validateurs personnalisés pour les formulaires de sondage
"""
import re
from django.core.exceptions import ValidationError
from django.core.validators import validate_email


def validate_full_name(value):
    """
    Valide que le nom complet respecte les règles strictes:
    - Au moins 2 mots (Nom + Prénom)
    - Chaque mot doit avoir au moins 2 lettres
    - Uniquement lettres (avec accents) et espaces simples
    - Pas de chiffres ni caractères spéciaux
    - Pas de mots génériques (test, user, admin, etc.)
    """
    if not value or not value.strip():
        raise ValidationError("Le nom et le prénom sont obligatoires.")
    
    # Normaliser: supprimer espaces multiples
    normalized_name = ' '.join(value.strip().split())
    
    # Vérifier qu'il y a au moins 2 mots
    words = normalized_name.split()
    if len(words) < 2:
        raise ValidationError(
            "Veuillez entrer votre nom ET votre prénom (ex : José Moutou)."
        )
    
    # Vérifier chaque mot
    for word in words:
        # Chaque mot doit avoir au moins 2 lettres
        if len(word) < 2:
            raise ValidationError(
                f"'{word}' est trop court. Chaque nom doit contenir au moins 2 lettres."
            )
        
        # Vérifier que le mot ne contient que des lettres (y compris accents) et pas de chiffres
        if not re.match(r'^[a-zA-ZÀ-ÿ\-\']+$', word):
            raise ValidationError(
                f"'{word}' contient des caractères non autorisés. "
                "Utilisez uniquement des lettres (accents autorisés)."
            )
    
    # Vérifier les mots génériques/interdits
    forbidden_words = [
        'test', 'user', 'admin', 'exemple', 'example', 
        'demo', 'fake', 'temp', 'temporary', 'azerty',
        'qwerty', 'abc', 'xyz', 'undefined', 'null',
        'anonymous', 'anonyme', 'inconnu', 'unknown'
    ]
    
    name_lower = normalized_name.lower()
    for word in words:
        word_lower = word.lower()
        if word_lower in forbidden_words:
            raise ValidationError(
                f"'{word}' n'est pas un nom valide. "
                "Veuillez entrer votre nom et prénom réels (ex : José Moutou)."
            )
        
        # Vérifier les répétitions (ex: "Jean Jean")
        if words.count(word) > 1:
            raise ValidationError(
                "Vous ne pouvez pas répéter le même mot. "
                "Veuillez entrer votre nom et prénom réels (ex : José Moutou)."
            )
    
    return normalized_name


def normalize_full_name(value):
    """
    Normalise un nom complet pour la comparaison anti-doublon:
    - Supprime les espaces multiples
    - Convertit en minuscules pour comparaison insensible à la casse
    - Capitalise proprement chaque mot
    """
    if not value:
        return ""
    
    # Supprimer espaces multiples et normaliser
    normalized = ' '.join(value.strip().split())
    
    # Capitaliser proprement chaque mot
    return normalized.title()


def validate_optional_email(value):
    """
    Valide l'email s'il est fourni (facultatif)
    Si l'utilisateur entre quelque chose, ça doit être un email valide
    """
    if not value or not value.strip():
        # Email facultatif, on accepte vide
        return None
    
    # Si fourni, doit être valide
    try:
        validate_email(value.strip())
        return value.strip().lower()
    except ValidationError:
        raise ValidationError(
            "L'adresse email n'est pas valide. "
            "Veuillez entrer une adresse email correcte (ex : jose.moutou@example.com) "
            "ou laissez ce champ vide."
        )
