"""
Vues pour l'interface d'administration personnalisée
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db.models import Count, Q
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
def admin_survey_delete(request, survey_id):
    """Supprimer un sondage"""
    survey = get_object_or_404(Survey, id=survey_id)
    
    if request.method == 'POST':
        title = survey.title
        survey.delete()
        messages.success(request, f'Le sondage "{title}" a été supprimé.')
        return redirect('admin_dashboard')
    
    context = {'survey': survey}
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
    """Téléchargement du document en HTML (peut être converti en PDF via impression)"""
    survey = get_object_or_404(Survey, id=survey_id)
    limit = int(request.GET.get('limit', 0))
    per_page = int(request.GET.get('per_page', 50))
    format_type = request.GET.get('format', 'html')
    sort_order = request.GET.get('sort', 'date_desc')
    filter_type = request.GET.get('filter', 'all')
    selected_ids = request.GET.get('selected_ids', '')
    
    # Export CSV pour les très gros volumes (plus efficace)
    if format_type == 'csv':
        return _export_to_csv(survey, limit, sort_order, filter_type, selected_ids)
    
    # Export HTML (comme avant mais optimisé)
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
    
    questions = survey.questions.prefetch_related('choices').order_by('order')
    
    responses_data = []
    response_count = 0
    
    # Optimisation pour gros volumes
    total_responses = responses_query.count()
    use_iterator = total_responses > 100
    
    responses_list = responses_query.iterator(chunk_size=100) if use_iterator else responses_query
    
    for response in responses_list:
        response_info = {
            'participant': response.participant_name or 'Anonyme',
            'email': response.participant_email,
            'date': response.submitted_at,
            'answers': [],
            'page_number': (response_count // per_page) + 1
        }
        
        # Récupérer toutes les réponses en une seule requête
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
                        multiple_answers = Answer.objects.filter(
                            response=response, 
                            question=question
                        ).select_related('choice')
                        answer_text = ', '.join([a.choice.text for a in multiple_answers if a.choice])
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
    """Export optimisé en CSV pour les très gros volumes"""
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
        headers.append(f'Q{i}: {question.text}')
    writer.writerow(headers)
    
    # Récupérer les réponses de manière optimisée
    responses_query = survey.responses.all()
    
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
    
    # Utiliser iterator pour économiser la mémoire
    for survey_response in responses_query.iterator(chunk_size=100):
        row = [
            survey_response.submitted_at.strftime('%d/%m/%Y %H:%M'),
            survey_response.participant_name or 'Anonyme',
            survey_response.participant_email
        ]
        
        # Récupérer toutes les réponses en une requête
        answers_dict = {answer.question_id: answer for answer in 
                       Answer.objects.filter(response=survey_response).select_related('choice', 'question')}
        
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
                        multiple_answers = Answer.objects.filter(
                            response=survey_response, 
                            question=question
                        ).select_related('choice')
                        answer_text = ', '.join([a.choice.text for a in multiple_answers if a.choice])
                elif question.question_type == 'rating':
                    answer_text = f"{answer.rating}/5" if answer.rating else '-'
            
            row.append(answer_text)
        
        writer.writerow(row)
    
    return http_response
