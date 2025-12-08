from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password, organization, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")
        if not organization:
            raise ValueError("Organization ID is required")
        
        try:
            organization = Organization.objects.get(id=organization.id)
        except Organization.DoesNotExist:
            raise ValueError(f"Organization with id {organization.id} does not exist")
        
        user = self.model(username=username, organization=organization, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password, organization, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, password, organization, **extra_fields)
        

# Create your models here.
class Organization(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class User(AbstractUser):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    
    objects = CustomUserManager()

    def __str__(self):
        return self.username
    
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline_datetime_with_tz = models.DateTimeField()
    priority = models.IntegerField()

    def __str__(self):
        return self.title
    