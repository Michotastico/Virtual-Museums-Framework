import os

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.decorators import group_required
from Apps.Curator.forms import UnityMuseumForm
from Apps.Curator.models.museums import Museum, UnityMuseum
from Apps.Curator.models.opinions import Opinion
from Apps.Curator.models.scheduling import Exposition
from Apps.Curator.views.resources import parse_inner_url


def delete_unity_files(museum_id):
    unity_museum = UnityMuseum.objects.get(id=museum_id)

    memory = unity_museum.memory.path
    javascript = unity_museum.javascript.path
    data = unity_museum.data.path

    def delete():
        os.remove(memory)
        os.remove(javascript)
        os.remove(data)

    return delete


@transaction.atomic
def get_unity_data(museum):
    data = dict()

    data['title'] = museum.name
    museum = UnityMuseum.objects.get(id=museum.id)
    data['data'] = parse_inner_url(museum.data.url)
    data['js'] = parse_inner_url(museum.javascript.url)
    data['mem'] = parse_inner_url(museum.memory.url)
    data['total_memory'] = museum.memory_to_allocate

    return data


MUSEUM_TYPES = {
    'unity': {'model': UnityMuseum, 'delete': delete_unity_files,
              'get': get_unity_data, 'template': 'curator/preview_unity.html'}
}


@transaction.atomic
def get_museums():
    museums_dict = {'museums': []}

    museums = Museum.objects.all()

    for museum in museums:
        expositions = Exposition.objects.filter(museum=museum).filter(status=True)
        published = True if len(expositions) > 0 else False
        rating_object = Opinion.objects.filter(museum=museum).filter(validated=True).aggregate(Avg('rating'))
        rating = rating_object['rating__avg']
        if rating is None:
            rating = 0
        museums_dict['museums'].append({'id': museum.id,
                                        'name': museum.name,
                                        'published': published,
                                        'visitors': museum.visitors,
                                        'rating': rating})
    return museums_dict


@transaction.atomic
def delete_museum(museum_id):
    museum = Museum.objects.get(id=museum_id)

    delete_function = MUSEUM_TYPES[museum.museum_type.museum_type]['delete'](museum_id)

    museum.delete()
    delete_function()


class MuseumsView(TemplateView):
    template_name = 'curator/museums.html'

    @method_decorator(group_required('Museum_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        museums = get_museums()
        return render(request, self.template_name, museums)

    @method_decorator(group_required('Museum_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        museum_id = request.POST.get('id_museum', None)
        delete = request.POST.get('delete', None)
        preview = request.POST.get('preview', None)

        if museum_id is not None:
            if delete in ['1']:
                delete_museum(museum_id)
            elif preview in ['1']:
                url = '/curator/museum-preview?id=' + museum_id
                return redirect(url)

        expositions = get_museums()

        return render(request, self.template_name, expositions)


class AddUnityView(TemplateView):
    template_name = 'curator/unity-museum.html'

    @method_decorator(group_required('Museum_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        form = UnityMuseumForm()
        parameters = {'form': form}

        return render(request, self.template_name, parameters)

    @method_decorator(group_required('Museum_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        request_form = UnityMuseumForm(request.POST, request.FILES)
        args = {}

        if request_form.is_valid():
            request_form.save()
            args['success'] = 'success'
            request_form = UnityMuseumForm()

        args['form'] = request_form

        return render(request, self.template_name, args)


@transaction.atomic
def get_museum_data(museum_id):
    museum = Museum.objects.get(id=museum_id)
    data = MUSEUM_TYPES[museum.museum_type.museum_type]['get'](museum)
    return data


@transaction.atomic
def get_museum_model(museum_id):
    return Museum.objects.get(id=museum_id)


class PreviewMuseumView(TemplateView):

    @method_decorator(group_required('Museum_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        museum_id = request.GET.get('id', None)

        if museum_id is None:
            return redirect('/curator')

        museum = get_museum_model(museum_id)
        template = MUSEUM_TYPES[museum.museum_type.museum_type]['template']

        args = get_museum_data(museum_id)

        return render(request, template, args)
