from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

# Create your models here.
class chatGroup(models.Model):
    roomName= models.CharField(max_length=30)
    def __str__(self):
        return self.roomName

class Messages(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(chatGroup, on_delete=models.CASCADE)
    def __str__(self):
        return f"{self.user} - {self.group}"