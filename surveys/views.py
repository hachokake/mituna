from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from .models import Survey, Question, Choice, Response, Answer


def home(request):
    """Page d'accueil avec la liste des sondages actifs"""
    surveys = Survey.objects.filter(
        is_active=True,
        start_date__lte=timezone.now()
    ).filter(
        Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
    ).annotate(
        response_count=Count('responses')
    )
    
    context = {
        'surveys': surveys,
    }
    return render(request, 'surveys/home.html', context)


def survey_detail(request, pk):
    """Affiche les détails d'un sondage"""
    survey = get_object_or_404(Survey, pk=pk)
    
    # Vérifier si le sondage est ouvert
    if not survey.is_open():
        messages.error(request, "Ce sondage n'est plus disponible.")
        return redirect('home')
    
    questions = survey.questions.all().prefetch_related('choices')
    
    context = {
        'survey': survey,
        'questions': questions,
    }
    return render(request, 'surveys/survey_detail.html', context)


def survey_submit(request, pk):
    """Traite la soumission d'un sondage"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if request.method != 'POST':
        return redirect('survey_detail', pk=pk)
    
    # Vérifier si le sondage est ouvert
    if not survey.is_open():
        messages.error(request, "Ce sondage n'est plus disponible.")
        return redirect('home')
    
    # Récupérer et valider les informations du participant (OBLIGATOIRES)
    participant_name = request.POST.get('participant_name', '').strip()
    participant_email = request.POST.get('participant_email', '').strip()
    
    if not participant_name or not participant_email:
        messages.error(request, "Votre nom et votre email sont obligatoires pour participer au sondage.")
        return redirect('survey_detail', pk=pk)
    
    # Vérifier si cet email a déjà répondu au sondage
    if Response.objects.filter(survey=survey, participant_email=participant_email).exists():
        messages.error(request, "Vous avez déjà participé à ce sondage avec cet email. Une seule participation par personne est autorisée.")
        return redirect('survey_detail', pk=pk)
    
    # Créer une réponse
    response = Response.objects.create(
        survey=survey,
        participant_name=participant_name,
        participant_email=participant_email,
        ip_address=get_client_ip(request)
    )
    
    # Traiter chaque question
    questions = survey.questions.all()
    for question in questions:
        if question.question_type == 'text':
            text_answer = request.POST.get(f'question_{question.id}', '')
            if text_answer or not question.is_required:
                Answer.objects.create(
                    response=response,
                    question=question,
                    text_answer=text_answer
                )
            else:
                messages.error(request, f"La question '{question.text}' est obligatoire.")
                response.delete()
                return redirect('survey_detail', pk=pk)
        
        elif question.question_type == 'single':
            choice_id = request.POST.get(f'question_{question.id}')
            if choice_id:
                choice = get_object_or_404(Choice, id=choice_id, question=question)
                Answer.objects.create(
                    response=response,
                    question=question,
                    choice=choice
                )
            elif question.is_required:
                messages.error(request, f"La question '{question.text}' est obligatoire.")
                response.delete()
                return redirect('survey_detail', pk=pk)
        
        elif question.question_type == 'multiple':
            choice_ids = request.POST.getlist(f'question_{question.id}')
            if choice_ids:
                for choice_id in choice_ids:
                    choice = get_object_or_404(Choice, id=choice_id, question=question)
                    Answer.objects.create(
                        response=response,
                        question=question,
                        choice=choice
                    )
            elif question.is_required:
                messages.error(request, f"La question '{question.text}' est obligatoire.")
                response.delete()
                return redirect('survey_detail', pk=pk)
        
        elif question.question_type == 'rating':
            rating = request.POST.get(f'question_{question.id}')
            if rating:
                Answer.objects.create(
                    response=response,
                    question=question,
                    rating=int(rating)
                )
            elif question.is_required:
                messages.error(request, f"La question '{question.text}' est obligatoire.")
                response.delete()
                return redirect('survey_detail', pk=pk)
    
    messages.success(request, "Merci pour votre participation ! Votre réponse a été enregistrée.")
    
    if survey.show_results:
        return redirect('survey_results', pk=pk)
    else:
        return redirect('home')


def survey_results(request, pk):
    """Affiche les résultats d'un sondage"""
    survey = get_object_or_404(Survey, pk=pk)
    
    if not survey.show_results:
        messages.error(request, "Les résultats de ce sondage ne sont pas disponibles.")
        return redirect('home')
    
    questions = survey.questions.all().prefetch_related('choices')
    total_responses = survey.total_responses()
    
    # Préparer les données pour chaque question
    questions_data = []
    for question in questions:
        question_data = {
            'question': question,
            'choices_data': []
        }
        
        if question.question_type in ['single', 'multiple']:
            for choice in question.choices.all():
                vote_count = choice.get_vote_count()
                percentage = choice.get_vote_percentage()
                question_data['choices_data'].append({
                    'choice': choice,
                    'count': vote_count,
                    'percentage': percentage
                })
        elif question.question_type == 'rating':
            # Calculer la moyenne des notes
            ratings = Answer.objects.filter(question=question).values_list('rating', flat=True)
            if ratings:
                avg_rating = sum(ratings) / len(ratings)
                question_data['avg_rating'] = round(avg_rating, 1)
                question_data['total_ratings'] = len(ratings)
        elif question.question_type == 'text':
            # Récupérer toutes les réponses texte
            text_answers = Answer.objects.filter(question=question).values_list('text_answer', flat=True)
            question_data['text_answers'] = list(text_answers)
        
        questions_data.append(question_data)
    
    context = {
        'survey': survey,
        'questions_data': questions_data,
        'total_responses': total_responses,
    }
    return render(request, 'surveys/survey_results.html', context)


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
