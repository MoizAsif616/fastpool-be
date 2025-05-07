from django.conf import settings

def get_server_url():
    # Use the first non-localhost IP from ALLOWED_HOSTS
    for host in settings.ALLOWED_HOSTS:
        if host not in ['localhost', '127.0.0.1']:
            return f"{host}:8000"  # Add your port
    return "http://localhost:8000"  # Fallback