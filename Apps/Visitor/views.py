from django.db import transaction
from django.shortcuts import render, redirect

# Create your views here.
from django.views.generic import TemplateView

from Apps.Curator.models.museums import UnityMuseum
from Apps.Curator.models.scheduling import Exposition
from Apps.Curator.views.resources import parse_inner_url


@transaction.atomic
def get_current_museum():
    exposition = Exposition.objects.filter(status=True)

    # TODO check dates

    if len(exposition) < 1:
        return redirect('/')
    arguments = {}
    exposition = exposition[0]

    museum = exposition.museum

    arguments['title'] = museum.name

    museum = UnityMuseum.objects.get(id=museum.id)
    arguments['data'] = parse_inner_url(museum.data)
    arguments['js'] = parse_inner_url(museum.javascript)
    arguments['mem'] = parse_inner_url(museum.memory)
    arguments['total_memory'] = museum.memory_to_allocate

    return arguments


class IndexView(TemplateView):
    template_name = 'visitor/index.html'

    def get(self, request, *a, **ka):
        arguments = get_current_museum()
        return render(request, self.template_name, arguments)