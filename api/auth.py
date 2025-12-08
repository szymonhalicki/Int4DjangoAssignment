import jwt
from ninja.security import HttpBearer
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        print(f"Token received: {token[:50] if token else 'None'}...")
        
        if not token:
            print("ERROR: No token provided")
            return None
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])       
            user = User.objects.get(id=payload["user_id"])
            
            if user and user.is_active:
                request.user = user
            
            return user
            
        except jwt.ExpiredSignatureError:
            return None
        except (jwt.InvalidTokenError, User.DoesNotExist):
            return None
        