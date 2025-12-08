from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.conf import settings
from ninja import NinjaAPI
from ninja.security import django_auth
from ninja.pagination import paginate
from . import models, schemas
from .auth import JWTAuth
from .permissions import OrganizationPermission
from datetime import datetime, timedelta, timezone
import jwt

api = NinjaAPI()


@api.post("auth/login")
def token_obtain(request, payload: schemas.LoginSchema):
    user = authenticate(request, username=payload.username,
                        password=payload.password)
    if not user:
        return 401, {"error": "Invalid credentials"}

    exp = datetime.now(timezone.utc) + timedelta(hours=8)
    token = jwt.encode({"user_id": user.id, "exp": exp},
                       settings.SECRET_KEY, algorithm="HS256")

    return {"access": token, "token_type": "bearer", "expires_at": exp.isoformat()}


@api.get("tasks/", auth=JWTAuth(), response=list[schemas.TaskSchema])
@paginate
def get_tasks(request):
    return models.Task.objects.filter(organization=request.organization).order_by("deadline_datetime_with_tz", "priority")


@api.post("tasks/", auth=JWTAuth())
def create_task(request, payload: schemas.TaskSchema):
    if not OrganizationPermission.is_assigned_to_in_user_organization(request, payload.assigned_to.id):
        return 403, {"error": "Assigned user does not belong to your organization"}

    try:
        task = models.Task.objects.create(
            title=payload.title,
            description=payload.description,
            completed=payload.completed,
            deadline_datetime_with_tz=payload.deadline_datetime_with_tz,
            priority=payload.priority,
            assigned_to=payload.user,
            organization=request.user.organization,
            created_at=datetime.datetime.now())

        task.save()
        return {"success": True}
    except Exception as e:
        return {"error": e}


@api.put("tasks/{task_id}", auth=JWTAuth())
def update_task(request, task_id: int, payload: schemas.TaskSchema):
    task = get_object_or_404(models.Task, id=task_id,
                             organization=request.organization)

    if payload.assigned_to and not OrganizationPermission.is_assigned_to_in_user_organization(request, payload.assigned_to):
        return 403, {"error": "Assigned user does not belong to your organization"}

    updated_fields = payload.dict(exclude_unset=True)
    for attr, value in updated_fields.items():
        setattr(task, attr, value)
    task.save()

    return {"success": True, "task_id": task.id}


@api.delete("tasks/{task_id}", auth=JWTAuth())
def delete_task(request, task_id: int):
    task = get_object_or_404(models.Task, id=task_id,
                             organization=request.organization)
    task.delete()

    return {"success": True, "task_id": task.id}


@api.get("users/", auth=JWTAuth(), response=list[schemas.UserSchema])
def get_users(request):
    return models.User.objects.filter(organization=request.organization)


@api.post("users/", auth=JWTAuth())
def create_user(request, payload: schemas.LoginSchema):
    if models.User.objects.filter(username=payload.username).exists():
        return 400, {"error": "Username already exists"}

    try:
        user = models.User.objects.create_user(
            username=payload.username,
            password=payload.password,
            organization=request.organization
        )
        return {"success": True, "user_id": user.id}
    except Exception as e:
        return 400, {"error": str(e)}
