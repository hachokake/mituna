from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Survey, Question, Choice, Response, Answer


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 3
    fields = ['text', 'order']
    classes = ['collapse']


class QuestionInline(admin.StackedInline):
    model = Question
    extra = 1
    fields = ['text', 'question_type', 'is_required', 'order']
    classes = ['collapse']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ['question', 'choice', 'text_answer', 'rating']
    can_delete = False
    classes = ['collapse']


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title_with_icon', 'status_badge', 'created_by', 'created_at', 
                    'responses_count', 'questions_count', 'view_results']
    list_filter = ['is_active', 'created_at', 'show_results']
    search_fields = ['title', 'description']
    inlines = [QuestionInline]
    date_hierarchy = 'created_at'
    list_per_page = 20
    
    fieldsets = (
        ('📋 Informations principales', {
            'fields': ('title', 'description', 'created_by'),
            'description': 'Informations de base du sondage'
        }),
        ('⚙️ Paramètres', {
            'fields': ('is_active', 'allow_multiple_submissions', 'show_results'),
            'description': 'Configuration du comportement du sondage'
        }),
        ('📅 Dates', {
            'fields': ('start_date', 'end_date'),
            'description': 'Période de disponibilité du sondage'
        }),
    )
    
    def title_with_icon(self, obj):
        icon = '✅' if obj.is_active else '❌'
        return format_html('{} <strong>{}</strong>', icon, obj.title)
    title_with_icon.short_description = 'Sondage'
    
    def status_badge(self, obj):
        if obj.is_open():
            return format_html(
                '<span style="background: linear-gradient(135deg, #10b981 0%, #059669 100%); '
                'color: white; padding: 5px 15px; border-radius: 50px; font-weight: 600; '
                'font-size: 0.75rem;">🟢 OUVERT</span>'
            )
        else:
            return format_html(
                '<span style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); '
                'color: white; padding: 5px 15px; border-radius: 50px; font-weight: 600; '
                'font-size: 0.75rem;">🔴 FERMÉ</span>'
            )
    status_badge.short_description = 'Statut'
    
    def responses_count(self, obj):
        count = obj.total_responses()
        color = '#10b981' if count > 0 else '#6b7280'
        return format_html(
            '<span style="color: {}; font-weight: 700; font-size: 1.1rem;">'
            '👥 {}</span>', color, count
        )
    responses_count.short_description = 'Réponses'
    
    def questions_count(self, obj):
        count = obj.questions.count()
        return format_html(
            '<span style="color: #6366f1; font-weight: 700; font-size: 1.1rem;">'
            '❓ {}</span>', count
        )
    questions_count.short_description = 'Questions'
    
    def view_results(self, obj):
        if obj.show_results:
            url = reverse('survey_results', kwargs={'pk': obj.pk})
            return format_html(
                '<a href="{}" target="_blank" style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); '
                'color: white; padding: 8px 20px; border-radius: 50px; text-decoration: none; '
                'font-weight: 600; display: inline-block; transition: all 0.3s ease;">'
                '📊 Voir</a>', url
            )
        return format_html('<span style="color: #9ca3af;">-</span>')
    view_results.short_description = 'Résultats'


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_preview', 'survey_link', 'type_badge', 
                    'required_badge', 'order', 'choices_count']
    list_filter = ['question_type', 'is_required', 'survey']
    search_fields = ['text', 'survey__title']
    inlines = [ChoiceInline]
    list_per_page = 25
    
    def question_preview(self, obj):
        text = obj.text[:80] + '...' if len(obj.text) > 80 else obj.text
        return format_html('<strong>{}</strong>', text)
    question_preview.short_description = 'Question'
    
    def survey_link(self, obj):
        url = reverse('admin:surveys_survey_change', args=[obj.survey.id])
        return format_html('<a href="{}" style="color: #6366f1;">📋 {}</a>', 
                          url, obj.survey.title)
    survey_link.short_description = 'Sondage'
    
    def type_badge(self, obj):
        colors = {
            'text': '#3b82f6',
            'single': '#10b981',
            'multiple': '#f59e0b',
            'rating': '#ec4899'
        }
        icons = {
            'text': '✏️',
            'single': '🔘',
            'multiple': '☑️',
            'rating': '⭐'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; '
            'border-radius: 50px; font-size: 0.75rem; font-weight: 600;">'
            '{} {}</span>',
            colors.get(obj.question_type, '#6b7280'),
            icons.get(obj.question_type, '❓'),
            obj.get_question_type_display()
        )
    type_badge.short_description = 'Type'
    
    def required_badge(self, obj):
        if obj.is_required:
            return format_html(
                '<span style="color: #ef4444; font-weight: 700;">✱ Oui</span>'
            )
        return format_html('<span style="color: #9ca3af;">Non</span>')
    required_badge.short_description = 'Obligatoire'
    
    def choices_count(self, obj):
        count = obj.choices.count()
        if count > 0:
            return format_html(
                '<span style="color: #6366f1; font-weight: 600;">{} choix</span>', count
            )
        return format_html('<span style="color: #9ca3af;">-</span>')
    choices_count.short_description = 'Choix'


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['text_display', 'question_preview', 'order', 'votes_count']
    list_filter = ['question__survey', 'question__question_type']
    search_fields = ['text', 'question__text']
    list_per_page = 50
    
    def text_display(self, obj):
        return format_html('<strong>{}</strong>', obj.text)
    text_display.short_description = 'Choix'
    
    def question_preview(self, obj):
        text = obj.question.text[:50] + '...' if len(obj.question.text) > 50 else obj.question.text
        url = reverse('admin:surveys_question_change', args=[obj.question.id])
        return format_html('<a href="{}" style="color: #6366f1;">{}</a>', url, text)
    question_preview.short_description = 'Question'
    
    def votes_count(self, obj):
        count = obj.get_vote_count()
        percentage = obj.get_vote_percentage()
        if count > 0:
            return format_html(
                '<span style="font-weight: 700; color: #10b981;">'
                '✓ {} vote(s) ({} %)</span>', count, percentage
            )
        return format_html('<span style="color: #9ca3af;">0 vote</span>')
    votes_count.short_description = 'Votes'


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ['response_id', 'survey_link', 'participant_info', 
                    'submitted_date', 'answers_count']
    list_filter = ['survey', 'submitted_at']
    search_fields = ['participant_name', 'participant_email', 'survey__title']
    inlines = [AnswerInline]
    readonly_fields = ['submitted_at', 'ip_address']
    date_hierarchy = 'submitted_at'
    list_per_page = 30
    
    def response_id(self, obj):
        return format_html('<span style="font-weight: 700; color: #6366f1;">#{}</span>', 
                          obj.id)
    response_id.short_description = 'ID'
    
    def survey_link(self, obj):
        url = reverse('admin:surveys_survey_change', args=[obj.survey.id])
        return format_html('<a href="{}" style="color: #6366f1;">📋 {}</a>', 
                          url, obj.survey.title)
    survey_link.short_description = 'Sondage'
    
    def participant_info(self, obj):
        if obj.participant_name or obj.participant_email:
            name = obj.participant_name or 'Anonyme'
            email = obj.participant_email or ''
            return format_html(
                '<div><strong>👤 {}</strong><br>'
                '<small style="color: #6b7280;">{}</small></div>',
                name, email
            )
        return format_html('<span style="color: #9ca3af;">👤 Anonyme</span>')
    participant_info.short_description = 'Participant'
    
    def submitted_date(self, obj):
        return format_html(
            '<span style="color: #6b7280;">🕒 {}</span>',
            obj.submitted_at.strftime('%d/%m/%Y %H:%M')
        )
    submitted_date.short_description = 'Date de soumission'
    
    def answers_count(self, obj):
        count = obj.answers.count()
        return format_html(
            '<span style="color: #10b981; font-weight: 700;">✓ {} réponse(s)</span>', 
            count
        )
    answers_count.short_description = 'Réponses'


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['answer_id', 'question_preview', 'response_link', 
                    'answer_content', 'answer_date']
    list_filter = ['question__survey', 'question__question_type']
    search_fields = ['question__text', 'text_answer']
    list_per_page = 50
    
    def answer_id(self, obj):
        return format_html('<span style="font-weight: 700; color: #6366f1;">#{}</span>', 
                          obj.id)
    answer_id.short_description = 'ID'
    
    def question_preview(self, obj):
        text = obj.question.text[:50] + '...' if len(obj.question.text) > 50 else obj.question.text
        return format_html('<strong>{}</strong>', text)
    question_preview.short_description = 'Question'
    
    def response_link(self, obj):
        url = reverse('admin:surveys_response_change', args=[obj.response.id])
        return format_html('<a href="{}" style="color: #6366f1;">🔗 Réponse #{}</a>', 
                          url, obj.response.id)
    response_link.short_description = 'Réponse'
    
    def answer_content(self, obj):
        if obj.choice:
            return format_html('🔘 <strong>{}</strong>', obj.choice.text)
        elif obj.rating:
            stars = '⭐' * obj.rating
            return format_html('<span style="color: #f59e0b;">{} ({})</span>', 
                             stars, obj.rating)
        elif obj.text_answer:
            text = obj.text_answer[:60] + '...' if len(obj.text_answer) > 60 else obj.text_answer
            return format_html('✏️ {}', text)
        return format_html('<span style="color: #9ca3af;">-</span>')
    answer_content.short_description = 'Contenu'
    
    def answer_date(self, obj):
        return format_html(
            '<span style="color: #6b7280; font-size: 0.875rem;">{}</span>',
            obj.response.submitted_at.strftime('%d/%m/%Y %H:%M')
        )
    answer_date.short_description = 'Date'


# Personnalisation du site admin
admin.site.site_header = "🎯 Administration Sondages Pro"
admin.site.site_title = "Sondages Pro Admin"
admin.site.index_title = "Tableau de Bord"
