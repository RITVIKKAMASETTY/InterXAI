from django.shortcuts import render
from .models import *
from django.contrib.auth.decorators import login_required

@login_required
def public_chat(request):

    rooms = chatGroup.objects.all()
    messages = Messages.objects.all().order_by('createdAt')

    return render(request, 'groupchat/gc.html', {
        'messages': messages,
        'rooms': rooms,  # Pass the list of usernames
    })