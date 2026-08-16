from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home_view, name='home'),
    path('circuit/<slug:slug>/', views.circuit_detail_view, name='circuit_detail'),
    path('category/<slug:category_slug>/', views.category_view, name='category_detail'),
    
    # NEW MODULE: AI Reverse Circuit Design
    path('reverse-design/', views.reverse_design_view, name='reverse_design'),
    path('reverse-design/history/', views.reverse_history_view, name='reverse_history'),
    path('reverse-design/export/pdf/<int:record_id>/', views.reverse_export_pdf_view, name='reverse_export_pdf'),
    
    # 5 NEW RESEARCH MODULES
    path('uncertainty-analysis/', views.uncertainty_analysis_view, name='uncertainty_analysis'),
    path('monte-carlo-analysis/', views.monte_carlo_analysis_view, name='monte_carlo_analysis'),
    path('active-learning/', views.active_learning_view, name='active_learning'),
    path('pareto-optimization/', views.pareto_optimization_view, name='pareto_optimization'),
    path('sensitivity-analysis/', views.sensitivity_analysis_view, name='sensitivity_analysis'),
    path('research-dashboard/', views.research_dashboard_view, name='research_dashboard'),
    path('research/export/<str:module_key>/<str:fmt>/', views.research_export_view, name='research_export'),

    # Advanced AI Features & Optimizers
    path('optimizer/', views.optimizer_page_view, name='optimizer'),
    path('api/chat/', views.api_chat_view, name='api_chat'),
    
    # Prediction Reports & Data Exports
    path('prediction/<int:record_id>/pdf/', views.export_pdf_view, name='export_pdf'),
    path('prediction/<int:record_id>/csv/', views.export_csv_view, name='export_csv'),
    path('prediction/<int:record_id>/excel/', views.export_excel_view, name='export_excel'),
    
    # Pages
    path('history/', views.history_view, name='history'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/', views.settings_view, name='settings'),
    
    # Auth
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]

