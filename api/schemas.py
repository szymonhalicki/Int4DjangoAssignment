from pydantic import BaseModel
from ninja import ModelSchema, Schema
from datetime import datetime
from .models import User, Task, Organization

class OrganizationSchema(ModelSchema):
    class Meta:
        model = Organization
        fields = ['id', 'name']

class UserSchema(ModelSchema):
    organization: OrganizationSchema
    
    class Meta:
        model = User
        fields = ['id', 'username', 'organization']
        
class LoginSchema(ModelSchema):
    class Meta:
        model = User
        fields = ['username', 'password']
        
class TaskSchema(ModelSchema):
    assigned_to: UserSchema
    organization: OrganizationSchema
    
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'completed', 'assigned_to', 'organization', 'created_at', 'deadline_datetime_with_tz', 'priority']

class TaskInputSchema(Schema):
    title: str
    description: str
    completed: bool = False
    assigned_to: int
    deadline_datetime_with_tz: datetime
    priority: int

class TokenSchema(Schema):
    token: str
    expires: datetime

class MessageSchema(Schema):
    message: str
    
class UserCreatedSchema(Schema):
    user_id: int 
    
class TaskCreatedSchema(Schema):
    task_id: int 