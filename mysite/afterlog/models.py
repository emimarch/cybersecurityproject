from django.db import models

from django.contrib.auth.models import User


class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.IntegerField()

class Message(models.Model):
    #source = models.ForeignKey(User, on_delete=models.CASCADE, related_name='source')
    #target = models.ForeignKey(User, on_delete=models.CASCADE, related_name='target')
    source=models.TextField()
    target = models.TextField()
    amount = models.TextField()
    time = models.DateTimeField(auto_now_add=True)
    content = models.TextField()

def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.owner.id, filename)

class Coupon(models.Model):
	#owner = models.ForeignKey(User, on_delete=models.CASCADE)
    owner = models.TextField()
    data = models.FileField(upload_to=user_directory_path)

class Mail(models.Model):
    	content = models.TextField()
