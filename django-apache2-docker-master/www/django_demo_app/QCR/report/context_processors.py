from django.conf import settings

def template_available(request):
    # return any necessary values
    return {
        'DEV_TOOLS': settings.DEV_TOOLS
    }