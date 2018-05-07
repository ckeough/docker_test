from .models import Review
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

def user_is_assigned_review(function):
    def wrap(request, *args, **kwargs):
        review = Review.objects.get(pk=kwargs['entry_id'])
        if review.user == request.user:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
	
def qcr_user_authenticated(function):
	def wrap(request, *args, **kwargs):
		if (request.user.is_authenticated) and ((request.user.groups.filter(name='qcr_user').exists()) or (request.user.is_staff) or (request.user.is_superuser)):
			return function(request, *args, **kwargs)
		
		else:
			url = reverse('notauser')
			return HttpResponseRedirect(url)
	
	wrap.__doc__ = function.__doc__
	wrap.__name__ = function.__name__
	return wrap