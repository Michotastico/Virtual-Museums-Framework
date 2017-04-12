from datetime import datetime

import copy
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from Apps.Curator.models.museums import Room
from Apps.Curator.models.scheduling import Exposition
from Apps.Curator.views.opinions import get_rooms_names


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