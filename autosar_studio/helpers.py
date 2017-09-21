from django.http import JsonResponse
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.db import IntegrityError, transaction

def APIResponse(status, message={}):
    return JsonResponse(message, status=status)


def access_error_wrapper(func):
    def func_wrapper(request, *args, **kwargs):
        try:
            with transaction.atomic():
                return func(request, *args, **kwargs)
        except Http404:
            return APIResponse(404)
        except ObjectDoesNotExist:
            return APIResponse(404)
        except PermissionDenied:
            return APIResponse(550)
        except MultiValueDictKeyError:
            return APIResponse(404, {'error' : 'Missing Parameter'})
        except IntegrityError:
            return APIResponse(500, {'error' : 'Integrity Error'})
        except Exception as exc:
            return APIResponse(500, {'error' : str(type(exc)) + ": " + str(exc)})
    return func_wrapper


def OwnsFile(user_file, user):
    if user_file is None or user_file.directory.GetProject() is None:
        raise Http404
    else:
        owner = user_file.directory.GetProject().user
        if user.is_staff or owner.id == user.id:
            return True
    return False
