from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from .models import Survey, Question, Choice, Response, Answer
from .validators import validate_full_name, normalize_full_name, validate_optional_email
import logging
import traceback

# Configuration du logger
logger = logging.getLogger('surveys')
error_logger = logging.getLogger('surveys.errors')


def home(request):
    """Page d'accueil avec la liste des sondages actifs"""
    try:
        # Récupérer tous les sondages actifs
        surveys = Survey.objects.filter(
            is_active=True,
            start_date__lte=timezone.now()
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
        ).annotate(
            response_count=Count('responses')
        ).order_by('-created_at')
        
        logger.info(f"Page d'accueil visitée - {surveys.count()} sondages affichés")
        
        context = {
            'surveys': surveys,
            'surveys_count': surveys.count(),
        }
        return render(request, 'surveys/home.html', context)
    
    except Exception as e:
        error_logger.error(f"Erreur dans home(): {str(e)}\n{traceback.format_exc()}")
        messages.error(request, "Une erreur est survenue lors du chargement des sondages.")
        return render(request, 'surveys/home.html', {'surveys': [], 'surveys_count': 0})


def home_debug(request):
    """Page de debug pour tester l'affichage des sondages sur mobile"""
    try:
        # Récupérer tous les sondages actifs
        surveys = Survey.objects.filter(
            is_active=True,
            start_date__lte=timezone.now()
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=timezone.now())
        ).annotate(
            response_count=Count('responses')
        ).order_by('-created_at')
        
        context = {
            'surveys': surveys,
            'surveys_count': surveys.count(),
        }
        return render(request, 'surveys/home_debug.html', context)
    
    except Exception as e:
        error_logger.error(f"Erreur dans home_debug(): {str(e)}\n{traceback.format_exc()}")
        return redirect('home')


def survey_detail(request, pk):
    """Affiche les détails d'un sondage"""
    try:
        survey = get_object_or_404(Survey, pk=pk)
        
        # Vérifier si le sondage est ouvert
        if not survey.is_open():
            messages.warning(request, "Ce sondage n'est plus disponible.")
            logger.warning(f"Tentative d'accès au sondage fermé {pk}")
            return redirect('home')
        
        questions = survey.questions.all().prefetch_related('choices')
        
        logger.info(f"Affichage détails sondage {pk} - {questions.count()} questions")
        
        context = {
            'survey': survey,
            'questions': questions,
        }
        return render(request, 'surveys/survey_detail.html', context)
    
    except Survey.DoesNotExist:
        messages.error(request, "Le sondage demandé n'existe pas.")
        logger.warning(f"Sondage introuvable: {pk}")
        return redirect('home')
    
    except Exception as e:
        error_logger.error(f"Erreur dans survey_detail({pk}): {str(e)}\n{traceback.format_exc()}")
        messages.error(request, "Une erreur est survenue lors du chargement du sondage.")
        return redirect('home')


def survey_submit(request, pk):
    """Traite la soumission d'un sondage"""
    try:
        survey = get_object_or_404(Survey, pk=pk)
    
        if request.method != 'POST':
            return redirect('survey_detail', pk=pk)
        
        # Vérifier si le sondage est ouvert
        if not survey.is_open():
            messages.error(request, "Ce sondage n'est plus disponible.")
            logger.warning(f"Tentative de soumission au sondage fermé {pk}")
            return redirect('home')
        
        # Récupérer les informations du participant
        participant_name = request.POST.get('participant_name', '').strip()
        participant_email = request.POST.get('participant_email', '').strip()
        
        # === VALIDATION STRICTE DU NOM ===
        try:
            # Valider et normaliser le nom complet
            normalized_name = validate_full_name(participant_name)
        except ValidationError as e:
            messages.error(request, str(e))
            logger.warning(f"Validation nom échouée pour sondage {pk}: {participant_name}")
            return redirect('survey_detail', pk=pk)
        
        # === VALIDATION DE L'EMAIL (FACULTATIF) ===
        validated_email = None
        if participant_email:
            try:
                validated_email = validate_optional_email(participant_email)
            except ValidationError as e:
                messages.error(request, str(e))
                logger.warning(f"Validation email échouée pour sondage {pk}: {participant_email}")
                return redirect('survey_detail', pk=pk)
        
        # === VÉRIFICATION ANTI-DOUBLON ===
        # Vérifier si une personne avec exactement le même nom (normalisé) a déjà répondu
        # Comparaison insensible à la casse et aux espaces multiples
        existing_response = Response.objects.filter(
            survey=survey,
            participant_name__iexact=normalized_name
        ).first()
        
        if existing_response:
            messages.error(
                request, 
                f"Vous avez déjà répondu à ce sondage avec le nom \"{normalized_name}\". "
                "Une seule participation par personne est autorisée."
            )
            logger.warning(f"Tentative de doublon pour sondage {pk}: {normalized_name}")
            return redirect('survey_detail', pk=pk)
        
        # Créer une réponse avec le nom normalisé
        response = Response.objects.create(
            survey=survey,
            participant_name=normalized_name,
            participant_email=validated_email or '',
            ip_address=get_client_ip(request)
        )
        
        logger.info(f"Nouvelle réponse créée pour sondage {pk} par {normalized_name}")
        
        # Traiter chaque question
        questions = survey.questions.all()
        answers_created = 0
        
        for question in questions:
            try:
                if question.question_type == 'text':
                    text_answer = request.POST.get(f'question_{question.id}', '')
                    if text_answer or not question.is_required:
                        Answer.objects.create(
                            response=response,
                            question=question,
                            text_answer=text_answer
                        )
                        answers_created += 1
                    elif question.is_required:
                        messages.error(request, f"La question '{question.text}' est obligatoire.")
                        response.delete()
                        logger.warning(f"Question obligatoire non remplie: {question.id}")
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
                        answers_created += 1
                    elif question.is_required:
                        messages.error(request, f"La question '{question.text}' est obligatoire.")
                        response.delete()
                        logger.warning(f"Question obligatoire non remplie: {question.id}")
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
                            answers_created += 1
                    elif question.is_required:
                        messages.error(request, f"La question '{question.text}' est obligatoire.")
                        response.delete()
                        logger.warning(f"Question obligatoire non remplie: {question.id}")
                        return redirect('survey_detail', pk=pk)
                
                elif question.question_type == 'rating':
                    rating = request.POST.get(f'question_{question.id}')
                    if rating:
                        Answer.objects.create(
                            response=response,
                            question=question,
                            rating=int(rating)
                        )
                        answers_created += 1
                    elif question.is_required:
                        messages.error(request, f"La question '{question.text}' est obligatoire.")
                        response.delete()
                        logger.warning(f"Question obligatoire non remplie: {question.id}")
                        return redirect('survey_detail', pk=pk)
            
            except Exception as e:
                error_logger.error(f"Erreur traitement question {question.id}: {str(e)}\n{traceback.format_exc()}")
                messages.error(request, "Une erreur est survenue lors de l'enregistrement de vos réponses.")
                response.delete()
                return redirect('survey_detail', pk=pk)
        
        logger.info(f"Soumission réussie sondage {pk}: {answers_created} réponses enregistrées")
        operations_logger = logging.getLogger('surveys.operations')
        operations_logger.info(
            f"SOUMISSION - Sondage: {survey.title} | Participant: {normalized_name} | "
            f"Réponses: {answers_created} | IP: {get_client_ip(request)}"
        )
        
        messages.success(request, "Merci pour votre participation ! Votre réponse a été enregistrée.")
        
        if survey.show_results:
            return redirect('survey_results', pk=pk)
        else:
            return redirect('home')
    
    except Survey.DoesNotExist:
        messages.error(request, "Le sondage demandé n'existe pas.")
        logger.warning(f"Tentative de soumission à un sondage inexistant: {pk}")
        return redirect('home')
    
    except Exception as e:
        error_logger.error(f"Erreur critique dans survey_submit({pk}): {str(e)}\n{traceback.format_exc()}")
        messages.error(request, "Une erreur est survenue. Veuillez réessayer ultérieurement.")
        return redirect('home')


def survey_results(request, pk):
    """Affiche les résultats d'un sondage"""
    try:
        survey = get_object_or_404(Survey, pk=pk)
    
        if not survey.show_results:
            messages.error(request, "Les résultats de ce sondage ne sont pas disponibles.")
            logger.warning(f"Tentative d'accès aux résultats masqués du sondage {pk}")
            return redirect('home')
        
        questions = survey.questions.all().prefetch_related('choices')
        total_responses = survey.total_responses()
        
        logger.info(f"Affichage résultats sondage {pk} - {total_responses} réponses")
        
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
    
    except Survey.DoesNotExist:
        messages.error(request, "Le sondage demandé n'existe pas.")
        logger.warning(f"Tentative d'accès aux résultats d'un sondage inexistant: {pk}")
        return redirect('home')
    
    except Exception as e:
        error_logger.error(f"Erreur dans survey_results({pk}): {str(e)}\n{traceback.format_exc()}")
        messages.error(request, "Une erreur est survenue lors du chargement des résultats.")
        return redirect('home')
    return render(request, 'surveys/survey_results.html', context)


def get_client_ip(request):
    """Récupère l'adresse IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
