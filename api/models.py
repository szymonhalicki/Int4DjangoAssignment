from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class User(AbstractUser):
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE)

    def __str__(self):
        return self.username
    
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline_datetime_with_tz = models.DateTimeField()
    priority = models.IntegerField()

    def __str__(self):
        return self.title
    