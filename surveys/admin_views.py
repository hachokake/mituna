"""
Vues pour l'interface d'administration personnalisée
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Q, Prefetch
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from .models import Survey, Question, Choice, Response, Answer
from .forms import AdminRegistrationForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from datetime import datetime, timedelta
import json
import csv
from django.utils import timezone
from django.db.models import Q


def is_admin(user):
    """Vérifie si l'utilisateur est administrateur"""
    return user.is_authenticated and user.is_staff


def apply_export_filters_and_sorting(responses_query, sort_order='date_desc', filter_type='all'):
    """
    Applique les filtres et le tri sur les réponses
    
    Arguments:
        responses_query: QuerySet des réponses
        sort_order: ordre de tri (date_desc, date_asc, name_asc, name_desc, email_asc, email_desc)
        filter_type: type de filtre (all, unique_names, unique_emails, last_7_days, last_30_days, this_month)
    
    Returns:
        QuerySet filtré et trié
    """
    # Appliquer les filtres
    if filter_type == 'unique_names':
        # Garder uniquement la première réponse pour chaque nom unique
        seen_names = set()
        filtered_ids = []
        for response in responses_query.order_by('submitted_at'):
            name_lower = (response.participant_name or '').lower().strip()
            if name_lower and name_lower not in seen_names:
                seen_names.add(name_lower)
                filtered_ids.append(response.id)
        responses_query = responses_query.filter(id__in=filtered_ids)
    
    elif filter_type == 'unique_emails':
        # Garder uniquement la première réponse pour chaque email unique
        seen_emails = set()
        filtered_ids = []
        for response in responses_query.order_by('submitted_at'):
            email_lower = (response.participant_email or '').lower().strip()
            if email_lower and email_lower not in seen_emails:
                seen_emails.add(email_lower)
                filtered_ids.append(response.id)
        responses_query = responses_query.filter(id__in=filtered_ids)
    
    elif filter_type == 'last_7_days':
        # Réponses des 7 derniers jours
        seven_days_ago = timezone.now() - timedelta(days=7)
        responses_query = responses_query.filter(submitted_at__gte=seven_days_ago)
    
    elif filter_type == 'last_30_days':
        # Réponses des 30 derniers jours
        thirty_days_ago = timezone.now() - timedelta(days=30)
        responses_query = responses_query.filter(submitted_at__gte=thirty_days_ago)
    
    elif filter_type == 'this_month':
        # Réponses de ce mois
        now = timezone.now()
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        responses_query = responses_query.filter(submitted_at__gte=start_of_month)
    
    # Appliquer le tri
    if sort_order == 'date_desc':
        responses_query = responses_query.order_by('-submitted_at')
    elif sort_order == 'date_asc':
        responses_query = responses_query.order_by('submitted_at')
    elif sort_order == 'name_asc':
        responses_query = responses_query.order_by('participant_name', 'submitted_at')
    elif sort_order == 'name_desc':
        responses_query = responses_query.order_by('-participant_name', 'submitted_at')
    elif sort_order == 'email_asc':
        responses_query = responses_query.order_by('participant_email', 'submitted_at')
    elif sort_order == 'email_desc':
        responses_query = responses_query.order_by('-participant_email', 'submitted_at')
    else:
        # Par défaut: date décroissante
        responses_query = responses_query.order_by('-submitted_at')
    
    return responses_query


def admin_login_view(request):
    """Page de connexion administrateur"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_staff:
            login(request, user)
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Identifiants incorrects ou accès non autorisé.')
    
    return render(request, 'admin_custom/login.html')


def admin_register_view(request):
    """Création du premier compte administrateur"""
    # Vérifier si un administrateur existe déjà
    if User.objects.filter(is_superuser=True).exists():
        messages.info(request, 'Un compte administrateur existe déjà.')
        return redirect('admin_login')
    
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} ! Votre compte administrateur a été créé.')
            return redirect('admin_dashboard')
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'admin_custom/register.html', {'form': form})


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_dashboard(request):
    """Tableau de bord principal"""
    surveys = Survey.objects.annotate(
        response_count=Count('responses'),
        question_count=Count('questions')
    ).order_by('-created_at')
    
    total_surveys = surveys.count()
    active_surveys = surveys.filter(is_active=True).count()
    total_responses = Response.objects.count()
    total_questions = Question.objects.count()
    
    # Statistiques récentes
    recent_responses = Response.objects.select_related('survey').order_by('-submitted_at')[:10]
    
    context = {
        'surveys': surveys,
        'total_surveys': total_surveys,
        'active_surveys': active_surveys,
        'total_responses': total_responses,
        'total_questions': total_questions,
        'recent_responses': recent_responses,
    }
    
    return render(request, 'admin_custom/dashboard.html', context)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_create(request):
    """Créer un nouveau sondage"""
    if request.method == 'POST':
        # Récupérer les données du formulaire
        title = request.POST.get('title')
        description = request.POST.get('description')
        is_active = request.POST.get('is_active') == 'on'
        allow_multiple = request.POST.get('allow_multiple_submissions') == 'on'
        show_results = request.POST.get('show_results') == 'on'
        
        # Créer le sondage
        survey = Survey.objects.create(
            title=title,
            description=description,
            created_by=request.user,
            is_active=is_active,
            allow_multiple_submissions=allow_multiple,
            show_results=show_results,
            start_date=timezone.now()
        )
        
        # Récupérer les questions (sous forme JSON)
        questions_data = request.POST.get('questions_data', '[]')
        try:
            questions = json.loads(questions_data)
            for q_data in questions:
                question = Question.objects.create(
                    survey=survey,
                    text=q_data['text'],
                    question_type=q_data['type'],
                    is_required=q_data.get('required', True),
                    order=q_data.get('order', 0)
                )
                
                # Ajouter les choix si c'est un type à choix
                if q_data['type'] in ['single', 'multiple']:
                    for idx, choice_text in enumerate(q_data.get('choices', [])):
                        Choice.objects.create(
                            question=question,
                            text=choice_text,
                            order=idx
                        )
        except json.JSONDecodeError:
            messages.error(request, 'Erreur lors de la création des questions.')
            survey.delete()
            return redirect('admin_survey_create')
        
        messages.success(request, f'Le sondage "{title}" a été créé avec succès !')
        return redirect('admin_dashboard')
    
    return render(request, 'admin_custom/survey_create.html')


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_edit(request, survey_id):
    """Modifier un sondage existant"""
    survey = get_object_or_404(Survey, id=survey_id)
    
    if request.method == 'POST':
        survey.title = request.POST.get('title')
        survey.description = request.POST.get('description')
        survey.is_active = request.POST.get('is_active') == 'on'
        survey.allow_multiple_submissions = request.POST.get('allow_multiple_submissions') == 'on'
        survey.show_results = request.POST.get('show_results') == 'on'
        survey.save()
        
        messages.success(request, f'Le sondage "{survey.title}" a été modifié.')
        return redirect('admin_dashboard')
    
    context = {
        'survey': survey,
        'questions': survey.questions.prefetch_related('choices').order_by('order')
    }
    
    return render(request, 'admin_custom/survey_edit.html', context)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_toggle_status(request, survey_id):
    """Activer/Désactiver un sondage (archivage sans perdre les données)"""
    survey = get_object_or_404(Survey, id=survey_id)
    
    if request.method == 'POST':
        # Inverser le statut
        survey.is_active = not survey.is_active
        survey.save()
        
        status_text = "activé" if survey.is_active else "archivé"
        messages.success(
            request, 
            f'Le sondage "{survey.title}" a été {status_text}. '
            f'{"Il est maintenant visible par les utilisateurs." if survey.is_active else "Il est maintenant masqué (les données sont conservées)."}'
        )
        return redirect('admin_dashboard')
    
    # Afficher une page de confirmation
    context = {
        'survey': survey,
        'action': 'activer' if not survey.is_active else 'archiver',
        'current_status': 'inactif (archivé)' if not survey.is_active else 'actif',
    }
    return render(request, 'admin_custom/survey_toggle_status.html', context)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_delete(request, survey_id):
    """Supprimer un sondage DÉFINITIVEMENT (perte de toutes les données)"""
    survey = get_object_or_404(Survey, id=survey_id)
    
    if request.method == 'POST':
        title = survey.title
        response_count = survey.responses.count()
        survey.delete()
        messages.warning(
            request, 
            f'Le sondage "{title}" et ses {response_count} réponse(s) ont été supprimés définitivement.'
        )
        return redirect('admin_dashboard')
    
    context = {
        'survey': survey,
        'response_count': survey.responses.count(),
    }
    return render(request, 'admin_custom/survey_delete.html', context)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_results(request, survey_id):
    """Voir les résultats d'un sondage"""
    survey = get_object_or_404(Survey, id=survey_id)
    questions = survey.questions.prefetch_related('choices', 'answer_set').order_by('order')
    
    # Calculer les statistiques pour chaque question
    questions_stats = []
    for question in questions:
        if question.question_type in ['single', 'multiple']:
            choices_data = []
            for choice in question.choices.all():
                count = choice.get_vote_count()
                percentage = choice.get_vote_percentage()
                choices_data.append({
                    'text': choice.text,
                    'count': count,
                    'percentage': percentage
                })
            questions_stats.append({
                'question': question,
                'choices_data': choices_data
            })
        elif question.question_type == 'rating':
            # Calculer la moyenne des notes
            ratings = question.answer_set.exclude(rating__isnull=True).values_list('rating', flat=True)
            avg_rating = sum(ratings) / len(ratings) if ratings else 0
            questions_stats.append({
                'question': question,
                'avg_rating': round(avg_rating, 1),
                'total_ratings': len(ratings)
            })
        else:  # text
            text_answers = question.answer_set.exclude(text_answer='').values_list('text_answer', flat=True)
            questions_stats.append({
                'question': question,
                'text_answers': list(text_answers)
            })
    
    context = {
        'survey': survey,
        'questions_stats': questions_stats,
        'total_responses': survey.total_responses()
    }
    
    return render(request, 'admin_custom/survey_results.html', context)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_participants(request, survey_id):
    """Voir tous les participants et leurs réponses détaillées"""
    survey = get_object_or_404(Survey, id=survey_id)
    questions = survey.questions.order_by('order')
    
    # Récupérer toutes les réponses avec préchargement des relations
    responses = survey.responses.prefetch_related(
        'answers__question',
        'answers__choice'
    ).order_by('-submitted_at')
    
    # Construire les données des participants
    participants_data = []
    for response in responses:
        # Récupérer toutes les réponses de ce participant
        answers_dict = {}
        for answer in response.answers.all():
            question_id = answer.question.id
            
            if answer.question.question_type == 'text':
                answers_dict[question_id] = answer.text_answer or '-'
            elif answer.question.question_type == 'single':
                answers_dict[question_id] = answer.choice.text if answer.choice else '-'
            elif answer.question.question_type == 'multiple':
                # Pour les choix multiples, regrouper toutes les réponses
                if question_id not in answers_dict:
                    answers_dict[question_id] = []
                if answer.choice:
                    answers_dict[question_id].append(answer.choice.text)
            elif answer.question.question_type == 'rating':
                answers_dict[question_id] = f"{answer.rating}/5" if answer.rating else '-'
        
        # Convertir les listes en chaînes pour les choix multiples
        for q_id in answers_dict:
            if isinstance(answers_dict[q_id], list):
                answers_dict[q_id] = ', '.join(answers_dict[q_id]) if answers_dict[q_id] else '-'
        
        participants_data.append({
            'response': response,
            'name': response.participant_name,
            'email': response.participant_email if response.participant_email else 'Non fourni',
            'date': response.submitted_at,
            'ip': response.ip_address or 'Non disponible',
            'answers': answers_dict
        })
    
    context = {
        'survey': survey,
        'questions': questions,
        'participants_data': participants_data,
        'total_participants': len(participants_data),
    }
    
    return render(request, 'admin_custom/survey_participants.html', context)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_statistics(request, survey_id):
    """Module statistique professionnel - Aperçu et export PDF"""
    survey = get_object_or_404(Survey, id=survey_id)
    questions = survey.questions.prefetch_related('choices', 'answer_set').order_by('order')
    
    # Nombre total de participants
    total_participants = survey.responses.count()
    
    # Calculer les statistiques détaillées pour chaque question
    questions_statistics = []
    
    for question in questions:
        question_data = {
            'id': question.id,
            'text': question.text,
            'type': question.question_type,
            'order': question.order
        }
        
        if question.question_type in ['single', 'multiple']:
            # STATISTIQUES POUR QUESTIONS À CHOIX
            choices_data = []
            total_responses = 0
            
            for choice in question.choices.all():
                count = choice.get_vote_count()
                total_responses += count
                choices_data.append({
                    'text': choice.text,
                    'count': count,
                    'id': choice.id
                })
            
            # Calculer les pourcentages et fréquences
            for choice_data in choices_data:
                if total_responses > 0:
                    percentage = (choice_data['count'] / total_responses) * 100
                    choice_data['percentage'] = round(percentage, 1)
                    choice_data['frequency'] = round(percentage / 100, 3)
                else:
                    choice_data['percentage'] = 0
                    choice_data['frequency'] = 0
            
            # Trier par nombre de votes décroissant
            choices_data.sort(key=lambda x: x['count'], reverse=True)
            
            # Réponse la plus choisie
            most_chosen = choices_data[0] if choices_data else None
            
            question_data['choices'] = choices_data
            question_data['total_responses'] = total_responses
            question_data['most_chosen'] = most_chosen
            question_data['response_rate'] = round((total_responses / total_participants * 100), 1) if total_participants > 0 else 0
            
        elif question.question_type == 'rating':
            # STATISTIQUES POUR QUESTIONS DE NOTATION
            ratings = list(question.answer_set.exclude(rating__isnull=True).values_list('rating', flat=True))
            
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                rating_distribution = {i: ratings.count(i) for i in range(1, 6)}
                
                # Calculer les pourcentages
                rating_percentages = {}
                for rating_value, count in rating_distribution.items():
                    rating_percentages[rating_value] = {
                        'count': count,
                        'percentage': round((count / len(ratings)) * 100, 1) if len(ratings) > 0 else 0
                    }
                
                question_data['avg_rating'] = round(avg_rating, 2)
                question_data['total_ratings'] = len(ratings)
                question_data['rating_distribution'] = rating_percentages
                question_data['response_rate'] = round((len(ratings) / total_participants * 100), 1) if total_participants > 0 else 0
                
                # Note la plus fréquente
                most_common = max(rating_distribution.items(), key=lambda x: x[1])
                question_data['most_common_rating'] = {
                    'value': most_common[0],
                    'count': most_common[1]
                }
            else:
                question_data['avg_rating'] = 0
                question_data['total_ratings'] = 0
                question_data['rating_distribution'] = {}
                question_data['response_rate'] = 0
                
        else:  # text
            # STATISTIQUES POUR QUESTIONS TEXTUELLES
            text_answers = list(question.answer_set.exclude(text_answer='').values_list('text_answer', flat=True))
            
            question_data['total_text_responses'] = len(text_answers)
            question_data['response_rate'] = round((len(text_answers) / total_participants * 100), 1) if total_participants > 0 else 0
            question_data['sample_answers'] = text_answers[:15]  # Échantillon de 15 réponses
            
            if text_answers:
                avg_length = sum(len(answer) for answer in text_answers) / len(text_answers)
                question_data['avg_answer_length'] = round(avg_length, 1)
                question_data['min_length'] = min(len(answer) for answer in text_answers)
                question_data['max_length'] = max(len(answer) for answer in text_answers)
        
        questions_statistics.append(question_data)
    
    # STATISTIQUES GÉNÉRALES
    total_questions = questions.count()
    
    # Calculer le taux de complétion global
    if total_participants > 0 and total_questions > 0:
        total_possible_answers = total_participants * total_questions
        total_actual_answers = sum(q.get('total_responses', q.get('total_ratings', q.get('total_text_responses', 0))) for q in questions_statistics)
        completion_rate = round((total_actual_answers / total_possible_answers * 100), 1)
    else:
        completion_rate = 0
    
    # Conclusion automatique
    conclusion = generate_survey_conclusion(survey, total_participants, completion_rate, questions_statistics)
    
    context = {
        'survey': survey,
        'total_participants': total_participants,
        'total_questions': total_questions,
        'completion_rate': completion_rate,
        'questions_statistics': questions_statistics,
        'conclusion': conclusion,
        'generated_date': timezone.now(),
        'questions_json': json.dumps(questions_statistics, default=str)
    }
    
    return render(request, 'admin_custom/survey_report_preview.html', context)


def generate_survey_conclusion(survey, total_participants, completion_rate, questions_stats):
    """Génère une conclusion automatique basée sur les résultats"""
    
    if total_participants == 0:
        return "Aucune participation n'a été enregistrée pour ce sondage à ce jour."
    
    conclusion_parts = []
    
    # Introduction
    conclusion_parts.append(f"Ce sondage a collecté un total de {total_participants} participation{'s' if total_participants > 1 else ''} avec un taux de complétion de {completion_rate}%.")
    
    # Analyse des questions à choix
    choice_questions = [q for q in questions_stats if q['type'] in ['single', 'multiple']]
    if choice_questions:
        for q in choice_questions[:2]:  # Analyser les 2 premières
            if q.get('most_chosen'):
                conclusion_parts.append(
                    f"Pour la question \"{q['text'][:50]}...\", la réponse la plus choisie est \"{q['most_chosen']['text']}\" "
                    f"avec {q['most_chosen']['count']} vote{'s' if q['most_chosen']['count'] > 1 else ''} ({q['most_chosen']['percentage']}%)."
                )
    
    # Analyse des notations
    rating_questions = [q for q in questions_stats if q['type'] == 'rating']
    if rating_questions:
        avg_ratings = [q['avg_rating'] for q in rating_questions if q.get('avg_rating', 0) > 0]
        if avg_ratings:
            overall_avg = round(sum(avg_ratings) / len(avg_ratings), 1)
            conclusion_parts.append(f"La note moyenne globale est de {overall_avg}/5 étoiles.")
    
    # Conclusion finale
    if completion_rate >= 80:
        conclusion_parts.append("Le taux de complétion élevé indique un fort engagement des participants.")
    elif completion_rate >= 50:
        conclusion_parts.append("Le taux de complétion modéré suggère un intérêt correct pour le sondage.")
    else:
        conclusion_parts.append("Le taux de complétion relativement faible suggère des opportunités d'amélioration pour encourager la participation complète.")
    
    return " ".join(conclusion_parts)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_report_download(request, survey_id):
    """Téléchargement du rapport statistique en PDF"""
    survey = get_object_or_404(Survey, id=survey_id)
    
    # Récupérer les mêmes données que l'aperçu
    questions = survey.questions.prefetch_related('choices', 'answer_set').order_by('order')
    total_participants = survey.responses.count()
    
    questions_statistics = []
    
    for question in questions:
        question_data = {
            'id': question.id,
            'text': question.text,
            'type': question.question_type,
            'order': question.order
        }
        
        if question.question_type in ['single', 'multiple']:
            choices_data = []
            total_responses = 0
            
            for choice in question.choices.all():
                count = choice.get_vote_count()
                total_responses += count
                choices_data.append({
                    'text': choice.text,
                    'count': count,
                    'id': choice.id
                })
            
            for choice_data in choices_data:
                if total_responses > 0:
                    percentage = (choice_data['count'] / total_responses) * 100
                    choice_data['percentage'] = round(percentage, 1)
                    choice_data['frequency'] = round(percentage / 100, 3)
                else:
                    choice_data['percentage'] = 0
                    choice_data['frequency'] = 0
            
            choices_data.sort(key=lambda x: x['count'], reverse=True)
            most_chosen = choices_data[0] if choices_data else None
            
            question_data['choices'] = choices_data
            question_data['total_responses'] = total_responses
            question_data['most_chosen'] = most_chosen
            question_data['response_rate'] = round((total_responses / total_participants * 100), 1) if total_participants > 0 else 0
            
        elif question.question_type == 'rating':
            ratings = list(question.answer_set.exclude(rating__isnull=True).values_list('rating', flat=True))
            
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                rating_distribution = {i: ratings.count(i) for i in range(1, 6)}
                rating_percentages = {}
                
                for rating_value, count in rating_distribution.items():
                    rating_percentages[rating_value] = {
                        'count': count,
                        'percentage': round((count / len(ratings)) * 100, 1) if len(ratings) > 0 else 0
                    }
                
                question_data['avg_rating'] = round(avg_rating, 2)
                question_data['total_ratings'] = len(ratings)
                question_data['rating_distribution'] = rating_percentages
                question_data['response_rate'] = round((len(ratings) / total_participants * 100), 1) if total_participants > 0 else 0
                
                most_common = max(rating_distribution.items(), key=lambda x: x[1])
                question_data['most_common_rating'] = {
                    'value': most_common[0],
                    'count': most_common[1]
                }
            else:
                question_data['avg_rating'] = 0
                question_data['total_ratings'] = 0
                question_data['rating_distribution'] = {}
                question_data['response_rate'] = 0
                
        else:  # text
            text_answers = list(question.answer_set.exclude(text_answer='').values_list('text_answer', flat=True))
            
            question_data['total_text_responses'] = len(text_answers)
            question_data['response_rate'] = round((len(text_answers) / total_participants * 100), 1) if total_participants > 0 else 0
            question_data['sample_answers'] = text_answers[:15]
            
            if text_answers:
                avg_length = sum(len(answer) for answer in text_answers) / len(text_answers)
                question_data['avg_answer_length'] = round(avg_length, 1)
        
        questions_statistics.append(question_data)
    
    total_questions = questions.count()
    
    if total_participants > 0 and total_questions > 0:
        total_possible_answers = total_participants * total_questions
        total_actual_answers = sum(q.get('total_responses', q.get('total_ratings', q.get('total_text_responses', 0))) for q in questions_statistics)
        completion_rate = round((total_actual_answers / total_possible_answers * 100), 1)
    else:
        completion_rate = 0
    
    conclusion = generate_survey_conclusion(survey, total_participants, completion_rate, questions_statistics)
    
    context = {
        'survey': survey,
        'total_participants': total_participants,
        'total_questions': total_questions,
        'completion_rate': completion_rate,
        'questions_statistics': questions_statistics,
        'conclusion': conclusion,
        'generated_date': timezone.now(),
        'is_pdf': True
    }
    
    # Rendre le template HTML pour le PDF
    html_content = render_to_string('admin_custom/survey_report_pdf.html', context)
    
    # Créer la réponse HTTP pour le PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Rapport_Statistique_{survey.title[:30]}_{datetime.now().strftime("%Y%m%d")}.pdf"'
    
    # Note: Pour une vraie conversion PDF, vous devrez installer weasyprint ou xhtml2pdf
    # Pour l'instant, on retourne le HTML
    # TODO: Intégrer weasyprint pour une vraie conversion PDF
    
    response = HttpResponse(html_content, content_type='text/html')
    response['Content-Disposition'] = f'attachment; filename="Rapport_Statistique_{survey.title[:30]}_{datetime.now().strftime("%Y%m%d")}.html"'
    
    return response


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_logout_view(request):
    """Déconnexion"""
    logout(request)
    messages.success(request, 'Vous êtes déconnecté.')
    return redirect('admin_login')


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_documents(request):
    """Page de gestion des documents/exports"""
    surveys = Survey.objects.annotate(
        response_count=Count('responses')
    ).order_by('-created_at')
    
    context = {
        'surveys': surveys,
    }
    return render(request, 'admin_custom/documents.html', context)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_export(request, survey_id):
    """Page de configuration de l'export"""
    survey = get_object_or_404(Survey, id=survey_id)
    total_responses = survey.responses.count()
    
    context = {
        'survey': survey,
        'total_responses': total_responses,
    }
    return render(request, 'admin_custom/survey_export.html', context)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_select_responses(request, survey_id):
    """Page de sélection manuelle des réponses à exporter"""
    survey = get_object_or_404(Survey, id=survey_id)
    responses = survey.responses.order_by('-submitted_at')
    
    context = {
        'survey': survey,
        'responses': responses,
    }
    return render(request, 'admin_custom/survey_select_responses.html', context)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_export_preview(request, survey_id):
    """Aperçu du document d'export en HTML"""
    survey = get_object_or_404(Survey, id=survey_id)
    limit = int(request.GET.get('limit', 0))
    per_page = int(request.GET.get('per_page', 50))
    sort_order = request.GET.get('sort', 'date_desc')
    filter_type = request.GET.get('filter', 'all')
    selected_ids = request.GET.get('selected_ids', '')
    
    # Récupérer les réponses de manière optimisée
    responses_query = survey.responses.select_related()
    
    # Si des IDs spécifiques sont sélectionnés, filtrer par ces IDs
    if selected_ids:
        ids_list = [int(id.strip()) for id in selected_ids.split(',') if id.strip()]
        responses_query = responses_query.filter(id__in=ids_list)
    else:
        # Appliquer les filtres et le tri normaux seulement si pas de sélection manuelle
        responses_query = apply_export_filters_and_sorting(responses_query, sort_order, filter_type)
    
    # Appliquer la limite si spécifiée et pas de sélection manuelle
    if limit > 0 and not selected_ids:
        responses_query = responses_query[:limit]
    
    # Récupérer toutes les questions avec leurs choix pré-chargés
    questions = survey.questions.prefetch_related('choices').order_by('order')
    
    # Préparer les données pour le document de manière optimisée
    responses_data = []
    response_count = 0
    
    # Utiliser iterator() pour économiser la mémoire avec de gros volumes
    # mais seulement si on a plus de 100 réponses
    total_responses = responses_query.count()
    use_iterator = total_responses > 100
    
    responses_list = responses_query.iterator(chunk_size=100) if use_iterator else responses_query
    
    for response in responses_list:
        response_info = {
            'participant': response.participant_name or 'Anonyme',
            'email': response.participant_email,
            'date': response.submitted_at,
            'answers': [],
            'page_number': (response_count // per_page) + 1  # Calcul de la page
        }
        
        # Récupérer toutes les réponses de ce participant en une seule requête
        answers_dict = {answer.question_id: answer for answer in 
                       Answer.objects.filter(response=response).select_related('choice', 'question')}
        
        for question in questions:
            answer = answers_dict.get(question.id)
            answer_text = ''
            
            if answer:
                if question.question_type == 'text':
                    answer_text = answer.text_answer or '-'
                elif question.question_type in ['single', 'multiple']:
                    if answer.choice:
                        answer_text = answer.choice.text
                    else:
                        # Pour les choix multiples, récupérer toutes les réponses
                        multiple_answers = Answer.objects.filter(
                            response=response, 
                            question=question
                        ).select_related('choice')
                        answer_text = ', '.join([a.choice.text for a in multiple_answers if a.choice])
                elif question.question_type == 'rating':
                    answer_text = f"{answer.rating}/5 ⭐" if answer.rating else '-'
            
            response_info['answers'].append({
                'question': question.text,
                'answer': answer_text
            })
        
        responses_data.append(response_info)
        response_count += 1
    
    # Calculer le nombre total de pages
    total_pages = (len(responses_data) + per_page - 1) // per_page if per_page > 0 else 1
    
    # Statistiques générales
    stats = {
        'total_responses': total_responses,
        'exported_responses': len(responses_data),
        'total_questions': questions.count(),
        'export_date': datetime.now(),
        'survey': survey,
        'total_pages': total_pages,
        'responses_per_page': per_page
    }
    
    context = {
        'survey': survey,
        'responses_data': responses_data,
        'questions': questions,
        'stats': stats,
        'is_preview': True,
        'per_page': per_page
    }
    
    return render(request, 'admin_custom/export_preview.html', context)


@login_required(login_url='admin_login')
@user_passes_test(is_admin, login_url='admin_login')
def admin_survey_export_download(request, survey_id):
    """Téléchargement du document en HTML ou CSV (optimisé pour gros volumes)"""
    survey = get_object_or_404(Survey, id=survey_id)
    limit = int(request.GET.get('limit', 0))
    per_page = int(request.GET.get('per_page', 50))
    format_type = request.GET.get('format', 'html')
    sort_order = request.GET.get('sort', 'date_desc')
    filter_type = request.GET.get('filter', 'all')
    selected_ids = request.GET.get('selected_ids', '')
    
    # Pour les gros volumes (> 500 réponses), forcer le CSV
    responses_query = survey.responses.all()
    if selected_ids:
        ids_list = [int(id.strip()) for id in selected_ids.split(',') if id.strip()]
        responses_query = responses_query.filter(id__in=ids_list)
    else:
        responses_query = apply_export_filters_and_sorting(responses_query, sort_order, filter_type)
    
    total_count = responses_query.count() if not limit else min(limit, responses_query.count())
    
    # Limite de sécurité : forcer CSV pour plus de 500 réponses en HTML
    if format_type == 'html' and total_count > 500:
        # Rediriger vers CSV automatiquement
        return _export_to_csv(survey, limit, sort_order, filter_type, selected_ids)
    
    # Export CSV pour les gros volumes ou sur demande
    if format_type == 'csv':
        return _export_to_csv(survey, limit, sort_order, filter_type, selected_ids)
    
    # Export HTML optimisé (pour ≤ 500 réponses)
    return _export_to_html(survey, limit, per_page, sort_order, filter_type, selected_ids)


def _export_to_html(survey, limit, per_page, sort_order, filter_type, selected_ids):
    """Export HTML optimisé avec préchargement des données"""
    responses_query = survey.responses.select_related().prefetch_related(
        Prefetch('answers', queryset=Answer.objects.select_related('question', 'choice'))
    )
    
    # Si des IDs spécifiques sont sélectionnés, filtrer par ces IDs
    if selected_ids:
        ids_list = [int(id.strip()) for id in selected_ids.split(',') if id.strip()]
        responses_query = responses_query.filter(id__in=ids_list)
    else:
        # Appliquer les filtres et le tri normaux
        responses_query = apply_export_filters_and_sorting(responses_query, sort_order, filter_type)
    
    # Appliquer la limite si spécifiée
    if limit > 0 and not selected_ids:
        responses_query = responses_query[:limit]
    
    questions = survey.questions.prefetch_related('choices').order_by('order')
    
    responses_data = []
    response_count = 0
    
    # Charger les réponses (déjà optimisé avec prefetch_related)
    total_responses = responses_query.count()
    
    for response in responses_query:
        response_info = {
            'participant': response.participant_name or 'Anonyme',
            'email': response.participant_email,
            'date': response.submitted_at,
            'answers': [],
            'page_number': (response_count // per_page) + 1
        }
        
        # Utiliser les réponses préchargées (pas de requête supplémentaire)
        answers_dict = {answer.question_id: answer for answer in response.answers.all()}
        
        for question in questions:
            answer = answers_dict.get(question.id)
            answer_text = ''
            
            if answer:
                if question.question_type == 'text':
                    answer_text = answer.text_answer or '-'
                elif question.question_type == 'single':
                    answer_text = answer.choice.text if answer.choice else '-'
                elif question.question_type == 'multiple':
                    # Récupérer toutes les réponses multiples pour cette question
                    multiple_answers = [a for a in response.answers.all() if a.question_id == question.id and a.choice]
                    answer_text = ', '.join([a.choice.text for a in multiple_answers]) if multiple_answers else '-'
                elif question.question_type == 'rating':
                    answer_text = f"{answer.rating}/5" if answer.rating else '-'
            
            response_info['answers'].append({
                'question': question.text,
                'answer': answer_text
            })
        
        responses_data.append(response_info)
        response_count += 1
    
    total_pages = (len(responses_data) + per_page - 1) // per_page if per_page > 0 else 1
    
    stats = {
        'total_responses': total_responses,
        'exported_responses': len(responses_data),
        'total_questions': questions.count(),
        'export_date': datetime.now(),
        'survey': survey,
        'total_pages': total_pages,
        'responses_per_page': per_page
    }
    
    context = {
        'survey': survey,
        'responses_data': responses_data,
        'questions': questions,
        'stats': stats,
        'is_preview': False,
        'per_page': per_page
    }
    
    html_content = render_to_string('admin_custom/export_document.html', context)
    
    response = HttpResponse(html_content, content_type='text/html; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="Rapport_Sondage_{survey.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html"'
    
    return response


def _export_to_csv(survey, limit=0, sort_order='date_desc', filter_type='all', selected_ids=''):
    """Export optimisé en CSV pour les gros volumes (jusqu'à 10 000+ réponses)"""
    http_response = HttpResponse(content_type='text/csv; charset=utf-8')
    http_response['Content-Disposition'] = f'attachment; filename="Sondage_{survey.id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
    
    # Ajouter BOM pour Excel
    http_response.write('\ufeff')
    
    writer = csv.writer(http_response, delimiter=';', quoting=csv.QUOTE_ALL)
    
    # Récupérer les questions
    questions = list(survey.questions.order_by('order'))
    
    # En-têtes du CSV
    headers = ['Date', 'Nom', 'Email']
    for i, question in enumerate(questions, 1):
        headers.append(f'Q{i}: {question.text[:100]}')  # Limiter à 100 chars pour Excel
    writer.writerow(headers)
    
    # Récupérer les réponses de manière optimisée avec préchargement
    responses_query = survey.responses.prefetch_related(
        Prefetch('answers', queryset=Answer.objects.select_related('question', 'choice'))
    )
    
    # Si des IDs spécifiques sont sélectionnés, filtrer par ces IDs
    if selected_ids:
        ids_list = [int(id.strip()) for id in selected_ids.split(',') if id.strip()]
        responses_query = responses_query.filter(id__in=ids_list)
    else:
        # Appliquer les filtres et le tri normaux
        responses_query = apply_export_filters_and_sorting(responses_query, sort_order, filter_type)
    
    # Appliquer la limite si spécifiée
    if limit > 0 and not selected_ids:
        responses_query = responses_query[:limit]
    
    # Utiliser iterator pour économiser la mémoire sur de très gros volumes
    # chunk_size=200 est un bon compromis entre performance et mémoire
    for survey_response in responses_query.iterator(chunk_size=200):
        row = [
            survey_response.submitted_at.strftime('%d/%m/%Y %H:%M'),
            survey_response.participant_name or 'Anonyme',
            survey_response.participant_email or ''
        ]
        
        # Utiliser les réponses préchargées (pas de requête supplémentaire)
        answers_dict = {}
        for answer in survey_response.answers.all():
            # Pour les questions multiples, accumuler les réponses
            if answer.question_id in answers_dict:
                if isinstance(answers_dict[answer.question_id], list):
                    answers_dict[answer.question_id].append(answer)
                else:
                    answers_dict[answer.question_id] = [answers_dict[answer.question_id], answer]
            else:
                answers_dict[answer.question_id] = answer
        
        for question in questions:
            answer_data = answers_dict.get(question.id)
            answer_text = ''
            
            if answer_data:
                if isinstance(answer_data, list):
                    # Questions à choix multiples
                    answer_text = ', '.join([a.choice.text for a in answer_data if a.choice])
                else:
                    # Question unique
                    answer = answer_data
                    if question.question_type == 'text':
                        answer_text = answer.text_answer or ''
                    elif question.question_type in ['single', 'multiple']:
                        answer_text = answer.choice.text if answer.choice else ''
                    elif question.question_type == 'rating':
                        answer_text = f"{answer.rating}/5" if answer.rating else ''
            
            row.append(answer_text)
        
        writer.writerow(row)
    
    return http_response
