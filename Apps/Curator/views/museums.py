import os

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Avg
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.decorators import group_required
from Apps.Curator.forms import UnityExhibitForm, NewExhibitForm
from Apps.Curator.models.museums import Exhibit, UnityExhibit
from Apps.Curator.models.opinions import Opinion
from Apps.Curator.models.scheduling import Exhibition
from Apps.Curator.views.resources import parse_inner_url


def delete_unity_files(exhibit_id):
    unity_exhibit = UnityExhibit.objects.get(id=exhibit_id)

    memory = unity_exhibit.memory.path
    javascript = unity_exhibit.javascript.path
    data = unity_exhibit.data.path

    def delete():
        os.remove(memory)
        os.remove(javascript)
        os.remove(data)

    return delete


@transaction.atomic
def get_unity_data(exhibit):
    data = dict()

    data['title'] = exhibit.name
    exhibit = UnityExhibit.objects.get(id=exhibit.id)
    data['data'] = parse_inner_url(exhibit.data.url)
    data['js'] = parse_inner_url(exhibit.javascript.url)
    data['mem'] = parse_inner_url(exhibit.memory.url)
    data['total_memory'] = exhibit.memory_to_allocate

    return data


MUSEUM_TYPES = {
    'Unity': {'delete': delete_unity_files, 'get': get_unity_data,
              'template': 'curator/preview_unity.html'}
}


@transaction.atomic
def get_exhibit():
    exhibit_dict = {'exhibits': []}

    exhibits = Exhibit.objects.all()

    for exhibit in exhibits:
        expositions = Exhibition.objects.filter(exhibits=exhibit).filter(status=True)
        published = True if len(expositions) > 0 else False
        rating_object = Opinion.objects.filter(exhibit=exhibit).filter(validated=True).aggregate(Avg('rating'))
        rating = rating_object['rating__avg']
        if rating is None:
            rating = 0
        exhibit_dict['exhibits'].append({'id': exhibit.id,
                                        'name': exhibit.name,
                                        'published': published,
                                        'visitors': exhibit.visitors,
                                        'rating': rating})
    return exhibit_dict


@transaction.atomic
def delete_exhibit(exhibit_id):
    exhibit = Exhibit.objects.get(id=exhibit_id)

    delete_function = MUSEUM_TYPES[exhibit.exhibit_type.name]['delete'](exhibit_id)

    exhibit.delete()
    delete_function()


class ExhibitView(TemplateView):
    template_name = 'curator/exhibits.html'

    @method_decorator(group_required('Museum_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        exhibits = get_exhibit()
        return render(request, self.template_name, exhibits)

    @method_decorator(group_required('Museum_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        exhibit_id = request.POST.get('id_exhibit', None)
        delete = request.POST.get('delete', None)
        preview = request.POST.get('preview', None)

        if exhibit_id is not None:
            if delete in ['1']:
                delete_exhibit(exhibit_id)
            elif preview in ['1']:
                url = '/curator/exhibit-preview?id=' + exhibit_id
                return redirect(url)

        expositions = get_exhibit()

        return render(request, self.template_name, expositions)


class AddExhibitView(TemplateView):
    template_name = 'curator/add-exhibit.html'
    form = NewExhibitForm
    exhibit_type = ''

    @method_decorator(group_required('Museum_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        form = self.form()
        parameters = {'form': form, 'exhibit_type': self.exhibit_type}

        return render(request, self.template_name, parameters)

    @method_decorator(group_required('Museum_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        request_form = self.form(request.POST, request.FILES)
        args = {'exhibit_type': self.exhibit_type}

        if request_form.is_valid():
            request_form.save()
            args['success'] = 'success'
            request_form = self.form()

        args['form'] = request_form

        return render(request, self.template_name, args)


class AddUnityView(AddExhibitView):
    form = UnityExhibitForm
    exhibit_type = 'Unity'


@transaction.atomic
def get_exhibit_data(exhibit_id):
    exhibit = Exhibit.objects.get(id=exhibit_id)
    data = MUSEUM_TYPES[exhibit.exhibit_type.name]['get'](exhibit)
    return data


@transaction.atomic
def get_exhibit_model(exhibit_id):
    return Exhibit.objects.get(id=exhibit_id)


class PreviewExhibitView(TemplateView):

    @method_decorator(group_required('Museum_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        exhibit_id = request.GET.get('id', None)

        if exhibit_id is None:
            return redirect('/curator')

        exhibit = get_exhibit_model(exhibit_id)
        template = MUSEUM_TYPES[exhibit.exhibit_type.name]['template']

        args = get_exhibit_data(exhibit_id)

        return render(request, template, args)
