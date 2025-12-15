from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.conf import settings
from ninja import NinjaAPI
from ninja.pagination import paginate
from . import models, schemas
from .auth import JWTAuth
from .tenant import get_current_organization
from datetime import datetime, timedelta, timezone
import jwt

api = NinjaAPI()


@api.post("auth/login", response={200: schemas.TokenSchema, 401: schemas.MessageSchema})
def token_obtain(request, payload: schemas.LoginSchema):
    print(f"Attempting login for: {payload.username}")
    user = authenticate(request, username=payload.username,
                        password=payload.password)
    if not user:
        return 401, {"message": "Invalid credentials"}

    exp = datetime.now(timezone.utc) + timedelta(hours=int(settings.JWT_EXPIRATION_HOURS))
    payload = {"user_id": user.id, "exp": int(exp.timestamp())}
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    return 200, {"token": token, "expires": exp.isoformat()}


@api.get("tasks", auth=JWTAuth(), response=list[schemas.TaskSchema])
@paginate
def get_tasks(request):
    return models.Task.objects.select_related('assigned_to', 'organization').all()

@api.post("tasks", auth=JWTAuth(), response={200: schemas.TaskCreatedSchema, 403: schemas.MessageSchema, 500: schemas.MessageSchema})
def create_task(request, payload: schemas.TaskInputSchema):
    try:
        task = models.Task.objects.create(
            title=payload.title,
            description=payload.description,
            completed=payload.completed,
            deadline_datetime_with_tz=payload.deadline_datetime_with_tz,
            priority=payload.priority,
            assigned_to_id=payload.assigned_to,
            organization_id=request.user.organization.id)

        return 200, {"task_id": task.id}
    except ValueError as e:
        return 403, {"message": str(e)}
    except Exception as e:
        return 500, {"message": str(e)}


@api.put("tasks/{task_id}", auth=JWTAuth(), response={200: schemas.TaskCreatedSchema, 403: schemas.MessageSchema, 500: schemas.MessageSchema})
def update_task(request, task_id: int, payload: schemas.TaskInputSchema):
    task = get_object_or_404(models.Task, id=task_id)
    
    task.title=payload.title
    task.description=payload.description
    task.completed=payload.completed
    task.deadline_datetime_with_tz=payload.deadline_datetime_with_tz
    task.priority=payload.priority
    task.assigned_to_id=payload.assigned_to

    try: 
        task.save()
        return 200, {"task_id": task.id}
    except ValueError as e:
        return 403, {"message": str(e)}
    except Exception as e:
        return 500, {"message": str(e)}

@api.delete("tasks/{task_id}", auth=JWTAuth(), response={200: schemas.MessageSchema})
def delete_task(request, task_id: int):
    task = get_object_or_404(models.Task, id=task_id)
    task.delete()

    return 200, {"message": "Task deleted"}


@api.get("users/", auth=JWTAuth(), response=list[schemas.UserSchema])
def get_users(request):
    return models.User.org_objects.all()


@api.post("users/", auth=JWTAuth(), response={200: schemas.UserCreatedSchema, 400: schemas.MessageSchema})
def create_user(request, payload: schemas.LoginSchema):
    if models.User.objects.filter(username=payload.username).exists():
        return 400, {"message": "Username already exists"}

    try:
        user = models.User.org_objects.create_user(
            username=payload.username,
            password=payload.password,
            organization=get_current_organization()
        )
        return 200, {"user_id": user.id}
    except Exception as e:
        return 400, {"message": str(e)}
