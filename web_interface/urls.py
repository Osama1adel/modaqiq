from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('judge-dashboard/', views.judge_dashboard, name='judge_dashboard'),
    path('success/', views.success_page, name='success_page'),
]
