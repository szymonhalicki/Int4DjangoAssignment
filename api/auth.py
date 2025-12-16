from ninja.security import HttpBearer
from django.conf import settings
from .models import User
from .tenant import set_current_organization
import jwt


class JWTAuth(HttpBearer):
    def authenticate(self, request, token):
        if hasattr(request, 'user'):
            request.user = None

        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return

        token = auth_header.removeprefix('Bearer ')

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                settings.JWT_ALGORITHM
            )
            
            user_id = payload.get("user_id")
            
            user = User.all_objects.get(id=user_id)
            request.user = user
            
        except jwt.ExpiredSignatureError:
            request.jwt_error = "Token has expired"
        except jwt.InvalidTokenError:
            request.jwt_error = "Invalid token"
        except User.DoesNotExist:
            request.jwt_error = "User not found or inactive"
        except Exception as e:
            request.jwt_error = f"Authentication error: {str(e)}"

        if hasattr(request.user, 'organization'):
            set_current_organization(request.user.organization)
            request.user = user
            return user

        if hasattr(request, 'jwt_error'):
            return None

        return None
