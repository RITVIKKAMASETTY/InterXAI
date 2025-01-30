from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

class posts(models.Model):
    post = models.CharField(max_length=100, default="Default Post Title")
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.post


class conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=1)
    post = models.ForeignKey(posts, on_delete=models.CASCADE, default=1)
    time = models.DateTimeField(auto_now_add=True)  # Automatically set to current time when created

    def __str__(self):
        return f"Conversation ({self.user.username if self.user else 'Unknown User'}, {self.post.post}, {self.time})"
class summary(models.Model):
    convo = models.ForeignKey(conversation, on_delete=models.CASCADE, db_index=True, default=1)
    sum = models.TextField()

class questions(models.Model):
    convo = models.ForeignKey(conversation, on_delete=models.CASCADE, db_index=True, default=1)
    user = models.CharField(max_length=100, default="user")
    question = models.TextField(default="Default question text")
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set to current time when created

    def __str__(self):
        return f"Question ({self.user}, {self.created_at})"

class VerificationCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)

    def is_expired(self):
        time_elapsed = timezone.now() - self.created_at
        return time_elapsed.total_seconds() > 30