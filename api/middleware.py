from .tenant import set_current_organization
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from .models import User
import jwt

class JWTAuthenticationMiddleware(MiddlewareMixin):
    def process_request(self, request):
        request.user = None
        request.jwt_error = None
        
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return
        
        token = auth_header.removeprefix('Bearer ')
        
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )
            
            user_id = payload.get("user_id")
            
            if user_id:
                request.user = User.objects.select_related('organization').get(
                    pk=user_id,
                    is_active=True
                )

        except jwt.ExpiredSignatureError:
            request.jwt_error = "Token has expired"
        except jwt.InvalidTokenError:
            request.jwt_error = "Invalid token"
        except User.DoesNotExist:
            request.jwt_error = "User not found or inactive"
        except Exception as e:
            request.jwt_error = f"Authentication error: {str(e)}"

class OrganizationContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        org = None
        
        if hasattr(request.user, 'organization'):
            org = request.user.organization

        set_current_organization(org)
        
        response = self.get_response(request)
        
        set_current_organization(None)
        
        return response