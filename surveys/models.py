from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse


class Survey(models.Model):
    """Modèle pour représenter un sondage"""
    title = models.CharField(max_length=200, verbose_name="Titre du sondage")
    description = models.TextField(verbose_name="Description", blank=True)
    created_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='surveys',
        verbose_name="Créé par",
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Créé le")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Modifié le")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="Date de début")
    end_date = models.DateTimeField(null=True, blank=True, verbose_name="Date de fin")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    allow_multiple_submissions = models.BooleanField(
        default=False, 
        verbose_name="Autoriser plusieurs soumissions"
    )
    show_results = models.BooleanField(
        default=True, 
        verbose_name="Afficher les résultats"
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Sondage"
        verbose_name_plural = "Sondages"
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('survey_detail', kwargs={'pk': self.pk})
    
    def is_open(self):
        """Vérifie si le sondage est ouvert"""
        now = timezone.now()
        if not self.is_active:
            return False
        if self.end_date and now > self.end_date:
            return False
        return now >= self.start_date
    
    def total_responses(self):
        """Retourne le nombre total de réponses"""
        return self.responses.count()


class Question(models.Model):
    """Modèle pour représenter une question dans un sondage"""
    QUESTION_TYPES = [
        ('text', 'Texte libre'),
        ('single', 'Choix unique'),
        ('multiple', 'Choix multiples'),
        ('rating', 'Évaluation (1-5)'),
    ]
    
    survey = models.ForeignKey(
        Survey, 
        on_delete=models.CASCADE, 
        related_name='questions',
        verbose_name="Sondage"
    )
    text = models.TextField(verbose_name="Question")
    question_type = models.CharField(
        max_length=20, 
        choices=QUESTION_TYPES, 
        default='single',
        verbose_name="Type de question"
    )
    is_required = models.BooleanField(default=True, verbose_name="Obligatoire")
    order = models.IntegerField(default=0, verbose_name="Ordre")
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Question"
        verbose_name_plural = "Questions"
    
    def __str__(self):
        return f"{self.survey.title} - {self.text[:50]}"


class Choice(models.Model):
    """Modèle pour représenter un choix de réponse"""
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE, 
        related_name='choices',
        verbose_name="Question"
    )
    text = models.CharField(max_length=200, verbose_name="Texte du choix")
    order = models.IntegerField(default=0, verbose_name="Ordre")
    
    class Meta:
        ordering = ['order', 'id']
        verbose_name = "Choix"
        verbose_name_plural = "Choix"
    
    def __str__(self):
        return self.text
    
    def get_vote_count(self):
        """Retourne le nombre de votes pour ce choix"""
        return self.answers.count()
    
    def get_vote_percentage(self):
        """Retourne le pourcentage de votes pour ce choix"""
        total = self.question.survey.total_responses()
        if total == 0:
            return 0
        return round((self.get_vote_count() / total) * 100, 1)


class Response(models.Model):
    """Modèle pour représenter une réponse complète à un sondage"""
    survey = models.ForeignKey(
        Survey, 
        on_delete=models.CASCADE, 
        related_name='responses',
        verbose_name="Sondage"
    )
    participant_name = models.CharField(
        max_length=100, 
        verbose_name="Nom du participant",
        default="Anonyme"
    )
    participant_email = models.EmailField(
        verbose_name="Email du participant",
        default="anonyme@example.com"
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name="Soumis le")
    ip_address = models.GenericIPAddressField(
        verbose_name="Adresse IP",
        null=True,
        blank=True
    )
    
    class Meta:
        ordering = ['-submitted_at']
        verbose_name = "Réponse"
        verbose_name_plural = "Réponses"
        # Empêcher qu'un même email réponde plusieurs fois au même sondage
        unique_together = [['survey', 'participant_email']]
    
    def __str__(self):
        return f"Réponse de {self.participant_name} à {self.survey.title}"


class Answer(models.Model):
    """Modèle pour représenter une réponse individuelle à une question"""
    response = models.ForeignKey(
        Response, 
        on_delete=models.CASCADE, 
        related_name='answers',
        verbose_name="Réponse"
    )
    question = models.ForeignKey(
        Question, 
        on_delete=models.CASCADE,
        verbose_name="Question"
    )
    choice = models.ForeignKey(
        Choice, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='answers',
        verbose_name="Choix"
    )
    text_answer = models.TextField(
        blank=True, 
        null=True,
        verbose_name="Réponse texte"
    )
    rating = models.IntegerField(
        null=True, 
        blank=True,
        verbose_name="Évaluation"
    )
    
    class Meta:
        verbose_name = "Réponse à une question"
        verbose_name_plural = "Réponses aux questions"
    
    def __str__(self):
        return f"Réponse à {self.question.text[:30]}"
