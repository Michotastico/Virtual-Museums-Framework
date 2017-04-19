import copy
from datetime import datetime
from django.db import transaction
from django.shortcuts import render, redirect
from django.http import JsonResponse

# Create your views here.
from django.utils.html import escapejs
from django.views.generic import TemplateView

from Apps.Curator.models.museums import UnityMuseum
from Apps.Curator.models.scheduling import Exposition
from Apps.Curator.views.resources import parse_inner_url


@transaction.atomic
def get_current_museum():
    today = datetime.today().date()
    exposition = Exposition.objects.filter(status=True).filter(start_date__lte=today).filter(end_date__gte=today)

    if len(exposition) < 1:
        return None

    arguments = dict()
    exposition = exposition[0]

    museum = exposition.museum

    arguments['title'] = museum.name
    arguments['id'] = museum.id

    museum = UnityMuseum.objects.get(id=museum.id)
    arguments['data'] = parse_inner_url(museum.data.url)
    arguments['js'] = parse_inner_url(museum.javascript.url)
    arguments['mem'] = parse_inner_url(museum.memory.url)
    arguments['total_memory'] = museum.memory_to_allocate

    return arguments


class IndexView(TemplateView):
    template_name = 'visitor/index.html'

    def get(self, request, *a, **ka):
        arguments = get_current_museum()
        if arguments is None:
            return redirect('/visitor/error')
        return render(request, self.template_name, arguments)


@transaction.atomic
def get_next_exposition():
    today = datetime.today().date()
    exposition = Exposition.objects.filter(status=True).filter(start_date__gte=today).order_by('start_date')

    if len(exposition) < 1:
        return None

    exposition = exposition[0]
    next_date = exposition.start_date

    return next_date


class NoExpositionView(TemplateView):
    template_name = 'visitor/no_expositions.html'

    def get(self, request, *a, **ka):
        arguments = dict()
        arguments['title'] = 'An error with the expositions just happened!'

        next_date = get_next_exposition()
        if next_date is None:
            arguments['body'] = 'There is no exposition active at this moment'
        else:
            arguments['body'] = 'The next active exposition is on ' + next_date.strftime("%B %d, %Y")
        return render(request, self.template_name, arguments)


class OpinionsView(TemplateView):
    template_name = 'visitor/opinions.html'

    def get(self, request, *a, **ka):
        return render(request, self.template_name)
