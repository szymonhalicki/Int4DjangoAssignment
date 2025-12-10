import jwt
from ninja.security import HttpBearer
from django.conf import settings
from django.contrib.auth import get_user_model
# from .models import User

User = get_user_model()

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        print(f"Token received: {token[:50] if token else 'None'}...")
        
        if not token:
            print("ERROR: No token provided")
            return None
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])    
            user = User.objects.get(pk=payload["user_id"])
            
            if user and user.is_active:
                request.organization = user.organization
                return user
            
            return None
        
        except User.DoesNotExist:
            return None
        except jwt.ExpiredSignatureError:
            return None
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return None
        