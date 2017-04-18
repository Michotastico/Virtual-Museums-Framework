import os

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.forms import UnityMuseumForm
from Apps.Curator.models.museums import Museum, UnityMuseum
from Apps.Curator.models.scheduling import Exposition
from Apps.Curator.views.resources import parse_inner_url


@transaction.atomic
def get_museums():
    museums_dict = {'museums': []}

    museums = Museum.objects.all()

    for museum in museums:
        expositions = Exposition.objects.filter(museum=museum).filter(status=True)
        published = True if len(expositions) > 0 else False
        museums_dict['museums'].append({'id': museum.id,
                                        'name': museum.name,
                                        'published': published,
                                        'visitors': museum.visitors})
    return museums_dict


@transaction.atomic
def delete_museum(museum_id):
    museum = Museum.objects.get(id=museum_id)
    # TODO Delete stored files
    unity_museum = UnityMuseum.objects.get(id=museum.id)

    memory = unity_museum.memory.path
    javascript = unity_museum.javascript.path
    data = unity_museum.data.path

    museum.delete()

    os.remove(memory)
    os.remove(javascript)
    os.remove(data)


class MuseumsView(TemplateView):
    template_name = 'curator/museums.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        museums = get_museums()
        return render(request, self.template_name, museums)

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

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        form = UnityMuseumForm()
        parameters = {'form': form}

        return render(request, self.template_name, parameters)

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
    data = dict()
    museum = Museum.objects.get(id=museum_id)

    data['title'] = museum.name

    museum = UnityMuseum.objects.get(id=museum.id)
    data['data'] = parse_inner_url(museum.data.url)
    data['js'] = parse_inner_url(museum.javascript.url)
    data['mem'] = parse_inner_url(museum.memory.url)
    data['total_memory'] = museum.memory_to_allocate

    return data


class PreviewMuseumView(TemplateView):
    template_name = 'curator/preview.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        museum_id = request.GET.get('id', None)

        if museum_id is None:
            return redirect('/curator')

        args = get_museum_data(museum_id)

        return render(request, self.template_name, args)
