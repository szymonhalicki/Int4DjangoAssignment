from pydantic import BaseModel
import models
import datetime

class LoginSchema(BaseModel):
    username: str
    password: str
    
class TaskCreateSchema(BaseModel):
    title: str
    description: str
    completed: bool
    deadline_datetime_with_tz: datetime
    priority: int
    
class TaskUpdateSchema(BaseModel):
    id: int
    title: str
    description: str
    completed: bool
    deadline_datetime_with_tz: datetime
    priority: int