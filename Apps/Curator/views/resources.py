import copy
import os
import re

from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.decorators import group_required
from Apps.Curator.forms import TemplateForm, VideoForm, ModelForm, ImageForm, MusicForm
from Apps.Curator.models.resources import ExternalModel, ExternalImage, ExternalVideo, ExternalMusic


def parse_inner_url(url):
    return re.sub(r'.*/static', '/static', url)


@transaction.atomic
def query_music():
    music_list = list()
    musics = ExternalMusic.objects.all()
    for music in musics:
        music_template = dict()
        music_template['id'] = music.id
        music_template['title'] = music.title
        music_template['description'] = music.description
        music_template['href'] = parse_inner_url(music.file.url)
        music_list.append(music_template)
    return music_list


@transaction.atomic
def delete_music(_id):
    music = ExternalMusic.objects.get(id=_id)
    path = music.file.path
    music.delete()
    os.remove(path)


@transaction.atomic
def query_video():
    video_list = list()
    videos = ExternalVideo.objects.all()
    for video in videos:
        video_template = dict()
        video_template['id'] = video.id
        video_template['title'] = video.title
        video_template['description'] = video.description
        video_template['href'] = parse_inner_url(video.file.url)
        video_list.append(video_template)
    return video_list


@transaction.atomic
def delete_video(_id):
    video = ExternalVideo.objects.get(id=_id)
    path = video.file.path
    video.delete()
    os.remove(path)


@transaction.atomic
def query_image():
    image_list = list()
    images = ExternalImage.objects.all()
    for image in images:
        image_template = dict()
        image_template['id'] = image.id
        image_template['title'] = image.title
        image_template['description'] = image.description
        image_template['href'] = parse_inner_url(image.file.url)
        image_list.append(image_template)
    return image_list


@transaction.atomic
def delete_image(_id):
    image = ExternalImage.objects.get(id=_id)
    path = image.file.path
    image.delete()
    os.remove(path)


@transaction.atomic
def query_model():
    model_list = list()
    models = ExternalModel.objects.all()
    for model in models:
        model_template = dict()
        model_template['id'] = model.id
        model_template['title'] = model.title
        model_template['description'] = model.description
        model_template['href'] = parse_inner_url(model.file.url)
        split_name = os.path.splitext(model_template['href'])
        ext = split_name[1]
        model_template['extension'] = ext
        model_list.append(model_template)
    return model_list


@transaction.atomic
def delete_model(_id):
    model = ExternalModel.objects.get(id=_id)
    path = model.file.path
    model.delete()
    os.remove(path)

POSSIBLE_RESOURCE = {
    'Music': {
        'name': 'Music', 'form': MusicForm, 'template': 'curator/resources/resources-music.html',
        'elements': query_music, 'delete': delete_music
    },
    'Image': {
        'name': 'Image', 'form': ImageForm, 'template': 'curator/resources/resources-images.html',
        'elements': query_image, 'delete': delete_image
    },
    'Model': {
        'name': 'Model', 'form': ModelForm, 'template': 'curator/resources/resources-models.html',
        'elements': query_model, 'delete': delete_model
    },
    'Video': {
        'name': 'Video', 'form': VideoForm, 'template': 'curator/resources/resources-video.html',
        'elements': query_video, 'delete': delete_video
    },
}


class ResourcesView(TemplateView):
    template_name = 'curator/resources/resources.html'
    selector = {'header': {'display': 'Models, Music, Images, etc:',
                           'selected': 'selected'}, 'options': []}
    for resource in POSSIBLE_RESOURCE:
        resource = POSSIBLE_RESOURCE[resource]
        local_dict = {'value': resource['name'],
                      'display': resource['name'],
                      'selected': ''}
        selector['options'].append(local_dict)

    def selector_current(self, specific_resource):

        specific_selector = copy.deepcopy(self.selector)
        specific_template = self.template_name

        if specific_resource:
            specific_selector['header']['selected'] = ''
            specific_template = POSSIBLE_RESOURCE.get(specific_resource, None)

            if specific_template is not None:
                specific_template = specific_template['template']
                for option in specific_selector['options']:
                    if option['value'] == specific_resource:
                        option['selected'] = 'selected'
        return specific_selector, specific_template

    @method_decorator(group_required('Resources_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        specific_resource = request.GET.get('resource', None)
        specific_selector, specific_template = self.selector_current(specific_resource)

        if specific_resource is not None:
            specific_selector['current_selection'] = specific_resource

        resource_list = POSSIBLE_RESOURCE.get(specific_resource, None)

        if resource_list is not None:
            resource_list = resource_list['elements']()
            specific_selector['elements'] = resource_list

        success = request.GET.get('success', None)
        if success is not None and success == 'true':
            specific_selector['success'] = True

        return render(request, specific_template, specific_selector)

    @method_decorator(group_required('Resources_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):

        specific_resource = request.POST.get('resource', None)
        new = request.POST.get('new-resource', None)
        delete_resource = request.POST.get('delete', '0')
        specific_selector, specific_template = self.selector_current(specific_resource)

        if delete_resource not in ['0']:
            try:
                deleter = POSSIBLE_RESOURCE[specific_resource]['delete']
                deleter(delete_resource)
                specific_selector['success_delete'] = True
            except IOError:
                specific_selector['error'] = 'True'

        resource_list = POSSIBLE_RESOURCE.get(specific_resource, None)

        if specific_resource is not None:
            specific_selector['current_selection'] = specific_resource

        if resource_list is not None:
            resource_list = resource_list['elements']()
            specific_selector['elements'] = resource_list

        if new in ['1']:
            url = '/curator/new-resources?resource='+specific_resource
            return redirect(url)

        return render(request, specific_template, specific_selector)


class NewResourcesView(TemplateView):
    template_name = 'curator/new-resource.html'

    @method_decorator(group_required('Resources_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        parameters = {}
        form_type = request.GET.get('resource', None)
        if form_type:
            form = POSSIBLE_RESOURCE.get(form_type, None)

            if form is not None:
                form = form['form']()
            else:
                form = TemplateForm()

            parameters = {'form': form, 'resource': form_type}

        return render(request, self.template_name, parameters)

    @method_decorator(group_required('Resources_team'))
    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        request_form = TemplateForm(request.POST, request.FILES)
        args = {}

        form_type = request.GET.get('resource', None)
        if form_type:
            args['resource'] = form_type
            form_type = POSSIBLE_RESOURCE.get(form_type, None)

            if form_type is not None:
                request_form = form_type['form'](request.POST, request.FILES)

        if request_form.is_valid():
            request_form.save()
            return redirect('/curator/resources?success=true&resource='+args['resource'])

        args['form'] = request_form

        return render(request, self.template_name, args)