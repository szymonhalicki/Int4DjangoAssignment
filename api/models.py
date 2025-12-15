from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from .tenant import get_current_organization

class OrganizationManager(models.Manager):    
    def get_queryset(self):
        qs = super().get_queryset()
        org_id = get_current_organization()
        
        if org_id is None:
            return qs.none()
        
        return qs.filter(organization_id=org_id)

class OrganizationUserManager(BaseUserManager, OrganizationManager):
    def create_user(self, username, password, organization, **extra_fields):
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")
        if not organization:
            raise ValueError("Organization ID is required")
        
        if hasattr(organization, "id"):
            org = organization
        else:
            try:
                org = Organization.objects.get(id=organization)
            except Organization.DoesNotExist:
                raise ValueError(f"Organization with id {organization} does not exist")
        
        user = self.model(username=username, organization=org, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, password, organization=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if organization is None:
            org, _ = Organization.objects.get_or_create(name="Default Organization")
            organization = org
            
        return self.create_user(username, password, organization, **extra_fields)

class Organization(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

class BaseOrganizationModel(models.Model):
    organization = models.ForeignKey(Organization,on_delete=models.CASCADE, db_index=True)
    
    objects = OrganizationManager()
    
    all_objects = models.Manager()
    
    class Meta:
        abstract = True


class User(AbstractUser):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    
    objects = BaseUserManager()
    
    org_objects = OrganizationUserManager()
    

class Task(BaseOrganizationModel):
    title = models.CharField(max_length=200)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    deadline_datetime_with_tz = models.DateTimeField()
    priority = models.IntegerField()

    objects = OrganizationManager()
    all_objects = models.Manager()
    
    def save(self, *args, **kwargs):
        if not self.organization:
            org = get_current_organization()
            if org:
                self.organization = org
            else:
                raise ValueError("No organization context set!")
        if self.assigned_to and self.assigned_to.organization != self.organization:
            raise ValueError("Cannot assign task to user from different organization")    
        
        super().save(*args, **kwargs)