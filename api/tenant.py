import threading

_thread_locals = threading.local()

def set_current_organization(org):
    _thread_locals.organization = org

def get_current_organization():
    return getattr(_thread_locals, 'organization', None)