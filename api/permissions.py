from django.shortcuts import get_object_or_404
from . import models

class OrganizationPermission:
    
    @staticmethod
    def is_task_in_user_organization(request, task_id):
        task = get_object_or_404(models.Task, id=task_id)
        return task.organization == request.organization

    @staticmethod
    def is_user_in_user_organization(request, user_id):
        user = get_object_or_404(models.User, id=user_id)
        return user.organization == request.organization

    @staticmethod
    def is_assigned_to_in_user_organization(request, assigned_to_id):
        assigned_user = get_object_or_404(models.User, id=assigned_to_id)
        return assigned_user.organization == request.organization