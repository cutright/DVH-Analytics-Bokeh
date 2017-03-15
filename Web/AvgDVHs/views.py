from django.http import HttpResponse


def index(request):
    return HttpResponse("DVH Database, OH YEAH!")