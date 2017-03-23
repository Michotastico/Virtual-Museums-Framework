import copy
import os

import re
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.forms import ImageForm, TemplateForm, ModelForm, MusicForm, VideoForm
from Apps.Curator.models.resources import ExternalMusic, ExternalImage, ExternalModel, ExternalVideo
from Apps.Curator.models.rooms import Room
from Apps.Curator.models.opinions import Opinion


class IndexView(TemplateView):
    template_name = 'curator/index.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)


@transaction.atomic
def delete_opinion(opinion_id):
    opinion = Opinion.objects.get(id=opinion_id)
    opinion.delete()


@transaction.atomic
def reverse_opinion_status(opinion_id):
    opinion = Opinion.objects.get(id=opinion_id)
    opinion.status = not opinion.status
    opinion.save()


@transaction.atomic
def query_opinion(room_name, approved, pending):
    opinion_list = list()

    if not approved and not pending:
        return opinion_list

    selected_room = Room.objects.get(name=room_name)
    opinions = Opinion.objects.filter(validated=True).filter(room=selected_room)
    if approved and not pending:
        opinions = opinions.exclude(status=False)
    elif pending and not approved:
        opinions = opinions.exclude(status=True)

    for opinion in opinions:
        opinion_template = dict()
        opinion_template['id'] = opinion.id
        opinion_template['name'] = opinion.person_name
        opinion_template['opinion'] = opinion.opinion
        opinion_template['avatar'] = opinion.avatar
        opinion_template['status'] = opinion.status
        opinion_template['email'] = opinion.email

        opinion_list.append(opinion_template)
    return opinion_list


class OpinionsView(TemplateView):
    template_name = 'curator/opinions.html'
    selector = {'header': {'display': 'Select a Room from the list:',
                           'selected': 'selected'},
                'options': [{'value': 'Master room', 'display': 'Master room', 'selected': ''},
                            {'value': 'Front yard', 'display': 'Front yard', 'selected': ''}],
                'approved': '',
                'pending': ''}

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name, self.selector)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        current_selector = copy.deepcopy(self.selector)

        current_room = request.POST.get('room', None)
        checkbox_approved = request.POST.get('approved', None)
        checkbox_pending = request.POST.get('pending', None)
        opinion_id = request.POST.get('id_opinion', None)

        reverse_option = request.POST.get('reverse', None)
        delete_option = request.POST.get('delete', None)

        if reverse_option is not None and reverse_option in ['1']:
            reverse_opinion_status(opinion_id)

        elif delete_option is not None and delete_option in ['1']:
            delete_opinion(opinion_id)

        approved = False
        pending = False

        if checkbox_approved is not None:
            current_selector['approved'] = 'checked'
            approved = True
        if checkbox_pending is not None:
            current_selector['pending'] = 'checked'
            pending = True

        if current_room is not None:
            current_selector['current_room'] = current_room
            current_selector['header']['selected'] = ''
            for option in current_selector['options']:
                if option['value'] == current_room:
                    option['selected'] = 'selected'
                    break

            opinions = query_opinion(current_room, approved, pending)
            current_selector['opinions'] = opinions

        return render(request, self.template_name, current_selector)


class NewRoomsView(TemplateView):
    template_name = 'curator/new-rooms.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)


class RoomsView(TemplateView):
    template_name = 'curator/rooms.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)


def parse_inner_url(url):
    return re.sub(r'.*/static', '/static', url)


@transaction.atomic
def query_music():
    music_list = list()
    musics = ExternalMusic.objects.all()
    for music in musics:
        music_template = dict()
        music_template['title'] = music.title
        music_template['description'] = music.description
        music_template['href'] = parse_inner_url(music.file.url)
        music_list.append(music_template)
    return music_list


@transaction.atomic
def query_video():
    video_list = list()
    videos = ExternalVideo.objects.all()
    for video in videos:
        video_template = dict()
        video_template['title'] = video.title
        video_template['description'] = video.description
        video_template['href'] = parse_inner_url(video.file.url)
        video_list.append(video_template)
    return video_list


@transaction.atomic
def query_image():
    image_list = list()
    images = ExternalImage.objects.all()
    for image in images:
        image_template = dict()
        image_template['title'] = image.title
        image_template['description'] = image.description
        image_template['href'] = parse_inner_url(image.file.url)
        image_list.append(image_template)
    return image_list


@transaction.atomic
def query_model():
    model_list = list()
    models = ExternalModel.objects.all()
    for model in models:
        model_template = dict()
        model_template['title'] = model.title
        model_template['description'] = model.description
        model_template['href'] = parse_inner_url(model.file.url)
        split_name = os.path.splitext(model_template['href'])
        ext = split_name[1]
        model_template['extension'] = ext
        model_list.append(model_template)
    return model_list

POSSIBLE_RESOURCE = {
    'Music': {
        'name': 'Music', 'form': MusicForm, 'template': 'curator/resources/resources-music.html',
        'elements': query_music
    },
    'Image': {
        'name': 'Image', 'form': ImageForm, 'template': 'curator/resources/resources-images.html',
        'elements': query_image
    },
    'Model': {
        'name': 'Model', 'form': ModelForm, 'template': 'curator/resources/resources-models.html',
        'elements': query_model
    },
    'Video': {
        'name': 'Video', 'form': VideoForm, 'template': 'curator/resources/resources-video.html',
        'elements': query_video
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

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        specific_resource = request.GET.get('resource', None)
        specific_selector, specific_template = self.selector_current(specific_resource)

        resource_list = POSSIBLE_RESOURCE.get(specific_resource, None)

        if resource_list is not None:
            resource_list = resource_list['elements']()
            specific_selector['elements'] = resource_list

        success = request.GET.get('success', None)
        if success is not None and success == 'true':
            specific_selector['success'] = True

        return render(request, specific_template, specific_selector)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):

        specific_resource = request.POST.get('resource', None)
        new = request.POST.get('new-resource', None)
        specific_selector, specific_template = self.selector_current(specific_resource)

        resource_list = POSSIBLE_RESOURCE.get(specific_resource, None)

        if resource_list is not None:
            resource_list = resource_list['elements']()
            specific_selector['elements'] = resource_list

        if new in ['1']:
            url = '/curator/new-resources?resource='+specific_resource
            return redirect(url)

        return render(request, specific_template, specific_selector)


class NewResourcesView(TemplateView):
    template_name = 'curator/new-resource.html'

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


class SchedulingView(TemplateView):
    template_name = 'curator/scheduling.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)
