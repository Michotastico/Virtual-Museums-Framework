import copy
import os

import re

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import IntegrityError
from django.db import transaction
from django.shortcuts import render, redirect

# Create your views here.
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.forms import ImageForm, TemplateForm, ModelForm, MusicForm, VideoForm
from Apps.Curator.models.resources import ExternalMusic, ExternalImage, ExternalModel, ExternalVideo
from Apps.Curator.models.rooms import Room
from Apps.Curator.models.opinions import Opinion
from Apps.Curator.models.scheduling import Exposition


class IndexView(TemplateView):
    template_name = 'curator/index.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)


@transaction.atomic
def confirm_opinion(key):
    opinion = Opinion.objects.get(hash_key=key)
    if opinion.validated:
        return False
    opinion.validated = True
    opinion.save()
    return True


class OpinionHashView(TemplateView):
    template_name = 'common-web/opinion_confirmation.html'

    def get(self, request, *a, **ka):
        hash_value = request.GET.get('key', None)
        results = {'title': 'Confirmation Error',
                   'body': 'The opinion you are trying to confirm is invalid or the code has expired.'}

        if hash_value is not None:
            if confirm_opinion(hash_value):
                results = {'title': 'Confirmation Successful!',
                           'body': 'Thanks for submitting your opinion!'}

        return render(request, self.template_name, results)


@transaction.atomic
def get_rooms_names():
    room_list = list()
    rooms = Room.objects.all()
    for room in rooms:
        room_list.append(room.name)
    return room_list


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
                'options': [],
                'approved': '',
                'pending': ''}

    def get_current_selector(self):
        current_selector = copy.deepcopy(self.selector)
        rooms = get_rooms_names()
        for room in rooms:
            room_template = {'value': room, 'display': room, 'selected': ''}
            current_selector['options'].append(room_template)
        return current_selector

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        current_selector = self.get_current_selector()
        return render(request, self.template_name, current_selector)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        current_selector = self.get_current_selector()

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


@transaction.atomic
def get_music_names_id():
    music_list = list()
    all_music = ExternalMusic.objects.all()
    for music in all_music:
        music_list.append({'name': music.title, 'id': music.id})
    return music_list


class NewRoomsView(TemplateView):
    template_name = 'curator/new-rooms.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        selector = dict()
        selector['music_options'] = get_music_names_id()

        edit_room = request.GET.get('roomname', None)
        if edit_room is not None:
            room = Room.objects.get(name=edit_room)
            selector['current_name'] = edit_room
            selector['current_music'] = room.background_music.id
        return render(request, self.template_name, selector)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        selector = dict()
        selector['music_options'] = get_music_names_id()

        room_name = request.POST.get('roomname', None)
        music_id = request.POST.get('music', None)
        edit = request.POST.get('edit', None)

        if edit in ['1']:
            previous_room_name = request.POST.get('previousName', None)
            if previous_room_name is not None:
                room = Room.objects.get(name=previous_room_name)
                if room_name is not None:
                    room.name = room_name
                if music_id is not None:
                    room.background_music = ExternalMusic.objects.get(id=music_id)
                try:
                    room.save()
                    selector['success'] = True
                except IntegrityError:
                    selector['failure'] = True
            else:
                selector['failure'] = True
        else:

            if room_name is not None and music_id is not None:
                room = Room()
                room.name = room_name
                room.background_music = ExternalMusic.objects.get(id=music_id)
                try:
                    room.save()
                    selector['success'] = True
                except IntegrityError:
                    selector['failure'] = True
            else:
                selector['failure'] = True

        return render(request, self.template_name, selector)


class RoomsView(TemplateView):
    template_name = 'curator/rooms.html'
    selector = {'header': {'display': 'Select a Room from the list:',
                           'selected': 'selected'}, 'options': []}

    def get_current_selector(self):
        current_selector = copy.deepcopy(self.selector)
        rooms = get_rooms_names()
        for room in rooms:
            room_template = {'value': room, 'display': room, 'selected': ''}
            current_selector['options'].append(room_template)
        return current_selector

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        current_selector = self.get_current_selector()

        return render(request, self.template_name, current_selector)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        current_selector = self.get_current_selector()

        current_room = request.POST.get('roomname', None)
        change_publish_status = request.POST.get('change_publish_status', None)
        edit_room = request.POST.get('edit', None)
        north_room = request.POST.get('north', u'None')
        south_room = request.POST.get('south', u'None')
        west_room = request.POST.get('west', u'None')
        east_room = request.POST.get('east', u'None')

        if current_room is not None:

            current_selector['header']['selected'] = ''
            for option in current_selector['options']:
                if option['value'] == current_room:
                    option['selected'] = 'selected'
                    break

            if edit_room in ['1']:
                url = '/curator/new-rooms?roomname=' + current_room
                return redirect(url)

            current_room = Room.objects.get(name=current_room)

            if change_publish_status in ['1']:
                current_room.published = not current_room.published
                current_room.save()

            else:

                if north_room not in [u'None']:
                    connected_room = Room.objects.get(name=north_room)
                    current_room.north_room = connected_room

                if south_room not in [u'None']:
                    connected_room = Room.objects.get(name=south_room)
                    current_room.south_room = connected_room

                if west_room not in [u'None']:
                    connected_room = Room.objects.get(name=west_room)
                    current_room.west_room = connected_room

                if east_room not in [u'None']:
                    connected_room = Room.objects.get(name=east_room)
                    current_room.east_room = connected_room
                current_room.save()

            room_data = dict()
            room_data['name'] = current_room.name
            room_data['published'] = current_room.published
            room_data['popularity'] = current_room.popularity
            if current_room.north_room is not None:
                room_data['connection_north'] = {'name': current_room.north_room.name}
            if current_room.south_room is not None:
                room_data['connection_south'] = {'name': current_room.south_room.name}
            if current_room.west_room is not None:
                room_data['connection_west'] = {'name': current_room.west_room.name}
            if current_room.east_room is not None:
                room_data['connection_east'] = {'name': current_room.east_room.name}
            current_selector['current_room'] = room_data

        return render(request, self.template_name, current_selector)


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


@transaction.atomic
def get_expositions():
    data = dict()
    exposition_list = list()
    expositions = Exposition.objects.all()

    for exposition in expositions:
        exposition_template = dict()
        exposition_template['id'] = exposition.id
        exposition_template['name'] = exposition.name
        if exposition.status:
            exposition_template['status'] = 'Active'
        else:
            exposition_template['status'] = 'Inactive'
        exposition_template['start_time'] = exposition.start_date
        exposition_template['end_time'] = exposition.end_date
        exposition_template['main_room'] = exposition.main_room.name

        exposition_list.append(exposition_template)

        data['expositions'] = exposition_list
    return data


class SchedulingView(TemplateView):
    template_name = 'curator/scheduling.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        expositions = get_expositions()
        return render(request, self.template_name, expositions)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        change_status = request.POST.get('changing_status', None)
        exposition_id = request.POST.get('id_exposition', None)
        editing = request.POST.get('editing', None)

        if editing in ['1'] and exposition_id is not None:
            return redirect('/curator/scheduling-exposition?id=' + exposition_id)

        if change_status in ['1'] and exposition_id is not None:
            exposition = Exposition.objects.get(id=exposition_id)
            exposition.status = not exposition.status
            exposition.save()

        expositions = get_expositions()

        return render(request, self.template_name, expositions)


class SchedulingExpositionView(TemplateView):
    template_name = 'curator/scheduling-exposition.html'
    default_selector = {'header': 'Select a Room:', 'options': []}

    def get_current_selector(self):
        current_selector = copy.deepcopy(self.default_selector)
        rooms = get_rooms_names()
        for room in rooms:
            room_template = {'value': room, 'display': room}
            current_selector['options'].append(room_template)
        return current_selector

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        selector = self.get_current_selector()
        editing_id = request.GET.get('id', None)

        if editing_id is not None:
            exposition = Exposition.objects.get(id=editing_id)
            selector['current_exposition'] = {'id': editing_id,
                                              'name': exposition.name,
                                              'room': exposition.main_room.name,
                                              'initial': exposition.start_date,
                                              'end': exposition.end_date}
        return render(request, self.template_name, selector)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        selector = self.get_current_selector()

        name = request.POST.get('name', None)
        room = request.POST.get('room', None)
        start_date = request.POST.get('initial', None)
        end_date = request.POST.get('end', None)

        id_editing = request.POST.get('id_exposition', None)

        try:
            if start_date is not None:
                start_date = datetime.strptime(start_date, "%d/%m/%Y")
            if end_date is not None:
                end_date = datetime.strptime(end_date, "%d/%m/%Y")
        except ValueError as err:
            print err
            selector['failure'] = True
            return render(request, self.template_name, selector)

        if name is not None \
                and room is not None \
                and start_date is not None \
                and end_date is not None:
            if id_editing is not None:
                exposition = Exposition.objects.get(id=id_editing)
            else:
                exposition = Exposition()
            exposition.name = name
            exposition.start_date = start_date
            exposition.end_date = end_date

            room = Room.objects.get(name=room)
            exposition.main_room = room

            try:
                exposition.save()
                selector['success'] = True
            except IntegrityError:
                selector['failure'] = True
        else:
            selector['failure'] = True
        return render(request, self.template_name, selector)


class CuratorAccount(TemplateView):
    template_name = 'curator/curator-account.html'

    @method_decorator(login_required(login_url='/auth/login'))
    def get(self, request, *a, **ka):
        return render(request, self.template_name)

    @method_decorator(login_required(login_url='/auth/login'))
    def post(self, request, *a, **ka):
        modifications = {'error': [], 'success': []}
        user = request.user

        fullname = request.POST.get('name', '')
        email = request.POST.get('email', '')

        new_password = request.POST.get('new-password', '')
        confirm_password = request.POST.get('confirm-password', '')

        password = request.POST.get('password', '')

        if len(new_password) > 0:
            if len(confirm_password) > 0\
                    and new_password == confirm_password:
                if len(password) > 0 and user.check_password(password):
                    user.set_password(new_password)
                    modifications['success'].append('Successful password change.')
                else:
                    modifications['error'].append('Incorrect password.')
            else:
                modifications['error'].append('Passwords mismatch.')

        if len(fullname) > 0:
            try:
                first, last = fullname.split(" ", 1)
                user.first_name = first
                user.last_name = last
                modifications['success'].append('Successful name change')
            except ValueError:
                modifications['error'].append('Name must have at least first and last name.')

        if len(email) > 0:
            try:
                validate_email(email)
                user.email = email
                modifications['success'].append('Successful email change')
            except ValidationError:
                modifications['error'].append('Wrong email structure.')

        if len(modifications['error']) != 0:
            modifications['success'] = []
        elif len(modifications['success']) < 1:
            modifications['error'].append('No changes was applied')
        else:
            user.save()
        return render(request, self.template_name, modifications)