from tkinter.font import names

from django.urls import path, include

from . import views

urlpatterns = [

    path('reg', views.register,name= 'reg'),
    path('login', views.login_view,name='login'),
    path('', views.home_view,name='home'),
    path('chat_create-<int:post>', views.chatcreate,name='chatcreate'),
    path('chat-<str:convoid>/',views.chat,name='chat'),
    path('previous_interviews/', views.previous_interviews, name='previous_interviews'),
    path('view_conversation/<int:convoid>/', views.view_conversation, name='view_conversation'),
    path('interview_simulator', views.interview_simulator, name='interview_simulator'),
    path('generate_question/', views.generate_question, name='generate_question'),
    path('generate_hint/', views.generate_hint, name='generate_hint'),
    path('generate_answer/', views.generate_answer, name='generate_answer'),
    path('end-conve/<str:convoid>',views.generate_summary,name='end-convo'),
    path('summary/<str:convoid>',views.summ,name='summary'),
]
