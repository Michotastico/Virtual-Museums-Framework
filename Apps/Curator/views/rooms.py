import copy
from django.contrib.auth.decorators import login_required
from django.db import transaction, IntegrityError
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.models.museums import Room
from Apps.Curator.models.resources import ExternalMusic
from Apps.Curator.views.opinions import get_rooms_data


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
        rooms = get_rooms_data()
        for room in rooms:
            room_template = {'value': room['name'], 'display': room['name'], 'selected': ''}
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