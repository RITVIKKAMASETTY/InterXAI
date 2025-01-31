from tkinter.font import names

from django.urls import path, include

from . import views

urlpatterns = [

    path('', views.register,name= 'reg'),
    path('login', views.login_view,name='login'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('resend-code/', views.resend_code, name='resend_code'),
    path('logout/', views.logoutView, name='logout'),
]
