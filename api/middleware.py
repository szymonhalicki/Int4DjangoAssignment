class OrganizationContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Middleware runs before authentication so the organization is set in AUTH. Could not solve it.
        if not hasattr(request, 'organization'):
            request.organization = None
            
        response = self.get_response(request)
        return response