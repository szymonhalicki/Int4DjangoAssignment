from pydantic import BaseModel
from ninja import ModelSchema
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