from django.urls import path, include

from . import views

urlpatterns = [

    path('', views.interview_simulator, name='interview_simulator'),
    path('generate_question/', views.generate_question, name='generate_question'),
    path('generate_hint/', views.generate_hint, name='generate_hint'),
    path('generate_answer/', views.generate_answer, name='generate_answer'),

]
