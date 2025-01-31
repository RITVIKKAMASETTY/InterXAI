from django.urls import path, include

from . import views

urlpatterns = [


    path('', views.home_view,name='home'),
    path('chat_create-<int:post>', views.chatcreate,name='chatcreate'),
    path('chat-<str:convoid>/',views.chat,name='chat'),
    path('previous_interviews/', views.previous_interviews, name='previous_interviews'),
    path('view_conversation/<int:convoid>/', views.view_conversation, name='view_conversation'),
    path('end-conve/<str:convoid>',views.generate_summary,name='end-convo'),
    path('summary/<str:convoid>',views.summ,name='summary'),

]
