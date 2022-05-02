from django.db import models

from django.contrib.auth.models import User


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField()

class Message(models.Model):
    source = models.ForeignKey(User, on_delete=models.CASCADE, related_name='source')
    target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target')
    content = models.TextField()
    amount = models.TextField()
    time = models.DateTimeField(auto_now_add=True)