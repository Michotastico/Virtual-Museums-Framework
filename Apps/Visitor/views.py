import copy
import hashlib
import random
from datetime import datetime

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.validators import validate_email
from django.db import transaction
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.html import escapejs
from django.views.generic import TemplateView

from Apps.Curator.models.museums import UnityMuseum, Museum
from Apps.Curator.models.opinions import Opinion
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


def generate_hash_key(name, email, opinion):
    random_list = [name, email, opinion]
    random.shuffle(random_list)
    string = "".join(random_list)
    hash = hashlib.sha512(string).hexdigest()
    return hash


class OpinionsView(TemplateView):
    template_name = 'visitor/opinions.html'

    def get(self, request, *a, **ka):
        arguments = dict()
        museum_id = request.GET.get('id', None)
        if museum_id is not None:
            arguments['museum_id'] = museum_id
        return render(request, self.template_name, arguments)

    def post(self, request, *a, **ka):
        arguments = {'error': [], 'success': []}

        museum_id = request.POST.get('museum', '')
        museum = None

        try:
            if len(museum_id) < 1:
                raise ObjectDoesNotExist()
            museum = Museum.objects.get(id=museum_id)
        except ObjectDoesNotExist:
            arguments['error'].append('Invalid form. Please send your opinion from the exposition interface.')

        arguments['museum_id'] = museum_id

        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        opinion = request.POST.get('opinion', '')

        if len(name) < 1:
            arguments['error'].append('Please input a non-empty name.')

        try:
            if len(email) < 1:
                raise ValidationError('Empty email.')
            validate_email(email)
        except ValidationError:
            arguments['error'].append('Please input a non-empty email.')

        if len(opinion) < 1:
            arguments['error'].append('Please input a non-empty opinion.')

        opinion = escapejs(opinion)

        if len(arguments['error']) < 1:
            new_opinion = Opinion()
            new_opinion.person_name = name
            new_opinion.email = email
            new_opinion.opinion = opinion
            new_opinion.hash_key = generate_hash_key(name, email, opinion)
            new_opinion.museum = museum

            new_opinion.save()

            arguments['success'].append('A confirmation email was sent to your address to validated your opinion.')

        return render(request, self.template_name, arguments)
