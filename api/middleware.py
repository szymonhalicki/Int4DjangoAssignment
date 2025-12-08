class OrganizationContextMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if request.user and hasattr(request.user, 'organization'):
            request.organization = request.user.organization
        else:
            request.organization = None

        response = self.get_response(request)

        return response