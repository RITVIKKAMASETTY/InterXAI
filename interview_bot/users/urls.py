from tkinter.font import names

from django.urls import path, include

from . import views

urlpatterns = [

    path('', views.register,name= 'reg'),
    path('login', views.login_view,name='login'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path('resend-code/', views.resend_code, name='resend_code'),
    path('logout/', views.logoutView, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-reset-code/', views.verify_reset_code, name='verify_reset_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-reset-code/', views.resend_reset_code, name='resend_reset_code'),
    ]
