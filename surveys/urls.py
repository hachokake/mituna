from django.urls import path
from . import views
from . import admin_views

urlpatterns = [
    # URLs publiques
    path('', views.home, name='home'),
    path('debug/', views.home_debug, name='home_debug'),
    path('survey/<int:pk>/', views.survey_detail, name='survey_detail'),
    path('survey/<int:pk>/submit/', views.survey_submit, name='survey_submit'),
    path('survey/<int:pk>/results/', views.survey_results, name='survey_results'),
    
    # URLs admin personnalisées
    path('admin/', admin_views.admin_login_view, name='admin_login'),
    path('admin/register/', admin_views.admin_register_view, name='admin_register'),
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/survey/create/', admin_views.admin_survey_create, name='admin_survey_create'),
    path('admin/survey/<int:survey_id>/edit/', admin_views.admin_survey_edit, name='admin_survey_edit'),
    path('admin/survey/<int:survey_id>/delete/', admin_views.admin_survey_delete, name='admin_survey_delete'),
    path('admin/survey/<int:survey_id>/results/', admin_views.admin_survey_results, name='admin_survey_results'),
    path('admin/documents/', admin_views.admin_documents, name='admin_documents'),
    path('admin/survey/<int:survey_id>/export/', admin_views.admin_survey_export, name='admin_survey_export'),
    path('admin/survey/<int:survey_id>/export/select/', admin_views.admin_survey_select_responses, name='admin_survey_select_responses'),
    path('admin/survey/<int:survey_id>/export/preview/', admin_views.admin_survey_export_preview, name='admin_survey_export_preview'),
    path('admin/survey/<int:survey_id>/export/download/', admin_views.admin_survey_export_download, name='admin_survey_export_download'),
    path('admin/logout/', admin_views.admin_logout_view, name='admin_logout'),
]
